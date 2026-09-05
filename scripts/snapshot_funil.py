"""O funil de um dia, repartido por porta, lido do registo de decisões de produção.

⚠️ POR QUE É QUE ESTE SCRIPT EXISTE. A Tabela~\\ref{tab:sis_funil} do Capítulo 4 é o único
resultado da dissertação que não tinha um ficheiro por trás: os números foram lidos do
`gate_log.jsonl` num dia concreto e escritos directamente na tese. O apêndice já declarava que a
medição não é regenerável --- o registo guarda três dias, porque é republicado a cada ciclo e o
custo é de publicação --- mas declarar que um número não se regenera não é o mesmo que mostrar de
onde ele veio. Este script mostra.

O QUE ELE NÃO RESOLVE, e fica dito aqui em vez de se descobrir depois: correr isto hoje dá os
últimos três dias, não o dia de 15 de agosto de 2026 que a tese cita. Esse dia saiu do registo e
não volta. O que este ficheiro faz é (a) deixar o dia da tese escrito como leitura datada, e (b)
tornar reproduzível o procedimento que o produziu, para que qualquer dia futuro tenha origem.

⚠️ E A ARMADILHA DE LEITURA, que é a razão pela qual a coluna se chama "avaliações" e não
"notícias". O sistema reavalia os mesmos títulos de 60 em 60 segundos. Um título que sobreviva a
todas as portas e seja travado no fim conta uma vez por minuto, não uma vez. Portanto estes
números medem **onde o tempo do sistema é gasto**, e não quantas histórias distintas cada porta
deitou fora. Ler a linha maior como "é esta a porta que mais corta" seria o mesmo erro que a
sessão 58 corrigiu no `already_sent`, cometido outra vez pelo lado da interpretação.

    python scripts/snapshot_funil.py            # lê a branch de dados
    python scripts/snapshot_funil.py --local    # lê a cópia local, se existir
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "evaluation" / "funil_por_porta.md"
URL = ("https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/gate_log.jsonl")

# O nome que cada etapa tem na tese, e o que ela quer dizer. A ordem é a do funil.
PORTAS: list[tuple[str, str, str]] = [
    ("stale", "Título velho", "publicado há mais de dois dias"),
    ("weak_precedent", "Sem precedente forte", "nenhum caso passado acima do chão de semelhança"),
    ("triage_suppressed", "Abaixo do piso da triagem", "o modelo pontuou abaixo do mínimo"),
    ("ladder_floor", "Piso escalonado", "o segundo alerta do dia exigia pontuação mais alta"),
    ("duplicate_story", "A mesma história", "já contada por outras palavras"),
    ("daily_budget", "Orçamento esgotado", "o dia já tinha gasto os cinco alertas"),
    ("already_sent", "Já avisei hoje", "este título já saiu neste dia"),
    ("no_news", "Sem notícias", "a fonte não devolveu nada para esta empresa"),
    ("none_relevant", "Nada relevante", "nenhum título mencionava a empresa"),
    ("error", "Erro", "a varredura falhou para esta empresa"),
    ("alerted", "Sobreviveu às portas", "chegou ao fim do funil"),
]

# A leitura que a dissertacao cita, e que ja nao esta no registo. Fica escrita para que o numero
# impresso tenha origem, e marcada como nao regeneravel para ninguem a tentar reproduzir.
TESE = {
    "dia": "2026-08-15",
    "nota": ("parte de um dia, lida no momento em que o registo foi consultado; "
             "os 333 de `alerted` são de ANTES de a etapa `already_sent` existir"),
    "contagens": {"weak_precedent": 2994, "triage_suppressed": 1194, "ladder_floor": 269,
                  "duplicate_story": 249, "daily_budget": 21, "alerted": 333},
    "entregues": 5,
}


def le(local: bool) -> list[dict]:
    if local:
        p = RAIZ / "data" / "gate_log.jsonl"
        if not p.exists():
            raise SystemExit(f"nao existe: {p}")
        bruto = p.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=60) as r:  # noqa: S310
            bruto = r.read()
    fora = []
    for linha in bruto.decode("utf-8", "replace").splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            fora.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return fora


def tabela(contagens: collections.Counter, entregues: int | None) -> list[str]:
    total = sum(contagens.values())
    linhas = ["| Onde morreu | Avaliações | % | O que é |", "|---|---:|---:|---|"]
    for chave, nome, o_que in PORTAS:
        n = contagens.get(chave, 0)
        if not n:
            continue
        linhas.append(f"| {nome} | {n:,} | {100 * n / total:.1f}% | {o_que} |".replace(",", " "))
    linhas.append(f"| **Total avaliado** | **{total:,}** | | |".replace(",", " "))
    if entregues is not None:
        linhas.append(f"| **Mensagens entregues** | **{entregues}** | | o orçamento do dia |")
    return linhas


def _dias_ja_escritos() -> dict[str, list[str]]:
    """Os dias que o ficheiro já tem, para não os perder ao regenerar."""
    if not SAIDA.exists():
        return {}
    partes = re.split(r"\n### (\d{4}-\d{2}-\d{2})[^\n]*\n", SAIDA.read_text(encoding='utf-8'))
    fora: dict[str, list[str]] = {}
    for i in range(1, len(partes), 2):
        linhas = partes[i + 1].split(chr(10))
        corte = next((k for k, ln in enumerate(linhas)
                      if ln.startswith('---') or ln.startswith('**Leitura')),
                     len(linhas))
        fora[partes[i]] = [ln for ln in linhas[:corte] if ln.strip()]
    return fora


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="ler data/gate_log.jsonl em vez da branch")
    args = ap.parse_args()

    registos = le(args.local)
    por_dia: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in registos:
        por_dia[str(r.get("date", ""))[:10]][r.get("stage", "?")] += 1

    out = ["# funil_por_porta.md — onde morre cada avaliação, por dia", "",
           "> Gerado por `scripts/snapshot_funil.py` a partir do `gate_log.jsonl` da branch de",
           "> dados `alerts-history`, a mesma fonte que a página serve. **Não editar à mão.**",
           "",
           "⚠️ **A coluna chama-se _avaliações_ e não _notícias_, e a diferença decide a leitura.**",
           "O sistema reavalia os mesmos títulos de 60 em 60 segundos, portanto um título que",
           "sobreviva às portas e seja travado no fim conta uma vez por minuto. Estes valores",
           "medem",
           "**onde o tempo do sistema é gasto**, não quantas histórias distintas cada porta deitou",
           "fora. Ler a maior como *«é esta a porta que mais corta»* seria repetir, pelo lado",
           "da interpretação, o defeito que a sessão 58 corrigiu no código.", "",
           "⚠️ **O registo guarda três dias.** É republicado a cada ciclo, logo o custo é de",
           "publicação e não de armazenamento. Correr este comando amanhã dá outros dias.", "",
           "---", "",
           f"## A leitura que a dissertação cita — {TESE['dia']} (NÃO REGENERÁVEL)", "",
           f"Esta é a Tabela~`tab:sis_funil` do Capítulo 4. É {TESE['nota']}. O dia já saiu do",
           "registo e não volta; fica escrito aqui para que o número impresso tenha origem.", ""]
    out += tabela(collections.Counter(TESE["contagens"]), TESE["entregues"])
    # ⚠️ ACUMULAR, NÃO SUBSTITUIR. O registo guarda três dias e este gerador reescrevia
    # o ficheiro inteiro: corrê-lo em setembro apagava os dias de agosto, e a dissertação
    # cita a AMPLITUDE do que cada porta elimina entre dias, que só existe se os dias
    # forem guardados. É a classe da sessão 57 -- um artefacto regenerável regenerado
    # noutro dia é indistinguível de um correcto, e nada avisa.
    ja = _dias_ja_escritos()
    novos = {dia: tabela(por_dia[dia], None) for dia in sorted(por_dia)}
    ja.update(novos)
    out += ["", "---", "",
            f"## O que o mesmo comando deu, dia a dia ({len(ja)} dias acumulados)", "",
            "Cada dia entra quando o comando corre e **nunca é retirado**; o registo de",
            "produção só guarda três dias de cada vez, pelo que um dia perdido não volta.",
            ""]
    for dia in sorted(ja):
        marca = "" if dia in novos else "  *(dia anterior, conservado)*"
        out += [f"### {dia}{marca}", ""] + ja[dia] + [""]
    out += ["**Leitura honesta do que mudou.** No dia citado pela dissertação o corte estava",
            "repartido pelas portas de evidência; nos dias acima é o **orçamento diário** que",
            "domina, e por uma razão de contagem e não de política: gastos os cinco alertas, cada",
            "ciclo de 60 segundos volta a registar todas as candidatas nessa etapa até ao fim do",
            "dia. É o mesmo artefacto que a ressalva do topo descreve, e é a razão pela qual a",
            "dissertação cita um dia e não uma média.", ""]

    SAIDA.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"[ok] {SAIDA.relative_to(RAIZ)} — {len(registos)} registos, {len(por_dia)} dias")
    return 0


if __name__ == "__main__":
    sys.exit(main())
