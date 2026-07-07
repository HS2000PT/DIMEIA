"""InvestiGator — interactive dashboard (Streamlit).

A thin, stateless UI over the *validated* InvestiGator functions. It demonstrates the two triggers
(news precedents; market anomaly) and shows the evaluation, so an examiner can click through the
XAI story without installing anything.

Run locally:
    pip install -r requirements-app.txt          # streamlit (light stack already covers the rest)
    streamlit run app/streamlit_app.py

Honesty notes (mirrors the thesis):
- No price prediction, no trading signals. Explanations only — evidence from the past.
- The interactive news trigger uses the offline baseline embedder (HashingEmbedder) over a
  curated multi-year FNSPID knowledge base (falls back to the small sample), so it runs anywhere
  with no downloads. The thesis's real method is SBERT; its measured advantage is on the
  Evaluation page.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
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


# ── Pages ──────────────────────────────────────────────────────────────────────

def _watchlist_config() -> tuple[list[str], int, float]:
    """Watchlist + parâmetros do z-score, da mesma fonte que o runner (config/alerts.yaml)."""
    try:
        import yaml

        cfg = yaml.safe_load((_ROOT / "config" / "alerts.yaml").read_text(encoding="utf-8"))
        m = cfg.get("market", {})
        return (list(m.get("tickers", [])) or ["AAPL"], int(m.get("window", 20)),
                float(m.get("threshold", 3.0)))
    except Exception:
        return (["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"], 20, 3.0)


@st.cache_data(ttl=120, show_spinner=False)
def _live_close(ticker: str) -> pd.Series:
    """Close series with a short TTL so the live board refreshes (yfinance, ~15 min delay)."""
    from investigator.market_data.prices import get_price_history

    return get_price_history(ticker)["Close"]


@st.fragment(run_every="120s")
def _live_board() -> None:
    from datetime import UTC, date, datetime

    from investigator.anomaly_detector.detector import detect_latest
    from investigator.market_data.prices import log_returns

    tickers, window, threshold = _watchlist_config()
    rows, n_anom, n_fresh = [], 0, 0
    for ticker in tickers:
        try:
            close = _live_close(ticker)
            if len(close) < window + 2:
                raise ValueError("not enough history")
            res = detect_latest(log_returns(close), window=window, threshold=threshold)
            last_idx = close.index[-1]
            bar_date = last_idx.date() if isinstance(last_idx, pd.Timestamp) else None
            fresh = bar_date == date.today() if bar_date else False
            n_fresh += int(fresh)
            if res.is_anomaly and fresh:
                n_anom += 1
                status = f"🔺 ANOMALY (|z| ≥ {threshold:g})"
            elif not fresh:
                status = f"closed · last session {bar_date}" if bar_date else "closed"
            else:
                status = "normal"
            rows.append({
                "Ticker": ticker,
                "Price": round(float(close.iloc[-1]), 2),
                "Move": float(close.iloc[-1] / close.iloc[-2] - 1.0),
                "z-score": round(float(res.z_score), 2),
                "Status": status,
                "Last 30 sessions": [float(x) for x in close.iloc[-30:]],
            })
        except Exception:
            rows.append({"Ticker": ticker, "Price": None, "Move": None,
                         "z-score": None, "Status": "⚠ no data right now",
                         "Last 30 sessions": None})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tickers watched", len(tickers))
    c2.metric("Anomalies (today)", n_anom)
    c3.metric("Market state", "open/fresh" if n_fresh else "closed")
    c4.metric("Updated (UTC)", datetime.now(UTC).strftime("%H:%M"))
    # to_numeric: se todos os tickers falharem a coluna é object (só None) e .abs() rebentava.
    df = pd.DataFrame(rows).sort_values(
        "z-score", key=lambda s: pd.to_numeric(s, errors="coerce").abs(),
        ascending=False, na_position="last",
    )
    st.dataframe(
        df,
        use_container_width=True, hide_index=True,
        column_config={
            "Move": st.column_config.NumberColumn(
                format="percent", help="Last session's close-to-close change."),
            "z-score": st.column_config.NumberColumn(
                help="How unusual the move is vs this stock's previous 20 sessions."),
            "Last 30 sessions": st.column_config.LineChartColumn(width="medium"),
        },
    )
    st.caption("Auto-refreshes every 2 min · yfinance prices (~15 min delay) · "
               "same rule the Telegram alerts use.")


def page_live() -> None:
    st.header("Markets now")
    st.caption("The watchlist, scored by how unusual today's move is — biggest movers first.")
    _live_board()
    st.info("Get these as push alerts on your phone → **📡 Get alerts** in the sidebar.",
            icon="📡")


def page_home() -> None:
    col_logo, col_title = st.columns([1, 4])
    if _MASCOT.exists():
        col_logo.image(str(_MASCOT), width=150)
    col_title.title("InvestiGator — Explainable Financial Alerts for Retail Investors")
    col_title.caption("_Investigate. Don't speculate._ 🐊🔍")
    st.markdown(
        """
