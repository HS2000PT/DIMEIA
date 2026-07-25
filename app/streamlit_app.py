"""InvestiGator — live market dashboard (Streamlit).

Design (2026-07-12, visão do aluno): DUAS vistas, e só duas.
- 📊 Live: faixa "Market now" (o dia dos 10 tickers num relance — 1 download em lote,
  cache 10 min, fail-open) + uma aba por empresa; em cada aba UM gráfico grande (estilo
  Google Finance) com intervalos 1D/5D/1M/6M, os EVENTOS detetados (anomalias + notícias,
  exatamente os que o canal Telegram recebeu) marcados no gráfico com hover, e a mesma
  lista numa tabela por baixo. Read-only: visualização, sem ações.
- ℹ️ About: o que é, como funciona, avaliação, como receber alertas, citação — tudo o que
  não é o painel vivo mora aqui (texto curto; detalhe em expanders — 2026-07-13).

Honesty notes (mirrors the thesis):
- No price prediction, no trading signals. Explanations only — evidence from the past.
- The history shown (chart markers + table) is read from the same shared record the Telegram
  channel's runner writes (branch alerts-history) — never recomputed here.
- Prices: yfinance first (intraday bars ~15 min delayed), with the multi-source daily
  fallback chain of the runner (Tiingo/Polygon/…) — see investigator/market_data/prices.py.
- Retrieval (About → try a headline) is semantic: the thesis's MiniLM in ONNX, with the
  word-overlap fallback and the live KB + age decay of the production runner.
"""

from __future__ import annotations

import os
import re
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
    page_title="InvestiGator — explainable market alerts", page_icon="🐊", layout="wide"
)

_ASSETS = Path(__file__).resolve().parent / "assets"
_LOGO = _ASSETS / "logo.svg"


def _phase_asset() -> Path:
    """Mascote sensível à hora (dia/noite), sincronizada com a hora local do aluno; cai no
    logo base se a mascote faltar ou algo falhar. Fun functionality, sempre on-brand."""
    try:
        from investigator.market_data.market_hours import day_phase

        cand = _ASSETS / ("mascot_night.svg" if day_phase().is_night else "mascot_day.svg")
        return cand if cand.exists() else _LOGO
    except Exception:  # noqa: BLE001
        return _LOGO


if _LOGO.exists():
    st.logo(str(_phase_asset()), size="large")

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


@st.cache_data(ttl=300, show_spinner=False)
def _live_monitoring_md() -> str | None:
    """Relatório de pós-validação ao vivo (live_monitoring.md na branch partilhada), fail-open.

    O loop de pós-fecho tornado VISÍVEL: como as decisões de triagem correram face à base
    rate (precisão das mantidas, Brier). Só leitura; ausente/offline/rede em baixo → None."""
    if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
        return None
    import requests

    url = _history_url().rsplit("/", 1)[0] + "/live_monitoring.md"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text if r.text.strip() else None
    except Exception:  # noqa: BLE001
        return None


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

@st.cache_data(ttl=600, show_spinner=False)
def _overview_moves(tickers: tuple[str, ...]) -> dict[str, float]:
    """Movimento do dia por ticker — UM download em lote (leve; cache 10 min; fail-open).

    "Quero ver como está o resto do mercado": a faixa dá o dia inteiro num relance sem
    repetir o problema de performance das tabs (1 chamada, não 10). Se o lote falhar,
    devolve {} e a faixa simplesmente não aparece. Em modo offline (testes/CI) nunca
    toca a rede — determinismo primeiro.
    """
    if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
        return {}
    try:
        import yfinance as yf

        df = yf.download(list(tickers), period="5d", interval="1d",
                         progress=False, group_by="ticker", threads=True)
        moves: dict[str, float] = {}
        for t in tickers:
            close = (df[t]["Close"] if isinstance(df.columns, pd.MultiIndex)
                     else df["Close"]).dropna()
            if len(close) >= 2:
                moves[t] = float(close.iloc[-1] / close.iloc[-2] - 1.0)
        return moves
    except Exception:  # noqa: BLE001  (a faixa é um extra — nunca pode derrubar a app)
        return {}


def _overview_line(moves: dict[str, float], tickers: list[str]) -> str:
    """Puro: a linha markdown da faixa (chips coloridos por direção; testável sem rede)."""
    chips = []
    for t in tickers:
        m = moves.get(t)
        if m is None:
            continue
        cor = "green" if m >= 0 else "red"
        chips.append(f":{cor}[**{t}** {m * 100:+.1f}%]")
    return " · ".join(chips)


