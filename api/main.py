"""API do InvestiGator — o processo web deixa de renderizar e passa a servir dados.

## O que mudou, e porquê é uma decisão de arquitectura e não de moda

O Streamlit **re-executa o script inteiro a cada interacção**, do lado do servidor. Trocar de
intervalo no gráfico, paginar uma tabela ou expandir um painel custa uma ida ao servidor e uma
repintura da página. O estudo de percursos mediu o efeito e escreveu a conclusão sem rodeios:
*"No CSS fixes this; a client-side interaction layer does."*

Aqui o servidor responde a pedidos e o cliente guarda o estado. Trocar de intervalo passa a
ser um recorte de um vector que já está no browser: sem rede, sem repintura, sem salto.

## A regra que mantém isto honesto

Nenhum número é calculado neste ficheiro. Todos os caminhos chamam `investigator/…` — os
mesmos motores que a avaliação da tese usa e que o worker corre de 60 em 60 segundos. Se a API
recalculasse fosse o que fosse, o produto e a avaliação podiam divergir sem ninguém dar por
isso, que é a classe de defeito que este projecto já pagou em três sítios diferentes.

## Fail-open em toda a superfície

Cada rota devolve o que conseguir e diz o que falta. Uma API que devolve 500 porque o GitHub
está lento transforma uma indisponibilidade parcial numa página branca — e uma página branca é
indistinguível de um produto avariado.
"""

from __future__ import annotations

import pathlib
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from api import services as S

RAIZ = pathlib.Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"