**InvestiGator** watches the US market for a retail investor and **explains** every alert.
There are two triggers:

1. **Abrupt market move** → a statistical anomaly (rolling *z*-score, no lookahead), explained in
   plain language.
2. **New financial news** → the most similar past headlines (sentence-embedding retrieval) and the
   impact those precedents actually had (event study) — **evidence, never a prediction**.

Use the sidebar to try each trigger, explore the evaluation, or read how it works.
        """
    )
    st.markdown("**Want it on your phone?** See **📡 Get alerts** in the sidebar.")


def _render_severity(ticker: str, headline: str) -> None:
    """Learned triage severity (RQ4) — shown only when models/ is present; silent otherwise.

    Uses the context-only logistic regression (light stack, no SBERT). Honest framing: the
    probability is triage evidence over historical cases, never a forecast.
    """
    from investigator.triage.infer import load_context_bundle, score_latest

    bundle = load_context_bundle()
    if bundle is None:
        return  # graceful absence: no models/ → the page simply has no severity section
    try:
        scored = score_latest(bundle, _cached_close(ticker), headline, ticker)
    except Exception:
        st.caption("Learned severity unavailable (price history could not be fetched).")
        return
    if scored is None:
        st.caption("Learned severity unavailable (not enough price history for this ticker).")
        return
    prob, contribs = scored
    st.subheader("Learned severity (materiality triage)")
    c1, c2 = st.columns([1, 2])
    c1.metric("P(abnormal move follows)", f"{prob:.0%}")
    c2.dataframe(
        pd.DataFrame(
            [{"Factor": name, "Pushes": "up" if c >= 0 else "down",
              "Logit contribution": round(c, 2)} for name, c in contribs],
        ),
        use_container_width=True, hide_index=True,
    )
    st.caption(
        "Context-only logistic regression trained by the author (RQ4) — the exact additive "
        "contributions above are the model's whole reasoning. Triage evidence, **not a "
        "forecast**; methodology and honest results in `docs/evaluation/evaluation_triage.md`."
    )


def page_news() -> None:
    from investigator.explanation_engine.explainer import plain_text
    from investigator.main import kb_query_embedder, preferred_light_kb, run_news_trigger

    st.header("Check a headline")
    st.caption(
        "Paste a headline — see the most similar past headlines and what the price did after."
    )
    kb_path = preferred_light_kb()
    col = st.columns([3, 1])
    headline = col[0].text_input("Headline", value="Nvidia demand surges on AI chip orders")
    ticker = col[1].text_input("Ticker", value="NVDA")
    top_k, horizon = 3, 5
    with st.expander("Advanced"):
        top_k = st.slider("How many precedents (k)", 1, 5, 3)
        horizon = st.selectbox("Impact horizon (trading days)", [1, 3, 5], index=2)
        st.caption(
            f"Knowledge base: {_kb_size(str(kb_path)):,} historical headlines "
            f"({'FNSPID 2018–2023, curated' if 'fnspid' in kb_path.name else 'small sample'}); "
            "matching is word-overlap (offline baseline) — weaker than the thesis's SBERT, so "
            "off-topic matches can appear (measured gap: About & method → Evaluation)."
        )

    if st.button("Find precedents", type="primary"):
        precedents, text = run_news_trigger(
            ticker=ticker.strip().upper(),
            headline=headline.strip(),
            kb_path=kb_path,
            embedder=kb_query_embedder(kb_path),
            top_k=top_k,
            horizon=horizon,
            send=False,
        )
        if not precedents:
            st.warning("No precedents found in the knowledge base.")
            return
        rows = []
        for rec, score in precedents:
            rows.append(
                {
                    "Date": rec.date,
                    "Ticker": rec.ticker,
                    "Similarity": round(float(score), 3),
                    "+1d": rec.impacts.get("1"),
                    "+3d": rec.impacts.get("3"),
                    "+5d": rec.impacts.get("5"),
                    "Headline": rec.headline,
                }
            )
        df = pd.DataFrame(rows)
        for c in ["+1d", "+3d", "+5d"]:
            df[c] = df[c].map(lambda v: f"{v:+.2%}" if v is not None else "—")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.text(plain_text(text))
        st.info(
            "Baseline embedder (word overlap). The thesis's real method is **SBERT** (semantic); "
            "see the Evaluation page for its measured advantage."
        )
        _render_severity(ticker.strip().upper(), headline.strip())


def page_market() -> None:
    st.header("Ticker check")
    st.caption(
        "Is the latest move unusual **for this stock**? Compared against its own recent "
        "behaviour — not a fixed percentage."
    )
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
    window, threshold = 20, 3.0
    with st.expander("Advanced"):
        window = st.slider("Window (days)", 10, 60, 20)
        threshold = st.slider("Threshold |z|", 2.0, 4.0, 3.0, step=0.5)

    if st.button("Check latest move", type="primary"):
        try:
            from investigator.anomaly_detector.detector import detect_latest
            from investigator.explanation_engine.explainer import (
                explain_anomaly,
                explain_normal,
                plain_text,
            )
            from investigator.market_data.prices import log_returns

            close = _cached_close(ticker)
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

        # Show the recent returns with the ±threshold·σ band around the rolling mean.
        band = pd.DataFrame({"return": returns.tail(60).reset_index(drop=True)})
        band["mean"] = res.mean
        band["+band"] = res.mean + threshold * res.std
        band["-band"] = res.mean - threshold * res.std
        st.line_chart(band, use_container_width=True)
        st.caption("Last ~60 daily log-returns with the anomaly band (mean ± threshold·σ).")


def page_evaluation() -> None:
    st.header("Evaluation — what the numbers mean")
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


def page_how() -> None:
    st.header("How it works")
    st.markdown(
        """
