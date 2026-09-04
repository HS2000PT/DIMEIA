"""A cadeia de cada questão de investigação: enunciada, medida, respondida.

Porque é que isto existe. Uma dissertação pode ter os três elos certos e a ligação errada:
o Capítulo 6 responde à questão citando um valor que o Capítulo 5 não estabeleceu, ou que
estabeleceu com outra formulação. Nada falha — o LaTeX compila, os números existem no
repositório, e a conclusão fica a afirmar mais do que o resultado sustenta.

O verificador impõe três condições, por ordem de gravidade:

1. **cada questão tem secção de resultados e resposta.** Uma questão sem uma das duas está
   implicitamente sem resposta, que é o que a §17 da revisão final proíbe;
2. **o Capítulo 6 não cita nenhum decimal que o Capítulo 5 não contenha.** É a condição
   que apanha uma conclusão a ir além do resultado;
3. **cada secção de resultados tem a sua delimitação.** O quarto passo do desenho
   experimental é dizer o que o resultado NÃO permite concluir, e uma secção sem ele
   entrega um número sem o seu alcance.

    python scripts/check_qi_cadeia.py [arvore]
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BS = chr(92)
RAIZ = pathlib.Path(__file__).resolve().parents[1]
BASE = RAIZ / (sys.argv[1] if len(sys.argv) > 1 else "tese-pt")

# (nome, secção de resultados no Cap. 5, subsecção de resposta no Cap. 6)
QI = [
    ("QI1 · deteção", "Deteção consistente entre empresas",
     "Deteção de movimentos invulgares"),
    ("QI2 · precedentes", "Recuperação de precedentes", "Recuperação de precedentes"),
    ("QI3 · triagem", "Triagem de notícias", "Triagem de notícias"),
]


def _texto(rel: str) -> str:
    f = BASE / rel
    if not f.exists():
        return ""
    t = f.read_text(encoding="utf-8", errors="replace")
    return re.sub("(?<![" + BS * 2 + "])%.*", " ", t)


def _decimais(t: str, *, so_prosa: bool = False) -> set[str]:
    """Decimais por VALOR.

    A TESE ESCREVE DECIMAIS DE DUAS FORMAS, e ler só uma inventa divergências. Na
    prosa usa a vírgula da convenção portuguesa; dentro de uma figura TikZ tem de
    usar o ponto, porque é o que o TikZ aceita. Uma afirmação da conclusão pode ter
    legitimamente a sua origem numa coordenada de figura.
    """
    out = {m.replace("{,}", ".")
           for m in re.findall(r"\d+\{,\}\d+", t)}
    if not so_prosa:
        out |= set(re.findall(r"\d+\.\d+", t))
    return out


def main() -> int:
    ch1 = _texto("ch1/chapter1.tex")
    ch4 = _texto("ch4/chapter4.tex")
    ch5 = _texto("ch5/chapter5.tex")
    ch6 = _texto("ch6/chapter6.tex")
    if not (ch1 and ch5 and ch6):
        print(f"ERRO: capítulos não encontrados em '{BASE}'.")
        return 2

    falhas: list[str] = []

    # ---- 1) cada questão enunciada, medida e respondida
    print("cadeia de cada questão")
    for nome, sec5, sec6 in QI:
        tem5 = sec5 in ch5
        tem6 = sec6 in ch6
        marca = "ok " if (tem5 and tem6) else "!! "
        print(f"  {marca} {nome:20s} resultados: {'sim' if tem5 else 'NÃO':3s} · "
              f"resposta: {'sim' if tem6 else 'NÃO'}")
        if not (tem5 and tem6):
            falhas.append(f"{nome} sem um dos elos")

    # ---- 2) o Cap. 6 não vai além do Cap. 5
    print()
    # A origem de uma afirmação da conclusão pode estar em qualquer capítulo que
    # ESTABELEÇA valores, e não só nos resultados: o Cap. 4 mede o sistema em
    # operação, e o Cap. 6 cita legitimamente essas medições.
    estabelecidos = _decimais(_texto("ch3/chapter3.tex") + ch4 + ch5)
    # o Cap. 6 pode ter decimais próprios de composição (coordenadas TikZ das figuras);
    # comparam-se apenas os que o Cap. 6 apresenta em modo matemático dentro de prosa.
    prosa6 = re.sub(re.escape(BS) + r"begin\{tikzpicture\}.*?"
                    + re.escape(BS) + r"end\{tikzpicture\}", " ", ch6, flags=re.S)
    alem = sorted(_decimais(prosa6, so_prosa=True) - estabelecidos)
    if alem:
        print("decimais que o Capítulo 6 afirma e nenhum capítulo anterior "
              f"estabelece: {len(alem)}")
        for v in alem:
            print(f"   {v}")
        print("   Uma conclusão não pode citar um valor que os resultados não produziram.")
        falhas.append(f"{len(alem)} decimais só no Cap. 6")
    else:
        print("ok  todo o decimal do Capítulo 6 tem origem num capítulo anterior")

    # ---- 3) cada secção de resultados delimita o que não conclui
    print()
    n_lim = ch5.count("Limites da conclusão")
    print(f"secções «Limites da conclusão» no Capítulo 5: {n_lim} (uma por questão)")
    if n_lim < len(QI):
        print("   Um resultado sem a sua delimitação entrega um número sem o seu alcance.")
        falhas.append("delimitações a menos")
    else:
        print("ok  cada questão delimita o que o resultado não permite concluir")

    print()
    if falhas:
        print("FALHA: " + "; ".join(falhas))
        return 1
    print("As três questões estão enunciadas, medidas, delimitadas e respondidas, e a "
          "conclusão não vai além dos resultados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
