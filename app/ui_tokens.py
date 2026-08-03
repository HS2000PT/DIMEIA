"""O sistema visual, num sítio só.

**Porque é que isto é um módulo e não CSS espalhado pela app.** As versões anteriores da
interface escolhiam cores no sítio onde eram precisas. Ao fim de cinco redesenhos havia
verdes diferentes para a mesma coisa, cinzentos que ninguém sabia de onde vinham, e nenhum
sítio onde responder à pergunta "que cor é 'em alta'?". Um sistema resolve isso por
construção: há uma resposta, está aqui, e mudar aqui muda em todo o lado.

**As duas regras que fazem o trabalho todo:**

1. **A cor só transporta significado.** Há exactamente quatro cores com sentido — subida,
   descida, atenção, informação. Tudo o resto é uma escala de cinzentos frios. Se um
   elemento não está a dizer nada sobre o mercado, não tem cor. É isto que separa um painel
   de dados de um cartaz.
2. **Os números são monoespaçados e tabulares.** Numa coluna de dez percentagens, os
   algarismos têm de alinhar verticalmente, senão o olho não consegue comparar sem ler cada
   linha. `font-variant-numeric: tabular-nums` é o que torna uma lista varrível.

**Os ícones.** Formas geométricas Unicode, não emoji. Um emoji depende da fonte do sistema:
o mesmo 📈 sai a cores num telemóvel, cinzento num servidor e como quadrado vazio numa
captura. Já produziu um defeito visível neste projeto — uma seta verde para cima num
movimento de −7,64%. ▲ e ▼ desenham-se com a fonte do texto, recebem a cor que **nós**
lhes damos, e por isso não podem contradizer o número que acompanham.
"""

from __future__ import annotations

# ── Cor ──────────────────────────────────────────────────────────────────────────────
# Superfícies: cinzentos frios (matiz azulada). Deliberado — um cinzento neutro ao lado de
# verde e vermelho parece sujo, e um cinzento quente compete com o âmbar.
BG = "#0B0E13"  # fundo da página
PANEL = "#131820"  # cartões
PANEL_2 = "#1A2029"  # estados de foco e caixas encaixadas
LINE = "#242C38"  # limites

# Texto: três níveis chegam. Mais do que três e a hierarquia deixa de se ler.
#
# Os dois níveis inferiores foram **clareados** depois de os medir contra o fundo. O
# `#5A6474` de antes dava cerca de 3,3:1 sobre `#0B0E13`, abaixo do mínimo de 4,5:1 que a
# WCAG pede para texto pequeno — e como quase tudo aqui é texto pequeno, metade da
# interface estava tecnicamente ilegível. Não era gosto, era contraste a menos.
FG = "#EDF1F7"  # ~16:1
FG_DIM = "#A3AEC2"  # ~9:1  — texto secundário
FG_MUTE = "#7C8AA3"  # ~5,4:1 — rótulos e legendas, ainda acima do mínimo

# Sinal: as únicas cores com significado em toda a interface.
UP = "#00D68F"  # subida
DOWN = "#FF5A5F"  # descida
FLAT = "#8A94A6"  # sem movimento material (é cinzento de propósito: não é sinal)
FLAG = "#FFB020"  # atenção — nunca direcção
NEWS = "#4A9EFF"  # informação — nunca direcção

# ── Ícones ───────────────────────────────────────────────────────────────────────────
# Um conjunto, usado igual em todo o lado. Direcção e estado são eixos SEPARADOS: um
# alerta pode ser de subida (▲) e sinalizado (⚑) ao mesmo tempo, e misturar os dois eixos
# num só glifo foi a origem da confusão nas versões anteriores.
# Cinco símbolos, **um significado cada**. A versão anterior tinha uma colisão real: `◆`
# era "volume invulgar" nas linhas e "alerta enviado" no gráfico, e `⚑` e `○` queriam
# ambos dizer "detectado". Um símbolo com dois sentidos é pior do que símbolo nenhum,
# porque o leitor não sabe que está a ler mal.
ICON_UP = "▲"  # direcção: subiu
ICON_DOWN = "▼"  # direcção: desceu
ICON_FLAT = "─"  # direcção: sem movimento material
ICON_ALERT = "⚑"  # passou todos os gates e saiu para o canal
ICON_DETECT = "○"  # o método detectou, mas um gate suprimiu
ICON_NEWS = "●"  # notícia captada, com impacto medido
# O volume invulgar mostra-se como texto (`3.3×`) e não como glifo: era o sexto símbolo, e
# a partir do quinto ninguém guarda a legenda. Um número com unidade não precisa de legenda.


