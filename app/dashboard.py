"""Dashboard v2 — uma superfície densa e escura, construída AO LADO da app atual.

*Estatuto.* Não substitui `app/streamlit_app.py`. A app antiga continua implantada e intocada;
esta corre em paralelo até passar `docs/design/dashboard_acceptance.md`. Se não passar, deita-se
fora. É o que permite fazer a sexta tentativa de redesenho sem arriscar a entrega.

*Desenho.* Justificado em `docs/design/dashboard_v2_design.md`, a partir de uma leitura do
worldmonitor.app. O que se aproveitou não foi o mapa: foi o padrão de **uma superfície densa com
divulgação progressiva**, em vez de ecrãs entre os quais se navega.

- fundo **escuro**, que é o que faz uma parede de números parecer um instrumento e não um
  formulário;
- **sparkline por linha**, para o olho varrer dez nomes num segundo sem clicar em nada;
- **salto rápido** por escrita, o equivalente prático da paleta de comandos;
- **o gráfico é o herói**, com os sinais em cima dele no eixo do tempo;
- direção por **texto** (▲ ▼ ─), que nunca depende de fontes de emoji.

*O que NÃO se copia, e está escrito porque:* score de convergência e badges de tipo de evento.
Existem no worldmonitor, ficam bem, e a nossa medição não os sustenta (critério **H4**). Copiar a
estética e ignorar a evidência é exatamente o que a tese critica nas ferramentas comerciais.

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

# ── Paleta: escura, com o verde da marca como único acento vivo ─────────────────
_BG, _PANEL, _LINE = "#0E1116", "#161A21", "#232935"
_TXT, _DIM = "#E6EAF0", "#8B94A3"
_UP_C, _DOWN_C, _FLAT_C, _WARN = "#22C55E", "#EF4444", "#8B94A3", "#F59E0B"
_ACCENT = "#0A8F52"

_CSS = f"""
<style>
  .stApp {{ background:{_BG}; color:{_TXT}; }}
  section.main > div {{ padding-top:1rem; }}
  .ig-row {{ background:{_PANEL}; border:1px solid {_LINE}; border-radius:10px;
             padding:10px 14px; margin-bottom:7px; }}
  .ig-row:hover {{ border-color:{_ACCENT}66; }}
  .ig-tkr {{ font-size:1.02rem; font-weight:700; letter-spacing:.02em; }}
  .ig-move {{ font-size:1.02rem; font-weight:700; }}
  .ig-sub {{ color:{_DIM}; font-size:.76rem; }}
  .ig-chip {{ display:inline-block; padding:1px 8px; border-radius:20px;
              font-size:.72rem; font-weight:600; margin-right:5px; }}
  .ig-split {{ font-size:.8rem; color:{_DIM}; font-variant-numeric:tabular-nums; }}
  .ig-split b {{ color:{_TXT}; }}
  div[data-testid="stExpander"] {{ background:{_PANEL}; border:1px solid {_LINE};
                                   border-radius:10px; }}
  div[data-testid="stMetricValue"] {{ color:{_TXT}; }}
  .ig-hdr {{ font-size:.78rem; color:{_DIM}; text-transform:uppercase;
             letter-spacing:.09em; margin-bottom:6px; }}
  div[data-testid="stTextInput"] input {{ background:{_PANEL}; color:{_TXT};
                                          border:1px solid {_LINE}; }}
  div[data-testid="stTextInput"] input::placeholder {{ color:{_DIM}; }}
  div[data-baseweb="select"] > div {{ background:{_PANEL}; border-color:{_LINE};
                                      color:{_TXT}; }}
  div[data-testid="stExpander"] summary {{ color:{_TXT}; }}
  div[data-testid="stExpander"] summary:hover {{ color:{_ACCENT}; }}
  /* O expander de detalhe pertence à linha acima: cola-se a ela. */
  div[data-testid="stExpander"] {{ margin-top:-9px; margin-bottom:12px; }}
  .stApp code, .stApp pre {{ background:{_BG}; color:{_TXT}; }}
  /* O Streamlit pinta os rótulos de widget de cinzento-claro, ilegível sobre escuro. */
  div[data-testid="stWidgetLabel"] p, label[data-testid="stWidgetLabel"] p,
  .stCheckbox label p, .stRadio label p {{ color:{_TXT} !important; }}
  .stApp p, .stApp li, .stApp span {{ color:{_TXT}; }}
  .stApp [data-testid="stCaptionContainer"] p {{ color:{_DIM}; }}
