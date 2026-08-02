"""InvestiGator — painel denso, construído de raiz.

**A pergunta a que este ecrã responde, por ordem.** Um investidor de retalho abre isto e
quer saber, em três segundos, *está a acontecer alguma coisa às minhas empresas?* Se sim,
num clique: *o quê, que tamanho, foi só o mercado, e já aconteceu antes?* A disposição é
literalmente essa ordem — lista à esquerda para a primeira pergunta, painel à direita para
as outras três.

**O que mudou em relação a tudo o que veio antes, e porquê.**

*Uma superfície, não três ecrãs.* As versões anteriores tinham `Today` / `Ticker` /
`Method` com botões de rádio. Mudar de ecrã perde o fio: chegas ao ticker e já não vês como
ele se compara com os outros. Aqui a lista nunca desaparece.

*Um painel de detalhe, em posição fixa.* A versão imediatamente anterior abria um cartão
por baixo de cada linha; com três nomes sinalizados o ecrã enchia-se e lia-se como seis
coisas. Agora clicar **troca o conteúdo** de um painel que está sempre no mesmo sítio.

*A história que já existia e não estava ligada.* O gráfico mostrava 220 alertas enviados —
e como os gates suprimem nove em cada dez varreduras, havia tickers com nada. Entretanto o
sistema tinha captado e medido **3 331 notícias** com impacto real, em `live_kb.jsonl`, sem
nunca as mostrar. O gráfico passa a ter três camadas, visualmente distintas de propósito:
o que foi **enviado** (◆), o que o método **detectaria** mas um gate travou (○), e as
**notícias** captadas com o impacto que vieram a ter (●). Ver a diferença entre a segunda e
a primeira camada é ver os gates a funcionar.

*Menos texto.* A decomposição era uma frase e passa a ser uma barra empilhada. O texto do
alerta continua lá — mas em detalhe, não no caminho principal.

**O que continua deliberadamente de fora.** Nenhum score de convergência e nenhum crachá de
tipo de evento, por muito bem que ficassem. Medimo-los: a convergência ganha em 1 de 3
orçamentos e a taxonomia tem silhueta 0,084. O critério **H4** de
`docs/design/dashboard_acceptance.md` proíbe mostrar um número que a nossa própria medição
não sustenta, e é essa recusa que separa isto de um clone.

Correr:  streamlit run app/dashboard.py
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

# O `streamlit run` põe no `sys.path` a pasta DO SCRIPT (`app/`), não a raiz do repositório
# — e portanto `from app import …` não resolve. Correr com `python -m streamlit` disfarça o
# problema, porque o `-m` acrescenta o directório actual; foi assim que isto passou a
# verificação e rebentou na primeira execução normal. Mesmo guarda que `streamlit_app.py`.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app import ui_tokens as T  # noqa: E402

WINDOW = 20
THRESHOLD = 1.5
HISTORY_BRANCH = "alerts-history"

# Intervalos. O primeiro é o defeito, e o defeito é HOJE: a pergunta que traz alguém aqui é
# "o que está a acontecer agora", não "como foi o mês".
RANGES: dict[str, tuple[str, str, bool]] = {
    "1D": ("1d", "5m", True),
    "5D": ("5d", "30m", True),
    "1M": ("1mo", "1d", False),
    "6M": ("6mo", "1d", False),
    "1Y": ("1y", "1d", False),
}

NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "TSLA": "Tesla",
    "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Meta", "JPM": "JPMorgan Chase",
    "AMD": "AMD", "NFLX": "Netflix",
}


# ══ Dados ════════════════════════════════════════════════════════════════════════════
# Tudo em cache e tudo a falhar aberto. Uma fonte em baixo tem de tirar uma linha do ecrã,
# nunca o ecrã inteiro.

def _watchlist() -> list[str]:
    # Caminho ancorado na raiz, não relativo ao directório de trabalho. Com um caminho
    # relativo isto falha sempre que a app é lançada de outra pasta — e como o caminho
    # falha aberto, a watchlist configurada seria ignorada **em silêncio**, mostrando a
    # lista de reserva como se fosse a dele.
    try:
        import yaml
        with open(_ROOT / "config" / "alerts.yaml", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
        return list(cfg.get("market", {}).get("tickers") or []) or list(NAMES)
    except Exception:  # noqa: BLE001
        return list(NAMES)


@st.cache_data(ttl=120, show_spinner=False)
def _daily(ticker: str) -> pd.DataFrame:
    from investigator.market_data.prices import get_price_history
    return get_price_history(ticker)


@st.cache_data(ttl=90, show_spinner=False)
def _intraday(ticker: str, period: str, interval: str) -> pd.DataFrame | None:
    """Barras intradiárias. `None` quando a fonte não as dá — e isso diz-se no ecrã."""
    try:
        import yfinance as yf
        frame = yf.Ticker(ticker).history(period=period, interval=interval)
        return frame if frame is not None and not frame.empty else None
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=300, show_spinner=False)
def _snapshot(ticker: str) -> dict | None:
    """Movimento do dia, z-score e volume — o que a linha da lista precisa."""
    try:
        from investigator.anomaly_detector.detector import detect_latest
        from investigator.market_data.prices import log_returns

        frame = _daily(ticker)
        close = frame["Close"]
        res = detect_latest(log_returns(close), window=WINDOW, threshold=THRESHOLD)
        out = {"ticker": ticker, "z": float(res.z_score), "move": float(res.last_return),
               "flagged": bool(res.is_anomaly), "vol_ratio": None}
        if "Volume" in frame:
            from investigator.anomaly_detector.volume import detect_volume_latest
            v = detect_volume_latest(frame["Volume"], window=WINDOW, threshold=2.0)
            if v.is_unusual:
                out["vol_ratio"] = float(v.ratio)
        return out
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=300, show_spinner=False)
def _replay(ticker: str, days: int) -> list[dict]:
    """Todos os dias que o método sinalizaria na janela mostrada.

    Esta é metade da resposta a "falta história": não é preciso gerar nada nem guardar
    nada. A regra da RQ1 corrida sobre o passado produz os eventos que ela *realmente*
    detectaria, e fá-lo com a mesma norma sem lookahead do tempo real.
    """
    try:
        from investigator.anomaly_detector.detector import detect_all
        from investigator.market_data.prices import log_returns

        close = _daily(ticker)["Close"].tail(days + WINDOW + 5)
        hits = detect_all(log_returns(close), window=WINDOW, threshold=THRESHOLD)
        return [{"date": pd.Timestamp(d).strftime("%Y-%m-%d"),
                 "z": float(r.z_score), "move": float(r.last_return)} for d, r in hits]
    except Exception:  # noqa: BLE001
        return []


def _raw(path: str) -> str:
    repo = os.getenv("INVESTIGATOR_HISTORY_REPO", "HS2000PT/DIMEIA")
    return f"https://raw.githubusercontent.com/{repo}/{HISTORY_BRANCH}/{path}"


@st.cache_data(ttl=60, show_spinner=False)
def _alerts() -> list:
    """Alertas efectivamente enviados ao canal."""
    try:
        from investigator.alerts_history import fetch_remote
        return fetch_remote(_raw("alerts_history.jsonl")) or []
    except Exception:  # noqa: BLE001
        return []


@st.cache_data(ttl=900, show_spinner=False)
def _news_by_ticker() -> dict[str, list[dict]]:
    """Notícias captadas com impacto já medido, por ticker.

    O ficheiro traz um vector de 384 dimensões por registo que aqui não serve para nada — é
    descartado à entrada, senão guardavam-se ~1,3 M de floats em cache para desenhar pontos.
    """
    import json
    import urllib.request

    out: dict[str, list[dict]] = {}
    try:
        with urllib.request.urlopen(_raw("live_kb.jsonl"), timeout=25) as resp:
            for linha in resp.read().decode("utf-8", "replace").splitlines():
                if not linha.strip():
                    continue
                try:
                    r = json.loads(linha)
                except ValueError:
                    continue
                imp = r.get("impacts") or {}
                out.setdefault(r.get("ticker", "?"), []).append({
                    "date": r.get("date", ""),
                    "headline": r.get("headline", ""),
                    "d1": imp.get("1"), "d5": imp.get("5"),
                })
    except Exception:  # noqa: BLE001
        return {}
    return out


@st.cache_data(ttl=300, show_spinner=False)
def _decomposition(ticker: str) -> dict | None:
    try:
        import numpy as np

        from investigator.correlation_engine.decomposition import decompose_move
        from investigator.news_fetcher.relevance import MARKET_INDEX, sector_etf

        etf = sector_etf(ticker)
        cols = {ticker: _daily(ticker)["Close"], MARKET_INDEX: _daily(MARKET_INDEX)["Close"]}
        if etf:
            cols[etf] = _daily(etf)["Close"]
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
                "driver": d.driver, "total": d.total, "fallback": bool(d.fallback)}
    except Exception:  # noqa: BLE001
        return None


def _market_state() -> tuple[bool, str]:
    agora = datetime.now(UTC).strftime("%H:%M UTC")
    try:
        from investigator.market_data.market_hours import is_market_open
        return bool(is_market_open()), agora
    except Exception:  # noqa: BLE001
        return False, agora


# ══ Apresentação ═════════════════════════════════════════════════════════════════════

def _logo_html(ticker: str, size: int = 18) -> str:
    """Logótipo, ou um quadrado com as iniciais. Nunca um espaço vazio."""
    try:
        from investigator.branding.logos import cached_logo
        uri = cached_logo(ticker)
    except Exception:  # noqa: BLE001
        uri = None
    if uri:
        return (f'<img src="{uri}" width="{size}" height="{size}" '
                f'style="border-radius:4px;vertical-align:middle;object-fit:contain;'
                f'background:#fff;padding:1px">')
    return (f'<span style="display:inline-block;width:{size}px;height:{size}px;'
            f'border-radius:4px;background:{T.PANEL_2};border:1px solid {T.LINE};'
            f'color:{T.FG_DIM};font-size:{size * 0.42:.0f}px;line-height:{size}px;'
            f'text-align:center;font-weight:700;vertical-align:middle">{ticker[:2]}</span>')


def _pct(value: float | None, digits: int = 2) -> str:
    return "—" if value is None else f"{value * 100:+.{digits}f}%"


def _header(rows: list[dict], n_alerts: int) -> None:
    aberto, agora = _market_state()
    cor = T.UP if aberto else T.FG_MUTE
    estado = "MARKET OPEN" if aberto else "MARKET CLOSED"
    sinalizados = sum(1 for r in rows if r["flagged"])
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:1.1rem;flex-wrap:wrap;
                        padding-bottom:0.6rem;border-bottom:1px solid {T.LINE}">
          <span style="font-size:15px;font-weight:800;letter-spacing:0.14em;color:{T.FG}">
            <span style="color:{T.UP}">◤</span> INVESTIGATOR</span>
          <span class="num" style="font-size:11.5px;color:{cor}">● {estado}</span>
          <span class="num" style="font-size:11.5px;color:{T.FG_MUTE}">{agora}</span>
          <span style="flex:1"></span>
          <span class="num" style="font-size:11.5px;color:{T.FLAG}">
            {T.ICON_ALERT} {sinalizados} flagged</span>
          <span class="num" style="font-size:11.5px;color:{T.FG_MUTE}">
            {n_alerts} alerts sent</span>
        </div>""",
        unsafe_allow_html=True,
    )


