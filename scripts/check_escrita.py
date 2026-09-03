"""A escrita da tese: PT-PT, registo académico, e um termo por conceito.

Cinco varreduras, todas com lista fechada e com fronteiras de palavra, porque a alternativa —
procurar por impressão — produz alarmes falsos e um verificador que grita de mais deixa de ser
lido. Este projecto já pagou isso cinco vezes.

  1. brasileirismos
  2. grafias anteriores ao Acordo Ortográfico de 1990
  3. regências erradas (o verbo "precisar" sem "de" é a mais frequente)
  4. anglicismos onde existe palavra portuguesa corrente e a tese já a usa
  5. o mesmo conceito com dois nomes

⚠️ Cada regra tem de sobreviver a um AUTOTESTE: planta-se uma ocorrência de cada e exige-se que
o verificador dispare. Um detector partido e um corpus limpo são indistinguíveis no ecrã.

    python scripts/check_escrita.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "tese"
T = RAIZ / BASE

BRASILEIRISMOS = [
    "usuário", "usuários", "arquivo", "arquivos", "tela", "telas", "time", "gerenciar",
    "gerenciamento", "acessar", "planilha", "estoque", "cadastro", "rodar o", "aplicativo",
    "celular", "trem de", "bilhão", "trilhão", "fatos", "objetivo é de",
]

PRE_ACORDO = [
    "pára", "acção", "acções", "actual", "actualmente", "actor", "actores", "objectivo",
    "objectivos", "projecto", "projectos", "óptimo", "directo", "directamente", "tecto",
    "aspecto", "aspectos", "excepto", "facto de que", "exacto", "exacta",
    # ⚠️ "contacto" SAIU desta lista a 2026-08-20, e a razao importa: em PT-PT o c de
    # "contacto" PRONUNCIA-SE, logo o Acordo de 1990 mantem-no. A forma sem c e a
    # brasileira. Este verificador acusou a palavra certa e eu, a obedecer-lhe, escrevi
    # um brasileirismo numa tese que tem "zero brasileirismos" como criterio. Um
    # verificador errado nao e neutro: produz o defeito que existe para evitar.
    "exactamente", "correcto", "correcta", "afecta", "adopta", "adoptar",
]

# (padrao, o que devia estar)
REGENCIA = [
    # ⚠️ O "de" pode vir ANTES ("a pergunta DE QUE o produto precisava") ou depois. A primeira
    # versão só olhava para a frente e acusava duas frases correctas.
    (r"(?<!de )\bque o sistema precisa\b(?! de)", "precisar DE: 'de que o sistema precisa'"),
    (r"(?<!de )\bque (?:o produto|ele|ela) precisava\b(?! de)", "precisar DE"),
    (r"\bnão bastam ser\b", "bastar não admite este sujeito com infinitivo"),
    (r"\bhouveram\b", "haver é impessoal: 'houve'"),
    (r"\bhaviam (?:muitos|muitas|vários|várias|alguns|algumas)\b", "haver é impessoal: 'havia'"),
]

ANGLICISMOS = ["setup", "watchlist", "baseline", "dataset", "insight", "feedback",
               "workflow", "output", "input", "framework", "app", "apps"]

# conceitos com mais do que um nome: (nome canónico, alternativas que não devem aparecer)
UM_NOME = [
    ("porta", ["portão", "portões"]),
    ("título", ["manchete", "manchetes"]),
    # ⚠️ A frase que DEFINE o termo ("a cobertura, também chamada recall") tem de o dizer, senão
    # o leitor que conhece a literatura em inglês não faz a ponte. Só se acusa fora da definição.
    ("cobertura", [r"(?<!também chamada \\emph\{)\bRecall\b"]),
    ("investidor particular", ["investidores de retalho", "investidor de retalho"]),
    ("aplicação", [r"\bApp\b", r"\bapps\b"]),
]

if (T / "ch1").is_dir():
    FICHEIROS = ([T / "frontmatter" / "frontmatter.tex"]
                 + [T / f"ch{i}" / f"chapter{i}.tex" for i in range(1, 7)]
                 + [T / "appendices" / "appendixA.tex",
                    T / "appendices" / "appendixB.tex"])
else:
    FICHEIROS = (sorted(T.rglob("cap*/capitulo*.tex"))
                 + [T / "apendices" / "apendiceA.tex",
                    T / "apendices" / "apendiceB.tex",
                    T / "frontmatter" / "frontmatter.tex"])


def limpa(t: str) -> str:
    """Fora comentários, desenhos, código e nomes de ficheiro."""
    # ⚠️ O abstract em INGLÊS não é prosa portuguesa: "baseline" e "dataset" são as palavras
    # certas lá dentro. Sem isto o verificador acusava o próprio abstract.
    t = re.sub(r"\\begin\{abstractotherlanguage\}.*?\\end\{abstractotherlanguage\}", " ",
               t, flags=re.S)
    t = re.sub(r"(?m)^\s*%.*$", " ", t)
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", " ", t, flags=re.S)
    t = re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:input|include)\{[^}]*\}", " ", t)  # ficheiros LaTeX incluídos
    t = re.sub(r"\\texttt\{[^}]*\}", " ", t)          # identificadores de código
    t = re.sub(r"\\(?:label|ref|autocite|textcite|cite\w*)\{[^}]*\}", " ", t)
    return t


def varre(nome: str, termos, achados: list, *, palavra=True) -> None:
    for f in FICHEIROS:
        if not f.exists():
            continue
        texto = limpa(f.read_text(encoding="utf-8", errors="replace"))
        for termo in termos:
            rx = (re.compile(r"(?<![\w-])" + termo + r"(?![\w-])", re.I) if palavra
                  else re.compile(termo, re.I))
            for m in rx.finditer(texto):
                ctx = re.sub(r"\s+", " ", texto[max(0, m.start() - 40):m.start() + 40])
                achados.append((nome, f.name, m.group(0), ctx))


def main() -> int:
    ausentes = [f for f in FICHEIROS if not f.exists()]
    if ausentes:
        print(f"ERRO: faltam {len(ausentes)} ficheiro(s) do corpus em {T}:")
        for f in ausentes:
            print(f"  - {f.relative_to(RAIZ)}")
        return 2
    achados: list = []
    varre("brasileirismo", [re.escape(x) for x in BRASILEIRISMOS], achados)
    varre("pré-Acordo", [re.escape(x) for x in PRE_ACORDO], achados)
    varre("anglicismo", [re.escape(x) for x in ANGLICISMOS], achados)
    for canonico, alternativas in UM_NOME:
        varre(f"dois nomes (usar '{canonico}')",
              [a if a.startswith(r"\b") else re.escape(a) for a in alternativas],
              achados, palavra=not any(a.startswith(r"\b") for a in alternativas))
    for padrao, porque in REGENCIA:
        for f in FICHEIROS:
            if not f.exists():
                continue
            texto = limpa(f.read_text(encoding="utf-8", errors="replace"))
            for m in re.finditer(padrao, texto, re.I):
                ctx = re.sub(r"\s+", " ", texto[max(0, m.start() - 40):m.start() + 40])
                achados.append((f"regência ({porque})", f.name, m.group(0), ctx))

    # ⚠️ AUTOTESTE: sem isto, um regex partido dá "0 achados" e lê-se como corpus limpo.
    planta = "O usuário abriu o arquivo e o projecto precisava setup."
    controlo = []
    for nome, termos in (("b", [re.escape(x) for x in BRASILEIRISMOS]),
                         ("p", [re.escape(x) for x in PRE_ACORDO]),
                         ("a", [re.escape(x) for x in ANGLICISMOS])):
        for termo in termos:
            rx = re.compile(r"(?<![\w-])" + termo + r"(?![\w-])", re.I)
            if rx.search(planta):
                controlo.append(nome)
                break
    if len(set(controlo)) < 3:
        print("ERRO: o autoteste falhou — as regras não disparam sobre uma frase que as viola.")
        print("      Um detector partido e um corpus limpo são indistinguíveis no ecrã.")
        return 2

    print(f"{len(FICHEIROS)} ficheiros · autoteste passou (as três famílias disparam)\n")
    if not achados:
        print("Nenhum achado.")
        return 0
    por_tipo: dict = {}
    for nome, ficheiro, termo, ctx in achados:
        por_tipo.setdefault(nome, []).append((ficheiro, termo, ctx))
    for nome, lista in sorted(por_tipo.items()):
        print(f"{nome}: {len(lista)}")
        for ficheiro, termo, ctx in lista[:10]:
            print(f"   {ficheiro}  «{termo}»  ...{ctx}")
    print(f"\ntotal: {len(achados)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
