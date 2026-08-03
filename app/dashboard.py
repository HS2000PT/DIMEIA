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

# Intervalos, na ordem convencional. O DEFEITO É `1M`, e isso mudou.
#
# Era `1D`, com a justificação de que a pergunta que traz alguém aqui é "o que está a
# acontecer agora". Mas essa pergunta é respondida no CARTÃO — o número grande, o veredicto
# e a raridade estão todos na grelha, sem clicar. Quem clica está a fazer a pergunta
# seguinte, que é a da tese: *já aconteceu antes, e o que se seguiu?*
#
# E essa não cabe num dia. Com `1D` o gráfico não tem nem um marcador (as três camadas de
# história são de dias passados) e a tabela de eventos abre vazia, porque o impacto de uma
# notícia só é observável +5 dias depois. Ou seja: o ecrã inteiro de detalhe abria sem a
# única coisa que ele existe para mostrar. Foi a captura que deu por isso — nos testes
# passava, porque um painel vazio é um painel válido.
RANGE_DEFAULT = "1M"
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
    "AMD": "AMD", "NFLX": "Netflix", "XOM": "Exxon Mobil", "JNJ": "Johnson & Johnson",
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


@st.cache_data(ttl=600, show_spinner=False)
def _daily(ticker: str) -> pd.DataFrame:
    """Um ANO de barras diárias.

    Eram seis meses, e o gráfico pedia 260 linhas para o intervalo "1Y" — ou seja, o botão
    1Y mostrava calado seis meses. O ano serve os dois: corrige o intervalo e dá as ~250
    sessões de que a contagem de raridade precisa para dizer "dos últimos 249 dias".

    **O `ttl` está deliberadamente em camadas, e esta é a de fora.** Era de 120 s, o que
    mandava buscar doze anos de barras à rede de dois em dois minutos — de longe a coisa
    mais lenta desta página, e a repetir-se atrás de cada repintura. As barras DIÁRIAS de
    um ano não mudam a esse ritmo. O que muda depressa é o preço de hoje, e esse chega por
    `_intraday` (ttl 90 s), que é pequeno e por ticker. Cachar a rede por mais tempo do que
    os números derivados dela é o que torna barata uma repintura.
    """
    from investigator.market_data.prices import get_price_history
    return get_price_history(ticker, period="1y")


@st.cache_data(ttl=900, show_spinner=False)
def _rarity(ticker: str):
    """Quantos dias do último ano se moveram pelo menos tanto como hoje.

    A tradução do z-score para linguagem comum, sem assumir distribuição nenhuma. Ver
    `investigator/anomaly_detector/frequency.py` para o porquê de não ser uma probabilidade.
    """
    try:
        from investigator.anomaly_detector.frequency import empirical_exceedance
        from investigator.market_data.prices import log_returns

        return empirical_exceedance(log_returns(_daily(ticker)["Close"]))
    except Exception:  # noqa: BLE001
        return None


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


@st.cache_data(ttl=900, show_spinner=False)
def _replay(ticker: str) -> list[dict]:
    """Todos os dias que o método sinalizaria no ano carregado.

    Esta é metade da resposta a "falta história": não é preciso gerar nada nem guardar
    nada. A regra da RQ1 corrida sobre o passado produz os eventos que ela *realmente*
    detectaria, e fá-lo com a mesma norma sem lookahead do tempo real.

    **Deixou de receber o tamanho da janela mostrada, e é essa a correcção.** Recebia-o, e
    portanto cada botão de intervalo (1M, 6M, 1Y) era uma chave de cache diferente: trocar
    de intervalo voltava a correr `detect_all` sobre a série de novo, o que é a coisa mais
    cara desta página. Agora corre uma vez por ticker e quem desenha filtra pelo que está
    no ecrã.

    O resultado é o mesmo **por construção**, e a razão está em `detect_all`: a norma é
    causal — o z do dia *i* usa os 20 dias imediatamente antes dele, nunca a série inteira.
    Logo cortar a série antes ou depois de detectar produz exactamente os mesmos dias, desde
    que o corte deixe 20 dias de história atrás do primeiro dia visível. Era precisamente
    isso que o `tail(days + WINDOW + 5)` da versão anterior garantia, e é o que o teste de
    regressão em `tests/test_dashboard_launch.py` fixa.
    """
    try:
        from investigator.anomaly_detector.detector import detect_all
        from investigator.market_data.prices import log_returns

        hits = detect_all(log_returns(_daily(ticker)["Close"]),
                          window=WINDOW, threshold=THRESHOLD)
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


BACKFILL = _ROOT / "data" / "samples" / "backfill_kb.jsonl"


def _absorver(linhas, out: dict[str, list[dict]], vistos: set) -> None:
    """Acrescenta registos de um JSONL, sem repetir (ticker, data, manchete)."""
    import json

    for linha in linhas:
        if not linha.strip():
            continue
        try:
            r = json.loads(linha)
        except ValueError:
            continue
        chave = (r.get("ticker"), r.get("date"), (r.get("headline") or "")[:80])
        if chave in vistos:
            continue
        vistos.add(chave)
        imp = r.get("impacts") or {}
        out.setdefault(r.get("ticker", "?"), []).append({
            "date": r.get("date", ""), "headline": r.get("headline", ""),
            "d1": imp.get("1"), "d5": imp.get("5"),
        })


@st.cache_data(ttl=900, show_spinner=False)
def _news_by_ticker() -> dict[str, list[dict]]:
    """Notícias captadas com impacto medido, por ticker — de duas fontes somadas.

    **Local primeiro** (`data/backfill_kb.jsonl`): um ano reconstruído, ~35 mil registos,
    lido do disco sem rede. É o que dá densidade ao gráfico desde o primeiro segundo,
    inclusive quando o GitHub está inacessível.

    **Depois a base viva**, da branch de dados: são as semanas mais recentes, que o ano
    reconstruído não pode ter porque o impacto a +5 dias ainda não é observável.

    A ordem importa e é esta de propósito: se a rede falhar, o painel perde as últimas
    semanas mas mantém o ano. O contrário — perder tudo porque um pedido HTTP falhou — era
    o comportamento anterior.
    """
    import urllib.request

    out: dict[str, list[dict]] = {}
    vistos: set = set()

    if BACKFILL.exists():
        try:
            with BACKFILL.open(encoding="utf-8") as fh:
                _absorver(fh, out, vistos)
        except OSError:
            pass

    try:
        with urllib.request.urlopen(_raw("live_kb.jsonl"), timeout=25) as resp:
            _absorver(resp.read().decode("utf-8", "replace").splitlines(), out, vistos)
    except Exception:  # noqa: BLE001
        pass  # o ano local chega para o painel funcionar

    return out