def _market_state_pill() -> None:
    """Estado da sessão US ao vivo (🟢 aberto / 🔴 fechado) com contagem para a próxima
    mudança. Refresca com o fragmento `_live_view` (run_every). Fail-open: nunca derruba."""
    try:
        from investigator.market_data.market_hours import us_market_status

        s = us_market_status()
        dot = "🟢" if s.is_open else "🔴"
        st.markdown(f"{dot} **US market {s.label.lower()}** · {s.detail}")
    except Exception:  # noqa: BLE001 — um indicador nunca pode partir a página
        pass


def _overview_strip() -> None:
    _market_state_pill()
    moves = _overview_moves(tuple(_watchlist()))
    linha = _overview_line(moves, _watchlist())
    if linha:
        st.markdown(f"**Market now** · {linha}")
        st.caption("Today's move per watchlist name (batch quote, ~10 min cache) — "
                   "companies in the same sector often move together.")


@st.cache_data(ttl=600, show_spinner=False)
def _risk_score(ticker: str):
    """Risco de fundo cacheado (10 min): o modelo não muda ao minuto; a app fica leve."""
    bundle = _triage_bundle()
    if bundle is None:
        return None
    from investigator.triage.infer import score_background

    try:
        return score_background(bundle, _daily_close(ticker), ticker)
    except Exception:
        return None


def _risk_line(ticker: str) -> None:
    """Risco de fundo do modelo treinado (RQ4) — uma linha compacta, read-only."""
    scored = _risk_score(ticker)
    if scored is None:
        return
    prob, contribs = scored
    factors = " and ".join(name for name, _ in contribs[:2])
    st.caption(f"**Background risk {prob:.0%}** — P(bigger-than-usual move ahead), from the "
               f"author-trained triage model; mainly {factors}. Evidence, not a forecast.")


_SIGNED_PCT = re.compile(r"([+-]\d[\d.]*)%")


def _market_down(text: str) -> bool:
    """Direção de um evento de mercado a partir do NÚMERO guardado (o sinal do 1.º '%').

    Robusto a entradas antigas que gravaram o emoji errado (o bug das setas): lemos o valor,
    não o ícone. Sem '%' no texto (ex.: entradas de teste) → assume subida (default seguro).
    """
    m = _SIGNED_PCT.search(text)
    return bool(m) and m.group(1).startswith("-")


def _event_hover(h) -> str:
    """Cartão de hover formatado (moderno, multi-linha) para o marcador do gráfico.

    O hover cru (texto até 220 chars numa linha) era ilegível. Agora: o facto a negrito,
    a linha de severidade por baixo, e uma nota discreta com a data. Plotly aceita um
    subconjunto de HTML (<b>, <br>, <span>)."""
    linhas = [ln.strip() for ln in h.text.split("\n") if ln.strip()]
    head = linhas[0] if linhas else ""
    partes = [f"<b>{head}</b>"]
    if len(linhas) > 1:
        partes.append(linhas[1])
    partes.append(f"<span style='font-size:11px;opacity:0.65'>{h.date} · "
                  "open the list below for the full alert</span>")
    return "<br>".join(partes)


def _event_positions(events: list, closes: pd.Series, intraday: bool):
    """Mapeia eventos (com data) a posições (x, y) no gráfico do intervalo atual."""
    xs, ys, hovers, colors, symbols = [], [], [], [], []
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
        hovers.append(_event_hover(h))
        if h.kind == "market":
            # Direção pelo sinal do movimento (fonte única do bug das setas): vermelho a
            # descer, verde a subir; o símbolo do triângulo acompanha.
            down = _market_down(h.text)
            colors.append("#EF4444" if down else "#10B981")
            symbols.append("triangle-down" if down else "triangle-up")
        else:
            colors.append("#3B82F6")  # notícia: azul neutro, círculo
            symbols.append("circle")
    return xs, ys, hovers, colors, symbols


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
    xs, ys, hovers, colors, symbols = _event_positions(events, closes, intraday)
    if xs:
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers", name="Events",
            marker={"size": 15, "color": colors, "symbol": symbols,
                    "line": {"width": 1.6, "color": "white"}},
            hovertext=hovers, hovertemplate="%{hovertext}<extra></extra>",
        ))
    ymin, ymax = float(closes.min()), float(closes.max())
    folga = (ymax - ymin) * 0.08 or ymax * 0.01
    fig.update_layout(
        height=520, margin={"l": 10, "r": 10, "t": 16, "b": 10}, showlegend=False,
        hovermode="closest", yaxis={"range": [ymin - folga, ymax + folga],
                                    "title": "Price ($)"},
        xaxis={"rangeslider": {"visible": False}, "showspikes": True,
               "spikemode": "across", "spikethickness": 1, "spikedash": "dot",
               "spikecolor": "#94A3B8"},
        # Tooltip moderno: cartão claro, alinhado à esquerda, legível em ambos os temas.
        hoverlabel={"align": "left", "bgcolor": "rgba(255,255,255,0.97)",
                    "bordercolor": "#CBD5E1", "font": {"size": 12, "color": "#0B1F2E"}},
    )
    fig.data[0].hovertemplate = "<b>$%{y:.2f}</b> · %{x|%b %d, %Y}<extra></extra>"
    return fig


