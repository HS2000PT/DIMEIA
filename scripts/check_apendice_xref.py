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

RAIZ = pathlib.Path(__file__).resolve().parents[1] / "tese"
NIVEL = {"section": 1, "subsection": 2, "subsubsection": 3}

seccoes = {}
ficheiros_capitulo = sorted(RAIZ.rglob("cap*/capitulo*.tex"))
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

maus = 0
for linha in linhas:
    lab = re.search(r"\\ref\{(sec:[^}]+)\}", linha).group(1)
    celulas = [c.strip() for c in linha.split("&")]
    # ⚠️ So DECIMAIS. Um inteiro solto ("17", "20", "5") e generico de mais para verificar,
    # e o corpo escreve-o muitas vezes por extenso ("dezassete"): testa-lo so produz alarmes
    # falsos, e um verificador que grita de mais deixa de ser lido.
    valores = re.findall(r"[-+]?\d+[.,]\d+", celulas[1] if len(celulas) > 1 else "")
    if lab not in seccoes:
        print(f"  !! {lab}: label nao existe")
        maus += 1
        continue
    titulo, texto, cap = seccoes[lab]
    # ⚠️ As coordenadas de TikZ sao numeros e nao afirmacoes. Sem as tirar, um "(1.5,3.35)"
    # de um desenho fazia o verificador aceitar uma referencia errada, porque 0.015 lido em
    # percentagem da 1.5. Foi assim que ele passou no proprio teste de sabotagem.
    sem_desenhos = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", texto, flags=re.S)
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
    marca = "ok " if not faltam else "!! "
    if faltam:
        maus += 1
    print(f"  {marca}{celulas[0][:44]:46s} -> {cap}/{titulo[:36]}")
    if faltam:
        print(f"       valores que NAO aparecem la: {faltam}")

print(f"\nlinhas com problema: {maus}")
if not linhas:
    # Um verificador que nao ve corpus tem de ser indistinguivel de um que falha, e nao
    # de um que passa. Ja aconteceu neste projecto.
    print("ERRO: nao encontrei nenhuma linha da tabela A.2. O corpus mudou de forma?")
    sys.exit(2)
sys.exit(1 if maus else 0)
