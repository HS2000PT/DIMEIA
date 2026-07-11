"""InvestiGator — live control room (Streamlit).

ONE page: a tab per watchlist ticker, each with the trained risk model, a live price chart
annotated with every detected event, and the history table — all built from the SAME shared
record the Telegram channel already sent (never recalculated independently). "Method &
evaluation" (how it works, the thesis's evaluation numbers, a free-text headline/ticker
sandbox, how to get alerts, citation) collapses into one section at the bottom, out of the
way but one click away.

Run locally:
    pip install -r requirements-app.txt          # streamlit (light stack already covers the rest)
    streamlit run app/streamlit_app.py

Honesty notes (mirrors the thesis):
- No price prediction, no trading signals. Explanations only — evidence from the past.
- The news trigger retrieves precedents SEMANTICALLY: the thesis's MiniLM model in ONNX
  (~23 MB, downloaded once, SHA256-pinned) over a curated multi-year FNSPID knowledge base;
  numerical parity vs SBERT is verified in docs/evaluation/onnx_minilm_validation.md. If the
  model is unavailable it falls back to the word-overlap baseline and says so.
- Every ticker tab also shows a "background risk" score from the materiality-triage model the
  author trained (RQ4) — it scores every day, even with no fresh headline (context features
  only; the thesis numbers for this model are in docs/evaluation/evaluation_triage.md).
- The history shown (chart markers + table) is read from the same file the Telegram channel's
  runner writes to (investigator/alerts_history.py) — not recomputed here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Allow `streamlit run app/streamlit_app.py` from the repo root (put the root on sys.path).
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

st.set_page_config(
    page_title="InvestiGator — Explainable Financial Alerts", page_icon="🐊", layout="wide"
)

_MASCOT = Path(__file__).resolve().parent / "assets" / "investigator.svg"
if _MASCOT.exists():
    st.logo(str(_MASCOT), size="large")

_DEFAULT_HISTORY_URL = (
    "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/alerts_history.jsonl"
)

# Validated evaluation numbers (source: docs/evaluation/, reproducible via scripts/evaluate*.py).
# Shown for display only — not recomputed here.
RETRIEVAL_P5 = pd.DataFrame(
    {
        "Method": [
            "SBERT (MPNet)",
            "SBERT (MiniLM)",
            "Lexical (baseline)",
            "Random (base rate)",
            "Recency",
        ],
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
        "⚠️ Research/educational tool for a Master's dissertation (MEIA, ISEP). "
        "It explains events with historical evidence — it is **not** financial advice and makes "
        "**no** price predictions."
    )


def _read_yaml_config() -> dict:
    import yaml

    return yaml.safe_load((_ROOT / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}


def _watchlist_config() -> tuple[list[str], int, float]:
    """Watchlist + parâmetros do z-score, da mesma fonte que o runner (config/alerts.yaml)."""
    try:
        m = _read_yaml_config().get("market", {})
        return (list(m.get("tickers", [])) or ["AAPL"], int(m.get("window", 20)),
                float(m.get("threshold", 3.0)))
    except Exception:
        return (["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"], 20, 3.0)


def _channel_url() -> str | None:
    """Optional public channel URL from config/alerts.yaml (non-secret; the channel is public)."""
    try:
        url = (_read_yaml_config().get("public", {}) or {}).get("channel_url")
        return str(url) if url else None
    except Exception:
        return None


def _history_url() -> str:
    """URL raw do histórico partilhado (branch `alerts-history`) — configurável, com defeito."""
    try:
        url = (_read_yaml_config().get("public", {}) or {}).get("history_url")
        return str(url) if url else _DEFAULT_HISTORY_URL
    except Exception:
        return _DEFAULT_HISTORY_URL


@st.cache_data(ttl=120, show_spinner=False)
def _live_close(ticker: str) -> pd.Series:
    """Close series with a short TTL so the board refreshes (yfinance, ~15 min delay)."""
    from investigator.market_data.prices import get_price_history

    return get_price_history(ticker)["Close"]


@st.cache_data(ttl=60, show_spinner=False)
def _read_shared_history() -> list:
    """O MESMO histórico que o Telegram recebeu — nunca recalculado, só lido (fail-open)."""
    from investigator.alerts_history import fetch_remote

    return fetch_remote(_history_url())


@st.cache_resource(show_spinner="Loading the semantic model (first time only)…")
def _retrieval_engine() -> tuple:
    """(kb_path, embedder) do produto, uma vez por processo. Semântico (MiniLM em ONNX,
    ~23 MB descarregados na 1.ª vez) com fail-open para a amostra word-overlap.
    INVESTIGATOR_OFFLINE=1 desliga o download (testes/CI ficam determinísticos)."""
    import os

    from investigator.main import product_retrieval

    return product_retrieval(auto_download=os.environ.get("INVESTIGATOR_OFFLINE") != "1")


@st.cache_resource(show_spinner=False)
def _triage_bundle():
    """O modelo de triagem TREINADO PELO AUTOR (RQ4) — None se `models/` não estiver presente
    (ausência graciosa: o resto da app funciona na mesma, só sem o medidor de risco)."""
    from investigator.triage.infer import load_context_bundle

    return load_context_bundle()


@st.cache_data(show_spinner=False)
def _kb_size(kb_path: str) -> int:
    """Cached record count of the knowledge base (one JSONL line per record)."""
    with open(kb_path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


# ── Painel por ticker ───────────────────────────────────────────────────────────

def _risk_gauge(ticker: str, close: pd.Series) -> None:
    """Risco de fundo do TEU modelo treinado — todos os dias, sem precisar de notícia."""
    bundle = _triage_bundle()
    if bundle is None:
        return
    from investigator.triage.infer import score_background

    try:
        scored = score_background(bundle, close, ticker)
    except Exception:
        return
    if scored is None:
        return
    prob, contribs = scored
    factors = ", ".join(name for name, _ in contribs[:2])
    c1, c2 = st.columns([1, 3])
    c1.metric(
        "Background risk", f"{prob:.0%}",
        help="P(an abnormal move follows), estimated by your trained triage model (RQ4) from "
             "price/volatility/sector context alone — no specific headline needed.",
    )
    c2.caption(f"Mainly driven by: {factors}. Triage evidence, not a forecast — the same model "
               "that gates the news alerts.")


def _ticker_chart(ticker: str, close: pd.Series, history: list) -> go.Figure:
    """Preço de fecho + um marcador por evento detetado (hover = o texto exato do alerta)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=close.index, y=close.to_numpy(), mode="lines", name="Close",
        line={"width": 1.6, "color": "#4c78a8"},
    ))
    close_by_date = {idx.date().isoformat(): float(v) for idx, v in close.items()}
    xs, ys, texts, colors, symbols = [], [], [], [], []
    for h in history:
        if h.ticker != ticker:
            continue
        y = close_by_date.get(h.date)
        if y is None:
            continue  # fora da janela do gráfico — continua a aparecer na tabela abaixo
        xs.append(h.date)
        ys.append(y)
        texts.append(h.text if len(h.text) <= 220 else h.text[:219] + "…")
        colors.append("#d62728" if h.kind == "market" else "#2ca02c")
        symbols.append("triangle-up" if h.kind == "market" else "circle")
    if xs:
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers", name="Alerts",
            marker={"size": 13, "color": colors, "symbol": symbols,
                    "line": {"width": 1, "color": "white"}},
            text=texts, hoverinfo="text",
        ))
    fig.update_layout(
        height=380, margin={"l": 10, "r": 10, "t": 20, "b": 10},
        showlegend=False, hovermode="closest",
        yaxis_title="Close ($)",
    )
    return fig


