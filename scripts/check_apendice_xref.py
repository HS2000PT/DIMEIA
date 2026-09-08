"""O apendice diz "este numero aparece na Seccao X". Aparece mesmo?

A Tabela A.2 promete que cada resultado esta rastreavel ate ao sitio onde e usado. Se a
seccao indicada nao contiver o numero, a promessa e falsa e ninguem daria por isso: o
LaTeX resolve a referencia na mesma.

⚠️ A primeira versao deste script acusou 9 de 12 linhas, e estava ERRADA: cortava o bloco
de uma \\section na primeira \\subsection, portanto nao via nada do conteudo dela. Uma
seccao vai ate a proxima do MESMO nivel ou superior.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A ARVORE E A CANONICA; apontava para `tese/`, superseda. Ver a nota em
# auditar_numeros.py: nao basta trocar a arvore, os nomes dos ficheiros mudam.
RAIZ = pathlib.Path(__file__).resolve().parents[1] / "tese-pt"
NIVEL = {"section": 1, "subsection": 2, "subsubsection": 3}

seccoes = {}
# Os NOMES mudam com a arvore: a canonica usa ch{i}/chapter{i}.tex, a anterior usava
# cap{i}/capitulo{i}.tex. Trocar a arvore sem trocar os nomes deixa o verificador cego,
# e por isso ele RECUSA-SE a validar quando nao encontra corpus.
# ⚠️ O `ch5/feedback_auto.tex` é GERADO e não se chama `chapter*`, pelo que o padrão acima o
# deixava de fora — e com ele a secção `sec:av_feedback`, que é uma subsecção real do Capítulo 5.
# Uma remissão do apêndice para ela era reportada como «label nao existe» enquanto o LaTeX a
# resolvia sem um único aviso: o verificador via menos documento do que o compilador.
ficheiros_capitulo = (sorted(RAIZ.rglob("ch*/chapter*.tex"))
                      or sorted(RAIZ.rglob("cap*/capitulo*.tex")))
ficheiros_capitulo += sorted(RAIZ.rglob("ch*/*_auto.tex"))
if not ficheiros_capitulo:
    print(f"ERRO: não encontrei capítulos em {RAIZ}. Não é seguro validar sem corpus.")
    sys.exit(2)

for f in ficheiros_capitulo:
    s = f.read_text(encoding="utf-8")
    marcas = [(m.start(), NIVEL[m.group(1)], m.group(2))
              for m in re.finditer(r"\\((?:sub)*section)\{([^}]*)\}", s)]
    for i, (pos, niv, titulo) in enumerate(marcas):
        # a seccao acaba na proxima marca de nivel IGUAL ou SUPERIOR (numero menor ou igual)
        fim = len(s)
        for pos2, niv2, _ in marcas[i + 1:]:
            if niv2 <= niv:
                fim = pos2
                break
        bloco = s[pos:fim]
        # o label pertence a esta seccao se vier antes da proxima marca qualquer
        prox = marcas[i + 1][0] if i + 1 < len(marcas) else len(s)
        lab = re.search(r"\\label\{(sec:[^}]+)\}", s[pos:prox])
        if lab:
            seccoes[lab.group(1)] = (titulo, bloco, f.parent.name)

apendice = RAIZ / "appendices" / "appendixA.tex"
if not apendice.exists():
    apendice = RAIZ / "apendices" / "apendiceA.tex"
if not apendice.exists():
    print(f"ERRO: não encontrei {apendice}. Não é seguro validar sem apêndice.")
    sys.exit(2)
ap = apendice.read_text(encoding="utf-8")
# ⚠️ Uma linha de tabela pode estar partida por varias linhas do ficheiro: o `\ref` cai na
# seguinte e o verificador deixava de a ver. Tres linhas novas passaram assim despercebidas.
# Junta-se por LINHA LOGICA, que acaba em `\\`.
logicas, acumulado = [], ""
for fisica in ap.split("\n"):
    acumulado += " " + fisica.strip()
    if fisica.rstrip().endswith("\\\\"):
        logicas.append(acumulado.strip())
        acumulado = ""
linhas = [x for x in logicas if "&" in x and "ref{sec:" in x]
print(f"linhas da tabela com referencia a seccao: {len(linhas)}\n")

BS_CH = chr(92)
maus = 0
nao_verificadas: list[str] = []
for linha in linhas:
    lab = re.search(r"\\ref\{(sec:[^}]+)\}", linha).group(1)
    celulas = [c.strip() for c in linha.split("&")]
    # ⚠️ So DECIMAIS. Um inteiro solto ("17", "20", "5") e generico de mais para verificar,
    # e o corpo escreve-o muitas vezes por extenso ("dezassete"): testa-lo so produz alarmes
    # falsos, e um verificador que grita de mais deixa de ser lido.
    #
    # ⚠️ E A CELULA TEM DE SER NORMALIZADA ANTES, senao NAO SE EXTRAI VALOR NENHUM. A tese
    # escreve os decimais na convencao PT-PT em modo matematico, `$0{,}015$`, e entre o `0`
    # e o `015` esta' `{,}` e nao uma virgula: o padrao `\d+[.,]\d+` nao casa, a lista sai
    # vazia, o ciclo de verificacao nao corre e a linha e' dada como `ok`. O palheiro ja'
    # era normalizado umas linhas abaixo (`limpo`) e a agulha nao -- uma assimetria de uma
    # linha que deixou este verificador a aprovar TUDO, incluindo uma referencia plantada de
    # proposito para a seccao errada. Encontrado a 2026-09-08 por sabotagem deliberada.
    bruto = celulas[1] if len(celulas) > 1 else ""
    valores = re.findall(r"[-+]?\d+[.,]\d+", bruto.replace("{,}", ".").replace("\\,", ""))
    if lab not in seccoes:
        print(f"  !! {lab}: label nao existe")
        maus += 1
        continue
    titulo, texto, cap = seccoes[lab]
    # ⚠️ As coordenadas de TikZ sao numeros e nao afirmacoes. Sem as tirar, um "(1.5,3.35)"
    # de um desenho fazia o verificador aceitar uma referencia errada, porque 0.015 lido em
    # percentagem da 1.5. Foi assim que ele passou no proprio teste de sabotagem.
    # ⚠️ E DEITAR FORA O DESENHO INTEIRO TAMBEM NAO SERVE: varias linhas do apendice apontam
    # para seccoes cuja evidencia E' a figura, e o valor so' la' existe desenhado. Deitar o
    # desenho fora fazia o verificador acusar duas linhas CORRECTAS. O discriminador e'
    # exacto e esta' no proprio ficheiro: dentro de um `tikzpicture`, uma COORDENADA
    # escreve-se com ponto (`axis cs:0.158,0.913`, `(0.281,vol)`) e um ROTULO DESENHADO
    # escreve-se na convencao do documento (`$F_1=0{,}269$`, `[0{,}281]`). So o segundo e'
    # uma afirmacao que o leitor ve'.
    def _so_rotulos(m: re.Match) -> str:
        return " " + " ".join(re.findall(r"\d+\{,\}\d+", m.group(0))) + " "

    sem_desenhos = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", _so_rotulos,
                          texto, flags=re.S)
    limpo = sem_desenhos.replace("{,}", ".").replace("\\,", "")
    def _solto(agulha, palheiro):
        # ⚠️ Sem fronteiras, "1.5" casa dentro de "21.5" e o verificador aprova tudo.
        return re.search(r"(?<![\d.])" + re.escape(agulha) + r"(?![\d])", palheiro) is not None

    def esta(v, limpo=limpo):
        v = v.replace(",", ".")
        if _solto(v, limpo):
            return True
        # ⚠️ O apendice tabela 0.592 e o corpo escreve 59.2%. E o mesmo numero em dois
        # formatos, e a primeira versao deste verificador acusou-o como ausente.
        try:
            pc = float(v) * 100
        except ValueError:
            return False
        # ⚠️ NADA de arredondar a zero casas: 0.015 em percentagem com `.0f` da "2", e um
        # "2" solto existe em qualquer texto. Com essa forma na lista, este verificador
        # aprovava uma referencia deliberadamente errada — passou no proprio teste de
        # sabotagem e so se percebeu porque eu insisti em ve-lo falhar.
        for forma in (f"{pc:.1f}", f"{pc:g}"):
            if len(forma.replace(".", "")) >= 2 and _solto(forma, limpo):
                return True
        return False

    faltam = [v for v in valores if not esta(v)]
    # ⚠️ UMA LINHA SEM DECIMAL NAO E' UMA LINHA VERIFICADA, e imprimi-la como `ok` e' a
    # forma exacta de um verificador mentir sem se enganar. Sao as linhas cujo valor e'
    # so' inteiros -- `23 de 23`, `9 de 9`, `743 -> 15` --, que a regra dos decimais
    # deliberadamente nao testa. Passam a dizer o que sao: NAO VERIFICADAS. Foi uma delas
    # que escondeu, a 2026-09-08, uma remissao para a seccao errada.
    if not valores:
        # ⚠️ O agrupamento por linha logica arrasta tambem a legenda e o fecho da tabela,
        # que nao sao linhas de resultado. Listá-los como «nao verificados» encheria o
        # relatorio de ruido, e um relatorio ruidoso deixa de ser lido -- que e' o mesmo
        # modo de falha que esta correcao esta' a fechar.
        if not celulas[0].lstrip().startswith((BS_CH + "chapter", BS_CH + "bottomrule")):
            nao_verificadas.append(celulas[0][:44].strip())
        print(f"  -- {celulas[0][:44]:46s} -> {cap}/{titulo[:36]}  (sem decimal)")
        continue
    marca = "ok " if not faltam else "!! "
    if faltam:
        maus += 1
    print(f"  {marca}{celulas[0][:44]:46s} -> {cap}/{titulo[:36]}")
    if faltam:
        print(f"       valores que NAO aparecem la: {faltam}")

if nao_verificadas:
    print(f"\n{len(nao_verificadas)} linha(s) SEM DECIMAL, que este verificador nao testa "
          "(a remissao tem de ser conferida a olho):")
    for n in nao_verificadas:
        print(f"   .. {n}")

print(f"\nlinhas com problema: {maus}")
if not linhas:
    # Um verificador que nao ve corpus tem de ser indistinguivel de um que falha, e nao
    # de um que passa. Ja aconteceu neste projecto.
    print("ERRO: nao encontrei nenhuma linha da tabela A.2. O corpus mudou de forma?")
    sys.exit(2)
sys.exit(1 if maus else 0)