def _watchlist_rows(rows: list[dict]) -> None:
    """A lista: um botão por empresa, e nada mais no DOM.

    Todo o conteúdo vai no rótulo, em monoespaçado com `white-space: pre`, para as colunas
    alinharem sem tabela. O logótipo entra por CSS como imagem de fundo do botão — é o que
    permite ter ícone **e** clique numa só linha.
    """
    st.markdown('<div class="label" style="margin:0.6rem 0 0.35rem">WATCHLIST</div>',
                unsafe_allow_html=True)
    try:
        from investigator.branding.logos import cached_logo
    except Exception:  # noqa: BLE001
        def cached_logo(_):  # type: ignore[misc]
            return None

    for r in rows:
        t = r["ticker"]
        icone, cor = T.direction(r["move"])
        sel = st.session_state.get("sel") == t

        marcas = (T.ICON_ALERT if r["flagged"] else " ")
        if r["vol_ratio"]:
            marcas += f" {r['vol_ratio']:.1f}x vol"

        rotulo = (f"{t:<6}{icone} {r['move'] * 100:+6.2f}%   "
                  f"z{r['z']:+5.2f}   {marcas}")

        st.markdown(T.row_css(t, cor, cached_logo(t), r["flagged"], sel),
                    unsafe_allow_html=True)
        if st.button(rotulo, key=f"btn_{t}", use_container_width=True):
            st.session_state.sel = t
            st.rerun()


