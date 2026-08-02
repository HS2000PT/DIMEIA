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
FG = "#E8ECF2"
FG_DIM = "#8A94A6"
FG_MUTE = "#5A6474"

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
ICON_UP = "▲"
ICON_DOWN = "▼"
ICON_FLAT = "─"
ICON_ALERT = "⚑"  # passou todos os gates e foi enviado
ICON_DETECT = "○"  # o método detectaria, mas um gate suprimiu
ICON_NEWS = "●"  # notícia captada, impacto medido
ICON_VOLUME = "◆"  # volume invulgar


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


def row_css(ticker: str, colour: str, logo_uri: str | None, flagged: bool,
            selected: bool) -> str:
    """Regra CSS para uma linha da lista, endereçada pela classe `st-key-*`.

    A cor e a atenção ficam em **eixos separados**: a cor do texto é a direcção do
    movimento, e a barra à esquerda é o estado (sinalizado / seleccionado). Misturar os
    dois num só canal foi o que produziu, numa versão anterior, uma seta verde por cima de
    um número negativo.
    """
    # `!important` em vez de tentar adivinhar a estrutura do DOM. A regra geral dos botões
    # (`div[data-testid="stButton"] > button`) é mais específica do que uma classe simples
    # e ganharia a esta em silêncio — foi assim que os logótipos desapareceram uma vez.
    botao = []
    if logo_uri:
        botao.append(f'background:transparent url("{logo_uri}") no-repeat '
                     f"7px center/17px 17px !important")
    if selected:
        botao.append(f"background-color:{PANEL_2} !important")
        botao.append(f"border-left-color:{colour} !important")
    elif flagged:
        botao.append(f"border-left-color:{FLAG} !important")
    alvo = f".st-key-btn_{ticker} button"
    return (f"<style>{alvo}{{{';'.join(botao)}}}"
            f"{alvo},{alvo} p{{color:{colour} !important}}</style>")


def css() -> str:
    """A folha de estilo. Devolvida como texto para a app a injectar uma vez."""
    return f"""
<style>
  /* Streamlit traz muito enchimento por defeito; num painel denso é espaço perdido. */
  .stApp {{ background: {BG}; }}
  .block-container {{ padding: 0.8rem 1.2rem 2rem; max-width: 1600px; }}
  #MainMenu, footer, header {{ visibility: hidden; }}

  html, body, [class*="css"] {{
    color: {FG};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}

  /* Todos os números da interface passam por aqui. */
  .num {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums;
  }}

  .rule {{ border: 0; border-top: 1px solid {LINE}; margin: 0.9rem 0 0.7rem; }}

  .label {{
    font-size: 10px; letter-spacing: 0.09em; text-transform: uppercase;
    color: {FG_MUTE}; font-weight: 600;
  }}

  .panel {{
    background: {PANEL}; border: 1px solid {LINE};
    border-radius: 8px; padding: 0.85rem 1rem;
  }}

  /* ── Linha da watchlist ─────────────────────────────────────────────────────────
     Cada linha é UM botão e mais nada. A tentativa anterior desenhava a linha em HTML e
     punha um botão por baixo para a tornar clicável: davam duas linhas por empresa, com o
     nome centrado, e a lista ficava com o dobro da altura e ilegível. Aqui o logótipo
     entra como imagem de fundo do próprio botão e os dados são o rótulo, em monoespaçado
     com `white-space: pre` — uma linha, alinhada em colunas, clicável em toda a largura. */
  div[data-testid="stButton"] {{ margin-bottom: -0.42rem; }}
  /* Nenhuma propriedade `background-*` aqui além da cor. Ter cá `background-repeat`,
     `-position` e `-size` parecia inofensivo, mas o browser volta a juntá-las na
     abreviatura `background`, e a abreviatura repõe `background-image: initial` — o que
     apagava, em silêncio, o logótipo que a regra por linha tinha acabado de definir.
     Todas as propriedades do logótipo vivem juntas em `row_css`. */
  div[data-testid="stButton"] > button {{
    background-color: transparent;
    border: 1px solid transparent; border-left: 2px solid transparent;
    border-radius: 6px; padding: 0.3rem 0.5rem 0.3rem 30px; width: 100%;
    min-height: 0; line-height: 1.2;
  }}
  div[data-testid="stButton"] > button:hover {{ background-color: {PANEL_2}; }}
  div[data-testid="stButton"] > button div[data-testid="stMarkdownContainer"] {{
    text-align: left; width: 100%;
  }}
  div[data-testid="stButton"] > button p {{
    text-align: left; margin: 0;
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-variant-numeric: tabular-nums; font-size: 12px; white-space: pre;
  }}

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
    font-size: 11px; color: {FG_DIM} !important; margin: 0;
  }}
  div[role="radiogroup"] > label:has(input:checked) {{
    background: {PANEL_2}; border-color: {UP};
  }}
  div[role="radiogroup"] > label:has(input:checked) p {{ color: {UP} !important; }}

  /* Rótulos dos widgets: cinzento-claro sobre escuro é ilegível. */
  label, .stSelectbox label {{ color: {FG_DIM} !important; }}
  div[data-testid="stCaptionContainer"] p {{ color: {FG_MUTE}; font-size: 11px; }}

  /* O texto do alerta: `st.text` herda um fundo claro e sai preto sobre preto. */
  .stCode, pre, div[data-testid="stText"] {{
    background: {PANEL_2} !important; color: {FG_DIM} !important;
    border: 1px solid {LINE} !important; border-radius: 6px; font-size: 11.5px;
  }}
  div[data-testid="stExpander"] {{ border-color: {LINE} !important; background: {PANEL}; }}
  div[data-testid="stExpander"] summary p {{ font-size: 11.5px; color: {FG_DIM};
    font-family: ui-monospace, Menlo, Consolas, monospace; }}
</style>
"""