def direction(value: float | None, floor: float = 0.0005) -> tuple[str, str]:
    """`(ícone, cor)` para um movimento. O piso evita chamar "subida" a +0,01%.

    Devolve os dois juntos de propósito: separá-los foi o que permitiu, no passado, uma
    seta para cima pintada de verde por cima de um número negativo.
    """
    if value is None:
        return ICON_FLAT, FG_MUTE
    if value > floor:
        return ICON_UP, UP
    if value < -floor:
        return ICON_DOWN, DOWN
    return ICON_FLAT, FLAT


def css() -> str:
    """A folha de estilo. Devolvida como texto para a app a injectar uma vez."""
    return f"""
<style>
  /* Streamlit traz muito enchimento por defeito; num painel denso é espaço perdido.
     O `max-width` era 1680 px, o que num ecrã de 1920 deixava 120 px de nada de cada
     lado — visível, e a queixa era exactamente essa. Subiu para 1920 para que o monitor
     mais comum fique cheio de ponta a ponta. Não desapareceu: sem tecto nenhum, um ecrã
     ultra-largo esticaria quatro cartões até uma linha de texto atravessar meio metro,
     que se lê pior do que a margem que estamos a recuperar. */
  .stApp {{ background: {BG}; }}
  .block-container {{ padding: 0.7rem 0.85rem 1rem; max-width: 1920px; }}
  #MainMenu, footer, header {{ visibility: hidden; }}

  html, body, [class*="css"] {{
    color: {FG};
    -webkit-font-smoothing: antialiased;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}

  /* Todos os números da interface passam por aqui. */
  .num {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums;
  }}

  .rule {{ border: 0; border-top: 1px solid {LINE}; margin: 0.9rem 0 0.7rem; }}

  /* O regresso à grelha. Discreto mas não escondido: chega-lhe a cor de informação, sem
     sublinhado, e ganha-o ao passar por cima — não precisa de competir com nada porque é
     a única coisa naquela linha. */
  a.back {{
    font-size: 12.5px; color: {NEWS}; text-decoration: none; font-weight: 600;
  }}
  a.back:hover {{ text-decoration: underline; }}

  /* "o que é isto?" — sublinhado a pontos e cursor de ajuda. Sem isto, o texto parece
     decoração e ninguém descobre que há uma explicação por trás dele. */
  .help {{ cursor: help; border-bottom: 1px dotted currentColor; }}

  .label {{
    font-size: 11px; letter-spacing: 0.09em; text-transform: uppercase;
    color: {FG_MUTE}; font-weight: 600;
  }}

  .panel {{
    background: {PANEL}; border: 1px solid {LINE};
    border-radius: 8px; padding: 0.85rem 1rem;
  }}

  /* ── Botões ─────────────────────────────────────────────────────────────────────
     Hoje os únicos botões da app são os da paginação. A regra que estava aqui vinha da
     lista da v2, onde cada empresa era um botão com o logótipo desenhado como imagem de
     fundo: trazia `padding-left: 30px` para abrir espaço ao ícone e `margin-bottom`
     negativo para colar as linhas umas às outras. Essa lista deixou de existir quando a
     grelha de cartões a substituiu, mas a regra ficou — e é geral, portanto teria
     deformado em silêncio o primeiro botão verdadeiro que aparecesse na página. */
  div[data-testid="stButton"] > button {{
    background-color: {PANEL}; color: {FG_DIM};
    border: 1px solid {LINE}; border-radius: 6px;
    padding: 0.25rem 0.7rem; min-height: 0; line-height: 1.35;
  }}
  div[data-testid="stButton"] > button:hover:not(:disabled) {{
    background-color: {PANEL_2}; border-color: {FG_MUTE}; color: {FG};
  }}
  div[data-testid="stButton"] > button:disabled {{ opacity: 0.38; }}
  div[data-testid="stButton"] > button p {{
    margin: 0; font-size: 12px;
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
  }}

  /* ── Tabelas de eventos ─────────────────────────────────────────────────────────
     Construídas à mão e não com `st.dataframe`. A sonda mostrou que o `st.dataframe`
     **não** briga com o tema escuro — esse risco era hipotético —, mas também não desenha
     a barra divergente do impacto, e a barra é o que deixa ver que a maioria dos desfechos
     foi negativa sem ler um único número. Ainda por cima, `format="%.2f%%"` mostrava
     −0,021 como "−0,02%": errado por um factor de cem, e errado em silêncio. */
  .trow {{
    display: flex; gap: 0.7rem; align-items: center;
    padding: 0.34rem 0; border-top: 1px solid {LINE};
  }}
  .thead {{ border-top: 0; padding: 0 0 0.25rem; }}
  .tcell {{
    flex: 1; min-width: 0; font-size: 13px; color: {FG_DIM};
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }}
  .tfoot {{
    font-size: 11.5px; color: {FG_MUTE}; padding-top: 0.45rem;
    font-family: ui-monospace, Menlo, Consolas, monospace;
  }}

  /* Campos de filtro: compactos, e escuros como tudo o resto. */
  div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {{
    background: {PANEL} !important; border-color: {LINE} !important;
    color: {FG} !important; font-size: 12.5px;
  }}
  div[data-testid="stTextInput"] input::placeholder {{ color: {FG_MUTE} !important; }}

  /* ── Selector de intervalo ──────────────────────────────────────────────────────
     Um rádio do Streamlit tem círculos grandes que num painel denso parecem um
     formulário. Escondidos, sobra o rótulo, que estilizamos como pastilhas. */
  div[role="radiogroup"] {{ gap: 0.3rem; }}
  div[role="radiogroup"] > label {{
    background: {PANEL}; border: 1px solid {LINE}; border-radius: 5px;
    padding: 0.16rem 0.6rem; margin: 0;
  }}
  div[role="radiogroup"] > label:hover {{ border-color: {FG_MUTE}; }}
  div[role="radiogroup"] > label > div:first-child {{ display: none; }}
  div[role="radiogroup"] > label p {{
    font-family: ui-monospace, Menlo, Consolas, monospace;
    font-size: 12px; color: {FG_DIM} !important; margin: 0;
  }}
  div[role="radiogroup"] > label:has(input:checked) {{
    background: {PANEL_2}; border-color: {UP};
  }}
  div[role="radiogroup"] > label:has(input:checked) p {{ color: {UP} !important; }}

  /* Rótulos dos widgets: cinzento-claro sobre escuro é ilegível. */
  label, .stSelectbox label {{ color: {FG_DIM} !important; }}
  div[data-testid="stCaptionContainer"] p {{ color: {FG_MUTE}; font-size: 12px; }}

  /* O texto do alerta: `st.text` herda um fundo claro e sai preto sobre preto. */
  .stCode, pre, div[data-testid="stText"] {{
    background: {PANEL_2} !important; color: {FG_DIM} !important;
    border: 1px solid {LINE} !important; border-radius: 6px; font-size: 12.5px;
  }}
  div[data-testid="stExpander"] {{ border-color: {LINE} !important; background: {PANEL}; }}
  div[data-testid="stExpander"] summary p {{ font-size: 12.5px; color: {FG_DIM};
    font-family: ui-monospace, Menlo, Consolas, monospace; }}
</style>
"""