InvestiGator integrates existing, transparent components: a pre-trained sentence embedder (SBERT,
inference only), a statistical *z*-score, cosine similarity, and event-study arithmetic. On top of
those sits **one model trained by the author** — the materiality-triage logistic regression (RQ4):
it estimates the probability that an *abnormal move* follows a news item (**never** direction or
price), with labels produced by the system's own event-study code. No computer vision, no deep
training, no forecasting.
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


def page_about() -> None:
    st.header("About & how to cite")
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


@st.cache_data(show_spinner=False)
def _cached_close(ticker: str) -> pd.Series:
    """Cached close-price series (avoids refetching on every widget interaction)."""
    from investigator.market_data.prices import get_price_history

    return get_price_history(ticker)["Close"]


@st.cache_data(show_spinner=False)
def _kb_size(kb_path: str) -> int:
    """Cached record count of the knowledge base (one JSONL line per record)."""
    with open(kb_path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def _channel_url() -> str | None:
    """Optional public channel URL from config/alerts.yaml (non-secret; the channel is public)."""
    try:
        import yaml

        cfg = yaml.safe_load((_ROOT / "config" / "alerts.yaml").read_text(encoding="utf-8"))
        url = (cfg.get("public", {}) or {}).get("channel_url")
        return str(url) if url else None
    except Exception:
        return None


def page_alerts() -> None:
    st.header("Get alerts on your phone — nothing to install")
    st.markdown(
        """
InvestiGator scans the watchlist **every 30 minutes during US market hours** and posts to a public
Telegram channel — automatically, no action needed from you. Each alert explains itself: the rule
that fired, the numbers behind it, and (for news) the historical precedents.
        """
    )
    url = _channel_url()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1 · Join the channel")
        if url:
            st.link_button("📡 Open the Telegram channel", url, type="primary")
        else:
            st.markdown("Open Telegram and search for the **InvestiGator Alerts** channel.")
        st.caption("One alert per unusual move or material headline per day — no spam by design.")
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
    st.subheader("What an alert looks like (real output)")
    st.code(
        '📰 News alert for NVDA\n'
        '"Nvidia demand surges on AI chip orders"\n'
        "Potential impact (from 3 similar past events): average 5-day move: +6.46%\n"
        "Historical precedents:\n"
        '  • 2023-05-25 NVDA (sim 0.60) → 5d +3.55%: "Nvidia guidance surges..."\n'
        '  • 2023-04-25 MSFT (sim 0.38) → 5d +10.89%: "Microsoft cloud growth..."\n'
        '  • 2023-06-13 NVDA (sim 0.38) → 5d +4.93%: "Nvidia unveils new AI..."\n'
        "Note: precedents are retrieved by semantic similarity; the impact is the observed past\n"
        "outcome, not a price prediction.",
        language=None,
    )
    st.caption("Produced by the system's own offline demo (`python scripts/demo.py`) — "
               "deterministic and reproducible.")


def page_method() -> None:
    tab_what, tab_how, tab_eval, tab_cite = st.tabs(
        ["What is this?", "How it works", "Evaluation", "About & cite"]
    )
    with tab_what:
        page_home()
    with tab_how:
        page_how()
    with tab_eval:
        page_evaluation()
    with tab_cite:
        page_about()


PAGES = {
    "📊 Markets now": page_live,
    "🔎 Ticker check": page_market,
    "📰 Check a headline": page_news,
    "📡 Get alerts": page_alerts,
    "🎓 About & method": page_method,
}


def main() -> None:
    st.sidebar.title("InvestiGator")
    st.sidebar.caption("Market alerts that explain themselves.")
    choice = st.sidebar.radio("Go to", list(PAGES.keys()), label_visibility="collapsed")
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "⚠️ Research tool (MSc dissertation, ISEP). Explains past evidence — "
        "**not** financial advice, **no** price predictions."
    )
    PAGES[choice]()


if __name__ == "__main__":
    main()