def _ticker_tab(ticker: str, history: list) -> None:
    try:
        close = _live_close(ticker)
    except Exception as exc:  # noqa: BLE001  (network/ticker errors shouldn't crash the tab)
        st.warning(f"No data right now for {ticker}: {type(exc).__name__}")
        return
    if len(close) < 2:
        st.warning(f"Not enough price history for {ticker} yet.")
        return

    ticker_hist = [h for h in history if h.ticker == ticker]
    move = float(close.iloc[-1] / close.iloc[-2] - 1.0)
    c1, c2 = st.columns(2)
    c1.metric(f"{ticker} last close", f"${close.iloc[-1]:.2f}", f"{move:+.2%}")
    c2.metric("Alerts on record", len(ticker_hist))

    _risk_gauge(ticker, close)
    st.plotly_chart(_ticker_chart(ticker, close, history), use_container_width=True,
                    config={"displayModeBar": False}, key=f"chart_{ticker}")

    st.subheader("History — same alerts sent to the Telegram channel")
    if ticker_hist:
        rows = [
            {"Date": h.date, "Type": "🔺 Market" if h.kind == "market" else "📰 News",
             "Alert": h.text}
            for h in reversed(ticker_hist)
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                    column_config={"Alert": st.column_config.TextColumn(width="large")})
    else:
        st.caption(f"No alerts recorded yet for {ticker} — this fills in as the scheduled "
                   "scan (every 30 min in US market hours) sends real alerts.")


