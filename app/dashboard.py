"""Dashboard v2 — uma superfície densa, construída AO LADO da app atual.

*Estatuto.* Isto **não** substitui `app/streamlit_app.py`. A app antiga continua implantada e
intocada; esta corre em paralelo até passar os critérios de
`docs/design/dashboard_acceptance.md`. Se não passar, deita-se fora e não se perde nada. É a
única forma de fazer a sexta tentativa de redesenho sem arriscar a entrega.

*O que muda, e porquê.* O desenho está justificado em `docs/design/dashboard_v2_design.md`, a
partir de uma leitura do worldmonitor.app. Em resumo:

- **uma página**, em vez de três ecrãs com botões de rádio: mudar de ecrã perde o contexto;
- **o gráfico é o herói**, com os sinais **em cima dele** no eixo do tempo, e não numa lista à
  parte;
- **direção por texto** (▲ ▼ ─) em vez de emoji, que renderizam de forma diferente conforme o
  sistema e já produziram um bug visível;
- **divulgação progressiva**: denso à primeira vista, detalhe só quando pedido.

*O que NÃO se copia, de propósito:* score de convergência e badges de tipo de evento. Existem no
worldmonitor e ficam bem, mas a nossa própria medição não os sustenta (critério H4). Copiar a
estética e ignorar a evidência seria fazer exatamente o que a tese critica.

Reutiliza as funções de dados da app atual, para não haver duas versões da verdade.

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

# As funções de dados vêm da app existente: uma só fonte de verdade para preços, história,
# decomposição e volatilidade. Se divergissem, uma delas estaria a mentir.
from app import streamlit_app as base  # noqa: E402

_HAS_PLOTLY = base._HAS_PLOTLY
if _HAS_PLOTLY:
    import plotly.graph_objects as go

# Direção em TEXTO. Os emoji 📈📉 renderizam a cores num sítio e como quadrados noutro, e a seta
# do `delta` do Streamlit chegou a mostrar verde-para-cima num movimento de −7,64%.
_UP, _DOWN, _FLAT = "▲", "▼", "─"
_GREEN, _RED, _GREY = "#0A8F52", "#C0392B", "#8A8A8A"


def _arrow(v: float) -> tuple[str, str]:
    """(símbolo, cor) para um retorno. Nunca depende de fontes nem de parsing."""
    if v > 0.0005:
        return _UP, _GREEN
    if v < -0.0005:
        return _DOWN, _RED
    return _FLAT, _GREY


def _chip(texto: str, cor: str = _GREY) -> str:
    return (f"<span style='background:{cor}1A;color:{cor};padding:1px 7px;"
            f"border-radius:9px;font-size:0.76rem;font-weight:600'>{texto}</span>")


# ── Cabeçalho: a promessa UMA vez (critério H1) ─────────────────────────────────
def _head() -> None:
    esq, dir_ = st.columns([3, 2])
    with esq:
        st.markdown("## InvestiGator")
        st.caption("**Every move investigated, never predicted.** Is this unusual · "
                   "company or market · has it happened before.")
    with dir_:
        base._market_state()
        base._latency_badge()


# ── A watchlist densa: uma linha por nome, tudo o que interessa nela ─────────────
@st.fragment(run_every=60)
def _watchlist_surface() -> None:
    linhas = [r for r in (base._unusualness(t) for t in base._watchlist()) if r]
    if not linhas:
        st.info("Market data is unavailable right now. Nothing is hidden: the price sources "
                "are not responding.")
        return
    linhas.sort(key=lambda r: -abs(r["z"]))

    sinalizados = [r for r in linhas if r["is_anomaly"]]
    calmos = [r for r in linhas if not r["is_anomaly"]]

    st.markdown(f"##### {len(sinalizados)} past the alert threshold · "
                f"{len(calmos)} quiet")
    for r in sinalizados:
        _row(r, destaque=True)
    if calmos:
        with st.expander(f"Quiet today ({len(calmos)})", expanded=False):
            for r in calmos:
                _row(r, destaque=False)


def _row(r: dict, destaque: bool) -> None:
    """Uma linha: nome, movimento, quão fora do normal, volume, e a repartição."""
    t = r["ticker"]
    seta, cor = _arrow(r["move"])
    c1, c2, c3 = st.columns([2.1, 2.4, 2.5])
    with c1:
        st.markdown(
            f"<span style='font-size:1.05rem'><b>{t}</b> "
            f"<span style='color:{cor};font-weight:700'>{seta} {r['move'] * 100:+.2f}%</span>"
            f"</span>", unsafe_allow_html=True)
        st.caption(f"{base.display_name(t) if hasattr(base, 'display_name') else ''}".strip())
    with c2:
        partes = [_chip(f"z {r['z']:+.2f}", cor if destaque else _GREY)]
        vol = base._volume_signal(t)
        if vol and vol.get("unusual"):
            partes.append(_chip(f"{vol['ratio']:.1f}× volume", "#B7791F"))
        st.markdown(" ".join(partes), unsafe_allow_html=True)
    with c3:
        d = base._decomposition(t)
        if d and not d.get("error"):
            st.markdown(
                f"<span style='font-size:0.84rem;color:#555'>"
                f"{d['market'] * 100:+.2f}% mkt · {d['sector'] * 100:+.2f}% sect · "
                f"<b>{d['company'] * 100:+.2f}% company</b></span>",
                unsafe_allow_html=True)
        else:
            st.caption("split unavailable")

    # Divulgação progressiva: o detalhe só aparece a pedido, mas sem mudar de página.
    with st.expander(f"Open {t}", expanded=False):
        _dossier(t)


# ── O dossiê: o gráfico com os sinais EM CIMA, e a evidência por baixo ───────────
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
            line={"width": 2, "color": "#2C6FBB"},
            hovertemplate="$%{y:.2f} · %{x}<extra></extra>", name=t))
        base._mark_alerts_on_chart(fig, t, serie)
        fig.update_layout(height=380, margin={"l": 0, "r": 0, "t": 6, "b": 0},
                          showlegend=False, hovermode="closest",
                          plot_bgcolor="rgba(0,0,0,0)")
        fig.update_xaxes(showgrid=False, showspikes=True, spikemode="across")
        fig.update_yaxes(gridcolor="#EEE")
        st.plotly_chart(fig, use_container_width=True, key=f"v2_chart_{t}_{rng}")
        st.caption("▲▼ market alerts · ● news alerts. Hover to read exactly what the channel "
                   "sent. Nothing here is recomputed.")
    else:
        st.line_chart(serie)

    esq, dir_ = st.columns(2)
    with esq:
        st.markdown("**Is it the company or the market?**")
        d = base._decomposition(t)
        if d and not d.get("error"):
            for etiqueta, chave in (("Market", "market"), ("Sector", "sector"),
                                    ("Company", "company")):
                s, c = _arrow(d[chave])
                st.markdown(f"{etiqueta} &nbsp; <span style='color:{c};font-weight:600'>"
                            f"{s} {d[chave] * 100:+.2f}%</span>", unsafe_allow_html=True)
            st.caption("Rolling beta against the index and a sector proxy, estimated only on "
                       "data before the day being explained.")
        else:
            st.caption("Split unavailable (needs index and sector data).")
    with dir_:
        st.markdown("**What the channel sent**")
        _events_flat(t)


def _events_flat(t: str) -> None:
    """Alertas do canal, SEM expander.

    A versão da app antiga usa um `st.expander` por alerta, e o Streamlit proíbe expanders
    dentro de expanders. Aqui o dossiê já é um expander, por isso a lista tem de ser plana:
    um seletor escolhe o alerta e o texto aparece por baixo, inteiro.
    """
    entradas = [e for e in base._shared_history() if e.ticker == t]
    if not entradas:
        st.caption("No alerts recorded for this company yet.")
        return
    entradas = list(reversed(entradas))[:8]
    rotulos = [
        f"{e.date} · {(e.text.strip().splitlines() or [e.kind])[0][:64]}" for e in entradas
    ]
    escolha = st.selectbox("Alert", range(len(entradas)), format_func=lambda i: rotulos[i],
                           label_visibility="collapsed", key=f"v2_ev_{t}")
    st.text(entradas[escolha].text)
    st.caption("Read from the same shared record the Telegram channel received. "
               "Never recomputed here.")


def main() -> None:
    _head()
    st.divider()
    _watchlist_surface()
    st.divider()
    with st.expander("Method, frozen numbers, and the negative result", expanded=False):
        base._method_view()


main()