app = FastAPI(
    title="InvestiGator API",
    description="Market intelligence: measured statistics, learned models, grounded generation.",
    version="5.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


# ── Dados ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict:
    snap = S.snapshot()
    return {"ok": True, "snapshot": bool(snap), "as_of": snap.get("as_of", ""),
            "age_s": snap.get("age_s"), "fresh": snap.get("fresh")}


def _decorate(rows: list[dict], market_open: bool) -> list[dict]:
    """Junta a cada linha o veredicto e o nome legível.

    ⚠️ **Calculado aqui e não no cliente, de propósito.** `app/verdict.py` tem 29 testes e
    resolve casos que não são óbvios: as duas réguas que discordam (a MSFT com +4,82% e z
    +1,11, "calma" pela norma recente e no top 2% do ano), a linha do motor que se cala
    quando o motor é a própria empresa, e um varrimento sobre 112 combinações contra 16
    palavras que impõe a proibição de prever.
    Reescrever isso em JavaScript criava uma segunda verdade que ninguém testaria, e as duas
    divergiriam na primeira alteração.
    """
    try:
        from app.verdict import verdict
        from investigator.anomaly_detector.frequency import Exceedance
        from investigator.news_fetcher.relevance import display_name
    except Exception:  # noqa: BLE001
        return rows

    out = []
    for r in rows:
        r = dict(r)
        name = display_name(r.get("ticker", ""))
        rar = r.get("rarity")
        exc = None
        if rar and rar.get("n") is not None and rar.get("move") is not None:
            # Sem `try` à volta da construção, e é deliberado. A primeira versão embrulhava
            # isto num `except` largo; `Exceedance` exige quatro campos, a construção com dois
            # levantava `TypeError`, o `except` transformava-o em `exc = None`, e o veredicto
            # caía no ramo "an ordinary day".
            #
            # O resultado medido: a AAPL a **-2,11%**, o 35.º maior movimento de 249 dias
            # (top 14%), descrita como "um dia normal". É EXACTAMENTE o defeito de honestidade
            # que a sessão 48 corrigiu na v3 — e voltou por uma porta diferente, escondido por
            # um `except` que tornava um erro de programação indistinguível de dados em falta.
            exc = Exceedance(move=float(rar["move"]), n=int(rar["n"]),
                             count=int(rar["count"]),
                             same_direction=int(rar.get("same_direction", 0)))
        r["name"] = name
        r["verdict"] = verdict(name, exc, r.get("decomp"), bool(r.get("flagged")),
                               market_open=market_open)
        out.append(r)
    return out


@app.get("/api/overview")
def overview() -> dict:
    """Tudo o que a primeira pintura precisa, num pedido. Sem rede por ticker."""
    snap = S.snapshot()
    mkt = S.market_state()
    rows = _decorate(snap.get("rows", []), bool(mkt.get("open")))
    alerts = S.alerts()
    today_alerts = [a for a in alerts if a.get("date", "")[:10] == (
        snap.get("as_of", "")[:10] or "___")]
    return {
        "as_of": snap.get("as_of", ""),
        "age_label": snap.get("age_label", ""),
        "age_s": snap.get("age_s"),
        "fresh": snap.get("fresh", False),
        "source": "snapshot(remote)" if snap.get("remote") else "snapshot(local)",
        "market": mkt,
        "watchlist": S.watchlist(),
        "rows": rows,
        "alerts_total": len(alerts),
        "alerts_today": len(today_alerts),
        "window": 20,
        "threshold": 1.5,
    }


@app.get("/api/asset/{ticker}")
def asset(ticker: str) -> dict:
    """O que é barato de um activo. O caro (precedentes, triagem) tem rota própria."""
    t = ticker.upper()
    snap = S.snapshot()
    row = next((r for r in snap.get("rows", []) if r.get("ticker") == t), None)
    if row is None:
        return JSONResponse({"error": f"{t} is not in the watchlist"}, status_code=404)

    news = S.news_days(t, limit=400)
    alerts = [a for a in S.alerts() if a.get("ticker") == t][:40]
    try:
        from investigator.news_fetcher.relevance import display_name, sector_etf
        name, sector = display_name(t), sector_etf(t)
    except Exception:  # noqa: BLE001
        name, sector = t, None
    return {
        "ticker": t, "name": name, "sector_etf": sector,
        "as_of": snap.get("as_of", ""),
        "move": row.get("move"), "z": row.get("z"), "flagged": row.get("flagged"),
        "rarity": row.get("rarity"), "decomp": row.get("decomp"),
        "vol_ratio": row.get("vol_ratio"),
        "closes": row.get("closes", []),
        "events": row.get("events", []),
        "news": news,
        "alerts": alerts,
    }


@app.get("/api/precedents/{ticker}")
def precedents(ticker: str, top_k: int = 4, q: str | None = None) -> dict:
    """A terceira pergunta da tese. Rota separada porque custa ~7 s a frio (modelo + KB)."""
    out = S.precedents(ticker, top_k=top_k, query=q)
    if out is None:
        return {"available": False,
                "reason": "no captured headline for this name, or the retrieval engine "
                          "is unavailable in this environment"}
    return {"available": True, **out}


@app.get("/api/triage/{ticker}")
def triage(ticker: str, headline: str = "") -> dict:
    out = S.triage_score(ticker, headline)
    if out is None:
        return {"available": False,
                "reason": "the trained model or the price history is unavailable here"}
    return {"available": True, **out}


@app.get("/api/logos")
def logos() -> dict:
    """Logótipos das empresas como `data:` URI, num pedido.

    Versionados em `app/assets/logos/` de propósito: a página desenha-os **sem chave, sem
    rede e sem limite de ritmo**, e o navegador não faz um único pedido a terceiros — que é a
    posição de privacidade que o resto do trabalho já defende. Um pedido para os doze em vez
    de doze pedidos: são ~40 KB no total e evitam doze idas ao servidor na primeira pintura.

    Degrada para as iniciais quando o ficheiro não existe (a XOM e a JNJ entraram na watchlist
    depois da recolha).
    """
    def _load():
        from investigator.branding.logos import cached_logo
        out: dict[str, str] = {}
        for t in S.watchlist():
            try:
                uri = cached_logo(t)
            except Exception:  # noqa: BLE001
                uri = None
            if uri:
                out[t] = uri
        return out
    return {"logos": S.cached("logos", 3600, _load)}


@app.get("/api/screener")
def screener() -> dict:
    """Porque é que o sistema ficou calado sobre cada nome. Com a margem que faltou."""
    return {"rows": S.screener()}


@app.get("/api/alerts")
def alerts() -> dict:
    return {"rows": S.alerts()[:200]}


@app.get("/api/method")
def method() -> dict:
    """Os números congelados da avaliação, cada um amarrado ao ficheiro que o produziu.

    Reutiliza `app/method.py`, onde cada `Number` guarda a cadeia exacta com que aparece no
    `.md` que o gerou — e `tests/test_method.py` abre esses ficheiros e exige-a. Se uma
    avaliação for recorrida, a suite parte, em vez de o produto continuar a afirmar um número
    que os documentos já não sustentam.
    """
    try:
        from app import method as M

        def pack(items) -> list[dict]:
            return [{"label": n.label, "value": n.value, "source": n.source,
                     "note": n.note} for n in items]

        return {
            "blocks": [
                {"key": "retrieval",
                 "title": "RQ2 — finding analogous past cases",
                 "metric": "precision@5 (higher is better)",
                 "numbers": pack(M.RETRIEVAL)},
                {"key": "anomaly",
                 "title": "RQ1 — detecting unusual moves",
                 "metric": "spread in firing rate across companies (lower is better)",
                 "numbers": pack(M.ANOMALY)},
                {"key": "triage",
                 "title": "RQ4 — deciding what deserves an alert",
                 "metric": "PR-AUC (higher is better)",
                 "numbers": pack(M.TRIAGE),
                 "verdict": M.TRIAGE_VERDICT},
            ],
        }
    except Exception as e:  # noqa: BLE001
        return {"blocks": [], "error": f"{type(e).__name__}: {e}"}


# ── Inteligência ──────────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    scope: str = Field("market", pattern="^(market|asset)$")
    ticker: str | None = None


def _bundle_for(scope: str, ticker: str | None, wants: list[str] | None = None):
    """Monta o pacote de evidência. Único sítio — o relatório e o analista têm de ver
    exactamente a mesma evidência, senão respondiam de maneira diferente à mesma pergunta."""
    from investigator.intelligence.context import build_asset_bundle, build_market_bundle

    snap = S.snapshot()
    rows = snap.get("rows", [])
    as_of = snap.get("as_of", "")
    if scope == "market" or not ticker:
        return build_market_bundle(rows, as_of)

    t = ticker.upper()
    row = next((r for r in rows if r.get("ticker") == t), None) or {"ticker": t}
    w = set(wants or ["move", "attribution", "news", "precedents"])

    heads = S.news_days(t, limit=4) if ("news" in w or "precedents" in w) else []
    prec = None
    if "precedents" in w and heads:
        p = S.precedents(t, top_k=4)
        prec = p.get("cases") if p else None
    tri = None
    if "triage" in w or "precedents" in w:
        tri = S.triage_score(t, heads[0]["headline"] if heads else "")
    gate = None
    if "gate" in w:
        hit = next((g for g in S.screener() if g["ticker"] == t), None)
        if hit:
            gate = {"reason": hit["stage"].replace("_", " "), "margin": hit["detail"],
                    "stage": hit["stage"]}

    spy = next((r for r in rows if r.get("ticker") == "SPY"), None)
    return build_asset_bundle(row, as_of, headlines=heads, precedents=prec,
                              triage=tri, gate=gate, market_row=spy)


@app.post("/api/report")
def report(req: ReportRequest) -> dict:
    """Relatório de situação generativo, ancorado no pacote de evidência.

    Nunca falha: sem LLM ou com a guarda a rejeitar, sai a composição determinística e o
    campo `source` di-lo. O produto **mostra** essa distinção — um texto gerado e um texto
    composto não valem o mesmo, e o utilizador tem direito a saber qual está a ler.
    """
    from investigator.intelligence.report import generate_report

    bundle = _bundle_for(req.scope, req.ticker)
    return generate_report(bundle).to_json()


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    context: dict[str, Any] = Field(default_factory=dict)


@app.post("/api/ask")
def ask(req: AskRequest) -> dict:
    """Analista conversacional: pergunta -> plano -> evidência -> resposta ancorada.

    A resposta traz `plan.action`, que a interface executa. É isso que faz da linguagem
    natural uma **segunda interface para os mesmos dados** em vez de uma caixa de texto ao
    lado do produto.
    """
    from investigator.intelligence import analyst

    tickers = S.watchlist()
    plan = analyst.route(req.question, tickers, req.context)
    bundle = _bundle_for(plan.scope, plan.ticker, plan.wants)
    return analyst.ask(req.question, bundle, plan).to_json()


@app.get("/api/evidence")
def evidence(scope: str = "market", ticker: str | None = None) -> dict:
    """O pacote de evidência em bruto — o que o gerador viu, sem o gerador.

    Existe para a afirmação "cada frase é rastreável" ser **verificável por quem duvida**, e
    não só demonstrável por quem construiu.
    """
    return _bundle_for(scope, ticker).to_json()


# ── Estáticos ─────────────────────────────────────────────────────────────────

if WEB.exists():
    app.mount("/assets", StaticFiles(directory=str(WEB / "assets")), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB / "index.html")

    @app.get("/{path:path}")
    def spa(path: str):
        """Qualquer caminho serve o SPA — o cliente resolve a rota.

        Ficheiros reais servem-se; o resto cai no `index.html` para que `?t=NVDA` e as URLs
        profundas funcionem com o botão "voltar" do browser, que é o que faz um produto web
        parecer um produto web.
        """
        f = WEB / path
        if f.is_file():
            return FileResponse(f)
        return FileResponse(WEB / "index.html")
