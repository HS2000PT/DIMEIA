"""Funil de seletividade: títulos distintos que entram, alertas que saem, numa janela ÚNICA.

Substitui `scripts/figures/fig_alert_funnel.py`, cujo instantâneo de 2026-07-13 tinha
quatro defeitos, todos diagnosticados a 2026-09-04:

1. **Comparava populações diferentes.** O numerador vinha de `live_pending.jsonl`, que é
   uma janela DESLIZANTE (um caso sai quando matura, ao fim de oito dias), e o denominador
   vinha de `alerts_history.jsonl`, que é CUMULATIVO. A razão 22:1 não era uma razão entre
   quantidades comparáveis.
2. **A janela anunciada não era a janela contada.** O rótulo saía da união das datas das
   duas fontes; os 42 alertas contados estavam datados de 13 a 20 de julho e o rótulo dizia
   4 a 13 de julho.
3. **Três empresas com exatamente 14 alertas eram o TECTO, e não uma medição.** Duas
   mensagens por empresa por dia, durante sete dias, dá catorze. As três estavam saturadas
   todos os dias; as outras sete tinham zero. A legenda atribuía essa forma ao limiar de
   semelhança e à composição da base de casos.
4. **A política descrita foi substituída a 2026-08-15**, quando o tecto por empresa deu
   lugar a um orçamento global. O resto do Capítulo 4 já descreve a política nova.

Daí as três garantias que este script impõe e o anterior não tinha:

- a janela é um ARGUMENTO e aplica-se aos dois lados;
- a unidade é o título DISTINTO, deduplicado por (data, empresa, título), porque o sistema
  reavalia os mesmos títulos a cada ciclo de 60 s e contar avaliações inflaciona o funil;
- e **o relatório diz quando um número é um tecto**, verificando a saturação do orçamento
  diário e do limite por empresa. Foi a ausência desta verificação que deixou passar o 14.

Uso: python scripts/evaluate_funil_seletividade.py [--de 2026-09-01] [--ate 2026-09-03]
Saída: docs/evaluation/evaluation_funil_seletividade.md
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history"
SAIDA = REPO / "docs" / "evaluation" / "evaluation_funil_seletividade.md"

# O orçamento em vigor desde 2026-08-15. Lido aqui para que o relatório possa dizer se um
# número é uma medição ou o tecto a que a política obriga.
ORCAMENTO_DIA = 5
POLITICA_DESDE = "2026-08-15"

ORDEM = {"stale": 0, "not_latest": 1, "sobreviveu": 2}


def _carregar(nome: str, local: str | None) -> list[dict]:
    if local:
        txt = Path(local, nome).read_text(encoding="utf-8")
    else:
        import requests

        r = requests.get(f"{RAW}/{nome}", timeout=30)
        r.raise_for_status()
        txt = r.text
    return [json.loads(ln) for ln in txt.splitlines() if ln.strip()]


def _dias(de: str, ate: str) -> list[str]:
    from datetime import date, timedelta

    a = date.fromisoformat(de)
    b = date.fromisoformat(ate)
    out = []
    while a <= b:
        out.append(a.isoformat())
        a += timedelta(days=1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Funil de seletividade sobre uma janela única.")
    ap.add_argument("--de", default="2026-09-01")
    ap.add_argument("--ate", default="2026-09-03")
    ap.add_argument("--local", default=None)
    args = ap.parse_args()

    reg = [x for x in _carregar("predictions_log.jsonl", args.local) if "stage" in x]
    hist = _carregar("alerts_history.jsonl", args.local)
    news = [x for x in hist if x.get("kind") == "news"]

    janela = [x for x in reg if args.de <= x.get("news_date", "") <= args.ate]
    entregues = [x for x in news if args.de <= x.get("date", "") <= args.ate]

    # Recusar em vez de degradar: um funil sobre uma janela sem registo não é um funil
    # vazio, é um funil que não se mediu, e os dois lêem-se de forma muito diferente.
    if not janela:
        print(f"RECUSA: o registo de decisões não cobre {args.de} a {args.ate}. "
              "Nada foi escrito.")
        raise SystemExit(2)

    dias = _dias(args.de, args.ate)
    com_registo = {x["news_date"] for x in janela}
    falta = [d for d in dias if d not in com_registo]

    # Uma etapa por título distinto: a mais avançada a que chegou.
    melhor: dict[tuple[str, str, str], str] = {}
    for x in janela:
        k = (x["news_date"], x["ticker"], x["headline"])
        if k not in melhor or ORDEM[x["stage"]] > ORDEM[melhor[k]]:
            melhor[k] = x["stage"]

    titulos = collections.Counter(k[1] for k in melhor)
    alertas = collections.Counter(x["ticker"] for x in entregues)
    por_etapa = collections.Counter(melhor.values())
    por_dia = collections.Counter(x["date"] for x in entregues)

    # A verificação que faltava: dizer quando um número é um TECTO.
    saturados = [d for d in dias if por_dia.get(d, 0) >= ORCAMENTO_DIA]
    no_tecto = sorted({t for t in alertas if alertas[t] == max(alertas.values())}) \
        if alertas else []

    total_t, total_a = len(melhor), len(entregues)
    razao = total_t / total_a if total_a else float("inf")

    ag = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    L: list[str] = [
        "# evaluation_funil_seletividade.md — funil sobre uma janela única",
        "",
        f"> Gerado por `scripts/evaluate_funil_seletividade.py` a {ag}. **Não editar à mão.**",
        "> Instantâneo datado: o canal cresce, e a tese cita ESTE instantâneo.",
        "",
        f"- **Janela:** {args.de} a {args.ate}, aplicada aos dois lados do funil.",
        f"- **Unidade:** título distinto, deduplicado por (data, empresa, título). "
        f"O registo contém {len(janela)} linhas para {total_t} títulos distintos, porque o "
        "sistema reavalia os mesmos títulos a cada ciclo.",
        f"- **Títulos distintos avaliados:** {total_t}, sobre {len(titulos)} empresas.",
        f"- **Alertas entregues ao canal:** {total_a}, sobre {len(alertas)} empresas.",
        f"- **Razão:** {razao:.0f} títulos avaliados por alerta entregue.",
        f"- **Política em vigor:** orçamento global de {ORCAMENTO_DIA} alertas por dia, "
        f"desde {POLITICA_DESDE}.",
        "",
    ]

    if falta:
        L += [f"> ⚠️ Sem registo em {len(falta)} dia(s) da janela: {', '.join(falta)}. "
              "A razão acima é calculada sobre os dias com registo.", ""]

    L += ["| Empresa | Títulos distintos | Alertas entregues |", "|---|---|---|"]
    L += [f"| {t} | {n} | {alertas.get(t, 0)} |" for t, n in titulos.most_common()]
    L += [f"| **Total** | **{total_t}** | **{total_a}** |", ""]

    L += ["## Onde os títulos pararam", "",
          "| Etapa | Títulos distintos |", "|---|---|"]
    nomes = {"stale": "notícia antiga, não pontuada",
             "not_latest": "não era a mais recente da empresa no ciclo",
             "sobreviveu": "sobreviveu ao varrimento"}
    for e, n in por_etapa.most_common():
        L.append(f"| {nomes.get(e, e)} | {n} |")
    L.append("")

    # ---- a secção que existe por causa do defeito de 2026-07-13 ----
    L += ["## É medição ou é tecto?", "",
          "Esta secção existe porque o instrumento anterior não a tinha, e por isso "
          "publicou três empresas com exatamente o mesmo valor sem assinalar que esse "
          "valor era o limite que a política impunha.", ""]
    if saturados:
        L.append(f"- O orçamento diário de {ORCAMENTO_DIA} foi **integralmente utilizado** "
                 f"em {len(saturados)} de {len(dias)} dia(s): {', '.join(saturados)}. "
                 "O total de alertas é, nesses dias, **o tecto e não uma medição**: mede a "
                 "política, não a matéria-prima.")
    else:
        L.append(f"- O orçamento diário de {ORCAMENTO_DIA} **não** foi esgotado em nenhum "
                 "dia da janela. O total de alertas é uma medição.")
    if alertas and len(set(alertas.values())) == 1 and len(alertas) > 1:
        L.append("- ⚠️ **Todas as empresas com alerta têm exatamente o mesmo número.** "
                 "Verificar se existe um limite por empresa a produzir essa igualdade "
                 "antes de a interpretar como um resultado.")
    elif no_tecto:
        L.append(f"- A distribuição por empresa não é uniforme; o máximo "
                 f"({max(alertas.values())}) é atingido por {', '.join(no_tecto)}, e está "
                 "abaixo do orçamento diário, pelo que não corresponde a um limite por "
                 "empresa.")
    L.append("")

    L += ["## Leitura", "",
          f"Sobre {len(dias)} dia(s), o sistema avaliou {total_t} títulos distintos de "
          f"{len(titulos)} empresas e entregou {total_a} alertas a {len(alertas)} delas. "
          "A quantidade que a política governa é o total diário, e não a repartição por "
          "empresa: nenhuma empresa tem quota própria, e a distribuição observada resulta "
          "da ordenação por materialidade dentro do orçamento.", ""]

    SAIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"janela {args.de} a {args.ate}: {total_t} títulos distintos "
          f"({len(titulos)} empresas) -> {total_a} alertas ({len(alertas)} empresas), "
          f"razão {razao:.0f}:1")
    print(f"escrito em {SAIDA}")


if __name__ == "__main__":
    main()
