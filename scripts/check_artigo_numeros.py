"""Cada número do artigo conferido contra a dissertação canónica e contra a evidência.

Porque é que isto existe, e é um defeito medido e não hipotético. A 2026-09-04 o
`paper/main.tex` estava tocado pela última vez a 13 de agosto, ou seja **antes** da
reescrita para `tese-v2`. Continha os valores antigos da recuperação e **não continha**
a estratégia trivial de `0,467` que leva a dissertação a abandonar o valor agregado em
favor da afirmação setor a setor. Submetido nesse estado, o artigo afirmaria o que a
dissertação declara não sustentar, e nada falhava: o LaTeX compilava, os testes passavam.

O verificador faz duas perguntas distintas:

1. **todo o número do artigo existe na dissertação?** Um número que só exista no artigo
   ou é novo (e então precisa de fonte própria) ou é resto de uma versão anterior;
2. **os resultados que a dissertação estreitou aparecem no artigo?** Uma afirmação
   retirada da tese que sobreviva no artigo é a pior das duas divergências, porque os
   dois documentos são lidos pelas mesmas pessoas.

    python scripts/check_artigo_numeros.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BS_ = chr(92)
RAIZ = pathlib.Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "paper" / "main.tex"
TESE = RAIZ / "tese-pt"
FICHEIROS_TESE = [f"ch{i}/chapter{i}.tex" for i in range(1, 7)] + [
    "appendices/appendixA.tex", "frontmatter/frontmatter.tex"]

AVAL = RAIZ / "docs" / "evaluation"

# Números de COMPOSIÇÃO, que não são afirmações: larguras de figura e derivações que o
# próprio texto mostra. A lista é curta de propósito; tudo o resto tem de ter fonte.
COMPOSICAO = {
    0.95,   # largura de coluna em \includegraphics
    2.1,    # "about 2.1x the random base rate", derivado de 0.514/0.240 no proprio texto
}

# Resultados que a dissertação ESTREITOU. Se o artigo os afirmar sem a ressalva, é a
# divergência que mais custa. A ressalva é procurada como cadeia, não como número.
ESTREITADOS: list[tuple[str, str, str]] = [
    ("0.514", "0.467",
     "o agregado da recuperação: a tese abandona-o porque existe uma estratégia trivial "
     "que vale 0.467. O artigo tem de nomear essa estratégia."),
    ("0.632", "1.67",
     "a precisão dentro do orçamento: a tese diz 1.67x e não 'quase quatro vezes', "
     "porque o chão de acaso real é 0.379 e não 0.163."),
]


def valores(texto: str, *, ingles: bool) -> set[float]:
    """Todos os decimais do texto, por VALOR e não por cadeia.

    ⚠️ A CHAVETA {,} NÃO SIGNIFICA O MESMO NAS DUAS LÍNGUAS, e tratá-la de forma
    igual inventa divergências. No artigo, que é inglês, separa MILHARES e tem de
    desaparecer: 3{,}714 é 3714. Na tese, que é portuguesa, é a vírgula DECIMAL e
    passa a ponto: 0{,}514 é 0.514. A sessão 56 pagou este defeito no sentido
    inverso, com o 88,5 do português lido como 885.
    """
    # ⚠️ EM PT-PT O SEPARADOR DE MILHARES E O ESPACO FINO `\\,`, e nao o
    # `{,}`, que fica reservado a virgula decimal. Sem esta linha, `38\\,214`
    # era lido como dois numeros e a contagem do artigo aparecia sem fonte na tese.
    texto = re.sub(r"(?<=\d)\\,(?=\d)", "", texto)
    texto = texto.replace("{,}", "" if ingles else ".")
    out: set[float] = set()
    for m in re.findall(r"\d+(?:\.\d+)?", texto):
        try:
            out.add(float(m))
        except ValueError:
            pass
    return out


# A tabela de resultados da triagem, conferida por PAR e nao por presenca.
# (rotulo no artigo, PR-AUC, Brier) tal como docs/evaluation/evaluation_triage.md os da.
TABELA_TRIAGEM = [
    ("Volatility only", "0.542", "0.218"),
    ("Company and day context", "0.538", "0.224"),
    ("Context and headline text", "0.496", "0.229"),
    ("Gradient boosting", "0.469", "0.228"),
    ("Headline text only", "0.439", "0.240"),
    ("Always alert", "0.378", "0.622"),
]


def _confere_tabela(art: str, falhas: list[str]) -> None:
    """Cada linha da tabela tem de trazer o PAR certo, e nao um numero plausivel."""
    print("tabela de triagem, conferida linha a linha")
    for rotulo, prauc, brier in TABELA_TRIAGEM:
        linha = next((ln for ln in art.split(chr(10)) if ln.startswith(rotulo)), None)
        if linha is None:
            print(f"  .. {rotulo}: não aparece na tabela do artigo")
            continue
        ok_p, ok_b = prauc in linha, brier in linha
        if ok_p and ok_b:
            print(f"  ok  {rotulo}: {prauc} / {brier}")
        else:
            errado = [n for n, o in ((prauc, ok_p), (brier, ok_b)) if not o]
            print(f"  !!  {rotulo}: a fonte diz {', '.join(errado)} e a linha não o traz")
            print(f"      {linha.strip()[:88]}")
            falhas.append(f"{rotulo} com valor errado")
    print()


def main() -> int:
    if not ARTIGO.exists():
        print("ERRO: paper/main.tex não existe. Um verificador que não vê o corpus "
              "tem de ser indistinguível de um que falha.")
        return 2

    art_txt = ARTIGO.read_text(encoding="utf-8", errors="replace")
    art_txt = re.sub(r"(?<!\\)%.*", " ", art_txt)
    # A bibliografia do artigo vive DENTRO do main.tex, por ser estilo LNCS, ao passo
    # que a da tese esta num .bib a parte que este verificador nao le. Sem este corte,
    # os intervalos de pagina das referencias entram como contagens sem fonte.
    art_txt = art_txt.split(BS_ + "begin{thebibliography}")[0]
    # O numero de aluno no endereco de correio nao e uma afirmacao sobre o sistema.
    art_txt = art_txt.split(BS_ + "maketitle")[-1]
    tese_txt = "\n".join((TESE / f).read_text(encoding="utf-8", errors="replace")
                         for f in FICHEIROS_TESE if (TESE / f).exists())

    # ⚠️ A ISENÇÃO DOS INTEIROS ERA LARGA DEMAIS, e custou um defeito real: o artigo
    # afirmava `4 366` decisões de triagem, número que não existe em lado nenhum da
    # dissertação atual, onde o valor canónico é `36 925`. O comentário anterior dizia
    # «os inteiros são anos, contagens e coordenadas» — e é justamente a contagem que é
    # uma afirmação sobre o sistema implantado, tão verificável como uma PR-AUC.
    #
    # A regra é estreita para não produzir um verificador que grita: só inteiros a partir
    # de mil, que a esta escala não são coordenadas nem corpos de letra. Os anos ficam de
    # fora, salvo com separador de milhares — ninguém escreve `2{,}026`, logo essa forma
    # é sempre uma contagem.
    def _conta(v: float, texto: str) -> bool:
        if v != int(v) or v < 1000:
            return False
        if 1900 <= v <= 2100:
            n = f"{int(v)}"
            return (n[0] + "{,}" + n[1:]) in texto
        return True

    art_dec = {v for v in valores(art_txt, ingles=True)
               if v != int(v) or _conta(v, art_txt)}
    tese_dec = {v for v in valores(tese_txt, ingles=False)
                if v != int(v) or _conta(v, tese_txt)}

    # Um número que o artigo tenha e a tese não NÃO é, por si só, um defeito: o artigo
    # pode reportar mais. O que é defeito é não ter fonte nenhuma. Por isso a segunda
    # pergunta é feita contra os artefactos de avaliação, e não contra a tese.
    so_no_artigo = sorted(v for v in art_dec - tese_dec if v not in COMPOSICAO)
    falhas: list[str] = []

    print(f"artigo: {len(art_dec)} valores (decimais e contagens) · tese canónica: {len(tese_dec)}")
    print()

    aval_txt = "\n".join(f.read_text(encoding="utf-8", errors="replace")
                         for f in sorted(AVAL.glob("*.md")))
    aval_dec = valores(aval_txt, ingles=True)

    # ⚠️ UMA CONTAGEM TEM DE VIR DA DISSERTACAO, e nao de um artefacto qualquer. O
    # controlo de 2026-09-06 nao disparou por causa disto: replantado o `4 366` que
    # escapara, a porta passou, porque esse numero existe mesmo em
    # `evaluation_gate_selectivity.md` — e a janela curta de uma figura, e a dissertacao
    # reporta `36 925`. Um resultado decimal pode existir so num artefacto, porque o artigo
    # pode reportar uma medicao que a tese comprime; uma contagem e uma afirmacao sobre o
    # sistema implantado, e os dois documentos sao lidos pelas mesmas pessoas.
    contagens = sorted(v for v in art_dec if v == int(v) and v >= 1000)
    fora_da_tese = [v for v in contagens if v not in tese_dec]
    if fora_da_tese:
        print(f"contagens do artigo que a dissertação NÃO reporta: {len(fora_da_tese)}")
        for v in fora_da_tese:
            onde = " (existe em docs/evaluation/)" if v in aval_dec else ""
            print(f"   {int(v)}{onde}")
        print("   Uma contagem é uma afirmação sobre o sistema implantado. Se os dois "
              "documentos\n   dão contagens diferentes, o leitor vê dois sistemas.")
        falhas.append(f"{len(fora_da_tese)} contagens fora da dissertação")
    else:
        print(f"ok  as {len(contagens)} contagens do artigo são as da dissertação")

    sem_fonte = [v for v in so_no_artigo if v not in aval_dec and not (
        v == int(v) and v >= 1000)]
    if sem_fonte:
        print(f"valores do artigo SEM fonte em lado nenhum: {len(sem_fonte)}")
        for v in sem_fonte:
            print(f"   {v:g}")
        print("   Não estão na dissertação nem em docs/evaluation/. Ou são novos e "
              "precisam de gerador, ou são resto de uma versão anterior.")
        falhas.append(f"{len(sem_fonte)} valores sem fonte")
    elif so_no_artigo:
        print(f"ok  {len(so_no_artigo)} valores só no artigo, todos com fonte em "
              "docs/evaluation/")
        print("    " + ", ".join(f"{v:g}" for v in so_no_artigo))
    else:
        print("ok  todo o valor do artigo existe também na dissertação canónica")

    print()
    _confere_tabela(art_txt, falhas)
    for numero, ressalva, porque in ESTREITADOS:
        if numero not in art_txt.replace("{,}", ""):
            print(f"ok  o artigo não afirma {numero}")
            continue
        if ressalva in art_txt.replace("{,}", ""):
            print(f"ok  {numero} aparece com a ressalva de {ressalva}")
        else:
            print(f"!!  o artigo afirma {numero} SEM a ressalva de {ressalva}")
            print(f"    {porque}")
            falhas.append(f"{numero} sem ressalva")

    print()
    if falhas:
        print("FALHA: " + "; ".join(falhas))
        return 1
    print("O artigo está alinhado com a dissertação canónica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
