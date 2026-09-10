"""Pré-visualização local com dados reais capturados; não inicia o worker nem envia mensagens.

    python -m scripts.preview_web --data output/web_audit --port 8879

Lê overview.json (com séries), alerts.json, screener.json e feedback.json. Se existir,
dashboard_news.json é a projeção completa; senão usa as notícias capturadas por empresa.
Não escreve nas fontes operacionais. As alterações do frontend aparecem ao atualizar a página.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def create_preview(folder: Path):
    from fastapi.responses import HTMLResponse
    from fastapi.routing import APIRoute

    from api import main as M
    from api import services as S

    def read(name):
        return json.loads((folder / f"{name}.json").read_text(encoding="utf-8"))

    snapshot = read("overview")
    rows = snapshot.get("rows", [])
    if not rows or any("closes" not in row for row in rows):
        raise ValueError("O instantâneo de revisão tem de incluir as séries por empresa.")
    # Uma captura nunca se apresenta como monitorização em tempo real.
    snapshot = {**snapshot, "fresh": False, "age_label": "captured snapshot"}
    S.snapshot = lambda: snapshot
    S.watchlist = lambda: [r["ticker"] for r in rows]
    S.market_state = lambda: snapshot.get("market", {})
    messages = read("alerts_full" if (folder / "alerts_full.json").exists() else "alerts")["rows"]
    S.alerts = lambda: messages

    records = read("screener")["rows"]
    day = max((r["date"] for r in records), default="")
    latest = {}
    for record in reversed(records):
        if record["date"] == day:
            latest.setdefault((record["ticker"], record["stage"]), record)
    S.screener = lambda: list(latest.values())
    if (folder / "dashboard_news.json").exists():
        projection = read("dashboard_news")["by_ticker"]
    else:
        projection = {r["ticker"]: read(f"asset_{r['ticker']}").get("news", [])
                      for r in rows if (folder / f"asset_{r['ticker']}.json").exists()}
    S.news_days = lambda ticker, limit=400: projection.get(ticker.upper(), [])[:limit]
    feedback = read("feedback")
    M.app.router.routes.insert(0, APIRoute("/api/feedback", lambda: feedback))

    @M.app.middleware("http")
    async def review_label(request, call_next):
        if request.url.path == "/":
            html = (M.WEB / "index.html").read_text(encoding="utf-8")
            price_day = max((r.get("closes") or [[""]])[-1][0] for r in rows)
            banner = ('<p class="notice" style="margin:0 0 20px">Local review · captured '
                      f'market data through {price_day} · '
                      'no live monitoring or message sending.</p>')
            return HTMLResponse(html.replace("<main>", "<main>" + banner),
                                headers={"Cache-Control": "no-store"})
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    return M.app


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8879)
    args = parser.parse_args()
    uvicorn.run(create_preview(args.data.resolve()), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
