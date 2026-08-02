"""Dashboard v2 — lista compacta à esquerda, UM painel de detalhe à direita.

*Estatuto.* Não substitui `app/streamlit_app.py`. A app antiga continua implantada e intocada;
esta corre ao lado até passar `docs/design/dashboard_acceptance.md`.

*Porque foi refeito o layout (3.ª iteração).* A versão anterior punha um expander por baixo de
cada linha. Resultado: três nomes sinalizados ocupavam o ecrã inteiro e liam-se como **seis**
itens, metade deles vazios. A informação estava lá e a interface estava suja.

Agora: **todos os nomes numa lista compacta à esquerda**, sempre visíveis, e **um só painel de
detalhe à direita**, num sítio fixo. Clicar num nome troca o conteúdo do painel; não abre nem
fecha nada, por isso a lista nunca salta debaixo do rato. É o padrão de dossiê do worldmonitor,
e é isso que faz aquilo parecer um instrumento em vez de um formulário.

*Intervalo por omissão: 1D.* É preferência registada do autor, e é a certa: a pergunta que o
painel responde é "o que está a acontecer **hoje**".

*O que NÃO se mostra, de propósito:* score de convergência e badges de tipo de evento. Existem no
worldmonitor, ficam bem, e a nossa própria medição não os sustenta (critério **H4**).

Correr:  streamlit run app/dashboard.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

st.set_page_config(page_title="InvestiGator", page_icon="🐊", layout="wide",
                   initial_sidebar_state="collapsed")

from app import streamlit_app as base  # noqa: E402

_HAS_PLOTLY = base._HAS_PLOTLY
if _HAS_PLOTLY:
    import plotly.graph_objects as go

_BG, _PANEL, _LINE = "#0E1116", "#161A21", "#232935"
_TXT, _DIM = "#E6EAF0", "#8B94A3"
_UP_C, _DOWN_C, _FLAT_C, _WARN = "#22C55E", "#EF4444", "#8B94A3", "#F59E0B"
_ACCENT = "#0A8F52"
_UP, _DOWN, _FLAT = "▲", "▼", "─"

_CSS = f"""
<style>
  .stApp {{ background:{_BG}; }}
  .stApp p, .stApp li, .stApp span, .stApp label {{ color:{_TXT}; }}
  .stApp [data-testid="stCaptionContainer"] p {{ color:{_DIM}; }}
  div[data-testid="stWidgetLabel"] p {{ color:{_TXT} !important; }}
  section.main > div {{ padding-top:.8rem; }}
  hr {{ border-color:{_LINE} !important; }}

  /* Cada nome é um BOTÃO de largura total, estilizado como linha de tabela. Um clique troca o
     painel de detalhe; nada abre nem fecha, por isso a lista nunca salta. */
  div[data-testid="stButton"] > button {{
      background:{_PANEL}; border:1px solid {_LINE}; border-radius:8px;
      color:{_TXT}; text-align:left; padding:6px 11px; width:100%;
      font-variant-numeric:tabular-nums; font-size:.84rem; line-height:1.3;
      white-space:pre; font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;
      margin-bottom:-6px; }}
  div[data-testid="stButton"] > button:hover {{ border-color:{_ACCENT}; color:{_TXT};
                                                background:#1B212A; }}
  div[data-testid="stButton"] > button:focus {{ box-shadow:none; color:{_TXT}; }}

  div[data-testid="stTextInput"] input {{ background:{_PANEL}; color:{_TXT};
                                          border:1px solid {_LINE}; }}
  div[data-testid="stTextInput"] input::placeholder {{ color:{_DIM}; }}
  div[data-baseweb="select"] > div {{ background:{_PANEL}; border-color:{_LINE}; }}
  div[data-testid="stExpander"] {{ background:{_PANEL}; border:1px solid {_LINE};
                                   border-radius:10px; }}
  .ig-hdr {{ font-size:.72rem; color:{_DIM}; text-transform:uppercase;
             letter-spacing:.1em; margin:2px 0 8px 0; }}
  .ig-sub {{ color:{_DIM}; font-size:.77rem; }}
  /* O Streamlit embrulha o rótulo do botão num <p> próprio; sem isto fica centrado e a
     lista lê-se esfarrapada. */
  div[data-testid="stButton"] > button p {{ text-align:left !important; color:{_TXT};
                                            font-family:inherit; font-size:inherit; }}
  div[data-testid="stButton"] > button div {{ justify-content:flex-start !important;
                                              width:100%; }}
  /* `st.text` renderiza num <pre> que herda fundo claro: ficava escuro sobre escuro. */
  .stApp code, .stApp pre, div[data-testid="stText"], div[data-testid="stText"] pre {{
      background:{_BG} !important; color:{_TXT} !important; border:1px solid {_LINE};
      border-radius:8px; padding:9px 11px; font-size:.8rem; }}
  div[data-baseweb="select"] div {{ color:{_TXT} !important; }}
  div[data-baseweb="popover"] li {{ background:{_PANEL}; color:{_TXT}; }}
</style>
"""


def _arrow(v: float) -> tuple[str, str]:
    """(símbolo, cor). Texto puro: nunca depende de fontes de emoji nem de parsing."""
    if v > 0.0005:
        return _UP, _UP_C
    if v < -0.0005:
        return _DOWN, _DOWN_C
    return _FLAT, _FLAT_C


def _head() -> None:
    a, b = st.columns([3, 2])
    with a:
        st.markdown(
            f"<div style='font-size:1.6rem;font-weight:800;letter-spacing:-.02em;"
            f"color:{_TXT}'>Investi<span style='color:{_ACCENT}'>Gator</span></div>"
            f"<div class='ig-sub'><b style='color:{_TXT}'>Every move investigated, never "
            f"predicted.</b> Is this unusual · company or market · has it happened before."
            f"</div>", unsafe_allow_html=True)
    with b:
        base._market_state()
        base._latency_badge()


# ── A lista: todos os nomes, sempre visíveis ────────────────────────────────────
@st.fragment(run_every=60)
def _surface() -> None:
    linhas = [r for r in (base._unusualness(t) for t in base._watchlist()) if r]
    if not linhas:
        st.info("Market data is unavailable. Nothing is hidden: the price sources are not "
                "responding.")
        return
    # Sinalizados primeiro, depois por quão fora do normal.
    linhas.sort(key=lambda r: (not r["is_anomaly"], -abs(r["z"])))

    busca = st.text_input("filter", placeholder="Filter: nvda, tsla…",
                          label_visibility="collapsed", key="v2_jump").strip().lower()
    mostrados = [r for r in linhas if busca in r["ticker"].lower()] if busca else linhas
    if not mostrados:
        st.caption("No name matches that.")
        return

    n = sum(1 for r in mostrados if r["is_anomaly"])
    st.markdown(f"<div class='ig-hdr'>{n} past threshold · {len(mostrados) - n} quiet "
                f"&nbsp;·&nbsp; click to inspect</div>", unsafe_allow_html=True)

    if st.session_state.get("v2_sel") not in {r["ticker"] for r in mostrados}:
        st.session_state.v2_sel = mostrados[0]["ticker"]

    for r in mostrados:
        _row_button(r)


def _row_button(r: dict) -> None:
    """Uma linha clicável na largura toda.

    Os botões do Streamlit não aceitam HTML no rótulo, por isso o alinhamento em colunas é
    feito com largura fixa e fonte monoespaçada. Lê-se como uma tabela e clica-se como uma
    linha, que é o que se quer.
    """
    t = r["ticker"]
    seta, _ = _arrow(r["move"])
    vol = base._volume_signal(t)
    marca = f" {vol['ratio']:.1f}x" if (vol and vol.get("unusual")) else "     "
    sinal = "●" if r["is_anomaly"] else "·"
    sel = "▏" if st.session_state.get("v2_sel") == t else " "
    rotulo = f"{sel}{sinal} {t:<6}{seta}{r['move'] * 100:+7.2f}%  z{r['z']:+6.2f}{marca}"
    if st.button(rotulo, key=f"v2_btn_{t}", use_container_width=True):
        st.session_state.v2_sel = t


# ── O painel: sempre no mesmo sítio, só o conteúdo muda ─────────────────────────
def _panel() -> None:
    t = st.session_state.get("v2_sel")
    if not t:
        st.caption("Select a name on the left.")
        return

    r = base._unusualness(t)
    if r:
        seta, cor = _arrow(r["move"])
        st.markdown(
            f"<div style='font-size:1.25rem;font-weight:700;color:{_TXT}'>{t} "
            f"<span style='color:{cor}'>{seta} {r['move'] * 100:+.2f}%</span></div>"
            f"<div class='ig-sub'>z-score {r['z']:+.2f} versus the 20-day norm"
            + (" · past the alert threshold" if r["is_anomaly"] else "")
            + "</div>", unsafe_allow_html=True)

    # 1D por omissão: a pergunta do painel é "o que está a acontecer hoje".
    rng = st.radio("Range", list(base._RANGES), horizontal=True, index=0,
                   label_visibility="collapsed", key="v2_range")
    try:
        serie = base._range_prices(t, rng)
    except Exception:  # noqa: BLE001
        st.caption("Price history unavailable.")
        return
    if serie is None or serie.empty:
        st.caption("No price data for this range.")
        return

    if _HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(serie.index), y=[float(v) for v in serie.values], mode="lines",
            line={"width": 2, "color": _ACCENT},
            hovertemplate="$%{y:.2f} · %{x}<extra></extra>", name=t))
        base._mark_alerts_on_chart(fig, t, serie)
        fig.update_layout(height=300, margin={"l": 0, "r": 0, "t": 4, "b": 0},
                          showlegend=False, hovermode="closest",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font={"color": _DIM})
        fig.update_xaxes(showgrid=False, showspikes=True, spikemode="across",
                         spikecolor=_LINE)
        fig.update_yaxes(gridcolor=_LINE, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, key=f"v2_chart_{t}_{rng}")
        st.markdown("<span class='ig-sub'>▲▼ market alerts · ● news alerts on the chart. "
                    "Hover reads exactly what the channel sent; nothing is recomputed.</span>",
                    unsafe_allow_html=True)
    else:
        st.line_chart(serie)

    st.markdown("<div class='ig-hdr' style='margin-top:12px'>Company or market?</div>",
                unsafe_allow_html=True)
    d = base._decomposition(t)
    if d and not d.get("error"):
        cols = st.columns(3)
        for col, (etiqueta, chave) in zip(
                cols, (("Market", "market"), ("Sector", "sector"), ("Company", "company")),
                strict=True):
            s, c = _arrow(d[chave])
            with col:
                st.markdown(
                    f"<div class='ig-sub'>{etiqueta}</div>"
                    f"<div style='font-size:1.15rem;font-weight:700;color:{c}'>"
                    f"{s} {d[chave] * 100:+.2f}%</div>", unsafe_allow_html=True)
        st.markdown("<div class='ig-sub' style='margin-top:4px'>Rolling beta against the index "
                    "and a sector proxy, estimated only on data before the day being "
                    "explained.</div>", unsafe_allow_html=True)
    else:
        st.caption("Split unavailable (needs index and sector data).")

    st.markdown("<div class='ig-hdr' style='margin-top:14px'>What the channel sent</div>",
                unsafe_allow_html=True)
    _events_flat(t)


def _events_flat(t: str) -> None:
    entradas = [e for e in base._shared_history() if e.ticker == t]
    if not entradas:
        st.caption("No alerts recorded for this company yet.")
        return
    entradas = list(reversed(entradas))[:8]
    rotulos = [f"{e.date} · {(e.text.strip().splitlines() or [e.kind])[0][:56]}"
               for e in entradas]
    i = st.selectbox("Alert", range(len(entradas)), format_func=lambda k: rotulos[k],
                     label_visibility="collapsed", key=f"v2_ev_{t}")
    st.text(entradas[i].text)
    st.markdown("<span class='ig-sub'>Read from the same shared record the Telegram channel "
                "received. Never recomputed here.</span>", unsafe_allow_html=True)


def main() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    _head()
    st.divider()
    esq, dir_ = st.columns([1, 1.9], gap="medium")
    with esq:
        _surface()
    with dir_:
        _panel()
    st.divider()
    if st.toggle("Method, frozen numbers, and the negative result", value=False,
                 key="v2_method"):
        base._method_view()


main()