@st.cache_data(ttl=900, show_spinner=False)
def _news_days(ticker: str) -> list[dict]:
    """As notícias de uma empresa agregadas a **uma entrada por dia**, mais recente primeiro.

    O impacto é medido por (ticker, dia): seis manchetes do mesmo dia partilham exactamente
    os mesmos +1d/+5d. Como pontos no gráfico isso são seis marcas indistinguíveis
    empilhadas no mesmo sítio — e, com o hover unificado, seis linhas iguais dentro da
    mesma caixa. O dia é a unidade em que estes dados existem, portanto é a unidade que se
    desenha; a contagem das outras manchetes vai no campo `n`, para não se perder.

    É também isto que faz o gráfico e a tabela concordarem **por construção** (D1): as duas
    lêem esta lista, logo não podem divergir uma da outra.
    """
    por_dia: dict[str, dict] = {}
    for n in _news_by_ticker().get(ticker, []):
        dia = n.get("date") or ""
        if not dia:
            continue
        if dia in por_dia:
            por_dia[dia]["n"] += 1
        else:
            por_dia[dia] = {**n, "n": 1}
    return sorted(por_dia.values(), key=lambda n: n["date"], reverse=True)


@st.cache_resource(show_spinner=False)
def _retrieval_engine() -> tuple:
    """(caminho da KB, embedder) para o produto. `cache_resource` porque o modelo não é dados.

    Fail-open por dentro (`product_retrieval`): sem `onnxruntime`, sem rede ou sem o modelo
    em cache, degrada para a KB-amostra com sobreposição de palavras em vez de deixar a
    página sem esta secção. O motor em uso é depois **dito no ecrã**, porque um precedente
    lexical e um precedente semântico não valem o mesmo e o utilizador tem direito a saber
    qual está a ver.
    """
    from investigator.main import product_retrieval

    return product_retrieval(auto_download=os.environ.get("INVESTIGATOR_OFFLINE") != "1")


@st.cache_resource(show_spinner=False)
def _retrieval_kbs(kb_path: str) -> list:
    """A KB viva (casos deste sistema) mais a histórica. Pela mesma ordem do runner.

    **`cache_resource` e não `cache_data`, e a diferença não é de estilo.** O `cache_data`
    guarda uma *cópia serializada* do que a função devolve — aqui, 19,4 MB de registos com
    embeddings de 384 dimensões, a serem escritos e relidos com pickle. Uma base de casos
    carregada não é um valor a copiar, é um recurso a partilhar, e é exactamente para isso
    que existe o `cache_resource`. (A v1 tem o mesmo `cache_data` neste sítio; ficou como
    estava, porque a v1 está implantada e não se toca.)
    """
    from investigator.historical_kb.knowledge_base import HistoricalKB
    from investigator.live_kb import fetch_remote_records

    kbs = []
    if os.environ.get("INVESTIGATOR_OFFLINE") != "1":
        try:
            vivos = fetch_remote_records(_raw("live_kb.jsonl"))
            if vivos:
                kbs.append(HistoricalKB(vivos))
        except Exception:  # noqa: BLE001
            pass
    kbs.append(HistoricalKB.load(kb_path))
    return kbs


@st.cache_data(ttl=900, show_spinner=False)
def _precedents(ticker: str, top_k: int = 4) -> dict | None:
    """*Já aconteceu antes, e o que se seguiu?* — a terceira pergunta da tese.

    **Esta é a que não estava no produto de todo.** O motor existe e funciona
    (`live_kb.merged_precedents`, avaliado na RQ2 com P@5 0,595 à escala), mas nenhuma das
    duas apps o mostrava: a v1 só o expunha numa demonstração, a v3 não o tinha. A base de
    casos é a razão de ser do trabalho e era invisível.

    A consulta é a **última manchete captada** desta empresa. Os casos que voltam são de
    **outras empresas também** — é essa a aposta da RQ2, que um acontecimento parecido
    noutro sítio informa este —, e por isso cada linha diz de quem é.

    O desfecho é **medido**, nunca projectado: `impacts` foi calculado depois do facto, com
    a regra de alinhamento sem lookahead. A repartição subiram/desceram vai junta para o
    ecrã poder aplicar a moldura tema ≠ direcção (H3) em vez de uma média que a esconde.
    """
    dias = _news_days(ticker)
    if not dias:
        return None
    consulta = dias[0]
    try:
        from investigator.live_kb import merged_precedents

        kb_path, embedder = _retrieval_engine()
        casos = merged_precedents(
            consulta["headline"], _retrieval_kbs(str(kb_path)), embedder,
            top_k=top_k, today=datetime.now(UTC).date())
    except Exception:  # noqa: BLE001
        return None
    if not casos:
        return None

    linhas, subiram, desceram = [], 0, 0
    for rec, sim in casos:
        imp = rec.impacts.get("5")
        if imp is not None and imp == imp:
            subiram += imp > 0
            desceram += imp < 0
        else:
            imp = None
        linhas.append({"ticker": rec.ticker, "date": rec.date, "headline": rec.headline,
                       "impact": imp, "sim": float(sim)})
    return {"query": consulta["headline"], "query_date": consulta["date"], "cases": linhas,
            "up": subiram, "down": desceram,
            "semantic": bool(getattr(embedder, "semantic", False))}


@st.cache_data(ttl=900, show_spinner=False)
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


@st.cache_data(ttl=3600, show_spinner=False)
def _brand_mark(size: int = 18) -> str:
    """A marca "The Tail", lida do SVG real em vez de um glifo de texto.

    Estava um `◤` no cabeçalho — um carácter emprestado a fazer de logótipo, enquanto o
    ficheiro da marca existia e não era usado em lado nenhum. O SVG usa `currentColor`,
    portanto herda a cor do contentor e não precisa de variante própria.
    """
    try:
        bruto = (_ROOT / "app" / "assets" / "logo-dark.svg").read_text(encoding="utf-8")
        corpo = bruto[bruto.index("<svg"):]
        for atrib in ('width="256"', 'height="256"'):
            corpo = corpo.replace(atrib, "", 1)
        return corpo.replace("<svg", f'<svg width="{size}" height="{size}"', 1)
    except Exception:  # noqa: BLE001
        return ""