# ── Método & avaliação (tudo o que não é o painel ao vivo, num só sítio) ────────

def _section_how() -> None:
    st.markdown(
        """
InvestiGator integrates existing, transparent components: a pre-trained sentence embedder (SBERT,
inference only), a statistical *z*-score, cosine similarity, and event-study arithmetic. On top of
those sits **one model trained by the author** — the materiality-triage logistic regression (RQ4):
it estimates the probability that an *abnormal move* follows a news item (**never** direction or
price), with labels produced by the system's own event-study code. It is the "Background risk"
gauge shown on every ticker tab above. No computer vision, no deep training, no forecasting.
        """
    )
    st.graphviz_chart(
        """
        digraph {
            rankdir=LR; node [shape=box, style=rounded, fontsize=11];
            headline [label="New headline"];
            emb [label="Embedder\\n(headline -> vector)"];
            kb [label="Knowledge base\\n(past cases: news + impact)"];
            sim [label="Cosine similarity\\n(top-k precedents)"];
            impact [label="Event study\\n(+1/+3/+5d impact)"];
            alert [label="XAI alert\\n(precedents + evidence)"];
            headline -> emb -> sim; kb -> sim -> impact -> alert;

            prices [label="Live prices"];
            ret [label="Log-returns"];
            z [label="Rolling z-score\\n(no lookahead)"];
            aalert [label="Anomaly alert\\n(plain-language)"];
            prices -> ret -> z -> aalert;
        }
        """
    )
    st.markdown(
        "**Data model:** a *case* (`NewsRecord`) = one past headline + what happened to its price. "
        "A new `NewsItem` shares the same schema, so it is directly comparable. `AnomalyResult` "
        "carries the z-score and the window that produced it, so every alert is traceable."
    )


def _section_evaluation() -> None:
    st.markdown(
        "All figures below come from `docs/evaluation/` and are reproducible with fixed seeds via "
        "`scripts/evaluate.py` / `scripts/evaluate_anomaly.py`."
    )
    st.subheader("1 · News retrieval beats every baseline (precision@5)")
    st.bar_chart(RETRIEVAL_P5, use_container_width=True)
    st.caption(
        "SBERT (MiniLM) P@5 = 0.514 vs 0.240 random base rate (lift +0.273). Lexical = 0.346."
    )
    st.subheader("2 · Retrieval quality per sector (SBERT vs random)")
    st.bar_chart(PER_SECTOR, use_container_width=True)
    st.subheader("3 · The z-score fires at a near-constant rate across stocks")
    st.dataframe(FIRING_RATE, use_container_width=True)
    st.caption(
        "The z-score's firing-rate spread across tickers is 0.015 vs 0.344 for a fixed % "
        "threshold — it normalises volatility. (F1 vs a proxy label: z-score 0.516 vs 0.218.)"
    )


