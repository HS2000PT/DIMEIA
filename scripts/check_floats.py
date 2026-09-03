"""Lente das figuras: cada flutuante e referenciado, discutido, e com legenda que se sustenta?

Um flutuante que ninguem invoca compila sem um unico aviso e o leitor nunca la vai.
Um flutuante referenciado uma so vez, e so na frase que o introduz, tambem nao foi discutido.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "tese"
RAIZ = REPO / BASE
if (RAIZ / "ch1").is_dir():
    FICH = (["frontmatter/frontmatter.tex"]
            + [f"ch{i}/chapter{i}.tex" for i in range(1, 7)]
            + ["appendices/appendixA.tex", "appendices/appendixB.tex"])
else:
    FICH = (["frontmatter/frontmatter.tex"]
            + [f"cap{i}/capitulo{i}.tex" for i in range(1, 7)]
            + ["apendices/apendiceA.tex", "apendices/apendiceB.tex"])

inv = []
partes = {}
ausentes = []
for f in FICH:
    p = RAIZ / f
    if not p.exists():
        ausentes.append(f)
        continue
    s = p.read_text(encoding="utf-8")
    partes[f] = s
    for m in re.finditer(r"\\begin\{(figure|table)\}(.*?)\\end\{\1\}", s, re.S):
        tipo, corpo = m.group(1), m.group(2)
        lab = re.search(r"\\label\{([^}]+)\}", corpo)
        cap = re.search(r"\\caption(?:\[([^\]]*)\])?", corpo)
        curta = cap.group(1) if cap and cap.group(1) else ""
        temlonga = bool(re.search(r"\\caption(\[[^\]]*\])?\{.{40,}", corpo, re.S))
        inv.append({
            "f": f, "linha": s[:m.start()].count("\n") + 1, "tipo": tipo,
            "lab": lab.group(1) if lab else "SEM-LABEL", "curta": curta,
            "longa": temlonga,
        })

if ausentes:
    print(f"ERRO: faltam {len(ausentes)} ficheiro(s) do corpus em {RAIZ}:")
    for f in ausentes:
        print("  -", f)
    raise SystemExit(2)
if not partes:
    print(f"ERRO: não encontrei corpus em {RAIZ}.")
    raise SystemExit(2)

todo = "\n".join(partes.values())

print(f"{'ficheiro':22s} {'lin':>5s} {'tipo':6s} {'refs':>4s} {'leg':>4s}  label")
achados = []
for x in inv:
    n = len(re.findall(r"\\(?:ref|autoref|eqref)\{" + re.escape(x["lab"]) + r"\}", todo))
    leg = "ok" if (x["curta"] and x["longa"]) else "!!"
    marca = ""
    if n == 0:
        marca = "  <-- NUNCA REFERENCIADO"
        achados.append((x["lab"], "nunca referenciado"))
    elif n == 1:
        marca = "  <-- referenciado uma so vez"
    if leg == "!!":
        marca += "  <-- legenda curta/longa em falta"
        achados.append((x["lab"], "legenda incompleta"))
    print(f"{x['f']:22s} {x['linha']:5d} {x['tipo']:6s} {n:4d} {leg:>4s}{marca}")

nfig = sum(1 for x in inv if x["tipo"] == "figure")
ntab = sum(1 for x in inv if x["tipo"] == "table")
print(f"\ntotal de flutuantes: {len(inv)}  ({nfig} figuras, {ntab} tabelas)")
for lab, o in achados:
    print("  -", lab, ":", o)

# ⚠️ ESTE VERIFICADOR RELATAVA E NÃO FALHAVA, o que é quase o mesmo que não existir: o
# `check_entrega.py` corre-o e olha para o código de saída, portanto um flutuante órfão passava
# a porta com um "ok" ao lado. Apanhado a 2026-08-20 com a `tab:av_causal`, que eu próprio
# acrescentei e nunca referenciei. Um relatório que ninguém lê não é uma porta.
if achados:
    print(f"\nFALHA: {len(achados)} flutuante(s) por corrigir. Um flutuante que nenhuma frase")
    print("invoca compila sem um único aviso, e o leitor nunca é mandado lá.")
    raise SystemExit(1)
print("\nTodos os flutuantes são invocados e têm legenda curta e longa.")
