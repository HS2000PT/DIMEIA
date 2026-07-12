"""InvestiGator — live market dashboard (Streamlit).

Design (2026-07-12, visão do aluno): DUAS vistas, e só duas.
- 📊 Live: uma aba por empresa; em cada aba UM gráfico grande (estilo Google Finance) com
  intervalos 1D/5D/1M/6M, os EVENTOS detetados (anomalias + notícias, exatamente os que o
  canal Telegram recebeu) marcados no gráfico com hover, e a mesma lista numa tabela por
  baixo. Read-only: visualização, sem ações.
- ℹ️ About: o que é, como funciona, avaliação, como receber alertas, citação — tudo o que
  não é o painel vivo mora aqui.

Honesty notes (mirrors the thesis):
- No price prediction, no trading signals. Explanations only — evidence from the past.
- The history shown (chart markers + table) is read from the same shared record the Telegram
  channel's runner writes (branch alerts-history) — never recomputed here.
- Prices are yfinance (free): intraday bars have ~15 min delay; the caption says so.
- Retrieval (About → try a headline) is semantic: the thesis's MiniLM in ONNX, with the
  word-overlap fallback and the live KB + age decay of the production runner.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Plotly é um "nice-to-have" (gráfico interativo com marcadores): a app NUNCA pode cair por
# causa dele (INVESTIGATOR_NO_PLOTLY=1 força o fallback nos testes).
_HAS_PLOTLY = os.environ.get("INVESTIGATOR_NO_PLOTLY") != "1"
if _HAS_PLOTLY:
    try:
        import plotly.graph_objects as go
    except ModuleNotFoundError:
        _HAS_PLOTLY = False
if not _HAS_PLOTLY:
    go = None

# Allow `streamlit run app/streamlit_app.py` from the repo root (put the root on sys.path).
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

st.set_page_config(
    page_title="InvestiGator — Market intelligence, explained", page_icon="📈", layout="wide"
)

_LOGO = Path(__file__).resolve().parent / "assets" / "logo.svg"
if _LOGO.exists():
    st.logo(str(_LOGO), size="large")

_DEFAULT_HISTORY_URL = (
    "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/alerts_history.jsonl"
)

# Intervalos do gráfico grande (estilo Google Finance): (period, interval) do yfinance.
_RANGES: dict[str, tuple[str, str]] = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "30m"),
    "1M": ("1mo", "1d"),
    "6M": ("6mo", "1d"),
}

# Validated evaluation numbers (source: docs/evaluation/, reproducible via scripts/evaluate*.py).
RETRIEVAL_P5 = pd.DataFrame(
    {
        "Method": ["SBERT (MPNet)", "SBERT (MiniLM)", "Lexical (baseline)",
                   "Random (base rate)", "Recency"],
        "P@5": [0.538, 0.514, 0.346, 0.240, 0.126],
    }
).set_index("Method")

FIRING_RATE = pd.DataFrame(
    {
        "Method": ["z-score", "Fixed threshold (%)"],
        "Min rate": [0.016, 0.009],
        "Max rate": [0.031, 0.353],
        "Spread (max-min)": [0.015, 0.344],
    }
).set_index("Method")

PER_SECTOR = pd.DataFrame(
    {
        "Sector": ["Technology", "Energy", "Health", "Banking", "Consumer"],
        "P@5 (SBERT)": [0.712, 0.448, 0.419, 0.272, 0.171],
        "Random (base)": [0.429, 0.072, 0.071, 0.072, 0.071],
    }
).set_index("Sector")


def _disclaimer() -> None:
    st.caption(
        "⚠️ Research/educational tool (MSc dissertation, MEIA/ISEP). It explains market events "
        "with historical evidence — **not** financial advice, **no** price predictions."
    )


# ── Config / dados partilhados ──────────────────────────────────────────────────

def _read_yaml_config() -> dict:
    import yaml

    return yaml.safe_load((_ROOT / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}


def _watchlist() -> list[str]:
    try:
        m = _read_yaml_config().get("market", {})
        return list(m.get("tickers", [])) or ["AAPL"]
    except Exception:
        return ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]


def _channel_url() -> str | None:
    try:
        url = (_read_yaml_config().get("public", {}) or {}).get("channel_url")
        return str(url) if url else None
    except Exception:
        return None


def _history_url() -> str:
    try:
        url = (_read_yaml_config().get("public", {}) or {}).get("history_url")
        return str(url) if url else _DEFAULT_HISTORY_URL
    except Exception:
        return _DEFAULT_HISTORY_URL


@st.cache_data(ttl=60, show_spinner=False)
def _read_shared_history() -> list:
    """O MESMO histórico que o Telegram recebeu — nunca recalculado, só lido (fail-open)."""
    from investigator.alerts_history import fetch_remote

    return fetch_remote(_history_url())


@st.cache_data(ttl=60, show_spinner=False)
def _range_prices(ticker: str, range_key: str) -> pd.Series:
    """Fechos para o intervalo escolhido (yfinance; intraday ~15 min de atraso)."""
    from investigator.market_data.prices import get_price_history

    period, interval = _RANGES[range_key]
    return get_price_history(ticker, period=period, interval=interval)["Close"]


@st.cache_data(ttl=120, show_spinner=False)
def _daily_close(ticker: str) -> pd.Series:
    """Fechos diários (6 meses) — para o risco de fundo e fallback."""
    from investigator.market_data.prices import get_price_history

    return get_price_history(ticker)["Close"]


@st.cache_resource(show_spinner="Loading the semantic model (first time only)…")
def _retrieval_engine() -> tuple:
    from investigator.main import product_retrieval

    return product_retrieval(auto_download=os.environ.get("INVESTIGATOR_OFFLINE") != "1")


@st.cache_resource(show_spinner=False)
def _triage_bundle():
    from investigator.triage.infer import load_context_bundle

    return load_context_bundle()


@st.cache_data(show_spinner=False)
def _kb_size(kb_path: str) -> int:
    with open(kb_path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def _live_kb_url() -> str:
    return _history_url().rsplit("/", 1)[0] + "/live_kb.jsonl"


@st.cache_data(ttl=300, show_spinner=False)
def _retrieval_kbs(kb_path: str) -> list:
    """[KB viva (remota, se existir), KB histórica local] — a fusão prefere o recente."""
    from investigator.historical_kb.knowledge_base import HistoricalKB
    from investigator.live_kb import fetch_remote_records

    kbs = []
    if os.environ.get("INVESTIGATOR_OFFLINE") != "1":
        vivos = fetch_remote_records(_live_kb_url())
        if vivos:
            kbs.append(HistoricalKB(vivos))
    kbs.append(HistoricalKB.load(kb_path))
    return kbs


# ── Vista LIVE: o gráfico grande + eventos ──────────────────────────────────────

def _risk_line(ticker: str) -> None:
    """Risco de fundo do modelo treinado (RQ4) — uma linha compacta, read-only."""
    bundle = _triage_bundle()
    if bundle is None:
        return
    from investigator.triage.infer import score_background

    try:
        scored = score_background(bundle, _daily_close(ticker), ticker)
    except Exception:
        return
    if scored is None:
        return
    prob, contribs = scored
    factors = " and ".join(name for name, _ in contribs[:2])
    st.caption(f"**Background risk {prob:.0%}** — P(bigger-than-usual move ahead), from the "
               f"author-trained triage model; mainly {factors}. Evidence, not a forecast.")


def _event_positions(events: list, closes: pd.Series, intraday: bool):
    """Mapeia eventos (com data) a posições (x, y) no gráfico do intervalo atual."""
    xs, ys, texts, colors, symbols = [], [], [], [], []
    if intraday:
        primeiro_do_dia: dict[str, object] = {}
        for idx in closes.index:
            chave = idx.date().isoformat()
            primeiro_do_dia.setdefault(chave, idx)
        posicao = {d: (idx, float(closes.loc[idx])) for d, idx in primeiro_do_dia.items()}
    else:
        posicao = {idx.date().isoformat(): (idx, float(v)) for idx, v in closes.items()}
    for h in events:
        par = posicao.get(h.date)
        if par is None:
            continue
        x, y = par
        xs.append(x)
        ys.append(y)
        texts.append(h.text if len(h.text) <= 220 else h.text[:219] + "…")
        colors.append("#EF4444" if h.kind == "market" else "#10B981")
        symbols.append("triangle-up" if h.kind == "market" else "circle")
    return xs, ys, texts, colors, symbols


def _big_chart(ticker: str, closes: pd.Series, events: list, intraday: bool):
    """O gráfico grande: linha de preço + marcadores de eventos com hover (o pedido)."""
    subiu = float(closes.iloc[-1]) >= float(closes.iloc[0])
    cor = "#10B981" if subiu else "#EF4444"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=closes.index, y=closes.to_numpy(), mode="lines", name="Price",
        line={"width": 2.2, "color": cor},
        fill="tozeroy", fillcolor=("rgba(16,185,129,0.08)" if subiu
                                   else "rgba(239,68,68,0.08)"),
    ))
    xs, ys, texts, colors, symbols = _event_positions(events, closes, intraday)
    if xs:
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers", name="Events",
            marker={"size": 14, "color": colors, "symbol": symbols,
                    "line": {"width": 1.5, "color": "white"}},
            text=texts, hoverinfo="text",
        ))
    ymin, ymax = float(closes.min()), float(closes.max())
    folga = (ymax - ymin) * 0.08 or ymax * 0.01
    fig.update_layout(
        height=520, margin={"l": 10, "r": 10, "t": 16, "b": 10}, showlegend=False,
        hovermode="closest", yaxis={"range": [ymin - folga, ymax + folga],
                                    "title": "Price ($)"},
        xaxis={"rangeslider": {"visible": False}},
    )
    return fig


def _ticker_tab(ticker: str, history: list) -> None:
    eventos = [h for h in history if h.ticker == ticker]
    intervalo = st.radio("Range", list(_RANGES), index=3, horizontal=True,
                         key=f"range_{ticker}", label_visibility="collapsed")
    try:
        closes = _range_prices(ticker, intervalo)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"No price data right now for {ticker}: {type(exc).__name__}")
        return
    if len(closes) < 2:
        st.warning(f"Not enough data for {ticker} in this range yet.")
        return

    var = float(closes.iloc[-1] / closes.iloc[0] - 1.0)
    c1, c2 = st.columns([1, 3])
    c1.metric(ticker, f"${float(closes.iloc[-1]):.2f}", f"{var:+.2%} ({intervalo})")
    with c2:
        _risk_line(ticker)

    intraday = intervalo in ("1D", "5D")
    if _HAS_PLOTLY:
        st.plotly_chart(_big_chart(ticker, closes, eventos, intraday),
                        use_container_width=True, config={"displayModeBar": False},
                        key=f"chart_{ticker}_{intervalo}")
    else:
        st.line_chart(closes, use_container_width=True)
        st.caption("Interactive chart unavailable in this environment (plotly not installed) "
                   "— all detected events remain in the table below.")
    st.caption("yfinance prices (intraday bars ~15 min delayed) · auto-refreshes · "
               "🔻/🔺 market anomaly · ● news event — hover a marker for the full alert.")

    st.subheader("Events — exactly as sent to the Telegram channel")
    if eventos:
        rows = [
            {"Date": h.date, "Type": "🔺 Market" if h.kind == "market" else "📰 News",
             "Alert": h.text}
            for h in reversed(eventos)
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                    column_config={"Alert": st.column_config.TextColumn(width="large")})
    else:
        st.caption(f"No events recorded yet for {ticker} — this fills in as the automated "
                   "scan detects anomalies and material news.")


@st.fragment(run_every="120s")
def _live_view() -> None:
    history = _read_shared_history()
    if not history:
        st.caption("⚠ No shared event history reachable right now — charts still show live "
                   "prices; events appear as the automated scan records them.")
    summaries = [h for h in history if h.kind == "summary"]
    if summaries:
        with st.expander(f"📊 Daily close summary ({summaries[-1].date}) — as sent to the "
                        "Telegram channel"):
            st.text(summaries[-1].text)
    tickers = _watchlist()
    tabs = st.tabs(tickers)
    for tab, ticker in zip(tabs, tickers, strict=True):
        with tab:
            _ticker_tab(ticker, history)


# ── Vista ABOUT: tudo o resto, fora do caminho ──────────────────────────────────

def _about_view() -> None:
    st.title("About InvestiGator")
    st.markdown(
        """
