"""InvestiGator — explainable market alerts (Streamlit).  ⛔ SUPERSEDIDA (v1).

⛔ **Já não é servida.** O `Procfile` serve `app/dashboard_v4.py` desde 2026-08-09. Esta é a
v1, mantida como registo da evolução do produto (v1 → v3 → v4), que a tese discute no
Cap. 4. Não a corras à espera de ver o produto: `streamlit run app/dashboard_v4.py`.

Redesenhada a 2026-07-29 contra critérios de aceitação ESCRITOS ANTES do código
(`docs/design/app_acceptance.md`). A app tinha sido redesenhada 4× e rejeitada sempre por
critério estético — que não tem condição de paragem. Agora tem.

**Três ecrãs, um por cada pergunta do posicionamento:**
- **Today** — *o que na minha watchlist merece atenção agora?* (z-score + triagem)
- **Ticker** — *é a empresa ou o mercado? já aconteceu antes?* (decomposição + retrieval)
- **Method** — *porque é que eu havia de acreditar nisto?* (avaliação congelada)

**Honestidade (espelha a tese):** sem previsão de preços, sem sinais de trading. O histórico
mostrado é lido do MESMO registo partilhado que o canal Telegram recebeu (branch
`alerts-history`) — nunca recalculado aqui. Preços: yfinance primeiro (intradiário ~15 min
atrasado) com a cadeia de fallback do runner.

**Desempenho:** o z-score de cada ticker só precisa da série própria; a decomposição precisa
do SPY + ETF de setor. Por isso ordena-se com z-scores (10 séries em cache) e só se decompõem
os movers efetivamente MOSTRADOS — não os 10.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Plotly é "nice-to-have": a app NUNCA pode cair por causa dele.
_HAS_PLOTLY = os.environ.get("INVESTIGATOR_NO_PLOTLY") != "1"
if _HAS_PLOTLY:
    try:
        import plotly.graph_objects as go
    except ModuleNotFoundError:
        _HAS_PLOTLY = False
if not _HAS_PLOTLY:
    go = None

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Tolerante a ser IMPORTADO. O dashboard v2 (`app/dashboard.py`) reutiliza as funções de dados
# daqui para não haver duas versões da verdade, e a importação executa este módulo. Sem o
# try/except, a segunda chamada a `set_page_config` rebenta a página inteira. Quando este
# ficheiro é o script principal, o comportamento é exatamente o de sempre.
try:
    st.set_page_config(
        page_title="InvestiGator — explainable market alerts", page_icon="🐊", layout="wide"
    )
except Exception:  # noqa: BLE001 — já configurado por quem nos importou
    pass

_ASSETS = Path(__file__).resolve().parent / "assets"
_LOGO = _ASSETS / "logo.svg"
if _LOGO.exists():
    st.logo(str(_LOGO), size="large")

_DEFAULT_HISTORY_URL = (
    "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/alerts_history.jsonl"
)
_RANGES: dict[str, tuple[str, str]] = {
    "1D": ("1d", "5m"), "5D": ("5d", "30m"), "1M": ("1mo", "1d"), "6M": ("6mo", "1d"),
}
_WINDOW = 20  # a mesma janela do detetor em produção

# Números congelados da avaliação (fonte: docs/evaluation/, reproduzíveis por scripts/).
RETRIEVAL_P5 = pd.DataFrame({
    "Method": ["SBERT (MiniLM), at scale", "SBERT (MPNet)", "SBERT (MiniLM)",
               "Lexical (baseline)", "Random (base rate)", "Recency"],
    "P@5": [0.595, 0.538, 0.514, 0.346, 0.240, 0.126],
}).set_index("Method")

TRIAGE = pd.DataFrame({
    "Model": ["Volatility only", "Context only", "Context + text", "Alert-always (floor)"],
    "PR-AUC": [0.542, 0.538, 0.496, 0.378],
}).set_index("Model")

GATES = pd.DataFrame({
    "Gate": ["Relevance filter", "Freshness (≤2d)", "Precedent similarity ≥0.45",
             "Learned triage ≥0.50", "Cap 2/ticker/day"],
    "Measured effect": ["removes mislabelled headlines", "anti-repetition",
                        "silenced 7 of 10 tickers", "silenced 2 of 10 tickers",
                        "anti-fatigue"],
}).set_index("Gate")


# ── Config e dados partilhados ──────────────────────────────────────────────────
def _read_yaml_config() -> dict:
    import yaml

    return yaml.safe_load((_ROOT / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}


def _watchlist() -> list[str]:
    try:
        return list(_read_yaml_config().get("market", {}).get("tickers", [])) or ["AAPL"]
    except Exception:  # noqa: BLE001
        return ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]


def _public(key: str, default=None):
    try:
        return (_read_yaml_config().get("public", {}) or {}).get(key) or default
    except Exception:  # noqa: BLE001
        return default


def _history_url() -> str:
    return str(_public("history_url", _DEFAULT_HISTORY_URL))


@st.cache_data(ttl=60, show_spinner=False)
def _shared_history() -> list:
    """O MESMO histórico que o Telegram recebeu — nunca recalculado, só lido (fail-open)."""
    from investigator.alerts_history import fetch_remote

    return fetch_remote(_history_url())


@st.cache_data(ttl=120, show_spinner=False)
def _price_frame(ticker: str) -> pd.DataFrame:
    """A barra completa, não só o fecho.

    O volume vem na mesma resposta e estava a ser deitado fora. Guardar a moldura inteira em
    cache serve o preço e o volume com **uma** busca, em vez de duas.
    """
    from investigator.market_data.prices import get_price_history

    return get_price_history(ticker)


def _daily_close(ticker: str) -> pd.Series:
    return _price_frame(ticker)["Close"]


@st.cache_data(ttl=120, show_spinner=False)
def _volume_signal(ticker: str) -> dict | None:
    """Quão invulgar foi o volume — a segunda metade de "isto é invulgar para esta ação?".

    Um movimento de 3% com volume normal e o mesmo movimento com o triplo do volume habitual
    não são o mesmo acontecimento, e até aqui a app não sabia distinguir os dois.
    """
    try:
        from investigator.anomaly_detector.volume import detect_volume_latest

        frame = _price_frame(ticker)
        if "Volume" not in frame:
            return None
        res = detect_volume_latest(frame["Volume"].to_numpy(), window=_WINDOW, threshold=2.0)
        return {"z": float(res.z_score), "ratio": float(res.ratio),
                "unusual": bool(res.is_unusual)}
    except Exception:  # noqa: BLE001 — sem volume a linha aparece na mesma, só sem esta parte
        return None


@st.cache_data(ttl=60, show_spinner=False)
def _range_prices(ticker: str, range_key: str) -> pd.Series:
    from investigator.market_data.prices import get_price_history

    period, interval = _RANGES[range_key]
    return get_price_history(ticker, period=period, interval=interval)["Close"]


@st.cache_resource(show_spinner=False)
def _triage_bundle():
    from investigator.triage.infer import load_context_bundle

    return load_context_bundle()


@st.cache_resource(show_spinner="Loading the semantic model (first time only)…")
def _retrieval_engine() -> tuple:
    from investigator.main import product_retrieval

    return product_retrieval(auto_download=os.environ.get("INVESTIGATOR_OFFLINE") != "1")


@st.cache_data(ttl=300, show_spinner=False)
def _retrieval_kbs(kb_path: str) -> list:
    from investigator.historical_kb.knowledge_base import HistoricalKB
    from investigator.live_kb import fetch_remote_records

    kbs = []
    if os.environ.get("INVESTIGATOR_OFFLINE") != "1":
        vivos = fetch_remote_records(_history_url().rsplit("/", 1)[0] + "/live_kb.jsonl")
        if vivos:
            kbs.append(HistoricalKB(vivos))
    kbs.append(HistoricalKB.load(kb_path))
    return kbs


# ── Cálculo: ranking e decomposição ─────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def _unusualness(ticker: str) -> dict | None:
    """z-score e movimento do último dia. Só precisa da série do PRÓPRIO ticker — por isso
    corre para toda a watchlist sem custo de índice/ETF."""
    try:
        from investigator.anomaly_detector.detector import detect_latest
        from investigator.market_data.prices import log_returns

        close = _daily_close(ticker)
        res = detect_latest(log_returns(close), window=_WINDOW, threshold=1.5)
        return {"ticker": ticker,
                "z": None if res.reported_z is None else float(res.reported_z),
                "score": float(res.score_magnitude), "move": float(res.last_return),
                "is_anomaly": bool(res.is_anomaly),
                "zero_variance": bool(res.zero_variance)}
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=300, show_spinner=False)
def _decomposition(ticker: str) -> dict | None:
    """Reparte o último movimento em mercado / setor / empresa (o diferenciador do produto).

    Só é chamada para os movers MOSTRADOS: precisa do SPY e do ETF de setor, e fazê-lo para
    a watchlist inteira triplicaria as buscas por nada."""
    try:
        import numpy as np

        from investigator.correlation_engine.decomposition import decompose_move
        from investigator.news_fetcher.relevance import MARKET_INDEX, sector_etf

        etf = sector_etf(ticker)
        cols = {ticker: _daily_close(ticker), MARKET_INDEX: _daily_close(MARKET_INDEX)}
        if etf:
            cols[etf] = _daily_close(etf)
        frame = pd.DataFrame(cols)
        frame.index = pd.to_datetime(frame.index)
        if getattr(frame.index, "tz", None) is not None:
            frame.index = frame.index.tz_localize(None)
        frame = frame.dropna()
        if len(frame) < 16:
            return None
        rets = np.log(frame / frame.shift(1)).dropna()
        d = decompose_move(rets[ticker].to_numpy(), rets[MARKET_INDEX].to_numpy(),
                           rets[etf].to_numpy() if etf else None)
        return {"market": d.market, "sector": d.sector, "company": d.idiosyncratic,
                "driver": d.driver, "fallback": bool(d.fallback)}
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=600, show_spinner=False)
def _risk_score(ticker: str):
    bundle = _triage_bundle()
    if bundle is None:
        return None
    from investigator.triage.infer import score_background

    try:
        return score_background(bundle, _daily_close(ticker), ticker)
    except Exception:  # noqa: BLE001
        return None


# ── Cabeçalho: a promessa aparece UMA vez (critério F3) ─────────────────────────
def _header() -> None:
    st.markdown("### InvestiGator")
    st.markdown(
        "**Markets move. We investigate.** This tool answers three questions "
        "about your watchlist: *is this move unusual*, *is it the company or the market*, "
        "and *has something like it happened before*, with real numbers you can check. "
        "It never predicts prices and never gives advice."
    )
    _market_state()


def _market_state() -> None:
    try:
        from investigator.market_data.market_hours import us_market_status

        s = us_market_status()
        st.caption(f"{'🟢' if s.is_open else '🔴'} US market {s.label.lower()} · {s.detail}")
    except Exception:  # noqa: BLE001
        pass


def _latency_badge() -> None:
    """Latência medida facto→entrega. Sem carimbos (histórico antigo) simplesmente não
    aparece — nunca se mostra um número que não foi medido."""
    try:
        entries = _shared_history()
        lat = [e.latency_seconds() for e in entries]
        lat = sorted(x for x in lat if x is not None)
        if not lat:
            return
        mid = lat[len(lat) // 2]
        unit = f"{mid / 60:.0f} min" if mid >= 90 else f"{mid:.0f} s"
        st.caption(f"⏱️ Median time from event to delivery: **{unit}** (measured, n={len(lat)})")
    except Exception:  # noqa: BLE001
        pass


# ── ECRÃ 1: Today ───────────────────────────────────────────────────────────────
def _fmt_pct(x: float) -> str:
    return f"{x * 100:+.2f}%"


@st.fragment(run_every=60)
def _today_view() -> None:
    """Ecrã Today, a redesenhar-se sozinho de 60 em 60 segundos.

    Sem isto a página só se atualiza quando o utilizador clica em alguma coisa, o que num painel
    de mercado é o comportamento errado: um alerta que chega às 14:35 ficava invisível até
    alguém mexer. As funções de dados já têm cache com prazo de 60 s, pelo que este intervalo
    apanha os dados novos assim que expiram, sem multiplicar pedidos às fontes.

    ``run_every`` leva um **inteiro** de propósito. A forma em texto ("60s") faz o Streamlit
    passar por um caminho do pandas que emite aviso de descontinuação e que deixaria de
    funcionar numa versão futura do numpy.
    """
    st.subheader("Today")
    tickers = _watchlist()
    rows = [r for r in (_unusualness(t) for t in tickers) if r]
    if not rows:
        st.info("Market data is unavailable right now. Nothing is being hidden — the price "
                "sources are not responding. Try again shortly.")
        return

    rows.sort(key=lambda r: -r["score"])
    movers = [r for r in rows if r["score"] >= 1.0][:5]
    quiet = [r for r in rows if r not in movers]

    if not movers:
        st.success("Quiet day: nothing in the watchlist stood out.")
    else:
        # "stood out" e não "moved unusually": a lista mostra os mais fora do normal, mas só
        # os que passam o limiar do detetor levam "flagged". Chamar "unusual" a um z=+1.03
        # seria exagerar — e a honestidade do texto é o produto.
        flagged = sum(1 for r in movers if r["is_anomaly"])
        st.caption(f"{len(movers)} name(s) stood out today, ranked by how far from normal "
                   f"({flagged} past the alert threshold).")

    for r in movers:
        _mover_row(r)

    if quiet:
        names = " · ".join(f"{r['ticker']} {_fmt_pct(r['move'])}" for r in quiet)
        st.caption(f"**Quiet:** {names}")

    _latency_badge()


def _mover_row(r: dict) -> None:
    """Uma linha por mover, com a decomposição JÁ na linha (critério F2: sem clicar)."""
    from investigator.news_fetcher.relevance import display_name

    t = r["ticker"]
    arrow = "📈" if r["move"] >= 0 else "📉"
    with st.container(border=True):
        left, right = st.columns([3, 2])
        with left:
            st.markdown(f"**{arrow} {t} ({display_name(t)}) {_fmt_pct(r['move'])}**")
            detail = (f"z-score {r['z']:+.2f} vs a {_WINDOW}-day norm"
                      if r["z"] is not None
                      else f"flat {_WINDOW}-day norm; z-score undefined")
            if r["is_anomaly"]:
                detail += " · flagged"
            # O volume só entra quando é INVULGAR. Anunciar "1,0x o volume habitual" em cada
            # linha seria ruído: a ausência desta frase já significa "volume normal".
            vol = _volume_signal(t)
            if vol and vol["unusual"]:
                detail += f" · **{vol['ratio']:.1f}× usual volume**"
            st.caption(detail)
        with right:
            d = _decomposition(t)
            if d is None:
                st.caption("Split unavailable (needs index and sector data).")
            else:
                st.markdown(
                    f"{_fmt_pct(d['market'])} market · {_fmt_pct(d['sector'])} sector · "
                    f"**{_fmt_pct(d['company'])} company**"
                )
                # Só se comenta o que SURPREENDE.
                #
                # A leitura por omissão de um movimento grande é "aconteceu alguma coisa nesta
                # empresa", e a linha em cima já mostra a parcela própria a negrito. Repetir
                # "Specific to this company." em todas as linhas gasta espaço e não informa:
                # numa captura real do painel, as cinco linhas diziam exatamente o mesmo.
                #
                # O que vale a pena dizer é o contrário: quando a ação se moveu com o mercado
                # ou com o setor, e portanto NÃO é uma história sobre a empresa. É a mesma
                # regra do detetor de volume, que se cala quando o volume é normal.
                verdict = {"market": "Moved with the whole market, not company news.",
                           "sector": "Sector-wide, not company-specific.",
                           "company": ""}[d["driver"]]
                if d["fallback"]:
                    verdict = (verdict + " Beta not estimated; split is indicative.").strip()
                if verdict:
                    st.caption(verdict)


# ── ECRÃ 2: Ticker ──────────────────────────────────────────────────────────────
def _ticker_view() -> None:
    tickers = _watchlist()
    t = st.radio("Company", tickers, horizontal=True, label_visibility="collapsed",
                 key="ticker_picker")
    from investigator.news_fetcher.relevance import display_name

    st.subheader(f"{t} — {display_name(t)}")

    r = _unusualness(t)
    if r:
        # A seta do `delta` do Streamlit é derivada de PARSEAR o texto como número. Passar-lhe
        # "z -4.60" não parseia, e ele mostra uma seta VERDE PARA CIMA por omissão. Resultado
        # visto ao vivo: a AAPL a cair -7,64% com "↑ z -4.60" a verde ao lado. É o mesmo bug
        # das setas que já tinha sido corrigido nos alertas, a reaparecer por outra porta.
        #
        # O `delta` também não é o sítio certo para isto: significa "variação face ao valor
        # anterior", e o z-score não é isso. Fica como legenda, onde não há seta para errar.
        st.metric(f"{display_name(t)} ({t})", _fmt_pct(r["move"]))
        estatistica = (f"z-score {r['z']:+.2f} versus the 20-day norm"
                       if r["z"] is not None
                       else "flat 20-day norm; z-score undefined")
        st.caption(estatistica + (" · flagged" if r.get("is_anomaly") else ""))

    _decomposition_panel(t)
    _price_chart(t)
    _events_for(t)
    _precedents_note()


def _decomposition_panel(t: str) -> None:
    d = _decomposition(t)
    if d is None:
        return
    st.markdown("**Is it the company or the market?**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Market", _fmt_pct(d["market"]))
    c2.metric("Sector", _fmt_pct(d["sector"]))
    c3.metric("Company-specific", _fmt_pct(d["company"]))
    note = {"market": "Most of this move came with the whole market.",
            "sector": "Most of this move was sector-wide.",
            "company": "Most of this move was specific to the company."}[d["driver"]]
    if d["fallback"]:
        note += " Beta could not be estimated, so treat the split as indicative."
    st.caption(note + " Rolling beta against SPY and a sector ETF, estimated only on data "
               "before the day being explained.")


def _price_chart(t: str) -> None:
    rng = st.radio("Range", list(_RANGES), horizontal=True, index=0,
                   label_visibility="collapsed", key=f"range_{t}")
    try:
        series = _range_prices(t, rng)
    except Exception:  # noqa: BLE001
        st.caption("Price history is unavailable right now.")
        return
    if series is None or series.empty:
        st.caption("No price data for this range.")
        return
    if _HAS_PLOTLY:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(series.index), y=[float(v) for v in series.values],
            mode="lines", name=t, hovertemplate="$%{y:.2f} · %{x}<extra></extra>",
        ))
        _mark_alerts_on_chart(fig, t, series)
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0),
                          showlegend=False, hovermode="closest")
        fig.update_xaxes(showspikes=True, spikemode="across")
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{t}_{rng}")
    else:
        st.line_chart(series)


# Cada tipo de alerta com a MESMA leitura visual que o canal do Telegram usa. A direção não é
# recalculada aqui: é lida do próprio texto que foi enviado, porque se a app e o canal
# divergissem um dos dois estaria a mentir, e é precisamente essa a promessa do produto.
_MARK = {
    "up":      {"symbol": "triangle-up",   "color": "#0A8F52", "label": "move up"},
    "down":    {"symbol": "triangle-down", "color": "#C0392B", "label": "move down"},
    "news":    {"symbol": "circle",        "color": "#2C6FBB", "label": "news"},
    "open":    {"symbol": "diamond",       "color": "#8A8A8A", "label": "opening note"},
    "summary": {"symbol": "square",        "color": "#8A8A8A", "label": "daily summary"},
}


def _mark_kind(entry) -> str:
    """Categoria visual de uma entrada, a partir do que o canal REALMENTE enviou.

    Os ícones 📈/📉 já estão no texto do alerta (vêm de `direction_icon`, a fonte única que
    corrigiu o bug das setas). Lê-los daqui garante que o marcador no gráfico e a mensagem no
    telemóvel dizem a mesma coisa, sem uma segunda cópia da lógica de direção.
    """
    kind = (getattr(entry, "kind", "") or "").lower()
    if kind in ("open", "summary"):
        return kind
    texto = getattr(entry, "text", "") or ""
    if "📈" in texto:
        return "up"
    if "📉" in texto:
        return "down"
    return "news"


def _mark_alerts_on_chart(fig, ticker: str, series) -> None:
    """Põe no gráfico um marcador por alerta, no dia em que o canal o enviou.

    Sem isto o gráfico e a lista de alertas viviam separados, e o utilizador tinha de os casar
    de cabeça: o momento que interessa (o movimento) e a prova de que o sistema o apanhou
    ficavam em sítios diferentes do ecrã.

    Fail-open: qualquer problema deixa o gráfico exatamente como estava.
    """
    try:
        import pandas as pd

        entradas = [e for e in _shared_history() if e.ticker == ticker and e.date]
        if not entradas:
            return
        idx = pd.to_datetime(pd.Index(series.index)).tz_localize(None)
        porto: dict[str, list] = {}
        for e in entradas:
            quando = pd.to_datetime(e.date, errors="coerce")
            if pd.isna(quando):
                continue
            # O alerta é diário; o gráfico pode ser intradiário. Ancora-se no ponto mais
            # próximo dentro do intervalo mostrado, e ignora-se o que cai fora dele.
            pos = int((idx - quando).to_series().abs().values.argmin())
            if abs((idx[pos] - quando).days) > 3:
                continue
            porto.setdefault(_mark_kind(e), []).append(
                (series.index[pos], float(series.values[pos]),
                 (e.text or "").strip().splitlines()[0][:110])
            )
        for categoria, pontos in porto.items():
            estilo = _MARK.get(categoria, _MARK["news"])
            fig.add_trace(go.Scatter(
                x=[p[0] for p in pontos], y=[p[1] for p in pontos],
                mode="markers", name=estilo["label"],
                marker={"symbol": estilo["symbol"], "size": 13,
                        "color": estilo["color"],
                        "line": {"width": 1.5, "color": "white"}},
                text=[p[2] for p in pontos],
                hovertemplate="<b>%{text}</b><br>$%{y:.2f} · %{x}<extra></extra>",
            ))
    except Exception:  # noqa: BLE001
        return


def _events_for(t: str) -> None:
    """Eventos EXATAMENTE como o canal os enviou — espelho, nunca recálculo."""
    entries = [e for e in _shared_history() if e.ticker == t]
    if not entries:
        st.caption("No alerts recorded for this company yet.")
        return
    st.markdown(f"**What the channel sent about {t}**")
    for e in list(reversed(entries))[:6]:
        first = e.text.strip().splitlines()[0] if e.text.strip() else e.kind
        with st.expander(f"{e.date} · {first[:90]}"):
            st.text(e.text)


def _precedents_note() -> None:
    st.caption("Similar past cases are retrieved by meaning, not keywords. They show what "
               "happened *after* comparable headlines — an observed pattern, never a "
               "prediction for this one. Similar in topic does not mean similar in direction.")


# ── ECRÃ 3: Method ──────────────────────────────────────────────────────────────
def _method_view() -> None:
    st.subheader("Method")
    st.markdown(
        "Every number here is reproducible from the dissertation's scripts. Where a result "
        "is negative, it is reported as it fell."
    )
    st.markdown("**Retrieving comparable past news (precision@5)**")
    st.dataframe(RETRIEVAL_P5, use_container_width=True)
    st.caption("Semantic retrieval beats lexical and random baselines. Direction agreement "
               "(0.708) sits close to chance (0.688): topic ≠ direction.")

    st.markdown("**Does text help decide what deserves an alert? (PR-AUC)**")
    st.dataframe(TRIAGE, use_container_width=True)
    st.caption("No text model beat the volatility baseline. Reported as it stands. The "
               "learned score still works as a *ranking* mechanism: precision@5/day 0.632 "
               "against a 0.163 base rate.")

    st.markdown("**Why the channel is quiet so often**")
    st.dataframe(GATES, use_container_width=True)
    st.caption("Measured on a single live scan (2026-07-29): 9 of 10 tickers were silenced, "
               "and four missed their gate by 0.04 or less.")

    with st.expander("What this system never does"):
        st.markdown(
            "- No price predictions, no direction forecasts, no targets.\n"
            "- No buy/sell/hold advice.\n"
            "- No third-party analyst forecasts — importing someone else's prediction into a "
            "system defined by not predicting would be a contradiction.\n"
            "- No personal holdings, so no personalised recommendation."
        )

    url = _public("channel_url")
    if url:
        st.link_button("📡 Open the Telegram channel", url)
    st.caption("Research/educational tool (MSc dissertation, MEIA/ISEP). Not financial "
               "advice.")


# ── Composição ──────────────────────────────────────────────────────────────────
def main() -> None:
    _header()
    view = st.sidebar.radio("View", ["📊 Today", "🔎 Ticker", "📐 Method"],
                            label_visibility="collapsed")
    if view.endswith("Today"):
        _today_view()
    elif view.endswith("Ticker"):
        _ticker_view()
    else:
        _method_view()


# Só desenha quando ESTE ficheiro é o que o Streamlit está a correr. Importado (pelo dashboard
# v2, ou por um teste), expõe as funções sem pintar a app antiga por cima da nova.
if __name__ == "__main__":
    main()