def _header(rows: list[dict], n_alerts: int) -> None:
    from app.verdict import FLAG_EXPLAINER

    aberto, agora = _market_state()
    cor = T.UP if aberto else T.FG_MUTE
    estado = "MARKET OPEN" if aberto else "MARKET CLOSED"
    sinalizados = sum(1 for r in rows if r["flagged"])
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:1.1rem;flex-wrap:wrap;
                        padding-bottom:0.6rem;border-bottom:1px solid {T.LINE}">
          <span style="display:flex;align-items:center;gap:0.5rem;font-size:15.5px;
                       font-weight:800;letter-spacing:0.13em;color:{T.FG}">
            <span style="color:{T.UP};display:flex">{_brand_mark(20)}</span>INVESTIGATOR</span>
          <span class="num" style="font-size:12px;color:{cor}">● {estado}</span>
          <span class="num" style="font-size:12px;color:{T.FG_MUTE}">{agora}</span>
          <span style="flex:1"></span>
          <a class="num help" href="?view=method" target="_self"
             style="font-size:12px;color:{T.FLAG};text-decoration:none"
             title="{FLAG_EXPLAINER}">
            {T.ICON_ALERT} {sinalizados} flagged &middot; what is this?</a>
          <a class="num" href="?view=method" target="_self"
             style="font-size:12px;color:{T.FG_MUTE};text-decoration:none">
            {n_alerts} alerts sent</a>
        </div>""",
        unsafe_allow_html=True,
    )


def _chart(ticker: str, rotulo: str) -> tuple[str, str] | None:
    """Desenha o gráfico e devolve a **janela de datas que realmente desenhou** (ISO).

    Devolvê-la é o que permite à tabela de eventos mostrar exactamente o que o gráfico
    mostra (D1). A alternativa — a tabela voltar a deduzir a janela a partir do rótulo do
    intervalo — seria uma segunda consulta paralela aos mesmos dados, e duas consultas
    paralelas divergem: basta o gráfico cair para barras diárias porque a fonte não deu
    intradiárias, e a tabela ficaria a falar de um período que não está desenhado. Aqui
    não pode acontecer, porque quem sabe o que foi desenhado é quem desenha.
    """
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
        return None

    close = frame["Close"]
    # A janela desenhada, tal como saiu — depois de todos os recuos. Se a fonte não deu
    # barras intradiárias e isto caiu para fechos diários, é o período dos fechos diários
    # que a tabela tem de usar, não o que o botão prometia.
    _idx = pd.to_datetime(close.index)
    janela = (_idx.min().strftime("%Y-%m-%d"), _idx.max().strftime("%Y-%m-%d"))

    try:
        import plotly.graph_objects as go
    except ImportError:
        st.line_chart(close)
        return janela

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
    # Sem a data no `hovertemplate`: com o hover unificado ela passa a ser o TÍTULO da
    # caixa, e repeti-la em cada linha era escrevê-la duas vezes na mesma caixa.
    fig.add_trace(go.Scatter(
        x=close.index, y=close.values, mode="lines", name="",
        line={"color": T.UP if subiu else T.DOWN, "width": 1.6},
        hovertemplate="%{y:$.2f}<extra></extra>"))

    if anterior is not None:
        fig.add_hline(y=anterior, line={"color": T.FG_MUTE, "width": 1, "dash": "dot"},
                      annotation_text=f"prev close ${anterior:,.2f}",
                      annotation_position="top left",
                      annotation_font={"size": 10, "color": T.FG_MUTE})

    # Os sinais desenham-se em TODOS os intervalos, incluindo os intradiários. Estavam
    # atrás de um `if not intra`, e por isso um acontecimento visível no gráfico de 1M
    # desaparecia ao carregar em 1D — no mesmo dia, com os mesmos dados. Não havia razão
    # para isso: só era preciso ensinar a sobreposição a encontrar a barra certa quando há
    # muitas barras por dia (ver `_overlay_signals`).
    _overlay_signals(fig, ticker, close, intraday=intra)

    baixo = min(float(close.min()), anterior or float(close.min()))
    cima = max(float(close.max()), anterior or float(close.max()))
    margem = (cima - baixo) * 0.14 or 1.0
    # `hovermode="x unified"` e não `"closest"`: com `closest`, um marcador de notícia rouba
    # o hover ao preço, e ler o valor de um dia obrigava a acertar no pixel da linha. Com a
    # coluna unificada basta estar algures na vertical daquele dia, e o preço e tudo o que
    # aconteceu nesse dia aparecem na MESMA caixa — que é a pergunta real ("o que houve
    # aqui?"), e não duas perguntas separadas.
    #
    # O `spikemode="across"` é o que desenha a linha vertical de ponta a ponta; sem ele o
    # espigão pára no ponto e não serve de fio-de-prumo contra o eixo.
    fig.update_layout(
        height=330, margin={"l": 0, "r": 0, "t": 8, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, hovermode="x unified",
        font={"color": T.FG_DIM, "size": 11},
        xaxis={"showgrid": False, "linecolor": T.LINE, "zeroline": False,
               "showspikes": True, "spikemode": "across", "spikesnap": "cursor",
               "spikethickness": 1, "spikedash": "dot", "spikecolor": T.FG_MUTE},
        yaxis={"gridcolor": T.LINE, "griddash": "dot", "side": "right", "zeroline": False,
               "range": [baixo - margem, cima + margem], "tickformat": "$,.0f"},
        hoverlabel={"bgcolor": T.PANEL, "bordercolor": T.LINE, "align": "left",
                    "font": {"color": T.FG, "size": 11}})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False},
                    key=f"chart_{ticker}_{rotulo}")
    if aviso:
        st.caption(aviso)
    return janela


def _overlay_signals(fig, ticker: str, close: pd.Series, intraday: bool = False) -> None:
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

    # Num gráfico diário há uma barra por dia e o mapa é directo. Num intradiário há
    # dezenas, e a chave `%Y-%m-%d` seria escrita e reescrita até sobrar a ÚLTIMA barra do
    # dia — o que colocaria a marca de uma notícia da manhã no fecho da tarde. Ancorar na
    # PRIMEIRA barra do dia é honesto e previsível: a marca aparece onde o dia começa, que
    # é o mais próximo do acontecimento que estes dados permitem afirmar.
    pares = list(zip(idx, close.values, strict=False))
    por_dia: dict[str, tuple] = {}
    for d, v in pares:
        chave = d.strftime("%Y-%m-%d")
        if chave not in por_dia:  # primeira barra do dia vence
            por_dia[chave] = (d, float(v))

    # Uma notícia de sábado não tem barra onde pousar. Antes, essas marcas simplesmente
    # não se desenhavam — e o resultado era o gráfico a mostrar 13 marcas enquanto a
    # tabela listava 18 dias, a mesma janela a dar dois números diferentes.
    #
    # A âncora é a **primeira sessão em ou depois** da data da notícia, que não é uma
    # invenção para tapar o buraco: é exactamente a regra com que o sistema alinha eventos
    # para medir o impacto (`live_kb.mature_entry`, e a KB histórica antes dela). Ou seja,
    # a marca aparece no mesmo dia contra o qual os +1d/+5d daquela linha foram medidos. O
    # hover continua a dizer a data real da manchete.
    from app.tables import anchor

    dias_ordenados = sorted(por_dia)

    def _ancora(dia: str) -> tuple | None:
        """A sessão onde esta data se desenha, ou `None` se cai fora do que está no ecrã."""
        sessao = anchor(dias_ordenados, dia)
        return por_dia[sessao] if sessao else None

    enviados = {getattr(e, "date", None) for e in _alerts()
                if getattr(e, "ticker", None) == ticker}

    det_x, det_y, det_t, al_x, al_y, al_t = [], [], [], [], [], []
    for hit in _replay(ticker):
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
    for n in _news_days(ticker):
        alvo = _ancora(n["date"])
        if alvo is None:
            continue
        d, y = alvo
        impacto = (f"<br>+1d {_pct(n['d1'])} · +5d {_pct(n['d5'])}"
                   if n["d1"] is not None else "")
        mais = f"<br>+{n['n'] - 1} more headline(s) that day" if n["n"] > 1 else ""
        nx.append(d)
        ny.append(y)
        nt.append(f"{(n['headline'] or '')[:88]}{impacto}{mais}")
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
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">'
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
        f'<div style="flex:1"><div class="label" style="font-size:10px;'
        f'color:{T.FG_DIM if chave == d["driver"] else T.FG_MUTE}">{k}</div>'
        f'<div class="num" style="font-size:17px;color:{T.UP if v > 0 else T.DOWN}">'
        f'{_pct(v)}</div></div>' for k, v, chave in partes)
    st.markdown(f'<div style="display:flex;gap:0.9rem">{celulas}</div>',
                unsafe_allow_html=True)
    if d["fallback"]:
        st.caption("Betas not estimable from recent history; market beta assumed 1.")


def _detail(ticker: str) -> None:
    snap = _snapshot(ticker)
    icone, cor = T.direction(snap["move"] if snap else None)
    cabeca = (
        f'<span class="num" style="font-size:27px;color:{cor};font-weight:700">'
        f'{icone} {_pct(snap["move"])}</span>'
        f'<span class="num" style="font-size:13px;color:{T.FG_MUTE};margin-left:0.55rem">'
        f'z {snap["z"]:+.2f}</span>') if snap else ""

    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.3rem">
          {_logo_html(ticker, 30)}
          <div><div style="font-size:19px;font-weight:700;color:{T.FG}">
            {NAMES.get(ticker, ticker)}</div>
          <div class="num" style="font-size:12px;color:{T.FG_MUTE}">{ticker}</div></div>
          <span style="flex:1"></span>{cabeca}
        </div>""", unsafe_allow_html=True)

    rotulo = st.radio("Range", list(RANGES), index=list(RANGES).index(RANGE_DEFAULT),
                      horizontal=True, key=f"rng_{ticker}", label_visibility="collapsed")
    # A janela sai do gráfico e desce para as duas tabelas. É o botão de intervalo que
    # serve de filtro de data — ter um segundo controlo de datas por baixo seria a mesma
    # decisão pedida duas vezes, que foi exactamente a queixa "coisas a mais de uma vez".
    janela = _chart(ticker, rotulo)

    st.markdown(
        f'<div class="num" style="display:flex;gap:1.1rem;font-size:11.5px;'
        f'color:{T.FG_MUTE};margin:-0.3rem 0 0.3rem">'
        f'<span style="color:{T.FLAG}">{T.ICON_ALERT} alert sent</span>'
        f'<span>{T.ICON_DETECT} detected, gated</span>'
        f'<span style="color:{T.NEWS}">{T.ICON_NEWS} news captured</span></div>',
        unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _decomp_bar(ticker)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    # A ordem é a das três perguntas: o quê e que tamanho (cabeçalho e gráfico), foi o
    # mercado (decomposição), já aconteceu antes (precedentes). Só depois a história desta
    # empresa em particular, que é uma pergunta diferente e mais estreita.
    _precedent_panel(ticker)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _news_panel(ticker, janela)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _alert_feed(ticker, janela)


def _impact_bar(valor: float | None, escala: float = 0.06) -> str:
    """O impacto medido como barra divergente a partir de um eixo central.

    Uma coluna de percentagens obriga a ler dez números para ver que a maioria é negativa;
    uma coluna de barras mostra-o sem ler nenhum. A escala é fixa (±6%) de propósito — se
    fosse relativa a cada linha, dois dias muito diferentes desenhariam barras iguais.
    """
    if valor is None:
        return f'<span style="color:{T.FG_MUTE};font-size:10px">n/a</span>'
    frac = max(-1.0, min(1.0, valor / escala))
    largura = abs(frac) * 50
    cor = T.UP if valor > 0 else T.DOWN
    esquerda = 50 - largura if valor < 0 else 50
    return (f'<div style="position:relative;height:9px;width:78px;background:{T.PANEL_2};'
            f'border-radius:2px">'
            f'<div style="position:absolute;left:50%;top:0;width:1px;height:100%;'
            f'background:{T.LINE}"></div>'
            f'<div style="position:absolute;left:{esquerda}%;width:{largura}%;height:100%;'
            f'background:{cor};border-radius:2px"></div></div>')


PER_PAGE = 8


def _pager(chave: str, n_pages: int, pagina: int, total: int, unidade: str) -> None:
    """Os controlos de página. Só aparecem quando há mais do que uma página.

    Um paginador sobre uma lista de três linhas é ruído a dizer que não há nada para
    fazer.
    """
    if n_pages <= 1:
        st.markdown(f'<div class="tfoot">{total} {unidade}</div>', unsafe_allow_html=True)
        return
    e, meio, d = st.columns([1, 6, 1])
    with e:
        if st.button("‹ Prev", key=f"prev_{chave}", disabled=pagina <= 1,
                     use_container_width=True):
            st.session_state[f"pg_{chave}"] = pagina - 1
            st.rerun()
    with meio:
        st.markdown(f'<div class="tfoot" style="text-align:center">'
                    f'Page {pagina} of {n_pages} &middot; {total} {unidade}</div>',
                    unsafe_allow_html=True)
    with d:
        if st.button("Next ›", key=f"next_{chave}", disabled=pagina >= n_pages,
                     use_container_width=True):
            st.session_state[f"pg_{chave}"] = pagina + 1
            st.rerun()


def _page_state(chave: str, assinatura: tuple) -> int:
    """A página actual, reposta a 1 sempre que os filtros mudam.

    Sem esta reposição existe um estado que parece dados em falta: filtrar estando na
    página 5 deixa a tabela vazia, com filtros que combinam e sem mensagem nenhuma. O
    `paginate` também corrige a página, mas corrigir e **repor** são coisas diferentes —
    quem acabou de escrever um filtro quer ver o princípio dos resultados, não o fim.
    """
    if st.session_state.get(f"sig_{chave}") != assinatura:
        st.session_state[f"sig_{chave}"] = assinatura
        st.session_state[f"pg_{chave}"] = 1
    return int(st.session_state.get(f"pg_{chave}", 1))


def _precedent_panel(ticker: str) -> None:
    """*Já aconteceu antes, e o que se seguiu?* — a pergunta que justifica a base de casos.

    O desfecho de cada caso é **medido**, e a moldura tema ≠ direcção (H3) aparece sempre,
    não só quando os casos discordam. A média deliberadamente **não** é o número de
    destaque: sobre casos que foram a +4% e a −8%, uma média de −2% descreve um valor que
    nunca aconteceu a ninguém.
    """
    from app.verdict import precedent_framing

    p = _precedents(ticker)
    st.markdown(
        '<div class="label">HAS THIS HAPPENED BEFORE? &middot; '
        f'<span style="text-transform:none;letter-spacing:0;color:{T.FG_MUTE}">'
        f'past cases on a similar topic, with the outcome that was measured</span></div>',
        unsafe_allow_html=True)

    if p is None:
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">'
                    f'No comparable past cases for {ticker} yet — the case base needs a '
                    f'captured headline to search from.</span>', unsafe_allow_html=True)
        return

    motor = ("semantic match (the dissertation's MiniLM model)" if p["semantic"]
             else "word overlap — the semantic model is unavailable, so these are weaker")
    st.markdown(
        f'<div style="font-size:12.5px;color:{T.FG_DIM};margin:0.1rem 0 0.5rem">'
        f'Closest to the latest captured headline '
        f'<span class="num" style="color:{T.FG_MUTE}">({p["query_date"]})</span>: '
        f'&ldquo;{(p["query"] or "")[:120]}&rdquo;'
        f'<div style="color:{T.FG_MUTE};font-size:11.5px;margin-top:0.15rem">'
        f'Found by {motor}.</div></div>', unsafe_allow_html=True)

    cabecalho = ('<div class="trow thead">'
                 '<span class="label" style="width:58px">CASE</span>'
                 '<span class="label" style="width:78px">DATE</span>'
                 '<span class="label" style="flex:1">HEADLINE</span>'
                 '<span class="label" style="width:82px">+5D THEN</span>'
                 '<span class="label" style="width:52px">SIM</span></div>')
    linhas = []
    for c in p["cases"]:
        linhas.append(
            f'<div class="trow">'
            f'<span class="num" style="width:58px;font-size:12px;color:{T.FG_DIM}">'
            f'{c["ticker"]}</span>'
            f'<span class="num" style="width:78px;font-size:12px;color:{T.FG_MUTE}">'
            f'{c["date"]}</span>'
            f'<span class="tcell">{(c["headline"] or "")[:110]}</span>'
            f'<span style="width:82px">{_impact_bar(c["impact"])}</span>'
            f'<span class="num" style="width:52px;font-size:11.5px;color:{T.FG_MUTE}">'
            f'{c["sim"]:.2f}</span></div>')
    st.markdown(cabecalho + "".join(linhas), unsafe_allow_html=True)

    # A moldura H3 vem SEMPRE, e a negrito. Não é uma ressalva a acrescentar quando calha:
    # é a diferença entre "casos parecidos" e "isto vai acontecer".
    st.markdown(
        f'<div style="font-size:12.5px;color:{T.FLAG};margin-top:0.5rem">'
        f'{precedent_framing(p["up"], p["down"])}</div>'
        f'<div style="font-size:11.5px;color:{T.FG_MUTE};margin-top:0.2rem">'
        f'Cases can come from other companies on purpose — that is what the retrieval was '
        f'evaluated for. Outcomes are what followed then, measured after the fact.</div>',
        unsafe_allow_html=True)