**InvestiGator** watches the US market and **explains** every alert it sends. Two independent
sensors feed one intelligence engine:

1. **Abrupt market moves** — a transparent statistical anomaly detector (rolling *z*-score,
   no lookahead), evaluated intraday from real-time quotes in watch mode. When it fires, the
   system *investigates*: it attaches the freshest relevant headline as a possible explanation
   — or honestly reports that none was found.
2. **Material news** — each relevant headline is compared semantically against a knowledge
   base of past cases (including a **living KB** that grows from the news the system itself
   scans, with impacts measured against real prices days later). Precedents are ranked with
   age decay and always show their age. **Evidence, never a prediction.**

On top sits the one model **trained by the author** (RQ4): a calibrated materiality-triage
classifier that scores every ticker daily and gates news alerts against noise.
        """
    )

    st.header("How it works")
    st.graphviz_chart(
        """
        digraph {
            rankdir=LR; node [shape=box, style=rounded, fontsize=11];
            headline [label="New headline"];
            emb [label="Embedder\\n(headline -> vector)"];
            kb [label="Knowledge bases\\n(historical + living)"];
            sim [label="Cosine similarity\\n+ age decay"];
            impact [label="Event study\\n(+1/+3/+5d impact)"];
            alert [label="Explained alert"];
            headline -> emb -> sim; kb -> sim -> impact -> alert;

            prices [label="Live prices / quotes"];
            ret [label="Returns"];
            z [label="Rolling z-score\\n(no lookahead)"];
            inv [label="Cross-investigation\\n(find explaining news)"];
            prices -> ret -> z -> inv -> alert;
        }
        """
    )

    st.header("Evaluation (frozen thesis numbers)")
    st.markdown("Reproducible with fixed seeds via `scripts/evaluate*.py`; "
                "full tables in `docs/evaluation/`.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Retrieval beats every baseline")
        st.bar_chart(RETRIEVAL_P5, use_container_width=True)
        st.caption("SBERT (MiniLM) P@5 = 0.514 vs 0.240 random (lift +0.273); lexical 0.346.")
    with col2:
        st.subheader("z-score fires consistently")
        st.dataframe(FIRING_RATE, use_container_width=True)
        st.caption("Firing-rate spread 0.015 vs 0.344 for a fixed % threshold.")
        st.subheader("Per sector (SBERT vs random)")
        st.bar_chart(PER_SECTOR, use_container_width=True)

    st.header("Get the alerts")
    url = _channel_url()
    c1, c2 = st.columns(2)
    with c1:
        if url:
            st.link_button("📡 Open the Telegram channel", url, type="primary")
        st.caption("Automatic alerts: anomalies (with investigation), material news (quality-"
                   "filtered), and a daily close summary. No spam by design.")
    with c2:
        st.markdown("**Personal watchlist (bot):** `/watch TSLA` · `/list` · `/unwatch` · "
                    "`/stop` — replies with the next scan.")

    with st.expander("🔬 Try the retrieval engine on any headline (demo)"):
        _try_headline()

    st.header("Cite / credits")
    st.markdown(
        """