def _kind_label(h) -> str:
    """Rótulo humano do tipo de evento (com direção correta para o mercado)."""
    if h.kind == "news":
        return "📰 News event"
    if h.kind == "summary":
        return "📊 Daily summary"
    return "📉 Market anomaly (down)" if _market_down(h.text) else "📈 Market anomaly (up)"


def _events_list(eventos: list) -> None:
    """A tabela ÚNICA e expansível (substitui as 2 tabelas antigas): cada evento é uma linha
    — a info principal no cabeçalho (data + facto), os detalhes (texto completo do alerta)
    ao expandir. Read-only: espelho exato do que o canal Telegram recebeu."""
    for h in reversed(eventos):  # mais recente primeiro
        facto = h.text.split("\n", 1)[0].strip()
        with st.expander(f"{h.date}  ·  {facto}"):
            st.markdown(h.text.replace("\n", "  \n"))
            st.caption(f"{_kind_label(h)} · sent to the Telegram channel")


def _ticker_tab(ticker: str, history: list) -> None:
    eventos = [h for h in history if h.ticker == ticker]
    intervalo = st.radio("Range", list(_RANGES), index=2, horizontal=True,
                         key=f"range_{ticker}", label_visibility="collapsed")
    try:
        closes = _range_prices(ticker, intervalo)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"No price data right now for {ticker}: {type(exc).__name__}")
        return
    if len(closes) < 2:
        st.warning(f"Not enough data for {ticker} in this range yet.")
        return

    from investigator.news_fetcher.relevance import display_name

    var = float(closes.iloc[-1] / closes.iloc[0] - 1.0)
    nome = display_name(ticker)
    rotulo = f"{nome} ({ticker})" if nome != ticker else ticker
    c1, c2 = st.columns([1, 3])
    c1.metric(rotulo, f"${float(closes.iloc[-1]):.2f}", f"{var:+.2%} ({intervalo})")
    with c2:
        _risk_line(ticker)

    intraday = intervalo in ("1D", "5D")
    if _HAS_PLOTLY:
        st.plotly_chart(_big_chart(ticker, closes, eventos, intraday),
                        use_container_width=True, config={"displayModeBar": False},
                        key=f"chart_{ticker}_{intervalo}")
    else:
        st.line_chart(closes, use_container_width=True)
        st.caption("Interactive chart unavailable in this environment (plotly not installed). "
                   "All detected events remain in the list below.")
    st.caption("Prices: yfinance + multi-source daily fallback (intraday ~15 min delayed). "
               "Auto-refreshes. Hover a marker for the alert.")

    st.subheader("Alert history")
    if eventos:
        n_mkt = sum(1 for h in eventos if h.kind == "market")
        n_news = sum(1 for h in eventos if h.kind == "news")
        st.caption(f"{len(eventos)} on record · {n_mkt} market · {n_news} news · "
                   "📈 up · 📉 down · 📰 news. Open a row for the full alert, "
                   "exactly as sent to the Telegram channel.")
        _events_list(eventos)
    else:
        st.caption(f"No events recorded yet for {ticker}. This fills in as the automated "
                   "scan detects anomalies and material news.")