def _section_try_headline() -> None:
    from investigator.explanation_engine.explainer import plain_text
    from investigator.main import run_news_trigger

    st.caption("Paste any headline — see the most similar past headlines and what the price "
               "did after. Uses the same retrieval engine as the live board.")
    kb_path, embedder = _retrieval_engine()
    semantic = bool(getattr(embedder, "semantic", False))
    col = st.columns([3, 1])
    headline = col[0].text_input("Headline", value="Nvidia demand surges on AI chip orders",
                                 key="try_headline_text")
    ticker = col[1].text_input("Ticker", value="NVDA", key="try_headline_ticker")
    engine = (
        "semantic matching — MiniLM (the thesis's SBERT model) running in ONNX"
        if semantic
        else "word-overlap matching (offline fallback) — weaker than the thesis's SBERT"
    )
    st.caption(f"Knowledge base: {_kb_size(str(kb_path)):,} historical headlines; {engine}.")

    if st.button("Find precedents", type="primary", key="try_headline_button"):
        precedents, text = run_news_trigger(
            ticker=ticker.strip().upper(), headline=headline.strip(),
            kb_path=kb_path, embedder=embedder, top_k=3, horizon=5, send=False,
        )
        if not precedents:
            st.warning("No precedents found in the knowledge base.")
            return
        # Mesmo chão de similaridade que o canal usa (config news.min_similarity):
        # aqui na sandbox mostramos na mesma, mas dizemos que o canal NÃO alertaria.
        min_sim = 0.45
        try:
            min_sim = float((_read_yaml_config().get("news", {}) or {})
                            .get("min_similarity", 0.45))
        except Exception:
            pass
        best = max(float(s) for _, s in precedents)
        if best < min_sim:
            st.info(f"Weak precedents (best similarity {best:.2f} < {min_sim:.2f} floor) — "
                    "the live channel would **not** alert on this headline. "
                    "Shown here for exploration only.")
        rows = [
            {"Date": rec.date, "Ticker": rec.ticker, "Similarity": round(float(score), 3),
             "+1d": rec.impacts.get("1"), "+3d": rec.impacts.get("3"),
             "+5d": rec.impacts.get("5"), "Headline": rec.headline}
            for rec, score in precedents
        ]
        df = pd.DataFrame(rows)
        for c in ["+1d", "+3d", "+5d"]:
            df[c] = df[c].map(lambda v: f"{v:+.2%}" if v is not None else "—")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.text(plain_text(text))
        _render_news_risk(ticker.strip().upper(), headline.strip())


def _render_news_risk(ticker: str, headline: str) -> None:
    """Risco de triagem PARA ESTA notícia concreta (distinto do "background risk" do painel)."""
    bundle = _triage_bundle()
    if bundle is None:
        return
    from investigator.triage.infer import score_latest

    try:
        scored = score_latest(bundle, _live_close(ticker), headline, ticker)
    except Exception:
        st.caption("Risk estimate unavailable (price history could not be fetched).")
        return
    if scored is None:
        st.caption("Risk estimate unavailable (not enough price history for this ticker).")
        return
    prob, contribs = scored
    st.subheader("Risk estimate for this headline (learned triage)")
    c1, c2 = st.columns([1, 2])
    c1.metric("P(abnormal move follows)", f"{prob:.0%}")
    c2.dataframe(
        pd.DataFrame([{"Factor": name, "Pushes": "up" if c >= 0 else "down",
                       "Logit contribution": round(c, 2)} for name, c in contribs]),
        use_container_width=True, hide_index=True,
    )
    st.caption(
        "Context-only logistic regression trained by the author (RQ4) — the exact additive "
        "contributions above are the model's whole reasoning. Triage evidence, **not a "
        "forecast**; methodology and honest results in `docs/evaluation/evaluation_triage.md`."
    )


