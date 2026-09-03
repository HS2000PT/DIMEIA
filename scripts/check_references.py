"""Empareja cada \\ref com o que o \\label realmente rotula.

Duas verificações, e só a primeira é mecânica:

1. **TIPO** — a palavra que introduz a referência ("Section", "Figure", "Table", "Chapter",
   "Listing") tem de bater com o que o alvo é. `Figure~\\ref{tab:x}` compila sem erro e está
   errado; nenhum compilador o apanha.
2. **CONTEÚDO** — se a frase diz "as measured in X", X tem de conter uma medição. Isto é
   leitura; o script só monta a tabela para a leitura ser rápida.

USO:  python refcheck.py [thesis|thesis-pt]  [--all]
"""
from __future__ import annotations

import pathlib
import re
import sys

# A consola do Windows e cp1252 e rebenta a imprimir simbolos. Um verificador que morre a
# imprimir o achado e pior do que um que nao corre: parece que passou.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "thesis"
MOSTRAR_TUDO = "--all" in sys.argv

# ⚠️ Duas convenções de nomes, porque a tese curta (`tese/`) usa nomes em português. Sem isto o
# script encontrava **zero** ficheiros e imprimia "0 referências, 0 labels" — que se lê como
# "está tudo bem" e é, na verdade, "não olhei para nada". Um verificador que não encontra o
# corpus tem de ser indistinguível de um que falha, e não de um que passa.
FICHEIROS_EN = [
    "frontmatter/frontmatter.tex",
    *[f"ch{i}/chapter{i}.tex" for i in range(1, 7)],
    "appendices/appendixA.tex",
    "appendices/appendixB.tex",
]
FICHEIROS_PT = [
    "frontmatter/frontmatter.tex",
    *[f"cap{i}/capitulo{i}.tex" for i in range(1, 7)],
    "apendices/apendiceA.tex",
    "apendices/apendiceB.tex",
]
FICHEIROS = FICHEIROS_PT if (pathlib.Path(BASE) / "cap1").is_dir() else FICHEIROS_EN

_encontrados = [f for f in FICHEIROS if (pathlib.Path(BASE) / f).exists()]
if not _encontrados:
    print(f"ERRO: nenhum ficheiro do corpus encontrado em '{BASE}/'. "
          "Um verificador que não vê o corpus não pode dizer que está tudo bem.")
    raise SystemExit(2)

# Que tipo de alvo cada prefixo de label anuncia.
PREFIXO_TIPO = {
    "chap": "chapter", "sec": "section", "fig": "figure",
    "tab": "table", "lst": "listing", "alg": "algorithm", "app": "appendix-or-section",
}
# Que tipo a palavra introdutória exige.
PALAVRA_TIPO = {
    "chapter": "chapter", "capítulo": "chapter", "capitulo": "chapter",
    "section": "section", "secção": "section", "seccao": "section", "seção": "section",
    "figure": "figure", "figura": "figure",
    "table": "table", "tabela": "table",
    "listing": "listing", "excerto": "listing",
    "algorithm": "algorithm", "algoritmo": "algorithm",
}

# `\eqref` conta como referência. Sem isto, as equações apareciam como "nunca referenciadas"
# e mandavam procurar um defeito que não existe — a classe de falso positivo que este projecto
# já pagou várias vezes.
RX_REF = re.compile(r"(\w+)?[~ ]*\\(?:eq)?ref\{([^}]+)\}")
RX_SEC = re.compile(r"\\(chapter|section|subsection|subsubsection)\*?\{")
RX_CAP = re.compile(r"\\caption(?:\[[^\]]*\])?\{")


