"""Nenhuma figura pode misturar as duas línguas dentro de si.

Porque é que isto existe. A política linguística do projeto está em
`docs/planos/POLITICA_LINGUISTICA.md` e admite duas configurações defensáveis: interior
das figuras todo em inglês, ou todo em português. O que não é defensável é uma figura
metade em cada, e foi isso que esta verificação encontrou a 2026-09-04: a figura do
percurso de um acontecimento, que é das mais importantes do Capítulo 4, tinha sete nós em
inglês e dois em português. Uma conversão anterior falhou-os, e nada assinalou.

O verificador é deliberadamente conservador: só acusa quando encontra as duas línguas em
rótulos DESENHADOS, e ignora tudo o que não chega ao papel — estilos TikZ, coordenadas
simbólicas, comentários e a legenda, que é portuguesa por desenho.

    python scripts/check_figuras_lingua.py [arvore]
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

RX_COM = re.compile("(?<![" + BS * 2 + "])%.*")
RX_LAB = re.compile(re.escape(BS) + r"label\{(fig:[^}]+)\}")
# só o que é DESENHADO: conteúdo de \node[...]{...} e de xlabel/ylabel/legend
RX_NODE = re.compile(re.escape(BS) + r"node\s*(?:\[[^\]]*\])?\s*(?:\([^)]*\))?\s*"
                     r"(?:at\s*\([^)]*\))?\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
# ⚠️ [^{}]+ NAO CHEGA: um `xlabel={\\gls{PSI} entre o bloco...}` tem chavetas
# la dentro e o padrao antigo nao casava com ele -- logo um rotulo de eixo portugues ao
# lado de ticks ingleses passava. Encontrado a 2026-09-05 na figura da deriva.
RX_EIXO = re.compile(r"(?:xlabel|ylabel|xticklabels|yticklabels"
                     r"|legend|legend entries)\s*=\s*\{([^{}]*"
                     r"(?:\{[^{}]*\}[^{}]*)*)\}")

ING = re.compile(r"(?<![A-Za-zÀ-ú])(the|and|of|for|with|per|from|day|days|news|headline|"
                 r"headlines|alert|alerts|market|company|companies|sector|price|score|"
                 r"threshold|budget|window|precedent|precedents|delivered|deliver|sent|"
                 r"flagged|rate|firing|detection|retrieval|triage|model|baseline|"
                 r"volatility|text|entering|funnel|below|above|already|strong|enough|"
                 r"exhausted|passes|always|distinct|observed|relevant|question|answer|"
                 r"evidence|impact|returns|collect|retrieve|compose|log)"
                 r"(?![A-Za-zÀ-ú])", re.IGNORECASE)
POR = re.compile(r"(?<![A-Za-zÀ-ú])(de|da|do|das|dos|para|com|sem|não|por|que|uma|dias|"
                 r"notícia|notícias|empresa|empresas|mercado|setor|preço|preços|limiar|"
                 r"orçamento|janela|precedente|precedentes|entregue|entregues|entregar|"
                 r"enviado|taxa|deteção|recuperação|recuperar|triagem|modelo|texto|"
                 r"título|títulos|alerta|alertas|resposta|evidência|retorno|retornos|"
                 r"registar|exige|estabelecido|ciclo|artefacto|artefactos|versionado|versionada|"
                r"teste|testes|mesmo|mesma|mesmos|mesmas|retreino|ausente|ausência|"
                r"construção|observação|validação|calibração|conjunto|rotulado|dados|"
                r"decisão|decisões|treino|aguardar|espera|produção|única|único|"
                r"deriva|repartição|semelhança|orçamento|manchete|manchetes|moderada|"
                r"moderado|significativa|significativo|bloco|entre|treino)"
                 r"(?![A-Za-zÀ-ú])", re.IGNORECASE)

# ⚠️ A LISTA FECHADA FOI A CAUSA DE UMA CEGUEIRA REAL, a 2026-09-05: a figura do ciclo
# de vida tinha `artefacto versionado`, `teste` e `retreino: ausente` ao lado de rótulos
# ingleses, e nenhuma dessas palavras estava na lista, pelo que a figura contava como
# monolingue. Daí este segundo sinal, que não depende de vocabulário nenhum: a ortografia.
ORTO = re.compile(r"[àáâãçéêíóôõú]", re.IGNORECASE)

# ⚠️ E O LADO INGLÊS TINHA A MESMA CEGUEIRA, encontrada no mesmo dia pelo outro lado: a
# figura do ciclo de retreino atravessou o verificador com `promotion gate` e `does not
# win: log and discard`, porque nenhuma dessas palavras estava na lista de cima e o lado
# português disparava pela ortografia. Dois sinais que não dependem do vocabulário desta
# tese, simétricos ao ORTO.
#
# Palavras funcionais escolhidas por NÃO existirem em português: `a`, `e`, `no`, `as`,
# `os`, `ou`, `se`, `da` ficariam a acusar todas as figuras portuguesas.
FUNC = re.compile(r"(?<![A-Za-zÀ-ú])(the|and|of|to|is|are|was|were|with|for|not|nor|"
                  r"does|did|from|by|that|this|these|those|its|it|each|both|than|then|"
                  r"when|where|what|how|why|only|still|they|their|there|been|have|has|"
                  r"had|but|into|onto|over|under|about|after|before|while|which|whose|"
                  r"any|all|none|such|same|other|another|between|within|without)"
                  r"(?![A-Za-zÀ-ú])", re.IGNORECASE)

# Terminações que o inglês tem e o português não. ⚠️ A fronteira final é o que separa
# `-ment` de `momento` e `-tion` de `ordenação`: sem ela, metade das figuras portuguesas
# passaria a ser acusada.
SUFX = re.compile(r"(?<![A-Za-zÀ-ú])[A-Za-z]{3,}"
                  r"(?:tion|ment|ing|ness|ity|ly|ed)(?![A-Za-zÀ-ú])")

FICH = [BASE / f"ch{i}/chapter{i}.tex" for i in range(1, 7)]
FICH += [BASE / "appendices/appendixA.tex"]
_exist = [f for f in FICH if f.exists()]
if not _exist:
    print(f"ERRO: nenhum capítulo encontrado em '{BASE}'. Um verificador que não vê o "
          "corpus tem de ser indistinguível de um que falha.")
    raise SystemExit(2)


# Termos que a regra 2 da política mantém na forma corrente da área: não contam para
# nenhuma das duas línguas, e sem isto 'z-score' fazia uma figura portuguesa parecer
# mista, porque contém a palavra inglesa 'score'.
BILINGUE = re.compile(r"z-score|bootstrap|Brier|PR-AUC|ROC-AUC|Platt|Vasicek|SBERT|"
                      r"ONNX|MiniLM|MPNet|FNSPID|beta|softmax|embedding|"
                      # nomes próprios de métodos, sem tradução nas duas línguas
                      r"Isolation Forest|Local Outlier Factor|Random Forest|"
                      r"Sentence-BERT|BERT|FinBERT|GARCH|ARCH|Wilson|PSI",
                      re.IGNORECASE)


# O texto entre aspas é material citado de um corpus inglês, e a política manda-o ficar
# como está: traduzir um título de notícia quebra a correspondência com a fonte, que é a
# propriedade que este trabalho existe para preservar. Sai antes de comparar, pela mesma
# razão pela qual a legenda já saía.
RX_CITA = re.compile(r"``[^`']*''|`[^`']*'")


def _limpa(t: str) -> str:
    t = RX_CITA.sub(" ", t)
    # ⚠️ O DELIMITADOR DE MATEMATICA TAMBEM ESCONDE UM TERMO BILINGUE. `\emph{z}-score`
    # perde o comando aqui e passa a casar com a lista BILINGUE; `$z$-score` nao tem
    # comando nenhum, sobrevivia inteiro, e a palavra `score` disparava o lado ingles
    # numa figura inteiramente portuguesa. E a terceira forma da mesma armadilha.
    t = re.sub(re.escape(BS) + r"[a-zA-Z]+", " ", t)
    t = t.replace("$", "")
    return t.replace("{", "").replace("}", "")


def rotulos(bloco: str) -> list[str]:
    """Só o texto que é efetivamente desenhado."""
    out = []
    for m in RX_NODE.finditer(bloco):
        t = m.group(1).strip()
        if t and not re.fullmatch(r"[\d.,\s$\\%+-]*", t):
            out.append(t)
    out += [m.group(1) for m in RX_EIXO.finditer(bloco)]
    return out


def main() -> int:
    mistas, total = [], 0
    for f in _exist:
        txt = f.read_text(encoding="utf-8", errors="replace")
        for b in re.split(re.escape(BS) + r"begin\{figure\*?\}", txt)[1:]:
            b = b.split(BS + "end{figure}")[0]
            total += 1
            m = RX_LAB.search(b)
            rot = m.group(1) if m else "(sem label)"
            # a legenda é portuguesa por desenho: sai antes de comparar
            corpo = re.sub(re.escape(BS) + r"caption(\[[^\]]*\])?\{.*", "", b, flags=re.S)
            corpo = RX_COM.sub("", corpo)
            labs = rotulos(corpo)
            # tirar comandos e chavetas ANTES de comparar: sem isto o rótulo
            # 'emph{z}-score' não casava com o termo bilingue 'z-score' e uma figura
            # inteiramente portuguesa aparecia como mista.
            labs = [BILINGUE.sub(" ", _limpa(t)) for t in labs]
            en = [t for t in labs
                  if ING.search(t) or FUNC.search(t) or SUFX.search(t)]
            pt = [t for t in labs if POR.search(t) or ORTO.search(t)]
            if en and pt:
                mistas.append((f.parts[-2], rot, pt, en))

    print(f"{total} figuras · {len(mistas)} com as duas línguas no interior")
    if not mistas:
        print("ok  nenhuma figura mistura português e inglês nos rótulos desenhados.")
        return 0
    print()
    for cap, rot, pt, en in mistas:
        print(f"  ⚠ {cap}  {rot}")
        print("      PT: " + " | ".join(t[:46] for t in pt[:3]))
        print("      EN: " + " | ".join(t[:46] for t in en[:3]))
    print()
    print("FALHA: uma figura metade em cada língua não é defensável sob nenhuma das duas "
          "configurações que a política admite. Ver docs/planos/POLITICA_LINGUISTICA.md.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
