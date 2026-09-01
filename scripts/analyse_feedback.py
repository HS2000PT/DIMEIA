#!/usr/bin/env python3
"""Analisa os votos do canal e escreve `docs/evaluation/evaluation_feedback.md`.

## As regras estão escritas ANTES de existirem dados, e é essa a razão de este ficheiro existir

Com uma amostra pequena e recolhida em aberto, quem decide as regras depois de ver os números
consegue sempre encontrar um recorte que diga o que quer. As regras abaixo ficam fixadas agora,
com o ficheiro de votos vazio, e o relatório aplica-as sem exceção:

1. **N mínimo para reportar uma proporção: 20 votos efetivos.** Abaixo disso o relatório
   imprime as contagens e escreve, com todas as letras, que não reporta proporção. Uma
   percentagem sobre sete votos é um número que engana quem o lê, incluindo quem o escreveu.
2. **Um voto por pessoa por alerta.** O último substitui o anterior. As mudanças de opinião
   são contadas à parte, porque são interessantes e não são ruído.
3. **Salvaguarda do votante dominante.** Se uma só pessoa representar mais de 40% dos votos
   efetivos, a proporção é reportada duas vezes — com e sem essa pessoa — e o relatório diz
   que o fez. Num canal pequeno, um leitor entusiasta pode sozinho decidir o resultado.
4. **Nunca se escreve «significativo».** Não há teste de hipótese aqui, e não vai haver com
   este N. Intervalos de Wilson a 95%, e a palavra «piloto» em todo o lado.
5. **Sobreposição de intervalos recusa uma afirmação, nunca a sustenta.** Com intervalos
   sobrepostos escreve-se «não é possível distinguir», e nunca «são iguais».

## O que isto NÃO é

Não é o estudo de utilidade do protocolo moderado (`docs/study/`, `analyse_usefulness.py`).
Esse pergunta se a explicação é compreendida e se calibra a confiança, com sessões conduzidas e
um guião. Este pergunta uma coisa mais estreita: se os alertas que o sistema decidiu enviar
foram considerados úteis por quem os recebeu, sem moderação e sem contexto. São instrumentos
diferentes, com validades diferentes, e o relatório diz isso na primeira linha para que ninguém
os junte.

Uso:
    python scripts/analyse_feedback.py
    python scripts/analyse_feedback.py --votos data/feedback.jsonl
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
import sys  # noqa: E402

sys.path.insert(0, str(REPO))

from investigator import feedback_log as FL  # noqa: E402
from investigator.evaluation.proportions import wilson  # noqa: E402

DEFAULT_VOTOS = REPO / "data" / "feedback.jsonl"
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_feedback.md"

# ── Regras pré-registadas. Alterar qualquer uma destas depois de haver dados é um ato que
#    tem de ficar registado no ESTADO.md, com a data e a razão. ──────────────────────────
N_MINIMO = 20          # votos efetivos abaixo dos quais NÃO se reporta proporção
DOMINANCIA_MAX = 0.40  # acima disto, reporta-se também sem o votante dominante


def _pct(x: float) -> str:
    return "—" if x != x else f"{x * 100:.0f}%"


def _linha_proporcao(rotulo: str, k: int, n: int) -> str:
    if n < N_MINIMO:
        return (f"| {rotulo} | {k} de {n} | não reportada | "
                f"abaixo do mínimo pré-registado de {N_MINIMO} |")
    lo, hi = wilson(k, n)
    return (f"| {rotulo} | {k} de {n} | {_pct(k / n)} | "
            f"IC 95% de Wilson: {_pct(lo)}–{_pct(hi)} |")


def relatorio(registos: list[FL.FeedbackRecord]) -> str:
    efetivos = FL.votos_efetivos(registos)
    resumo = FL.resumo(registos)
    n = len(efetivos)
    uteis = sum(1 for r in efetivos.values() if r.acao == FL.UTIL)

    por_pessoa = Counter(v for v, _ in efetivos)
    dominante, n_dominante = (por_pessoa.most_common(1) or [("", 0)])[0]
    fracao_dominante = (n_dominante / n) if n else 0.0

    L: list[str] = []
    L.append("# Feedback do canal — piloto não moderado")
    L.append("")
    L.append("> **O que este documento é, e o que não é.** Mede se os alertas que o sistema "
             "decidiu enviar foram considerados úteis por quem os recebeu, através de dois "
             "botões na própria mensagem. Não é o estudo de utilidade do protocolo moderado "
             "(`docs/study/`), que pergunta se a explicação é compreendida e se calibra a "
             "confiança. São instrumentos diferentes e não se somam.")
    L.append("")
    L.append("> **Todas as regras de análise foram fixadas antes de existirem dados** e estão "
             "no cabeçalho de `scripts/analyse_feedback.py`. Nenhuma foi alterada depois.")
    L.append("")
    L.append(f"> Gerado por `scripts/analyse_feedback.py` a "
             f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.")
    L.append("")

    if not registos:
        L.append("## Ainda não há votos")
        L.append("")
        L.append("O ficheiro de votos está vazio. Não há nada a reportar, e a ausência de "
                 "dados não é um resultado de zero por cento — é a ausência de dados.")
        L.append("")
        return "\n".join(L) + "\n"

    L.append("## Dimensão da amostra")
    L.append("")
    L.append("| Medida | Valor |")
    L.append("|---|---|")
    L.append(f"| Votos registados | {resumo['votos_brutos']} |")
    L.append(f"| Votos efetivos (um por pessoa e alerta) | {resumo['votos_efetivos']} |")
    L.append(f"| Pessoas distintas | {resumo['pessoas']} |")
    L.append(f"| Alertas votados | {resumo['alertas_votados']} |")
    L.append(f"| Mudanças de voto | {resumo['mudancas_de_voto']} |")
    L.append("")

    L.append("## Resultado")
    L.append("")
    L.append("| Recorte | Contagem | Proporção | Nota |")
    L.append("|---|---|---|---|")
    L.append(_linha_proporcao("Alertas considerados úteis", uteis, n))

    if fracao_dominante > DOMINANCIA_MAX and n:
        sem = {k: v for k, v in efetivos.items() if k[0] != dominante}
        uteis_sem = sum(1 for r in sem.values() if r.acao == FL.UTIL)
        L.append(_linha_proporcao("O mesmo, sem o votante dominante", uteis_sem, len(sem)))
    L.append("")

    if fracao_dominante > DOMINANCIA_MAX:
        L.append(f"⚠️ **Salvaguarda do votante dominante aplicada.** Uma só pessoa representa "
                 f"{_pct(fracao_dominante)} dos votos efetivos, acima do limite pré-registado "
                 f"de {_pct(DOMINANCIA_MAX)}. A segunda linha da tabela mostra o mesmo cálculo "
                 f"sem essa pessoa. Se as duas linhas divergirem, a leitura a reportar é a "
                 f"segunda.")
        L.append("")

    if n < N_MINIMO:
        L.append(f"**Nenhuma proporção é reportada.** Há {n} votos efetivos e a regra "
                 f"pré-registada exige {N_MINIMO}. As contagens acima são o resultado, e são "
                 f"tudo o que esta amostra sustenta.")
    else:
        lo, hi = wilson(uteis, n)
        L.append(f"A proporção de alertas considerados úteis é de {_pct(uteis / n)}, com "
                 f"intervalo de confiança de Wilson a 95% entre {_pct(lo)} e {_pct(hi)}. "
                 f"A largura deste intervalo é a medida honesta do que {n} votos permitem "
                 f"afirmar, e é por isso que é reportada ao lado do valor central e nunca "
                 f"depois dele.")
    L.append("")

    L.append("## Ameaças à validade, e nenhuma delas é resolúvel com mais votos")
    L.append("")
    L.append("- **Autosseleção.** Vota quem quer. Quem acha um alerta indiferente tende a não "
             "carregar em nada, o que empurra a amostra para os dois extremos.")
    L.append("- **Ausência de contrafactual.** Não há um grupo que receba a variação de preço "
             "sem explicação, portanto nada aqui atribui a utilidade à explicação em si.")
    L.append("- **Utilidade percebida não é decisão melhor.** É a hipótese fundadora do "
             "trabalho, e continua por testar: um alerta pode agradar e conduzir a uma "
             "decisão pior.")
    L.append("- **Canal público.** Não se sabe quem são as pessoas, nem se são investidores "
             "particulares, que é o público que a dissertação assume.")
    L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--votos", default=str(DEFAULT_VOTOS))
    ap.add_argument("--out", default=str(OUT_MD))
    args = ap.parse_args()

    registos = FL.load_jsonl(args.votos)
    texto = relatorio(registos)
    saida = Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(f"[feedback] {len(registos)} voto(s) lido(s) de {args.votos}")
    print(f"[feedback] relatório escrito em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