# run_every numérico (segundos): evita o caminho pd.Timedelta(str) do Streamlit, que
# sob numpy>=2.5 emite a deprecação "generic unit for timedelta" (e falha num numpy futuro).
# 120 segundos, comportamento idêntico.
def _health_strip(history, monitoring) -> None:
    """Prova de vida AO TOPO: quantos alertas explicados já saíram e — se a pós-validação
    existir — a precisão das decisões MANTIDAS vs a base rate, fora da amostra. Combate o
    'parece parado/ignorado'. Fail-open; sem st.metric (a guarda de performance conta metrics)."""
    from investigator.evaluation.monitoring import parse_live_monitoring

    n = sum(1 for h in history if h.kind in ("market", "news"))
    bits = []
    if n:
        bits.append(f"**{n}** explained alerts delivered")
    health = parse_live_monitoring(monitoring)
    if health:
        bits.append(
            f"kept-alert precision **{health.kept_precision:.0%}** vs "
            f"{health.base_rate:.0%} base rate (+{health.lift_points:.0f} pts, out-of-sample)"
        )
    if bits:
        st.success("✅ Live & tracked — " + " · ".join(bits))


@st.fragment(run_every=120)
def _live_view() -> None:
    history = _read_shared_history()
    _overview_strip()
    monitoring = _live_monitoring_md()
    _health_strip(history, monitoring)
    if not history:
        st.caption("⚠ No shared event history reachable right now. Charts still show live "
                   "prices; events appear as the automated scan records them.")
    openings = [h for h in history if h.kind == "open"]
    summaries = [h for h in history if h.kind == "summary"]
    if openings:
        with st.expander(f"🔔 Market open snapshot ({openings[-1].date})"):
            st.text(openings[-1].text)
    if summaries:
        with st.expander(f"📊 Daily close summary ({summaries[-1].date})"):
            st.text(summaries[-1].text)
    if monitoring:
        with st.expander("📈 How our alerts are doing (live monitoring)"):
            st.markdown(monitoring)
    tickers = _watchlist()
    # Seletor de empresa em vez de st.tabs: o Streamlit renderiza TODAS as tabs a cada
    # interação (10× fetch/scoring — a app arrastava-se). Assim só a empresa escolhida é
    # renderizada — o aspeto de tabs mantém-se, a app fica ~10× mais leve por interação.
    escolhido = st.radio("Company", tickers, index=0, horizontal=True,
                         key="ticker_sel", label_visibility="collapsed")
    _ticker_tab(escolhido or tickers[0], history)


# ── Vista ABOUT: tudo o resto, fora do caminho ──────────────────────────────────