def _section_check_ticker() -> None:
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.explanation_engine.explainer import (
        explain_anomaly,
        explain_normal,
        plain_text,
    )
    from investigator.market_data.prices import log_returns

    st.caption("Check any ticker, not just the watchlist above — is its latest move unusual "
               "**for that stock** (compared with its own recent behaviour)?")
    ticker = st.text_input("Ticker", value="AAPL", key="check_ticker_input").strip().upper()
    c1, c2 = st.columns(2)
    window = c1.slider("Window (days)", 10, 60, 20, key="check_ticker_window")
    threshold = c2.slider("Threshold |z|", 2.0, 4.0, 3.0, step=0.5, key="check_ticker_thr")

    if st.button("Check latest move", type="primary", key="check_ticker_button"):
        try:
            close = _live_close(ticker)
            returns = log_returns(close)
            res = detect_latest(returns, window=window, threshold=threshold)
        except Exception as exc:  # noqa: BLE001  (network/ticker errors shouldn't crash the UI)
            st.error(f"Could not fetch/evaluate '{ticker}': {type(exc).__name__}: {exc}")
            return
        m1, m2, m3 = st.columns(3)
        m1.metric("z-score", f"{res.z_score:+.2f}")
        m2.metric("Anomaly?", "YES" if res.is_anomaly else "no")
        m3.metric("Latest return", f"{res.last_return:+.2%}")
        text = explain_anomaly(ticker, res) if res.is_anomaly else explain_normal(ticker, res)
        st.text(plain_text(text))
        band = pd.DataFrame({"return": returns.tail(60).reset_index(drop=True)})
        band["mean"] = res.mean
        band["+band"] = res.mean + threshold * res.std
        band["-band"] = res.mean - threshold * res.std
        st.line_chart(band, use_container_width=True)
        st.caption("Last ~60 daily log-returns with the anomaly band (mean ± threshold·σ).")


def _section_get_alerts() -> None:
    url = _channel_url()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1 · Join the channel")
        if url:
            st.link_button("📡 Open the Telegram channel", url, type="primary")
        else:
            st.markdown("Open Telegram and search for the **InvestiGator Alerts** channel.")
        st.caption("Scans every 30 min during US market hours — no spam by design "
                   "(one alert per unusual move or material headline per day per ticker).")
    with c2:
        st.subheader("2 · Optional: your own watchlist")
        st.markdown(
            """
Send the bot a direct message:

| Command | What it does |
|---|---|
| `/watch TSLA` | add a ticker to *your* list |
| `/list` | see your list |
| `/unwatch TSLA` | remove it |
| `/stop` | pause (list is kept) |
            """
        )
        st.caption("Replies arrive with the next scan (≤30 min in market hours).")


def _section_about() -> None:
    st.markdown(
        """
**InvestiGator** accompanies the MEIA (ISEP) master's dissertation
*"Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and
News–Market Impact Correlation."*

- **Author:** Henrique José da Silva Santos — ISEP
- **Supervisor:** Prof. Luís Gomes · **Co-supervisor:** Rafael Silva
- **Repository:** https://github.com/HS2000PT/DIMEIA (see `CITATION.cff` for how to cite)

Attributions: FNSPID (CC BY-SA 4.0), yfinance, Telegram Bot API, ISEP MEIA LaTeX template.
        """
    )
    _disclaimer()


def _method_and_evaluation() -> None:
    label = "📖 Method, evaluation & more (how it works, cite it, get it on your phone)"
    with st.expander(label):
        tabs = st.tabs(["How it works", "Evaluation", "Try a headline", "Check any ticker",
                       "Get alerts", "About"])
        with tabs[0]:
            _section_how()
        with tabs[1]:
            _section_evaluation()
        with tabs[2]:
            _section_try_headline()
        with tabs[3]:
            _section_check_ticker()
        with tabs[4]:
            _section_get_alerts()
        with tabs[5]:
            _section_about()


def main() -> None:
    st.sidebar.title("InvestiGator")
    st.sidebar.caption("_Investigate. Don't speculate._ 🐊🔍")
    st.sidebar.markdown("---")
    with st.sidebar:
        _disclaimer()

    st.title("Markets now")
    st.caption("Same watchlist, same detector, same alerts as the Telegram channel — "
               "pick a ticker below.")

    tickers, _window, _threshold = _watchlist_config()
    history = _read_shared_history()
    if not history:
        st.caption("⚠ No shared alert history available right now (network, or none sent yet) "
                   "— the charts below still show live prices; alerts will appear once the "
                   "scheduled scan records them.")

    # O resumo diário de fecho (o mesmo enviado ao canal) — visão de mercado num relance.
    summaries = [h for h in history if h.kind == "summary"]
    if summaries:
        with st.expander(f"📊 Daily close summary ({summaries[-1].date}) — as sent to the "
                        "Telegram channel"):
            st.text(summaries[-1].text)

    tabs = st.tabs(tickers)
    for tab, ticker in zip(tabs, tickers, strict=True):
        with tab:
            _ticker_tab(ticker, history)

    _method_and_evaluation()


if __name__ == "__main__":
    main()