</style>
"""

_UP, _DOWN, _FLAT = "▲", "▼", "─"


def _arrow(v: float) -> tuple[str, str]:
    """(símbolo, cor). Texto puro: nunca depende de fontes de emoji nem de parsing."""
    if v > 0.0005:
        return _UP, _UP_C
    if v < -0.0005:
        return _DOWN, _DOWN_C
    return _FLAT, _FLAT_C


def _chip(t: str, c: str) -> str:
    return f"<span class='ig-chip' style='background:{c}22;color:{c}'>{t}</span>"


def _sparkline(serie, cor: str) -> str:
    """Sparkline como SVG inline.

    Um gráfico do Plotly por linha tornaria a página lenta e pesada; isto é um caminho SVG de
    algumas centenas de bytes, e é o que permite varrer dez nomes de uma vez sem clicar.
    """
    try:
        vals = [float(v) for v in serie.values if v == v][-40:]
        if len(vals) < 3:
            return ""
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or 1.0
        w, h = 108, 26
        pts = " ".join(
            f"{i / (len(vals) - 1) * w:.1f},{h - (v - lo) / span * (h - 3) - 1.5:.1f}"
            for i, v in enumerate(vals)
        )
        return (f"<svg width='{w}' height='{h}' style='vertical-align:middle'>"
                f"<polyline points='{pts}' fill='none' stroke='{cor}' stroke-width='1.6' "
                f"stroke-linejoin='round'/></svg>")
    except Exception:  # noqa: BLE001
        return ""


# ── Cabeçalho ───────────────────────────────────────────────────────────────────
def _head() -> None:
    a, b = st.columns([3, 2])
    with a:
        st.markdown(
            f"<div style='font-size:1.7rem;font-weight:800;letter-spacing:-.02em'>"
            f"Investi<span style='color:{_ACCENT}'>Gator</span></div>"
            f"<div class='ig-sub'><b style='color:{_TXT}'>Every move investigated, never "
            f"predicted.</b> &nbsp;Is this unusual · company or market · has it happened "
            f"before.</div>", unsafe_allow_html=True)
    with b:
        base._market_state()
        base._latency_badge()


# ── A superfície ────────────────────────────────────────────────────────────────
@st.fragment(run_every=60)
def _surface() -> None:
    linhas = [r for r in (base._unusualness(t) for t in base._watchlist()) if r]
    if not linhas:
        st.info("Market data is unavailable right now. Nothing is hidden: the price sources "
                "are not responding.")
        return
    linhas.sort(key=lambda r: -abs(r["z"]))

    # O equivalente prático da paleta de comandos: escrever filtra, sem aprender interface.
    busca = st.text_input("jump", placeholder="Type to jump: nvda, tsla…",
                          label_visibility="collapsed", key="v2_jump").strip().lower()
    if busca:
        linhas = [r for r in linhas if busca in r["ticker"].lower()]
        if not linhas:
            st.caption("No name matches that.")
            return

    sinalizados = [r for r in linhas if r["is_anomaly"]]
    calmos = [r for r in linhas if not r["is_anomaly"]]

    st.markdown(
        f"<div class='ig-hdr'>{len(sinalizados)} past the alert threshold · "
        f"{len(calmos)} quiet</div>", unsafe_allow_html=True)
    for r in sinalizados:
        _row(r)
    if calmos:
        with st.expander(f"Quiet · {len(calmos)} names", expanded=False):
            for r in calmos:
                _row(r, compacto=True)


def _row(r: dict, compacto: bool = False) -> None:
    t = r["ticker"]
    seta, cor = _arrow(r["move"])
    try:
        spark = _sparkline(base._range_prices(t, "1M"), cor)
    except Exception:  # noqa: BLE001
        spark = ""

    chips = [_chip(f"z {r['z']:+.2f}", cor if r["is_anomaly"] else _FLAT_C)]
    vol = base._volume_signal(t)
    if vol and vol.get("unusual"):
        chips.append(_chip(f"{vol['ratio']:.1f}× vol", _WARN))

    d = base._decomposition(t)
    if d and not d.get("error"):
        split = (f"<span class='ig-split'>{d['market'] * 100:+.2f}% mkt · "
                 f"{d['sector'] * 100:+.2f}% sect · "
                 f"<b>{d['company'] * 100:+.2f}% co</b></span>")
    else:
        split = "<span class='ig-split'>split unavailable</span>"

    st.markdown(
        f"<div class='ig-row'><table style='width:100%;border:none'><tr>"
        f"<td style='width:20%'><span class='ig-tkr'>{t}</span> "
        f"<span class='ig-move' style='color:{cor}'>{seta} {r['move'] * 100:+.2f}%</span></td>"
        f"<td style='width:14%'>{spark}</td>"
        f"<td style='width:22%'>{''.join(chips)}</td>"
        f"<td style='text-align:right'>{split}</td>"
        f"</tr></table></div>", unsafe_allow_html=True)

    if not compacto:
        with st.expander(f"Open {t}", expanded=False):
            _dossier(t)


# ── O dossiê ────────────────────────────────────────────────────────────────────
def _dossier(t: str) -> None:
    rng = st.radio("Range", list(base._RANGES), horizontal=True, index=2,
                   label_visibility="collapsed", key=f"v2_range_{t}")
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
        fig.update_layout(height=380, margin={"l": 0, "r": 0, "t": 6, "b": 0},
                          showlegend=False, hovermode="closest",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font={"color": _DIM})
        fig.update_xaxes(showgrid=False, showspikes=True, spikemode="across",
                         spikecolor=_LINE)
        fig.update_yaxes(gridcolor=_LINE, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, key=f"v2_chart_{t}_{rng}")
        st.markdown("<span class='ig-sub'>▲▼ market alerts · ● news alerts. Hover to read "
                    "exactly what the channel sent. Nothing here is recomputed.</span>",
                    unsafe_allow_html=True)
    else:
        st.line_chart(serie)

    a, b = st.columns(2)
    with a:
        st.markdown("<div class='ig-hdr'>Company or market?</div>", unsafe_allow_html=True)
        d = base._decomposition(t)
        if d and not d.get("error"):
            for etiqueta, chave in (("Market", "market"), ("Sector", "sector"),
                                    ("Company", "company")):
                s, c = _arrow(d[chave])
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;max-width:230px'>"
                    f"<span class='ig-sub'>{etiqueta}</span>"
                    f"<span style='color:{c};font-weight:700'>{s} {d[chave] * 100:+.2f}%</span>"
                    f"</div>", unsafe_allow_html=True)
            st.markdown("<span class='ig-sub'>Rolling beta against the index and a sector "
                        "proxy, estimated only on data before the day being explained.</span>",
                        unsafe_allow_html=True)
        else:
            st.caption("Split unavailable (needs index and sector data).")
    with b:
        st.markdown("<div class='ig-hdr'>What the channel sent</div>", unsafe_allow_html=True)
        _events_flat(t)


def _events_flat(t: str) -> None:
    """Alertas do canal, sem expander (o dossiê já é um, e o Streamlit não os aninha)."""
    entradas = [e for e in base._shared_history() if e.ticker == t]
    if not entradas:
        st.caption("No alerts recorded for this company yet.")
        return
    entradas = list(reversed(entradas))[:8]
    rotulos = [f"{e.date} · {(e.text.strip().splitlines() or [e.kind])[0][:60]}"
               for e in entradas]
    i = st.selectbox("Alert", range(len(entradas)), format_func=lambda k: rotulos[k],
                     label_visibility="collapsed", key=f"v2_ev_{t}")
    st.text(entradas[i].text)
    st.markdown("<span class='ig-sub'>Read from the same shared record the Telegram channel "
                "received. Never recomputed here.</span>", unsafe_allow_html=True)


def main() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    _head()
    st.markdown(f"<hr style='border-color:{_LINE};margin:.8rem 0'>", unsafe_allow_html=True)
    _surface()
    st.markdown(f"<hr style='border-color:{_LINE};margin:.8rem 0'>", unsafe_allow_html=True)
    # `_method_view` usa expanders por dentro, e o Streamlit não os aninha. Um interruptor
    # dá a mesma divulgação progressiva sem criar o segundo nível.
    if st.toggle("Method, frozen numbers, and the negative result", value=False,
                 key="v2_method"):
        base._method_view()


main()