def card_css() -> str:
    """A grelha de cartões da v3.

    **A decisão que governa este bloco.** Um cartão sinalizado e um cartão calmo têm de
    distinguir-se por **quatro canais redundantes** — posição, quantidade de tinta, corpo de
    letra e uma palavra — e **nunca só por cor** (critério V3). Um utilizador com daltonismo
    tem de conseguir varrer esta página, e mesmo com visão normal a cor sozinha não cria
    hierarquia: dez cartões verdes e vermelhos são dez cartões igualmente ruidosos.

    O cartão calmo é deliberadamente **mais vazio**, não mais pequeno. Vazio é o sinal: se
    todos os dias fossem iguais, o ecrã ficaria quase em branco, que é exactamente a
    mensagem certa para quem só quer permissão para não fazer nada.
    """
    return f"""
<style>
  /* Uma escada explícita, não `auto-fit`/`minmax`. Com `auto-fit` o número de colunas é o
     que calhar caber, e com doze cartões isso produzia linhas órfãs — cinco, cinco e
     **dois** —, que se lê como se os dois últimos fossem outra coisa. Aqui as larguras
     são decididas: 4 colunas dão 4×3 exacto, e cada degrau abaixo continua a dividir doze
     sem deixar ninguém sozinho numa linha (3×4, 2×6, 1×12).

     `minmax(0, 1fr)` e nunca `1fr`: o mínimo implícito de uma coluna de grelha é
     `auto`, ou seja, o tamanho do conteúdo — e como o número grande do cartão é
     `white-space: nowrap`, uma coluna estreita seria empurrada para além da sua largura
     em vez de encolher. O `0` é o que autoriza a célula a ser mais pequena do que aquilo
     que tem lá dentro. */
  /* `align-items: start` e não o `stretch` que a grelha faz por defeito. Sem isto, uma
     célula calma numa linha que tem cartões sinalizados é esticada até à altura deles, e
     o resultado é um rectângulo com borda e nada lá dentro — que se lê como se faltasse
     qualquer coisa. O comentário aqui em baixo afirmava que o cartão calmo era
     "genuinamente mais curto"; era falso enquanto a grelha o esticava, e a captura
     mostrou-o. Agora é verdade. */
  .grid {{
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
    align-items: start;
    gap: 0.55rem; margin: 0.55rem 0 0.9rem;
  }}
  @media (max-width: 1279px) {{
    .grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  }}
  @media (max-width: 899px) {{
    .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  }}
  @media (max-width: 599px) {{
    .grid {{ grid-template-columns: minmax(0, 1fr); }}
  }}

  /* O cartão inteiro é a área de clique. Sem botão por baixo: essa tentativa deu duas
     linhas por empresa e o dobro da altura (ver a nota em `css()`). */
  a.card {{
    display: block; text-decoration: none; color: inherit;
    background: {PANEL}; border: 1px solid {LINE}; border-left: 3px solid transparent;
    border-radius: 8px; padding: 0.55rem 0.7rem 0.6rem;
    /* Sem `min-height`. Era 132 px e um cartão calmo tem uma linha, portanto sobravam
       ~70 px de nada, dez vezes. O alinhamento fica ao cargo da grelha (as células de
       uma linha já têm a mesma altura), e o cartão calmo passa a ser genuinamente mais
       curto — o que reforça a distinção em vez de a esconder atrás de espaço morto. */
    transition: background-color .12s ease, border-color .12s ease;
  }}
  a.card:hover {{ border-color: {FG_MUTE}; background: {PANEL_2}; }}
  a.card:focus-visible {{ outline: 2px solid {UP}; outline-offset: 2px; }}
  a.card--flagged {{ border-left-color: {FLAG}; }}
  a.card--quiet {{ background: transparent; }}

  /* A escala subiu um degrau em todo o cartão. A anterior tinha sido afinada a olhar para
     um terminal denso, e a 12,5 px o veredicto — que é a única coisa que este ecrã existe
     para fazer ler — pedia esforço a quem não passa o dia em painéis. Densidade não é
     letra pequena; é não desperdiçar espaço. O espaço veio das margens (ver `css()`) e da
     linha que a pílula libertou. */
  .card-top {{ display: flex; align-items: center; gap: 0.4rem;
               margin-bottom: 0.35rem; min-width: 0; }}
  /* `min-width: 0` e `flex: 1 1 auto`: sem eles um item flex recusa-se a encolher abaixo
     do seu conteúdo, e o `text-overflow: ellipsis` nunca chega a disparar — o nome
     empurrava o número para fora do cartão em vez de reticenciar. */
  .card-name {{
    flex: 1 1 auto; min-width: 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    font-size: 14px; font-weight: 700; color: {FG};
  }}
  .card-tick {{ font-size: 11px; color: {FG_MUTE}; flex: 0 0 auto; }}
  /* `nowrap` e um corpo que se adapta: numa coluna estreita, "+14.25%" com 21 px partia
     em duas linhas e a seta ficava sozinha por cima do número. `clamp` deixa-o encolher
     em vez de partir. */
  .card-move {{
    margin-left: auto; flex: 0 0 auto; font-weight: 700; white-space: nowrap;
    font-size: clamp(16px, 1.35vw, 21px);
  }}
  .card--quiet .card-move {{ font-size: clamp(14px, 1.05vw, 16px); font-weight: 500; }}

  /* A linha da pílula. Existe só nos cartões sinalizados — num cartão calmo não há linha
     nenhuma, e é o vazio que faz o trabalho. */
  .card-state {{ margin-bottom: 0.3rem; }}
  .pill {{
    font-size: 10px; letter-spacing: 0.09em; font-weight: 700; color: {BG};
    background: {FLAG}; border-radius: 3px; padding: 1.5px 6px;
  }}

  /* O veredicto é o herói. É a primeira coisa que se lê e a única obrigatória. */
  .verdict {{ font-size: 14px; line-height: 1.45; color: {FG}; }}
  .card--quiet .verdict {{ color: {FG_DIM}; font-size: 13px; }}

  .chips {{
    display: flex; flex-wrap: wrap; gap: 0.4rem 0.7rem; margin-top: 0.5rem;
    font-size: 11px; color: {FG_MUTE};
  }}
  .spark {{ margin-top: 0.45rem; display: block; }}
</style>
"""