def _news_panel(ticker: str, janela: tuple[str, str] | None = None) -> None:
    """As notícias captadas e **o que aconteceu a seguir**, dentro da janela do gráfico.

    Isto é a pergunta central da tese — *já aconteceu antes, e o que se seguiu?* Nada aqui
    é previsão: são desfechos **observados** de notícias passadas, e é por isso que a
    coluna se chama "what followed" e não "expected".

    **O que mudou (D1).** Mostrava as seis notícias mais recentes, sempre as mesmas,
    independentemente do que estivesse no gráfico. Quem olhasse para seis meses de curva
    com marcas espalhadas por ela e depois para a tabela via seis dias de Julho — duas
    coisas a falar de períodos diferentes, uma por baixo da outra, sem nada a avisar. Agora
    a janela vem do gráfico (`_chart` devolve-a) e a lista vem de `_news_days`, a mesma que
    desenha as marcas. Cada marca no gráfico tem linha na tabela porque é literalmente a
    mesma lista.
    """
    from app.tables import (
        DIRECTIONS,
        MAGNITUDES,
        ORDERS,
        filter_events,
        paginate,
        sort_events,
        within,
    )

    todas = _news_days(ticker)
    na_janela = within(todas, *(janela or (None, None)))

    periodo = (f"{janela[0]} → {janela[1]}" if janela else "all captured history")
    st.markdown(
        f'<div class="label">NEWS CAPTURED &middot; '
        f'<span style="text-transform:none;letter-spacing:0;color:{T.FG_MUTE}">'
        f'{periodo} &middot; what followed, measured — not a forecast</span></div>',
        unsafe_allow_html=True)

    if not todas:
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">'
                    f'No captured news for this company yet.</span>',
                    unsafe_allow_html=True)
        return

    c1, c2, c3, c4 = st.columns([3, 1.1, 1.1, 1.5])
    with c1:
        q = st.text_input("Search headlines", key=f"q_{ticker}",
                          placeholder="e.g. earnings, chips, lawsuit")
    with c2:
        direccao = st.selectbox("What followed", DIRECTIONS, key=f"dir_{ticker}")
    with c3:
        mag = st.selectbox("Minimum move", list(MAGNITUDES), key=f"mag_{ticker}")
    with c4:
        ordem = st.selectbox("Sort by", ORDERS, key=f"ord_{ticker}")

    filtradas = sort_events(
        filter_events(na_janela, query=q, direction=direccao, min_abs=MAGNITUDES[mag]),
        ordem)

    chave = f"news_{ticker}"
    pagina = _page_state(chave, (q, direccao, mag, ordem, janela))
    fatia, pagina, n_pages = paginate(filtradas, pagina, PER_PAGE)

    if not filtradas:
        # Três estados vazios diferentes, e nunca o mesmo texto para os três. "Não há
        # nada", "os teus filtros não deixam passar nada" e "a janela é curta demais" são
        # problemas distintos com soluções distintas, e um utilizador que não sabe qual
        # deles tem desiste do produto em vez de mexer no controlo que o resolve.
        if na_janela:
            motivo = (f"None of the {len(na_janela)} days with news in this window match "
                      f"those filters.")
        else:
            motivo = (f"No captured news inside the window shown above — but there are "
                      f"{len(todas)} days of it for {ticker}. Widen the range to see them.")
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">{motivo}</span>',
                    unsafe_allow_html=True)
        return

    cabecalho = ('<div class="trow thead">'
                 '<span class="label" style="width:78px">DATE</span>'
                 '<span class="label" style="flex:1">HEADLINE</span>'
                 '<span class="label" style="width:82px">+1D</span>'
                 '<span class="label" style="width:82px">+5D</span></div>')
    linhas = []
    for n in fatia:
        titulo = (n["headline"] or "")[:110]
        extra = (f'<span style="color:{T.FG_MUTE}"> +{n["n"] - 1} more</span>'
                 if n.get("n", 1) > 1 else "")
        linhas.append(
            f'<div class="trow">'
            f'<span class="num" style="width:78px;font-size:12px;color:{T.FG_MUTE}">'
            f'{n["date"]}</span>'
            f'<span class="tcell">{titulo}{extra}</span>'
            f'<span style="width:82px">{_impact_bar(n["d1"])}</span>'
            f'<span style="width:82px">{_impact_bar(n["d5"])}</span></div>')
    st.markdown(cabecalho + "".join(linhas), unsafe_allow_html=True)
    _pager(chave, n_pages, pagina, len(filtradas), "days with news")