Master's dissertation (MEIA, ISEP): *"Explainable Financial Alerts for Retail Investors:
Integrating Statistical Anomaly Detection and News–Market Impact Correlation."*
**Author:** Henrique José da Silva Santos · **Supervisor:** Prof. Luís Gomes ·
**Co-supervisor:** Rafael Silva · Repository: <https://github.com/HS2000PT/DIMEIA>
(see `CITATION.cff`). Attributions: FNSPID (CC BY-SA 4.0), yfinance, Finnhub, Telegram Bot API.
        """
    )
    _disclaimer()


def _try_headline() -> None:
    """Sandbox mínima (única ação da app, deliberadamente fora da vista Live): útil para a
    demo da defesa — o júri pode testar o motor de precedentes com qualquer manchete."""
    from investigator.explanation_engine.explainer import plain_text

    kb_path, embedder = _retrieval_engine()
    semantic = bool(getattr(embedder, "semantic", False))
    col = st.columns([3, 1])
    headline = col[0].text_input("Headline", value="Nvidia demand surges on AI chip orders",
                                 key="try_headline_text")
    ticker = col[1].text_input("Ticker", value="NVDA", key="try_headline_ticker")
    engine = ("semantic (MiniLM in ONNX — the thesis's model)" if semantic
              else "word-overlap fallback")
    st.caption(f"Knowledge base: {_kb_size(str(kb_path)):,} cases + live KB; engine: {engine}.")
    if st.button("Find precedents", type="primary", key="try_headline_button"):
        from datetime import date as _date

        from investigator.explanation_engine.explainer import explain_news_impact
        from investigator.live_kb import merged_precedents

        news_cfg = _read_yaml_config().get("news", {}) or {}
        max_age_cfg = news_cfg.get("max_precedent_age_days")
        precedents = merged_precedents(
            headline.strip(), _retrieval_kbs(str(kb_path)), embedder, top_k=3,
            today=_date.today(),
            half_life_days=float(news_cfg.get("recency_half_life_days", 365)),
            max_age_days=int(max_age_cfg) if max_age_cfg is not None else None,
        )
        if not precedents:
            st.warning("No precedents found in the knowledge base.")
            return
        min_sim = float(news_cfg.get("min_similarity", 0.45))
        best = max(float(s) for _, s in precedents)
        if best < min_sim:
            st.info(f"Weak precedents (best similarity {best:.2f} < {min_sim:.2f} floor) — "
                    "the live channel would **not** alert on this. Shown for exploration only.")
        text = explain_news_impact(ticker.strip().upper(), headline.strip(), precedents,
                                   horizon=5, today=_date.today().isoformat())
        st.text(plain_text(text))


# ── Entrada ─────────────────────────────────────────────────────────────────────

def main() -> None:
    st.sidebar.title("InvestiGator")
    st.sidebar.caption("_Market intelligence, explained._")
    vista = st.sidebar.radio("View", ["📊 Live", "ℹ️ About"], label_visibility="collapsed")
    st.sidebar.markdown("---")
    with st.sidebar:
        _disclaimer()

    if vista == "📊 Live":
        _live_view()
    else:
        _about_view()


if __name__ == "__main__":
    main()