def _chart(ticker: str, rotulo: str) -> None:
    periodo, intervalo, intra = RANGES[rotulo]

    frame = _intraday(ticker, periodo, intervalo) if intra else None
    aviso = None
    if frame is None:
        dias = {"1D": 5, "5D": 10, "1M": 22, "6M": 130, "1Y": 260}[rotulo]
        frame = _daily(ticker).tail(dias)
        if intra:
            aviso = "Intraday bars unavailable from the free feed — showing daily closes."
        intra = False
    if frame is None or frame.empty:
        st.markdown(f'<div class="panel" style="color:{T.FG_MUTE}">No price data.</div>',
                    unsafe_allow_html=True)
        return

    close = frame["Close"]
    try:
        import plotly.graph_objects as go
    except ImportError:
        st.line_chart(close)
        return

    # Num gráfico intradiário a referência não é a primeira barra, é o FECHO ANTERIOR.
    # Sem ela, um dia que abriu com um salto de +14% desenha-se como uma subida de +2% e o
    # número grande no topo parece contradizer a curva — foi exactamente o que aconteceu
    # com a Amazon no dia de resultados.
    anterior = None
    if intra:
        try:
            diario = _daily(ticker)["Close"]
            se_hoje = pd.to_datetime(close.index[0]).date()
            passado = diario[pd.to_datetime(diario.index).date < se_hoje]
            anterior = float(passado.iloc[-1]) if len(passado) else None
        except Exception:  # noqa: BLE001
            anterior = None

    base = anterior if anterior is not None else float(close.iloc[0])
    subiu = float(close.iloc[-1]) >= base
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=close.index, y=close.values, mode="lines", name="",
        line={"color": T.UP if subiu else T.DOWN, "width": 1.6},
        hovertemplate="%{y:$.2f}<br>%{x|%d %b %H:%M}<extra></extra>"))

    if anterior is not None:
        fig.add_hline(y=anterior, line={"color": T.FG_MUTE, "width": 1, "dash": "dot"},
                      annotation_text=f"prev close ${anterior:,.2f}",
                      annotation_position="top left",
                      annotation_font={"size": 10, "color": T.FG_MUTE})

    if not intra:
        _overlay_signals(fig, ticker, close)

    baixo = min(float(close.min()), anterior or float(close.min()))
    cima = max(float(close.max()), anterior or float(close.max()))
    margem = (cima - baixo) * 0.14 or 1.0
    fig.update_layout(
        height=330, margin={"l": 0, "r": 0, "t": 8, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, hovermode="closest",
        font={"color": T.FG_DIM, "size": 11},
        xaxis={"showgrid": False, "linecolor": T.LINE, "zeroline": False},
        yaxis={"gridcolor": T.LINE, "griddash": "dot", "side": "right", "zeroline": False,
               "range": [baixo - margem, cima + margem], "tickformat": "$,.0f"},
        hoverlabel={"bgcolor": T.PANEL, "bordercolor": T.LINE,
                    "font": {"color": T.FG, "size": 11}})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False},
                    key=f"chart_{ticker}_{rotulo}")
    if aviso:
        st.caption(aviso)