def sem_comentarios(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


def chaves(s: str, i: int) -> str:
    """Devolve o conteúdo do grupo {...} que começa em i (equilibrando chavetas)."""
    d, out = 0, []
    for c in s[i:]:
        if c == "{":
            d += 1
            if d == 1:
                continue
        elif c == "}":
            d -= 1
            if d == 0:
                break
        if d >= 1:
            out.append(c)
    return "".join(out)


# ── 1. o que cada label rotula ────────────────────────────────────────────────
alvos: dict[str, tuple[str, str]] = {}      # label -> (tipo, título)
for f in FICHEIROS:
    p = pathlib.Path(BASE) / f
    if not p.exists():
        continue
    s = sem_comentarios(p.read_text(encoding="utf-8"))
    for m in re.finditer(r"\\label\{([^}]+)\}", s):
        lab, pos = m.group(1), m.start()
        antes = s[:pos]
        # secção/capítulo mais próximo antes do label
        sec = None
        for ms in RX_SEC.finditer(antes):
            sec = (ms.group(1), chaves(s, ms.end() - 1), ms.start())
        # caption mais próximo antes do label
        cap = None
        for mc in RX_CAP.finditer(antes):
            cap = (chaves(s, mc.end() - 1), mc.start())
        # ambiente flutuante aberto?
        env = None
        rx_env = r"\\begin\{(figure\*?|table\*?|sidewaysfigure|lstlisting|algorithm)\}"
        for me in re.finditer(rx_env, antes):
            env = (me.group(1), me.start())
        if cap and (not sec or cap[1] > sec[2]):
            e = env[0] if env else ""
            tipo = ("figure" if "figure" in e else
                    "table" if "table" in e else
                    "algorithm" if "algorithm" in e else
                    "listing" if "lstlisting" in e else "float")
            alvos[lab] = (tipo, cap[0][:70])
        elif sec:
            tipo = "chapter" if sec[0] == "chapter" else "section"
            alvos[lab] = (tipo, sec[1][:70])
        else:
            alvos[lab] = ("?", "")
    # listings rotulados no argumento opcional
    # ⚠️ As opções do lstlisting atravessam VÁRIAS LINHAS e o label vem entre chavetas
    # (`label={lst:zscore}`). Sem `re.S` e sem as chavetas opcionais, os quatro excertos de
    # código ficavam de fora e apareciam como "label ausente" — um falso alarme que faria
    # procurar um defeito que não existe.
    for m in re.finditer(r"\\begin\{lstlisting\}\[(.*?)\]\s*\n", s, re.S):
        opts = m.group(1)
        cap = re.search(r"caption\s*=\s*\{(.*?)\}\s*,\s*label", opts, re.S)
        for lm in re.finditer(r"label\s*=\s*\{?([\w:.-]+)\}?", opts):
            titulo = " ".join(cap.group(1).split())[:70] if cap else ""
            alvos[lm.group(1)] = ("listing", titulo)

# ── 2. cada ref, com a palavra que a introduz ─────────────────────────────────
linhas = []
for f in FICHEIROS:
    p = pathlib.Path(BASE) / f
    if not p.exists():
        continue
    s = sem_comentarios(p.read_text(encoding="utf-8"))
    for m in RX_REF.finditer(s):
        palavra = (m.group(1) or "").lower().strip()
        lab = m.group(2)
        tipo_exig = PALAVRA_TIPO.get(palavra)
        tipo_real, titulo = alvos.get(lab, ("AUSENTE", ""))
        pref = lab.split(":")[0]
        ctx = " ".join(s[max(0, m.start() - 95):m.start()].split())[-95:]
        mismatch = bool(tipo_exig) and tipo_real not in ("?", "AUSENTE") and (
            tipo_exig != tipo_real
            and not (tipo_exig == "section" and tipo_real == "chapter" and pref in ("app",))
            and not (tipo_exig in ("figure", "table") and tipo_real == "float")
        )
        linhas.append((mismatch, f, palavra or "-", lab, tipo_real, titulo, ctx, pref))

maus = [x for x in linhas if x[0]]
print(f"=== {BASE}: {len(linhas)} referências, {len(alvos)} labels ===")
print(f"=== incompatibilidades de TIPO (palavra vs alvo): {len(maus)} ===\n")
for _m, f, pal, lab, tipo, tit, ctx, _p in maus:
    print(f"  ⚠ {f}\n     ...{ctx}\n     '{pal}' -> {lab} que é um {tipo}: \"{tit}\"\n")

# ── flutuantes que existem e ninguém invoca ───────────────────────────────────
# Uma figura ou tabela sem `\ref` é um defeito real: o LaTeX coloca-a onde couber e o leitor
# nunca é mandado lá. Passa despercebida porque compila sem aviso nenhum.
citados = {x[3] for x in linhas}
orfaos = [(lab, t, ti) for lab, (t, ti) in alvos.items()
          if t in ("figure", "table", "algorithm", "listing", "float") and lab not in citados]
print(f"=== flutuantes NUNCA referenciados: {len(orfaos)} ===")
for lab, t, ti in sorted(orfaos):
    print(f"  ⚠ {lab:32s} [{t}] \"{ti}\"")
print()

ausentes = [x for x in linhas if x[4] == "AUSENTE"]
if ausentes:
    print(f"=== labels não encontrados pelo extractor: {len(set(x[3] for x in ausentes))} ===")
    for lab in sorted({x[3] for x in ausentes}):
        print(f"  {lab}")

if MOSTRAR_TUDO:
    # Agrupado por ALVO: para cada label, o que ele é e todas as frases que o invocam.
    # É assim que se lê 263 referências em minutos em vez de horas — a pergunta passa a ser
    # "estas frases descrevem todas a mesma coisa?", uma vez por alvo e não uma vez por citação.
    from collections import defaultdict
    por_alvo: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for _m, f, pal, lab, _t, _ti, ctx, _p in linhas:
        por_alvo[lab].append((f, pal, ctx))
    print(f"\n=== {len(por_alvo)} ALVOS, agrupados (para leitura) ===")
    for lab in sorted(por_alvo, key=lambda k: (alvos.get(k, ("", ""))[0], k)):
        tipo, tit = alvos.get(lab, ("AUSENTE", ""))
        usos = por_alvo[lab]
        print(f"\n▸ {lab}  [{tipo}] \"{tit}\"   ({len(usos)}x)")
        vistos = set()
        for f, pal, ctx in usos:
            chave = ctx[-55:]
            if chave in vistos:
                continue
            vistos.add(chave)
            print(f"    {f.split('/')[0]:12s} {pal:9s} ...{ctx[-88:]}")

if maus or orfaos or ausentes:
    raise SystemExit(1)