def _alert_feed(ticker: str, janela: tuple[str, str] | None = None) -> None:
    """O que o canal enviou sobre esta empresa. Texto, mas fora do caminho principal.

    Ganhou os mesmos filtros da tabela de eventos, e pela mesma razão: há tickers com
    dezenas de alertas e mostrar sempre os seis mais recentes torna os outros invisíveis.
    A procura corre sobre o texto **inteiro** do alerta e não só sobre a primeira linha —
    quem procura "sector" quer os alertas que falam de setor, e essa palavra vive no corpo.
    """
    from app.tables import filter_events, paginate

    todos = [{"date": getattr(e, "date", ""), "obj": e,
              "text": (getattr(e, "text", "") or "").strip()}
             for e in _alerts() if getattr(e, "ticker", None) == ticker]
    dentro = [r for r in todos
              if not janela or (janela[0] <= str(r["date"]) <= janela[1])]

    st.markdown(f'<div class="label">ALERTS SENT &middot; {len(todos)} all time</div>',
                unsafe_allow_html=True)
    if not todos:
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">'
                    f'Nothing passed every gate for this company yet — the chart still shows '
                    f'what the method detected.</span>', unsafe_allow_html=True)
        return

    q = st.text_input("Search alert text", key=f"aq_{ticker}",
                      placeholder="e.g. sector, volume, precedent")
    filtrados = sorted(filter_events(dentro, query=q, text_key="text"),
                       key=lambda r: str(r["date"]), reverse=True)

    chave = f"alerts_{ticker}"
    pagina = _page_state(chave, (q, janela))
    fatia, pagina, n_pages = paginate(filtrados, pagina, PER_PAGE)

    if not filtrados:
        motivo = ("No alerts inside the window shown above." if not dentro else
                  f"None of the {len(dentro)} alerts in this window match that search.")
        st.markdown(f'<span style="color:{T.FG_DIM};font-size:13px">{motivo}</span>',
                    unsafe_allow_html=True)
        return

    for r in fatia:
        e, texto = r["obj"], r["text"]
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
    _pager(chave, n_pages, pagina, len(filtrados), "alerts in this window")


