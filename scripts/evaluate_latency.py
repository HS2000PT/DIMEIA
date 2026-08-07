"""Onde está o tempo entre o facto e a notificação? — latência, decomposta e medida.

A PERGUNTA
----------
O aluno reportou o sintoma em uso real: *"fui notificado depois de a coisa já ter acontecido"*.
A explicação registada no projecto era que a mediana mostrada (208 min) estava contaminada pelo
histórico do cron do GitHub, medido em 1,5–2 h, e que a latência **actual** — com o worker do
Heroku a 60 s desde 2026-08-02 — seria muito melhor.

**Este script existe porque essa explicação era uma hipótese, e é falsa.** Separar as duas eras
não faz o número descer para minutos: desce de ~196 min para ~143 min. O ciclo de 60 s comprou
muito menos do que se assumiu, e o motivo só aparece quando se **decompõe** a latência em vez de
a medir de ponta a ponta.

DESENHO
-------
Cada alerta entregue tem, desde 2026-07-29, três carimbos (`investigator/alerts_history.py`):

    event_at ──── descoberta ────> detected_at ── pipeline ──> sent_at

- **descoberta** = `event_at → detected_at`: quanto tempo passou entre a publicação da manchete
  (hora que a própria fonte declara) e o ciclo que a viu. Aqui vivem a cadência do produtor, o
  atraso da fonte a listar a história, e a **idade da manchete mais recente que passa o filtro
  de relevância** — que não é a manchete mais recente do feed.
- **pipeline** = `detected_at → sent_at`: o nosso lado. Recuperação de precedentes, triagem,
  render e entrega ao Telegram.

Reporta-se a mediana e o p90 de cada componente, por era, e a decomposição diz qual das duas
domina. É a única forma de a afirmação "melhorámos a latência" ser verificável: encurtar o ciclo
só ajuda se o tempo estiver na descoberta *por causa da cadência* — e não está.

O QUE ISTO NÃO MEDE
-------------------
`event_at` é a hora de publicação **declarada pela fonte**, não o instante em que o facto
aconteceu no mundo. Um comunicado publicado 40 min depois do acontecimento conta como 0 min de
atraso nesta medição. Portanto os números aqui são um **limite inferior** da latência sentida, e
está dito assim no relatório: um número apresentado como mais do que é vale menos do que nenhum.

Alertas de mercado e resumos não entram — só notícias têm hora de publicação. Entradas sem
carimbos (histórico anterior a 2026-07-29) são excluídas em vez de estimadas.

USO
---
    python scripts/evaluate_latency.py
    python scripts/evaluate_latency.py --escrever
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from investigator.alerts_history import HistoryEntry, parse_jsonl_lines  # noqa: E402

# Fronteira das eras. Até aqui o produtor era o cron do GitHub Actions (best-effort, medido em
# 1,5–2 h entre corridas); a partir daqui o worker do Heroku corre a 60 s (sessão 44).
FRONTEIRA_WORKER = "2026-08-02"

_SAIDA = _RAIZ / "docs" / "evaluation" / "evaluation_latency.md"
_HIST_LOCAL = _RAIZ / "data" / "alerts_history.jsonl"
_BRANCH = "origin/alerts-history:alerts_history.jsonl"


def carregar_historico() -> list[HistoryEntry]:
    """Lê o histórico partilhado: ficheiro local se existir, senão a branch de dados.

    Falha ALTO e não aberto — ao contrário do caminho de produto, aqui um histórico vazio
    produziria um relatório de latência sobre nada, e isso é pior do que um erro.
    """
    if _HIST_LOCAL.exists():
        return parse_jsonl_lines(_HIST_LOCAL.read_text(encoding="utf-8").splitlines())
    try:
        bruto = subprocess.run(
            # `encoding` explícito: as manchetes trazem acentos e emoji, e o padrão do
            # Windows (cp1252) rebentaria a descodificar exactamente as linhas que interessam.
            ["git", "show", _BRANCH], cwd=_RAIZ, capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            f"Sem histórico: nem {_HIST_LOCAL} nem {_BRANCH} "
            f"({type(exc).__name__}). Corre `git fetch origin alerts-history` primeiro."
        ) from exc
    return parse_jsonl_lines(bruto.splitlines())


def _instante(carimbo: str) -> datetime | None:
    try:
        return datetime.fromisoformat(carimbo.replace("Z", "+00:00"))
    except ValueError:
        return None


@dataclass(frozen=True)
class Resumo:
    """Estatística de uma componente. `None` em vez de 0 quando não há amostra — um zero
    inventado aqui leria-se como 'instantâneo', o oposto da verdade."""

    n: int
    mediana: float | None
    p90: float | None
    minimo: float | None
    maximo: float | None

    @classmethod
    def de(cls, valores: list[float]) -> Resumo:
        if not valores:
            return cls(0, None, None, None, None)
        ordenados = sorted(valores)
        # p90 pelo método do índice mais próximo por baixo, explícito para o número ser
        # reproduzível sem depender da convenção de nenhuma biblioteca.
        idx = min(len(ordenados) - 1, int(0.9 * len(ordenados)))
        return cls(len(ordenados), statistics.median(ordenados), ordenados[idx],
                   ordenados[0], ordenados[-1])


def componentes(entradas: list[HistoryEntry]) -> dict[str, list[float]]:
    """Decompõe em minutos: total (facto→entrega), descoberta e pipeline.

    Só entradas com os carimbos necessários entram em cada componente — uma entrada pode
    contar para o total e não para a descoberta, e as contagens `n` dizem-no.
    """
    total: list[float] = []
    descoberta: list[float] = []
    pipeline: list[float] = []
    for e in entradas:
        seg = e.latency_seconds()
        if seg is not None:
            total.append(seg / 60)
        t_ev, t_det, t_env = (_instante(e.event_at), _instante(e.detected_at),
                             _instante(e.sent_at))
        if t_ev and t_det:
            descoberta.append((t_det - t_ev).total_seconds() / 60)
        if t_det and t_env:
            pipeline.append((t_env - t_det).total_seconds() / 60)
    return {"total": total, "descoberta": descoberta, "pipeline": pipeline}


def por_era(entradas: list[HistoryEntry], fronteira: str = FRONTEIRA_WORKER
            ) -> dict[str, list[HistoryEntry]]:
    """Divide pela data de ENVIO — é o produtor que muda, não o dia do evento."""
    cron = [e for e in entradas if e.sent_at and e.sent_at[:10] < fronteira]
    worker = [e for e in entradas if e.sent_at and e.sent_at[:10] >= fronteira]
    return {"cron (Actions, best-effort)": cron, f"worker 60 s (≥{fronteira})": worker}


def _fmt(r: Resumo, unidade: str = "min") -> str:
    if r.n == 0 or r.mediana is None:
        return "— (sem amostra)"
    if unidade == "s":
        return (f"{r.mediana * 60:.0f} s (p90 {r.p90 * 60:.0f} s, "
                f"máx {r.maximo * 60:.0f} s, n={r.n})")
    return f"{r.mediana:.0f} min (p90 {r.p90:.0f} min, máx {r.maximo:.0f} min, n={r.n})"


def relatorio(entradas: list[HistoryEntry]) -> str:
    com_carimbo = [e for e in entradas if e.event_at and e.sent_at]
    if not com_carimbo:
        raise SystemExit("Nenhuma entrada com event_at e sent_at — nada a medir.")
    janela = (min(e.sent_at for e in com_carimbo)[:10],
              max(e.sent_at for e in com_carimbo)[:10])
    geral = componentes(com_carimbo)
    r_total, r_desc, r_pipe = (Resumo.de(geral["total"]), Resumo.de(geral["descoberta"]),
                               Resumo.de(geral["pipeline"]))
    quota = (100 * r_desc.mediana / r_total.mediana
             if r_total.mediana and r_desc.mediana else float("nan"))

    linhas = [
        "# Latência facto → notificação, decomposta",
        "",
        "> Gerado por `python scripts/evaluate_latency.py --escrever`. Não editar à mão.",
        "",
        f"Histórico partilhado: **{len(entradas)} entradas**, das quais **{len(com_carimbo)}** "
        f"têm hora de publicação e de envio (só alertas de notícia as têm). "
        f"Janela de envio: {janela[0]} a {janela[1]}.",
        "",
        "## O resultado, e ele contradiz a explicação que estava registada",
        "",
        "| componente | mediana |",
        "|---|---|",
        f"| **total** (publicação → entrega) | {_fmt(r_total)} |",
        f"| descoberta (publicação → detecção) | {_fmt(r_desc)} |",
        f"| pipeline (detecção → entrega) | {_fmt(r_pipe, 's')} |",
        "",
        f"**A descoberta é {quota:.0f}% da mediana total. O nosso lado do sistema custa "
        f"{r_pipe.mediana * 60:.0f} s.**",
        "",
        "A hipótese que estava escrita no projecto era que a mediana mostrada estava "
        "contaminada pelo histórico do cron do GitHub Actions e que a latência actual seria "
        "muito melhor. Separando as duas eras:",
        "",
        "| era do produtor | total | descoberta | pipeline |",
        "|---|---|---|---|",
    ]
    for nome, grupo in por_era(com_carimbo).items():
        c = componentes(grupo)
        linhas.append(
            f"| {nome} | {_fmt(Resumo.de(c['total']))} | {_fmt(Resumo.de(c['descoberta']))} "
            f"| {_fmt(Resumo.de(c['pipeline']), 's')} |"
        )

    linhas += [
        "",
        "Passar de um cron best-effort de 1,5–2 h para um ciclo de 60 s **não** trouxe a "
        "latência para a ordem dos minutos. Encurtar o ciclo só paga se o tempo estiver na "
        "descoberta **por causa da cadência do produtor** — e não está.",
        "",
        "## Então onde está o tempo",
        "",
        "Com o worker a 60 s, uma manchete que esteja no feed é vista em menos de um minuto. "
        "O que a medição mostra é que, quando o alerta sai, a manchete **já é velha**, e há "
        "três causas possíveis, por ordem do que este número consegue distinguir:",
        "",
        "1. **A fonte lista tarde.** O Finnhub *company news* não é um canal em tempo real; "
        "uma história pode aparecer no feed horas depois da hora de publicação que ela própria "
        "declara. Isto é fora do nosso controlo e é a limitação já reportada em "
        "[`evaluation_news_coverage.md`](evaluation_news_coverage.md).",
        "2. **A manchete mais recente do feed não é a mais recente RELEVANTE.** O filtro de "
        "relevância exige menção da empresa e rejeita boilerplate de mercado. Numa amostra ao "
        "vivo (2026-08-07, 14 h UTC) o feed da NVDA trazia 250 manchetes com a mais recente às "
        "11:39, mas das 30 relevantes a mais recente era de **08:14** — mais de cinco horas "
        "antes. O alerta sai correctamente sobre a manchete certa; ela é que é velha.",
        "3. **O tecto diário já foi gasto** — ver a secção seguinte. Este é um defeito "
        "separado, e é o único dos três que **apaga** histórias em vez de as atrasar, portanto "
        "não aparece nesta medição: um alerta que nunca sai não tem `sent_at`.",
        "",
        "As três são diagnósticos diferentes e a primeira é a única que este histórico não "
        "consegue isolar sozinho: exigiria registar quando é que cada item apareceu no feed, "
        "não só quando foi publicado. Fica dito como o que é — **não medido** — em vez de "
        "atribuído por eliminação.",
        "",
        "## O tecto diário: um segundo defeito, encontrado a medir isto",
        "",
        "A investigação da latência destapou um defeito que não é de latência. A 2026-08-05 "
        "escreveu-se que o tecto diário passara a ser servido por **materialidade** em vez de "
        "por ordem de chegada. **Não passou.** A ordenação acrescentada vale dentro de um ciclo, "
        "e o scan de notícias emite **uma manchete por ticker por ciclo** — duas candidatas ao "
        "mesmo tecto (que é por ticker) nunca coexistem no lote, logo a ordenação nunca as pode "
        "reordenar. O teste que a validava comparava três manchetes do mesmo ticker numa só "
        "chamada, um cenário que a produção não sabe produzir.",
        "",
        "A correcção (2026-08-07) é um **piso escalonado**: o k-ésimo alerta de um ticker no dia "
        "exige um P(movimento anormal) maior. Os pisos são derivados do varrimento de política "
        "— τ*(R=1)=0,49 para o primeiro, τ*(R=0,5)=0,64 para o segundo, onde o custo dominante "
        "passa a ser a fadiga. Não há piso de \"última hora\" acima disso porque o score máximo "
        "observado está entre 0,65 e 0,66: seria código morto com aparência de rigor.",
        "",
        "**O que continua sem solução, e nenhum algoritmo online a tem:** o primeiro slot é gasto "
        "na primeira manchete que passe o gate, porque nesse momento a notícia da tarde ainda não "
        "existe. Não se reserva quota para uma história que ainda não se viu, nem se retira um "
        "alerta já entregue. O que se pode é tornar cada slot extra mais caro.",
        "",
        "## Limite inferior, não estimativa",
        "",
        "`event_at` é a hora que a **fonte declara**, não o instante do acontecimento no mundo. "
        "Um comunicado publicado 40 minutos depois do facto conta aqui como 0 minutos de "
        "atraso. Portanto todos os números acima são um **limite inferior** da latência que o "
        "utilizador sente.",
        "",
        "## Consequência para o produto",
        "",
        "O ganho de ciclo (1,5–2 h → 60 s) está medido e é real, mas é pequeno face ao total: "
        "a latência sentida é dominada por uma componente que não se compra com infra-estrutura. "
        "A afirmação defensável é **\"o sistema entrega em segundos o que a fonte lhe dá\"** "
        f"(pipeline {_fmt(r_pipe, 's')}), e não \"o sistema alerta em tempo quase real\".",
        "",
    ]
    return "\n".join(linhas) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escrever", action="store_true",
                   help=f"escreve {_SAIDA.relative_to(_RAIZ)}")
    args = p.parse_args()
    texto = relatorio(carregar_historico())
    if args.escrever:
        _SAIDA.parent.mkdir(parents=True, exist_ok=True)
        _SAIDA.write_text(texto, encoding="utf-8")
        print(f"escrito: {_SAIDA.relative_to(_RAIZ)}")
    else:
        print(texto)


if __name__ == "__main__":
    main()