def _about_view() -> None:
    c1, c2 = st.columns([1, 5])
    with c1:
        try:
            st.image(str(_phase_asset()), width=96)  # mascote dia/noite (sincronizada)
        except Exception:  # noqa: BLE001
            pass
    with c2:
        st.title("About InvestiGator")
        saud = _gator_greeting()
        if saud:
            st.caption(saud)
    st.markdown(
        """
**InvestiGator** watches the US market and **explains** every alert it sends:
**abrupt moves** (transparent rolling *z*-score with severity levels, a sector check and a
cross-investigation for the explaining headline) and **material news** (semantic precedents
from historical + living knowledge bases, ranked with age decay). On top sits the one model
**trained by the author** (RQ4): a calibrated triage classifier that gates news alerts
against noise. **Evidence, never a prediction.**
        """
    )

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
    st.caption("Reproducible with fixed seeds via `scripts/evaluate*.py`; "
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

    with st.expander("🔬 Try the retrieval engine on any headline (demo)"):
        _try_headline()

    with st.expander("📖 Cite / credits"):
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

# ── Painel de admin (guest por defeito; password de admin desbloqueia a edição) ──────────
def _secret(name: str):
    """Lê um segredo do Streamlit sem rebentar quando não há secrets.toml."""
    try:
        return st.secrets.get(name)
    except Exception:  # noqa: BLE001
        return None


def _admin_unlocked() -> bool:
    return bool(st.session_state.get("admin_ok"))


def _repo_slug() -> str | None:
    """Deriva OWNER/REPO do history_url (raw.githubusercontent.com/OWNER/REPO/branch/...)."""
    parts = (_history_url() or "").split("/")
    try:
        i = parts.index("raw.githubusercontent.com")
        return f"{parts[i + 1]}/{parts[i + 2]}"
    except (ValueError, IndexError):
        return None


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_branch_overrides() -> dict:
    """Overrides já aplicados (branch), para pré-preencher o formulário. Fail-open."""
    if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
        return {}
    url = _history_url()
    if not url:
        return {}
    import json

    import requests
    try:
        r = requests.get(url.rsplit("/", 1)[0] + "/alerts_overrides.json", timeout=5)
        if r.status_code == 404:
            return {}
        r.raise_for_status()
        return json.loads(r.text) or {}
    except Exception:  # noqa: BLE001
        return {}


def _put_branch_file(repo: str, token: str, content: str) -> tuple[bool, str]:
    """Cria/atualiza alerts_overrides.json na branch partilhada via GitHub API. Server-side."""
    import base64

    import requests
    api = f"https://api.github.com/repos/{repo}/contents/alerts_overrides.json"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        g = requests.get(api, params={"ref": "alerts-history"}, headers=headers, timeout=10)
        sha = g.json().get("sha") if g.status_code == 200 else None
        body = {"message": "admin: update alert overrides", "branch": "alerts-history",
                "content": base64.b64encode(content.encode()).decode()}
        if sha:
            body["sha"] = sha
        p = requests.put(api, json=body, headers=headers, timeout=10)
        if p.status_code in (200, 201):
            return True, "ok"
        return False, f"HTTP {p.status_code}: {p.json().get('message', '')[:120]}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)[:120]


def _admin_login_sidebar() -> None:
    with st.sidebar.expander("🔒 Admin", expanded=False):
        if _admin_unlocked():
            st.caption("Admin mode — settings apply to the live channel.")
            if st.button("Log out"):
                st.session_state["admin_ok"] = False
                st.rerun()
            return
        secret = _secret("admin_password")
        if not secret:
            st.caption("Guest (read-only). Set an `admin_password` secret to enable editing.")
            return
        pw = st.text_input("Admin password", type="password", key="admin_pw")
        if st.button("Unlock") and pw:
            if pw == secret:
                st.session_state["admin_ok"] = True
                st.rerun()
            else:
                st.error("Wrong password.")


def _admin_settings_panel() -> None:
    """Editor dos parâmetros de alerta (admin). Publica na branch → o scanner usa na próxima
    corrida. Sem token, mostra o JSON para copiar para o runner."""
    from investigator.settings_overrides import (
        TUNABLES,
        current_values,
        merge_overrides,
        validate_overrides,
    )

    effective = merge_overrides(_read_yaml_config(), _fetch_branch_overrides())
    cur = current_values(effective)
    st.caption("These are deployment settings (the thesis evaluation stays frozen at 3.0). "
               "Changes take effect on the scanner's next run.")
    chosen: dict = {}
    for t in TUNABLES:
        val = cur.get(t.key)
        if t.kind == "bool":
            chosen[t.key] = st.checkbox(t.label, value=bool(val), help=t.help or None)
        elif t.kind == "int":
            chosen[t.key] = st.slider(t.label, int(t.lo), int(t.hi),
                                      int(val if val is not None else t.lo), help=t.help or None)
        else:
            chosen[t.key] = st.slider(t.label, float(t.lo), float(t.hi),
                                      float(val if val is not None else t.lo), step=0.05,
                                      help=t.help or None)
    if st.button("Apply to live alerts", type="primary"):
        import json

        clean = validate_overrides(chosen)
        payload = json.dumps(clean, indent=2)
        token, repo = _secret("github_token"), _repo_slug()
        if token and repo:
            ok, msg = _put_branch_file(repo, token, payload)
            if ok:
                _fetch_branch_overrides.clear()
                st.success("Applied. The scanner will use these on its next run.")
            else:
                st.error(f"Could not publish ({msg}). Copy this to the runner instead:")
                st.code(payload, language="json")
        else:
            st.info("No write token — set a `github_token` secret to apply remotely, or paste "
                    "this into `config/alerts_overrides.yaml` on the runner:")
            st.code(payload, language="json")


def _gator_greeting() -> str:
    """Saudação do investigador sincronizada com a hora (☀️/🌙). Fail-open → sem saudação."""
    try:
        from investigator.market_data.market_hours import day_phase

        ph = day_phase()
        return f"{ph.emoji} {ph.greeting}"
    except Exception:  # noqa: BLE001
        return ""


def main() -> None:
    st.sidebar.title("InvestiGator")
    st.sidebar.caption("_Every move investigated, never predicted._")
    saudacao = _gator_greeting()
    if saudacao:
        st.sidebar.caption(saudacao)
    vista = st.sidebar.radio("View", ["📊 Live", "ℹ️ About"], label_visibility="collapsed")
    url = _channel_url()
    if url:
        st.sidebar.link_button("📡 Get alerts on Telegram", url, use_container_width=True)
    st.sidebar.markdown("---")
    _admin_login_sidebar()
    with st.sidebar:
        _disclaimer()

    if _admin_unlocked():
        with st.expander("⚙️ Alert settings — changes apply to the live channel", expanded=True):
            _admin_settings_panel()

    if vista == "📊 Live":
        _live_view()
    else:
        _about_view()


if __name__ == "__main__":
    main()