# ══ Página do método ═════════════════════════════════════════════════════════════════

@st.cache_data(ttl=900, show_spinner=False)
def _live_health() -> dict | None:
    """A prova de vida: o mecanismo medido **fora da amostra**, sobre decisões reais.

    Vem do `live_monitoring.md`, que o `post_validate.py` regenera ao fecho a partir das
    decisões que o runner registou e que já maturaram. É o número mais honesto do projecto
    inteiro, porque não foi escolhido por ninguém: é o que aconteceu.
    """
    import urllib.request

    from investigator.evaluation.monitoring import parse_live_monitoring

    md = None
    local = _ROOT / "docs" / "evaluation" / "live_monitoring.md"
    if local.exists():
        md = local.read_text(encoding="utf-8")
    else:
        try:
            with urllib.request.urlopen(_raw("live_monitoring.md"), timeout=15) as r:
                md = r.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            return None
    h = parse_live_monitoring(md)
    return None if h is None else {"kept": h.kept_precision, "base": h.base_rate,
                                   "lift": h.lift_points}


def _latency() -> str | None:
    """Mediana facto→entrega, e **só quando foi medida** (critério R3).

    O histórico antigo não tem carimbos de tempo. Nesses casos não se mostra nada — nunca
    se inventa uma latência plausível para preencher o espaço.
    """
    try:
        valores = sorted(x for x in (e.latency_seconds() for e in _alerts()) if x is not None)
        if not valores:
            return None
        m = valores[len(valores) // 2]
        return (f"{m / 60:.0f} min" if m >= 90 else f"{m:.0f} s") + f" (n={len(valores)})"
    except Exception:  # noqa: BLE001
        return None


def _num_table(titulo: str, numeros, legenda: str = "") -> None:
    from app.method import Number  # noqa: F401  (só para o tipo ser legível aqui)

    linhas = "".join(
        f'<div class="trow">'
        f'<span class="tcell" style="white-space:normal">{n.label}'
        + (f'<div style="color:{T.FG_MUTE};font-size:11.5px">{n.note}</div>'
           if n.note else "")
        + f'</span>'
        f'<span class="num" style="width:72px;text-align:right;font-size:14px;'
        f'color:{T.FG}">{n.value}</span></div>'
        for n in numeros)
    st.markdown('<div class="mcol">'
                + (f'<div class="label" style="margin-top:0.2rem">{titulo}</div>'
                   if titulo else "")
                + (f'<div style="font-size:12.5px;color:{T.FG_DIM};margin:0.15rem 0 0.3rem">'
                   f'{legenda}</div>' if legenda else "")
                + linhas + "</div>", unsafe_allow_html=True)


def _method_page() -> None:
    """A avaliação inteira, numa página, alcançável por um link (critério V7).

    Vive **fora** da grelha e do detalhe de propósito. Quem abre o painel quer saber o que
    aconteceu às suas empresas; quem quer saber se pode confiar no método faz uma pergunta
    diferente, e merece uma página inteira em vez de ressalvas espalhadas pelas outras.
    """
    from app.method import ANOMALY, RETRIEVAL, TRIAGE, TRIAGE_BUDGET, TRIAGE_VERDICT
    from app.verdict import FLAG_EXPLAINER

    st.markdown(
        f'<a class="back" href="?" target="_self">← All companies</a>'
        f'<div style="height:1px;background:{T.LINE};margin:0.15rem 0 0.7rem"></div>'
        f'<div style="font-size:19px;font-weight:700;color:{T.FG}">How this works, '
        f'and how well</div>'
        f'<div style="font-size:13px;color:{T.FG_DIM};margin:0.25rem 0 0.2rem;'
        f'max-width:74ch">Every number on the other pages is produced by the procedure '
        f'below. The results are from the dissertation and are reported as they fell, '
        f'including where the method lost.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)

    # ── prova de vida: o que aconteceu de facto, fora da amostra
    st.markdown('<div class="label">RUNNING SYSTEM</div>', unsafe_allow_html=True)
    saude, lat = _live_health(), _latency()
    cartoes = []
    if saude:
        cartoes.append(("Kept decisions that proved right", f"{saude['kept']:.3f}",
                        f"against {saude['base']:.3f} if it had kept everything"))
    if lat:
        cartoes.append(("Median time from event to delivery", lat, "measured, not estimated"))
    cartoes.append(("Alerts actually sent to the channel", f"{len(_alerts())}", "all time"))
    st.markdown(
        '<div style="display:flex;gap:1.6rem;flex-wrap:wrap;margin:0.35rem 0 0.2rem">'
        + "".join(
            f'<div><div class="num" style="font-size:22px;color:{T.UP};font-weight:700">'
            f'{v}</div>'
            f'<div style="font-size:12px;color:{T.FG_DIM}">{k}</div>'
            f'<div style="font-size:11.5px;color:{T.FG_MUTE}">{sub}</div></div>'
            for k, v, sub in cartoes)
        + "</div>", unsafe_allow_html=True)
    if not saude:
        st.markdown(f'<span style="color:{T.FG_MUTE};font-size:12px">Live post-validation '
                    f'not available right now.</span>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)

    # ── a regra do alerta: o que saiu do balão de ajuda em B, agora com casa própria
    st.markdown(
        f'<div class="label">WHEN A DAY IS FLAGGED</div>'
        f'<div style="font-size:13px;color:{T.FG_DIM};margin:0.2rem 0;max-width:74ch">'
        f'{FLAG_EXPLAINER}</div>'
        f'<div style="font-size:12.5px;color:{T.FG_MUTE};max-width:74ch">'
        f'Precisely: the day\'s log return is compared with the mean and standard deviation '
        f'of the <b>{WINDOW}</b> trading days before it — never including the day itself — '
        f'and it is flagged when that distance exceeds <b>{THRESHOLD}</b> standard '
        f'deviations. The dissertation evaluates the rule at 3.0; the deployed threshold is '
        f'lower on purpose, and the alert text carries the severity so a 1.6 never reads '
        f'like a 3.2.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _num_table("FINDING PRECEDENTS · precision@5", RETRIEVAL,
               "Of the five cases retrieved for a headline, how many were genuinely "
               "comparable. Higher is better.")

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _num_table("DETECTING UNUSUAL DAYS · spread in firing rate", ANOMALY,
               "How much the firing rate varies from company to company. Here <b>lower is "
               "better</b>: it means the same rule treats a calm stock and a volatile one "
               "alike.")

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    _num_table("DECIDING WHAT DESERVES AN ALERT · PR-AUC", TRIAGE,
               "Whether reading the headline text helps decide if a day matters.")
    st.markdown(
        f'<div style="font-size:13px;color:{T.FLAG};margin:0.5rem 0 0.4rem;max-width:74ch">'
        f'{TRIAGE_VERDICT}</div>', unsafe_allow_html=True)
    _num_table("", TRIAGE_BUDGET)

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="label">WHAT THIS DELIBERATELY DOES NOT DO</div>'
        f'<div style="font-size:13px;color:{T.FG_DIM};margin-top:0.25rem;max-width:74ch;'
        f'line-height:1.6">'
        f'· No price targets, no buy or sell calls, and nothing about what happens next.<br>'
        f'· No converting a z-score into a probability — that would assume a bell curve, '
        f'and market returns have far fatter tails than one. The rarity is counted from the '
        f'data instead.<br>'
        f'· No combined "confidence score" across signals, and no event-type badges: both '
        f'were built and measured, and the measurements did not support showing them.<br>'
        f'· No average outcome as a headline number, because an average over cases that went '
        f'+4% and −8% describes something that happened to nobody.</div>',
        unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:1.2rem"><a class="back" href="?" target="_self">'
        '← All companies</a></div>', unsafe_allow_html=True)


# ══ Página ═══════════════════════════════════════════════════════════════════════════

@st.fragment(run_every=60)
def _grid_live() -> None:
    """A grelha, a repintar-se sozinha de 60 em 60 segundos.

    O produto está num dyno sempre ligado com um ciclo de 60 s justamente para os dados
    serem frescos; um painel que só actualiza quando alguém carrega em F5 desperdiça isso.
    `st.fragment` repinta **só este bloco**, e as caches (`ttl` de 120-300 s) absorvem a
    maior parte dos ciclos, por isso o custo por repintura é quase todo local.
    """
    linhas = [s for s in (_snapshot(t) for t in _watchlist()) if s]
    if linhas:
        _grid_view(linhas)


def _grid_view(linhas: list[dict]) -> None:
    """A grelha: as dez empresas ao mesmo nível, nenhuma privilegiada ao abrir (V1).

    A ordenação é por **raridade**, não por |z|. Parece a mesma coisa e não é: o cartão
    afirma "6 dos últimos 249 dias", portanto a ordem tem de ser essa, senão a página
    contradiz-se — o primeiro cartão diria um número maior do que o segundo enquanto
    estivesse mais abaixo.
    """
    from app.verdict import card_html, gloss_z, sparkline_svg

    aberto, _ = _market_state()

    def chave(r: dict) -> tuple:
        exc = _rarity(r["ticker"])
        # Sem contagem, cai para |z| — é melhor do que uma ordem arbitrária.
        return (not r["flagged"], exc.count if exc else 10_000, -abs(r["z"]))

    cartoes = []
    for r in sorted(linhas, key=chave):
        t = r["ticker"]
        icone, cor = T.direction(r["move"])
        exc = _rarity(t)
        decomp = _decomposition(t) if r["flagged"] else None

        chips = []
        if r["flagged"]:
            chips.append(gloss_z(r["z"]))
            if r["vol_ratio"]:
                chips.append(f"{r['vol_ratio']:.1f}x usual volume")
            # A contagem de precedentes só se calcula para os cartões sinalizados (V6). Nos
            # calmos não é omissão por esquecimento: é o mesmo princípio do resto do cartão
            # calmo — sem nada a assinalar, não se gasta nem tinta nem uma consulta à base
            # de casos. Doze consultas a cada abertura da grelha custariam mais do que a
            # página inteira, e para nove delas ninguém tinha perguntado nada.
            # SEM contagem de precedentes aqui, e a razão está medida — ver a emenda V6′ em
            # `dashboard_acceptance.md`. Pôr o número no cartão obriga a carregar o modelo
            # semântico, a base de casos e a KB viva pela rede **na página de entrada**, e
            # media-se: a grelha a frio passava de 6,2 s para 13,7 s. Sete segundos e meio
            # para escrever "4 similar past cases" num chip, contra um critério (P1) que
            # pede menos de cinco no total. A lista continua a um clique, no detalhe, que é
            # onde ela é de facto útil.
            if any(getattr(e, "ticker", None) == t for e in _alerts()):
                chips.append(f"{T.ICON_ALERT} alert sent")

        cartoes.append(card_html(
            ticker=t, name=NAMES.get(t, t), move=r["move"], icone=icone, cor=cor,
            frase=_verdict_de(NAMES.get(t, t), exc, decomp, r["flagged"], aberto),
            flagged=r["flagged"], chips=chips, logo=_logo_html(t, 18),
            spark=sparkline_svg(_daily(t)["Close"].tail(30), cor) if r["flagged"] else "",
        ))

    st.markdown(f'<div class="grid">{"".join(cartoes)}</div>', unsafe_allow_html=True)


def _verdict_de(nome: str, exc, decomp, flagged: bool, aberto: bool) -> str:
    from app.verdict import verdict
    return verdict(nome, exc, decomp, flagged, aberto)


def main() -> None:
    st.markdown(T.css() + T.card_css(), unsafe_allow_html=True)

    linhas = [s for s in (_snapshot(t) for t in _watchlist()) if s]
    if not linhas:
        st.markdown('<div class="panel">No market data available right now.</div>',
                    unsafe_allow_html=True)
        return

    _header(linhas, len(_alerts()))

    # A avaliação vive numa página **própria**, alcançável por um link e ausente da grelha
    # e do detalhe (critério V7). É também a casa dos números que saíram do balão de ajuda
    # do cabeçalho: o limiar e a janela deixaram de ser explicação a quem não perguntou, e
    # passaram a estar aqui, a um clique, para quem perguntar.
    if st.query_params.get("view") == "method":
        _method_page()
        return

    # O estado da página vive no URL, não em `session_state`: `?t=NVDA` é partilhável, o
    # botão "voltar" do browser funciona, e um cartão pode ser uma âncora em vez de um
    # botão com um bloco desenhado por baixo (que foi o que na v2 duplicou a altura).
    escolhido = st.query_params.get("t")
    validos = {r["ticker"] for r in linhas}
    if escolhido in validos:
        # O regresso vive **antes** do que ele fecha. Estava no fim da página, ou seja
        # depois do gráfico, da decomposição, da tabela de notícias e da lista de alertas
        # — para voltar atrás era preciso primeiro percorrer tudo aquilo de que se queria
        # sair. Um controlo de voltar pertence ao canto superior esquerdo, que é onde
        # todos os outros o puseram e onde o olho já o procura.
        st.markdown(
            f'<a class="back" href="?" target="_self">← All companies</a>'
            f'<div style="height:1px;background:{T.LINE};margin:0.15rem 0 0.55rem"></div>',
            unsafe_allow_html=True)
        _detail(escolhido)
    else:
        _grid_live()

    st.markdown(
        f'<div style="margin-top:1.6rem;padding-top:0.7rem;border-top:1px solid {T.LINE};'
        f'font-size:11.5px;color:{T.FG_MUTE};line-height:1.55">'
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
