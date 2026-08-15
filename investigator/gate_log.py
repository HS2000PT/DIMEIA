"""Funil de gates — onde é que cada ticker morreu, em cada varredura.

**Porque existe.** `docs/evaluation/alert_funnel.md` mostra o resultado agregado do funil
(944 manchetes relevantes → 42 alertas) e um facto que salta à vista: cinco dos dez tickers
receberam ZERO alertas apesar de 135 (AAPL), 91 (AMZN), 83 (NFLX), 75 (MSFT) e 71 (GOOGL)
manchetes relevantes. A pergunta óbvia — *qual dos gates os matou?* — não tinha resposta:
o registo de decisões (`triage/postval.py`) só é escrito DEPOIS dos gates de frescura e de
similaridade, por isso tudo o que morre antes nunca era registado. Os dados retroativos não
existem; este módulo garante que passam a existir.

Puro: só constrói e resume registos. Quem os persiste (e onde) é `scripts/run_alerts.py`.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

# Etapas do funil, pela ordem em que o runner as aplica. A ordem importa: é a ordem do
# relatório e a ordem em que um ticker pode "morrer".
STAGES: tuple[str, ...] = (
    "no_news",            # a fonte não devolveu nada para este ticker
    "none_relevant",      # veio notícia, mas nenhuma passou o filtro de relevância
    "stale",              # a mais recente relevante é antiga demais (max_age_days)
    "weak_precedent",     # nenhum precedente com cosseno >= min_similarity
    "triage_suppressed",  # o modelo aprendido pontuou abaixo de min_materiality
    "error",              # exceção no processamento deste ticker (fail-open)
    # ── as três abaixo acontecem DEPOIS da varredura, no `filter_new_alerts` ──────
    # ⚠️ Existem porque a sua ausência fazia o ecrã mentir. O `_gate()` corre dentro do
    # `scan_news`; o tecto diário, a escada de materialidade e a quase-repetição correm a
    # seguir, e nada re-etiquetava o que elas suprimiam. Resultado: `alerted` queria dizer
    # "sobreviveu à varredura" e o screener traduzia-o para **"Alert sent"** — dizendo ao
    # utilizador que um alerta tinha sido enviado quando não tinha, na vista cuja razão de
    # existir é tornar o silêncio inspeccionável.
    "daily_cap",          # o tecto de alertas/ticker/dia já estava cheio
    "ladder_floor",       # o k-ésimo alerta do dia exigia P mais alto do que este tem
    "duplicate_story",    # a mesma história noutras palavras, já alertada hoje
    # ⚠️ E esta faltava, pela MESMA razão, e é a que mais distorcia a contagem. A supressão
    # "esta manchete exacta já foi alertada hoje" fazia `continue` sem registar nada, ao
    # contrário das três acima. Com o ciclo de 60 s a mesma manchete é reavaliada todos os
    # minutos e passava a contar como `alerted` de cada vez. Medido a 2026-08-15: **330
    # registos `alerted` num dia em que o canal recebeu 4 mensagens** — a vista que existe
    # para tornar as decisões inspeccionáveis exagerava por perto de duas ordens de grandeza.
    "already_sent",       # esta manchete exacta já tinha sido entregue hoje
    # ⚠️ O ORÇAMENTO GLOBAL DO DIA, e a razão de existir é medida.
    # Até 2026-08-15 o volume era controlado por um limiar fixo sobre o score da triagem.
    # Medido sobre 4366 decisões reais: em 84% delas o resultado estava determinado pela
    # EMPRESA antes de se ler a manchete (três empresas passavam sempre, cinco nunca), porque
    # dentro de cada empresa o score quase não varia. O limiar controlava o volume
    # seleccionando tickers, não notícias.
    # O orçamento substitui-o pela política que a própria dissertação AVALIA — as k melhores
    # do dia — fechando uma divergência entre o que é medido e o que é implantado.
    "daily_budget",       # o orçamento global de alertas do dia já estava gasto
    "alerted",            # sobreviveu a tudo E foi mesmo entregue
)

_TERMINAL_OK = "alerted"


@dataclass(frozen=True)
class GateRecord:
    """Um ticker, uma varredura, a etapa onde parou.

    `detail` guarda o número que justificou a paragem (ex.: "sim 0.31 < 0.45") — é o que
    transforma uma contagem numa explicação defensável."""

    date: str
    ticker: str
    stage: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError(f"etapa desconhecida: {self.stage!r} (esperado: {STAGES})")


def summarise(records: list[GateRecord]) -> dict[str, int]:
    """Contagem por etapa, com TODAS as etapas presentes (zeros incluídos).

    Os zeros são deliberados: um relatório onde a etapa simplesmente desaparece quando não
    dispara esconde precisamente a informação que se quer ler."""
    counts = Counter(r.stage for r in records)
    return {stage: counts.get(stage, 0) for stage in STAGES}


def per_ticker(records: list[GateRecord]) -> dict[str, dict[str, int]]:
    """Contagem por ticker → etapa. Responde a 'o que mata a AAPL?' diretamente."""
    out: dict[str, dict[str, int]] = {}
    for r in records:
        out.setdefault(r.ticker, {stage: 0 for stage in STAGES})[r.stage] += 1
    return out


def attrition_table(records: list[GateRecord]) -> list[tuple[str, int, str]]:
    """Por ticker: (ticker, nº de varreduras que alertaram, etapa que mais o matou).

    Ordenado por alertas ascendente — os tickers silenciosos aparecem primeiro, que é
    exatamente a lista que interessa investigar."""
    rows: list[tuple[str, int, str]] = []
    for ticker, counts in per_ticker(records).items():
        alerted = counts[_TERMINAL_OK]
        blockers = {s: n for s, n in counts.items() if s != _TERMINAL_OK and n > 0}
        top = max(blockers, key=lambda s: blockers[s]) if blockers else "-"
        rows.append((ticker, alerted, top))
    return sorted(rows, key=lambda r: (r[1], r[0]))


def append_jsonl(records: list[GateRecord], path: str | Path, max_entries: int = 20000,
                 max_days: int = 3) -> None:
    """Acrescenta ao ficheiro e apara. Fail-open: um erro aqui nunca pode travar um ciclo.

    ⚠️ A retenção é por **DIAS**, e o tecto de linhas é só uma rede de segurança.

    O tecto era de 5000 linhas, e foi dimensionado quando o sistema corria num agendador de
    30 em 30 minutos: 12 tickers x 48 ciclos = ~576 registos por dia, ou seja ~8 dias de
    história. Com o ciclo de 60 segundos são ~1440 ciclos por dia, **30x mais**, e o mesmo
    tecto passou a guardar **menos de um dia** — medido a 2026-08-15: as 5000 linhas do
    ficheiro publicado eram todas do próprio dia.

    Isso esvazia a única vista que existe para tornar o silêncio do sistema inspeccionável.
    Uma retenção contada em linhas muda de significado sempre que a cadência muda; contada em
    dias, não muda. Daí a ordem: apara-se primeiro por dia, e o tecto de linhas só actua se um
    dia sozinho for anormalmente grande.

    ⚠️ **A restrição que fixa estes números não é o disco, é a PUBLICAÇÃO.** O ficheiro é
    republicado na branch de dados a cada ciclo de 60 s, portanto o custo cresce com o
    tamanho e não com a idade. Três dias a ~9000 registos/dia (a taxa medida) cabem
    folgadamente nos 20000, e o ficheiro fica na ordem dos 2 MB. Guardar uma semana seria
    honesto em retenção e desonesto em custo, e a escolha fica escrita em vez de parecer
    arbitrária.
    """
    if not records:
        return
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        existing = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
        new = [json.dumps(asdict(r), ensure_ascii=False) for r in records]
        combined = existing + new

        if max_days > 0:
            dias = []
            for linha in combined:
                try:
                    d = json.loads(linha).get("date")
                except (json.JSONDecodeError, AttributeError):
                    continue
                if d and d not in dias:
                    dias.append(d)
            if len(dias) > max_days:
                manter = set(sorted(dias)[-max_days:])
                filtradas = []
                for linha in combined:
                    try:
                        if json.loads(linha).get("date") in manter:
                            filtradas.append(linha)
                    except json.JSONDecodeError:
                        continue  # linha corrompida: não sobrevive à aparagem
                combined = filtradas

        if max_entries > 0:
            combined = combined[-max_entries:]
        p.write_text("\n".join(combined) + "\n", encoding="utf-8")
    except OSError:
        return


def load_jsonl(path: str | Path) -> list[GateRecord]:
    """Lê o funil; ficheiro em falta ou linhas inválidas não são erro (fail-open)."""
    p = Path(path)
    if not p.exists():
        return []
    out: list[GateRecord] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            out.append(GateRecord(**{k: payload[k] for k in ("date", "ticker", "stage")
                                     if k in payload},
                                  detail=str(payload.get("detail", ""))))
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            continue
    return out
