"""InvestiGator — interactive dashboard (Streamlit).

A thin, stateless UI over the *validated* InvestiGator functions. It demonstrates the two triggers
(news precedents; market anomaly) and shows the evaluation, so an examiner can click through the
XAI story without installing anything.

Run locally:
    pip install -r requirements-app.txt          # streamlit (light stack already covers the rest)
    streamlit run app/streamlit_app.py

Honesty notes (mirrors the thesis):
- No price prediction, no trading signals. Explanations only — evidence from the past.
- The interactive news trigger uses the offline baseline embedder (HashingEmbedder) and the small
  sample knowledge base, so it runs anywhere with no downloads. The thesis's real method is SBERT;
  its measured advantage is on the Evaluation page.
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

def page_home() -> None:
    col_logo, col_title = st.columns([1, 4])
    if _MASCOT.exists():
        col_logo.image(str(_MASCOT), width=150)
    col_title.title("InvestiGator — Explainable Financial Alerts for Retail Investors")
    col_title.caption("_Investigate. Don't speculate._ 🐊🔍")
    _disclaimer()
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
    c1, c2, c3 = st.columns(3)
    c1.metric("Automated tests", "103 ✓")
    c2.metric("Verified citations", "52 / 52")
    c3.metric("Price predictions made", "0 (by design)")

    with st.expander("📱 Get the alerts on your phone (free)"):
        st.markdown(
            """
- **Channel:** join the Telegram channel the scheduled scan posts to (one alert per anomalous
  ticker per day, after US close).
- **Personal watchlist (bot):** when the operator runs the interactive bot
  (`python scripts/run_bot.py`), talk to it on Telegram — `/watch TSLA`, `/list`, `/stop` —
  and the scan also delivers *your* tickers to you. Subscriptions stay in a local SQLite file.
- Everything explains **past evidence** (z-score, precedents). No forecasts, no advice.
            """
        )


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
    from investigator.main import run_news_trigger

    st.header("News trigger — precedents and their impact")
    _disclaimer()
    st.markdown(
        "Type a headline and a ticker. InvestiGator finds the most **similar past headlines** "
        "in its knowledge base and shows what happened to the price afterwards."
    )
    col = st.columns([3, 1])
    headline = col[0].text_input("Headline", value="Nvidia demand surges on AI chip orders")
    ticker = col[1].text_input("Ticker", value="NVDA")
    c1, c2 = st.columns(2)
    top_k = c1.slider("How many precedents (k)", 1, 5, 3)
    horizon = c2.selectbox("Impact horizon (trading days)", [1, 3, 5], index=2)

    if st.button("Find precedents", type="primary"):
        precedents, text = run_news_trigger(
            ticker=ticker.strip().upper(),
            headline=headline.strip(),
            top_k=top_k,
            horizon=horizon,
            send=False,
        )
        if not precedents:
            st.warning("No precedents found in the sample knowledge base.")
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
        st.text(text)
        st.info(
            "Baseline embedder (word overlap). The thesis's real method is **SBERT** (semantic); "
            "see the Evaluation page for its measured advantage."
        )
        _render_severity(ticker.strip().upper(), headline.strip())


def page_market() -> None:
    st.header("Market trigger — is today an anomaly?")
    _disclaimer()
    st.markdown(
        "InvestiGator compares the latest daily return against this stock's own recent behaviour "
        "(rolling *z*-score). A large |z| means the move is unusual **for this stock**."
    )
    c1, c2, c3 = st.columns(3)
    ticker = c1.text_input("Ticker", value="AAPL").strip().upper()
    window = c2.slider("Window (days)", 10, 60, 20)
    threshold = c3.slider("Threshold |z|", 2.0, 4.0, 3.0, step=0.5)

    if st.button("Check latest move", type="primary"):
        try:
            from investigator.anomaly_detector.detector import detect_latest
            from investigator.explanation_engine.explainer import explain_anomaly, explain_normal
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
        st.text(text)

        # Show the recent returns with the ±threshold·σ band around the rolling mean.
        band = pd.DataFrame({"return": returns.tail(60).reset_index(drop=True)})
        band["mean"] = res.mean
        band["+band"] = res.mean + threshold * res.std
        band["-band"] = res.mean - threshold * res.std
        st.line_chart(band, use_container_width=True)
        st.caption("Last ~60 daily log-returns with the anomaly band (mean ± threshold·σ).")


def page_evaluation() -> None:
    st.header("Evaluation — what the numbers mean")
    _disclaimer()
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
    _disclaimer()
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


PAGES = {
    "Home": page_home,
    "News trigger": page_news,
    "Market trigger": page_market,
    "Evaluation": page_evaluation,
    "How it works": page_how,
    "About": page_about,
}


def main() -> None:
    st.sidebar.title("InvestiGator")
    st.sidebar.caption("Explainable financial alerts")
    choice = st.sidebar.radio("Go to", list(PAGES.keys()))
    st.sidebar.markdown("---")
    st.sidebar.caption("No predictions · free APIs · every alert explained.")
    PAGES[choice]()


if __name__ == "__main__":
    main()