def _overlay_signals(fig, ticker: str, close: pd.Series) -> None:
    """As três camadas de história, sobre a curva.

    Distintas de propósito. Um ◆ é um alerta que **saiu** para o canal; um ○ é um dia que o
    método sinalizaria e que um gate travou; um ● é uma notícia captada com o impacto que
    veio a ter. A distância entre ○ e ◆ é o custo dos gates, e mostrá-la é mais honesto do
    que só desenhar as vitórias.
    """
    import plotly.graph_objects as go

    idx = pd.to_datetime(close.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    pares = zip(idx, close.values, strict=False)
    por_dia = {d.strftime("%Y-%m-%d"): (d, float(v)) for d, v in pares}

    enviados = {getattr(e, "date", None) for e in _alerts()
                if getattr(e, "ticker", None) == ticker}

    det_x, det_y, det_t, al_x, al_y, al_t = [], [], [], [], [], []
    for hit in _replay(ticker, len(close)):
        if hit["date"] not in por_dia:
            continue
        d, y = por_dia[hit["date"]]
        rotulo = f"{hit['date']}<br>{_pct(hit['move'])} · z {hit['z']:+.2f}"
        # Uma instrução por linha, e nunca `a.append(x), b.append(y)`. A vírgula faz disto
        # um tuplo solto, e a "magia" do Streamlit desenha **qualquer** expressão solta do
        # script principal — inclusive dentro de funções. A versão com vírgulas pintou 253
        # caixas `(None, None, None)` por cima do gráfico.
        if hit["date"] in enviados:
            al_x.append(d)
            al_y.append(y)
            al_t.append(rotulo + "<br>alert sent")
        else:
            det_x.append(d)
            det_y.append(y)
            det_t.append(rotulo + "<br>detected, gated")

    if det_x:
        fig.add_trace(go.Scatter(
            x=det_x, y=det_y, mode="markers", name="",
            marker={"size": 9, "color": "rgba(0,0,0,0)", "symbol": "circle",
                    "line": {"color": T.FG_DIM, "width": 1.4}},
            text=det_t, hovertemplate="%{text}<extra></extra>"))
    if al_x:
        fig.add_trace(go.Scatter(
            x=al_x, y=al_y, mode="markers", name="",
            marker={"size": 11, "color": T.FLAG, "symbol": "diamond",
                    "line": {"color": T.BG, "width": 1}},
            text=al_t, hovertemplate="%{text}<extra></extra>"))

    nx, ny, nt = [], [], []
    for n in _news_by_ticker().get(ticker, []):
        if n["date"] not in por_dia:
            continue
        d, y = por_dia[n["date"]]
        impacto = (f"<br>+1d {_pct(n['d1'])} · +5d {_pct(n['d5'])}"
                   if n["d1"] is not None else "")
        nx.append(d)
        ny.append(y)
        nt.append(f"{(n['headline'] or '')[:88]}{impacto}")
    if nx:
        fig.add_trace(go.Scatter(
            x=nx, y=ny, mode="markers", name="",
            marker={"size": 5, "color": T.NEWS, "symbol": "circle", "opacity": 0.7},
            text=nt, hovertemplate="%{text}<extra></extra>"))


def _decomp_bar(ticker: str) -> None:
    """A decomposição como barra, não como frase.

    Responde à primeira pergunta de quem detém a acção — *é a minha empresa ou é o
    mercado?* — sem obrigar a ler. As três larguras somam o movimento; a cor diz o sentido
    de cada parte, e uma parte pode puxar ao contrário do total.
    """
    d = _decomposition(ticker)
    st.markdown('<div class="label">WHY IT MOVED</div>', unsafe_allow_html=True)
    if d is None:
        st.markdown(f'<span style="color:{T.FG_MUTE};font-size:12px">'
                    f'Not enough aligned history to attribute this move.</span>',
                    unsafe_allow_html=True)
        return

    partes = [("MARKET", d["market"], "market"), ("SECTOR", d["sector"], "sector"),
              ("COMPANY", d["company"], "company")]
    total_abs = sum(abs(v) for _, v, _ in partes) or 1.0
    # Separadores entre segmentos e uma largura mínima: sem isso, um movimento em que a
    # empresa vale 91% desenha-se como uma barra lisa e as outras duas partes somem, o que
    # é precisamente a informação que a barra existe para dar.
    segmentos = "".join(
        f'<div style="width:{max(abs(v) / total_abs * 100, 1.5):.1f}%;height:100%;'
        f'background:{T.UP if v > 0 else T.DOWN};'
        f'opacity:{1.0 if chave == d["driver"] else 0.45};'
        f'border-right:2px solid {T.PANEL}"></div>'
        for _, v, chave in partes)
    st.markdown(
        f'<div style="display:flex;height:10px;border-radius:5px;overflow:hidden;'
        f'background:{T.PANEL_2};margin:0.4rem 0 0.55rem">{segmentos}</div>',
        unsafe_allow_html=True)

    celulas = "".join(
        f'<div style="flex:1"><div class="label" style="font-size:9px;'
        f'color:{T.FG_DIM if chave == d["driver"] else T.FG_MUTE}">{k}</div>'
        f'<div class="num" style="font-size:15px;color:{T.UP if v > 0 else T.DOWN}">'
        f'{_pct(v)}</div></div>' for k, v, chave in partes)
    st.markdown(f'<div style="display:flex;gap:0.9rem">{celulas}</div>',
                unsafe_allow_html=True)
    if d["fallback"]:
        st.caption("Betas not estimable from recent history; market beta assumed 1.")


def _detail(ticker: str) -> None:
    snap = _snapshot(ticker)
    icone, cor = T.direction(snap["move"] if snap else None)
    cabeca = (
        f'<span class="num" style="font-size:25px;color:{cor};font-weight:700">'
        f'{icone} {_pct(snap["move"])}</span>'
        f'<span class="num" style="font-size:12px;color:{T.FG_MUTE};margin-left:0.55rem">'
        f'z {snap["z"]:+.2f}</span>') if snap else ""

    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.3rem">
          {_logo_html(ticker, 30)}
          <div><div style="font-size:17px;font-weight:700;color:{T.FG}">
            {NAMES.get(ticker, ticker)}</div>
          <div class="num" style="font-size:11px;color:{T.FG_MUTE}">{ticker}</div></div>
          <span style="flex:1"></span>{cabeca}
        </div>""", unsafe_allow_html=True)

    rotulo = st.radio("Range", list(RANGES), index=0, horizontal=True,
                      key=f"rng_{ticker}", label_visibility="collapsed")
    _chart(ticker, rotulo)

    st.markdown(
        f'<div class="num" style="display:flex;gap:1.1rem;font-size:10.5px;'
        f'color:{T.FG_MUTE};margin:-0.3rem 0 0.3rem">'
        f'<span style="color:{T.FLAG}">{T.ICON_ALERT} alert sent</span>'
        f'<span>{T.ICON_DETECT} detected, gated</span>'
        f'<span style="color:{T.NEWS}">{T.ICON_NEWS} news captured</span></div>',
        unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _decomp_bar(ticker)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _alert_feed(ticker)


def _alert_feed(ticker: str) -> None:
    """O que o canal enviou sobre esta empresa. Texto, mas fora do caminho principal."""
    entradas = [e for e in _alerts() if getattr(e, "ticker", None) == ticker]
    st.markdown(f'<div class="label">ALERTS SENT · {len(entradas)}</div>',
                unsafe_allow_html=True)
    if not entradas:
        st.markdown(f'<span style="color:{T.FG_MUTE};font-size:12px">'
                    f'Nothing passed every gate for this company yet — the chart still shows '
                    f'what the method detected.</span>', unsafe_allow_html=True)
        return
    for e in sorted(entradas, key=lambda x: getattr(x, "date", ""), reverse=True)[:6]:
        texto = (getattr(e, "text", "") or "").strip()
        primeira = texto.splitlines()[0] if texto else "(no text)"
        # O resumo usa o NOSSO glifo, não o do texto guardado. Os alertas antigos trazem
        # 📈 para cima e 🔻 para baixo — dois sistemas de ícones diferentes na mesma lista,
        # e um deles nem sequer é um par do outro. O corpo do alerta fica intacto: é o
        # registo do que saiu para o canal e reescrevê-lo seria falsificá-lo.
        for lixo in ("📈", "📉", "🔺", "🔻", "📊", "📰", "🔔", "⚠️"):
            primeira = primeira.replace(lixo, "")
        primeira = primeira.strip(" ·")
        glifo = {"market": T.ICON_ALERT, "news": T.ICON_NEWS}.get(
            getattr(e, "kind", ""), T.ICON_DETECT)
        with st.expander(f"{getattr(e, 'date', '?')}  {glifo}  {primeira[:72]}"):
            st.text(texto)


# ══ Página ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    st.markdown(T.css(), unsafe_allow_html=True)

    linhas = [s for s in (_snapshot(t) for t in _watchlist()) if s]
    if not linhas:
        st.markdown('<div class="panel">No market data available right now.</div>',
                    unsafe_allow_html=True)
        return
    linhas.sort(key=lambda r: (not r["flagged"], -abs(r["z"])))

    st.session_state.setdefault("sel", linhas[0]["ticker"])
    _header(linhas, len(_alerts()))

    esquerda, direita = st.columns([1, 2.1], gap="medium")
    with esquerda:
        _watchlist_rows(linhas)
    with direita:
        _detail(st.session_state.sel)

    st.markdown(
        f'<div style="margin-top:1.6rem;padding-top:0.7rem;border-top:1px solid {T.LINE};'
        f'font-size:10.5px;color:{T.FG_MUTE};line-height:1.55">'
        f'Evidence from the past, never a forecast. Every number on this page is produced '
        f'by the procedure described in the dissertation. Company marks belong to their '
        f'owners and are shown to identify the subject of the data.</div>',
        unsafe_allow_html=True)


try:
    st.set_page_config(page_title="InvestiGator", page_icon="◤", layout="wide",
                       initial_sidebar_state="collapsed")
except Exception:  # noqa: BLE001
    pass  # já configurada quando importada por um teste

if __name__ == "__main__":
    main()
