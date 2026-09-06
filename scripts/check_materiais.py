"""Os materiais que o aluno estuda dizem o mesmo que a tese?

O juri ve mais do que a dissertacao: ve os slides, e o aluno estuda pelo guia e pelo quizz.
Se um deles ensinar um numero que a tese corrigiu, ele decora o errado e a contradicao
aparece em directo. Ja aconteceu neste projecto: um documento de defesa mandava decorar um
valor que tinha sido retirado.

Verifica tres coisas de uma vez, sobre tese/:
  1. cada decimal de resultado dos materiais existe tambem na tese
  2. zero travessoes em prosa (a regra de escrita deste trabalho)
  3. zero decimais com virgula NUA em modo matematico (a forma correcta e `0{,}5`, que
     da o espacamento certo; `0,5` da espacamento de enumeracao)

Comparam-se decimais com DUAS OU TRES casas: sao os resultados. Coordenadas de desenho,
anos, versoes e valores de CSS nao sao afirmacoes.

Ate 2026-09-06 so se comparavam duas casas, e a maioria dos valores deste trabalho tem
tres: a porta via 23 numeros nos tres materiais quando ha 133.

    python scripts/check_materiais.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# ⚠️ A ÁRVORE A VERIFICAR VEM POR ARGUMENTO, E O PADRÃO É A CANÓNICA. Corrigido a 2026-09-04.
#
# Este verificador apontava para `tese/`, que foi SUPERSEDA por `tese-pt/`. Continuava a passar
# ou a falhar sobre um documento que já não é entregue — ou seja, gritava por defeitos que não
# contam e ficava cego aos que contam. É a mesma classe que a sessão 58 encontrou no
# `check_references`, que só conhecia os nomes ingleses e imprimia «0 referências» como se
# fosse um estado saudável.
BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "tese-pt"
T = RAIZ / BASE

# ⚠️ DUAS ÁRVORES, E É DE PROPÓSITO. A prosa a verificar é a da dissertação CANÓNICA
# (`tese-pt/`), mas os materiais de estudo — slides, guia, quizz, guião de gravação — nunca
# foram movidos e continuam em `tese/`. Apontar as duas ao mesmo sítio faria uma delas ser
# lida a partir de um caminho que não existe, e o relatório dizia «(ausente)» para tudo, que
# se lê como «não há nada a verificar» e é «não olhei para nada».
# ⚠️ OS MATERIAIS SEGUEM A ARVORE. Estavam presos a `tese-pt`, pelo que
# `check_materiais.py tese-eng` teria comparado os slides PORTUGUESES contra a tese inglesa --
# nem uma coisa nem outra. O deck ingles existe desde 2026-09-06, para a audiencia do artigo.
MATERIAIS_RAIZ = T
MATERIAIS = [MATERIAIS_RAIZ / "slides" / "main.tex", MATERIAIS_RAIZ / "guia" / "main.tex",
             MATERIAIS_RAIZ / "quiz" / "index.html", MATERIAIS_RAIZ / "GRAVACAO.md"]

# ⚠️ O PACOTE DE DEFESA E O QUE O AUTOR DECORA, e estava fora desta porta. A sessao 55
# encontrou o guiao a listar, na tabela dos numeros a saber, um par que tinha sido RETIRADO,
# e o simulacro a mandar decora-lo. A 2026-09-06 encontrou-se ali a latencia antiga em tres
# ficheiros, um deles com a conclusao invertida — e nada olhava para eles.
# O pacote de defesa e portugues e nao tem versao inglesa: so entra com a arvore PT.
if BASE == "tese-pt":
    MATERIAIS += sorted((RAIZ / "docs" / "defence").glob("*.md"))

if (T / "ch1").is_dir():          # árvore nova: ch1/chapter1.tex
    PROSA = ([T / "frontmatter" / "frontmatter.tex"]
             + [T / f"ch{i}" / f"chapter{i}.tex" for i in range(1, 7)]
             + [T / "appendices" / "appendixA.tex", T / "appendices" / "appendixB.tex"])
else:                            # árvore antiga: cap5/capitulo5.tex
    PROSA = sorted(T.rglob("cap*/capitulo*.tex")) + [T / "apendices" / "apendiceA.tex",
                                                     T / "frontmatter" / "frontmatter.tex"]
PROSA = [p for p in PROSA if p.exists()]

# ⚠️ AS DUAS CONVENCOES, e comparadas por VALOR e nao por cadeia. Ate 2026-09-06 esta
# expressao so conhecia o ponto, e a dissertacao ja escrevia `$0{,}542$`: no dia em que
# os materiais foram convertidos, a porta passou a ver 1 decimal nos slides em vez de
# dezenas e a declarar «0 sem par na tese». Nao encontrar nada e aprovar tudo tem o
# mesmo aspecto no ecra.
RX_RESULTADO = re.compile(r"\d+(?:\.|\{,\})\d{2,3}(?!\d)")


def _valor(cadeia: str) -> str:
    """Normaliza as duas convencoes decimais para uma so, para comparar numeros."""
    return cadeia.replace("{,}", ".")


def limpa(t: str) -> str:
    """Fora o que nao e afirmacao: desenhos, estilos e blocos de codigo."""
    # ⚠️ EM PROSA PT-PT, `2.478` E DOIS MIL QUATROCENTOS E SETENTA E OITO, nao um decimal.
    # A regra que os separa sem ambiguidade neste corpus: um valor deste trabalho tem parte
    # inteira ZERO — sao precisoes, PR-AUC e taxas —, e um separador de milhares nunca a tem.
    # Mais as remissoes de seccao, que nao sao numeros afirmados.
    t = re.sub(r"(?<![\d.])[1-9]\d{0,2}\.\d{3}(?![\d])", " ", t)
    t = re.sub(r"§\s*\d+\.\d+", " ", t)
    # ⚠️ E AS REMISSOES POR NOME, pela mesma razao. `a Figura 5.12` nao afirma o valor
    # cinco virgula doze -- e um ponteiro. Ate 2026-09-06 nenhum material desta lista nomeava
    # figuras por numero, e o primeiro que o fez fez a porta gritar por dois numeros correctos.
    # A regra e estreita de proposito: so apaga o numero QUE SE SEGUE a uma destas palavras.
    t = re.sub(r"\b(?:Figuras?|Fig\.|Tabelas?|Table|Figure|Sec\w{2,3}o|Section|Equa\w{2,3}o|"
               r"Equation|Algoritmos?|Algorithms?)\s*\d+\.\d+", " ", t)
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", " ", t, flags=re.S)
    # ⚠️ A `tcolorbox` do Capitulo 4 reproduz um alerta TAL COMO FOI ENTREGUE, copiado
    # do registo do canal sem edicao. O que la esta e citacao, nao prosa: alterar um
    # caracter ali e o defeito que a sessao 61 encontrou com o titulo do Coronavirus,
    # numa tese cuja afirmacao central e que a evidencia e verbatim.
    t = re.sub(r"\\begin\{tcolorbox\}.*?\\end\{tcolorbox\}", " ", t, flags=re.S)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    # ⚠️ MEDIDAS DE COMPOSICAO NAO SAO RESULTADOS. Um "0.62" em `egin{column}{0.62	extwidth}`
    # ou em `height=0.78	extheight` e uma fraccao da pagina, nao um numero que a tese afirme.
    # Sem isto o verificador acusava cinco larguras de coluna como afirmacoes sem fonte, e um
    # verificador que grita de mais deixa de ser lido -- este projecto ja pagou isso cinco vezes.
    t = re.sub(r"\d+\.\d+\s*\\(?:text|line|column|page)(?:width|height)", " ", t)
    # ⚠️ UM COMENTARIO NAO E UMA AFIRMACAO, e este verificador acusava-os. Corrigido a
    # 2026-09-04: uma nota de composicao («2mm punha a caixa 0.52pt acima do slide») era
    # reportada como um numero que os materiais dizem e a tese nao. E a MESMA classe das
    # larguras de coluna acima, uma linha antes, na mesma funcao.
    #
    # O `%` tem de NAO estar escapado: `\\%` e o sinal de percentagem e aparece
    # dentro dos proprios numeros que interessa verificar, como `$0.41\\%$`.
    # Apagar por ai cegava o verificador exactamente onde ele serve.
    t = re.sub(r"(?<!\\)%.*", " ", t)
    return t


# Valores que os materiais podem trazer sem que a tese os afirme, com a razao ao lado.
# ⚠️ A lista e de ISENCAO e nao de acusacao: um numero novo que ninguem previu faz a
# verificacao FALHAR, em vez de passar em silencio.
ISENTOS: dict[str, str] = {
    # O guia ensina a NAO dizer estes, e explica porque foram retirados: eram 12 decisoes,
    # com intervalo que contem a taxa-base. Cita-los com a retratacao e o antidoto do
    # defeito que esta porta existe para apanhar, nao o defeito.
    "0.667": "precisao ao vivo RETIRADA, citada como retirada (guia, Nivel 5)",
    "0.455": "taxa-base do par retirado, citada como retirada",
    "0.391": "limite inferior do intervalo do par retirado",
    "0.862": "limite superior do intervalo do par retirado",
}


def _opcoes_certas(html: str) -> str:
    """So a opcao CERTA do banco de perguntas.

    ⚠️ Um quizz TEM de conter numeros errados: sao os distractores. Exigir que todas as
    opcoes existam na tese e pedir um quizz que nao pergunta nada. O que tem de existir na
    tese e a resposta certa, e o formato do banco da-a: `opts:[...], ok:<indice>`.
    """
    saida = []
    for m in re.finditer(r"opts:\s*\[(.*?)\]\s*,\s*ok:\s*(\d+)", html, re.S):
        opts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
        i = int(m.group(2))
        if i < len(opts):
            saida.append(opts[i])
    # o enunciado tambem conta: e prosa, e afirma
    saida += re.findall(r'q:\s*"((?:[^"\\]|\\.)*)"', html)
    return "\n".join(saida)


def main() -> int:
    corpo = [p for p in PROSA if p.exists()]
    if not corpo:
        print("ERRO: nao encontrei o corpo da tese. Um verificador que nao ve corpus tem de "
              "ser indistinguivel de um que falha.")
        return 2

    tese = "\n".join(p.read_text(encoding="utf-8") for p in corpo).replace("{,}", ".")
    tese_n = {_valor(x) for x in RX_RESULTADO.findall(tese)}

    # ⚠️ SEGUNDA FONTE, pelo mesmo criterio da porta do artigo: um material pode mostrar as
    # ⚠️ O QUE ESTA PORTA NAO GARANTE, medido a 2026-09-06 para nao ser suposto: a
    # uniao das duas fontes tem 563 decimais distintos, dos quais 337 da forma `0.xyz` -- ou
    # seja 33,7% desse espaco. Um numero inventado ao acaso com tres casas tem cerca de uma
    # hipotese em tres de encontrar par por coincidencia e passar. A porta apanha a maioria
    # dos numeros retirados, que e para o que serve, e NAO e prova de que todo o numero dos
    # materiais foi verificado. Quem quiser essa prova le a Tabela A.1.
    #
    # parcelas de um numero que a tese resume. Os slides dao o minimo e o maximo da taxa de
    # disparo e a tese so a amplitude que deles resulta -- os tres estao em
    # `evaluation_anomaly.md`, que e a saida do proprio protocolo.
    aval = RAIZ / "docs" / "evaluation"
    aval_txt = "\n".join(f.read_text(encoding="utf-8", errors="replace")
                         for f in sorted(aval.glob("*.md"))) if aval.exists() else ""
    fontes_n = tese_n | {_valor(x) for x in RX_RESULTADO.findall(aval_txt)}

    falhas = 0

    print(f"tese: {len(corpo)} ficheiros, {len(tese_n)} decimais de resultado")
    for p in MATERIAIS:
        if not p.exists():
            print(f"  (ausente) {p.parent.name}/{p.name}")
            continue
        t = limpa(p.read_text(encoding="utf-8", errors="replace"))
        if p.suffix == ".html":
            t = _opcoes_certas(t)
        n = {_valor(x) for x in RX_RESULTADO.findall(t)}
        fora = sorted(x for x in n - fontes_n if x not in ISENTOS)
        marca = "ok  " if not fora else "!!  "
        print(f"  {marca}{p.parent.name}/{p.name}: {len(n)} decimais, {len(fora)} sem par na tese")
        for x in fora:
            m = re.search(r".{0,58}" + re.escape(x) + r".{0,38}", t)
            ctx = re.sub(r"\s+", " ", m.group(0)) if m else ""
            print(f"        {x}  ...{ctx}")
        falhas += len(fora)

    # travessoes em prosa e decimais com virgula, na tese e nos materiais
    # ⚠️ As duas regras correm sobre o texto LIMPO, e nao sobre as linhas em bruto. Sem isso
    # o verificador acusava as coordenadas de TikZ `(3.9,0)` de serem decimais com virgula, e
    # as barras `---` do Markdown de serem travessoes. Um verificador que grita de mais deixa
    # de ser lido, e este projecto ja pagou isso mais do que uma vez.
    travessoes, virgulas = [], []
    for p in corpo + [x for x in MATERIAIS if x.exists()]:
        # `md` marca o que NAO e corpus LaTeX: Markdown e o quizz em HTML sao material
        # informal, e a regra do travessao e da dissertacao.
        md = p.suffix.lower() in (".md", ".html")
        texto = limpa(p.read_text(encoding="utf-8", errors="replace"))
        for n, linha in enumerate(texto.split("\n"), 1):
            if linha.lstrip().startswith("%"):
                continue
            # travessao a serio: entre palavras. Em Markdown, `---` sozinho e uma barra
            # horizontal e `|---|` e uma tabela: nenhum dos dois e travessao.
            barra = md and linha.lstrip().startswith(("|", "-"))
            # ⚠️ AS DUAS FORMAS. Ate 2026-09-06 so se procurava `---`, a forma que se
            # escreve em LaTeX; o caracter `—` (U+2014) rende exactamente igual no PDF
            # e passava invisivel. Foi assim que dois travessoes meus entraram no
            # Apendice B sem esta porta dizer nada.
            # ⚠️ O CARACTER SO CONTA NO CORPUS LaTeX. A regra «zero travessoes em
            # prosa» vem do brief de reescrita da DISSERTACAO; os documentos de defesa
            # sao notas de trabalho em Markdown e o quizz e HTML, onde um `—` num
            # titulo e pontuacao corrente. Aplicar-lhes a regra dava 151 achados, quase
            # todos legitimos.
            padrao = (r"\w\s*---\s*\w" if md
                      else r"\w\s*(?:---|\u2014)\s*\w")
            if re.search(padrao, linha) and not barra:
                travessoes.append(f"{p.name}:{n}  {linha.strip()[:60]}")
            if re.search(r"\$[^$]*\d,\d[^$]*\$", linha):
                virgulas.append(f"{p.name}:{n}  {linha.strip()[:60]}")

    print(f"  {'ok  ' if not travessoes else '!!  '}travessoes em prosa: {len(travessoes)}")
    for x in travessoes[:8]:
        print(f"        {x}")
    print(f"  {'ok  ' if not virgulas else '!!  '}decimais com virgula: {len(virgulas)}")
    for x in virgulas[:8]:
        print(f"        {x}")

    falhas += len(travessoes) + len(virgulas)
    if falhas:
        print("\nUm numero que o aluno estuda e a tese nao diz e um numero que ele vai citar "
              "sem o poder mostrar.")
        return 1
    print("\nTudo bate certo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
