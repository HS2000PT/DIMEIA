"""Projeção de leitura do painel: as notícias, sem carregar vetores no processo web.

Não calcula impactos nem semelhanças. Conserva os valores observados e agrupa pelo mesmo
dia que a interface usa. O corpus de investigação permanece intacto.
"""

from __future__ import annotations

import json
from collections.abc import Iterable


def news_projection(lines: Iterable[str], limit: int = 400) -> dict[str, list[dict]]:
    days: dict[str, dict[str, dict]] = {}
    seen: set[tuple] = set()
    for line in lines:
        if not line.strip():
            continue
        r = json.loads(line)  # ficheiro corrompido: não substituir a projeção válida
        ticker, day, headline = r.get("ticker"), r.get("date"), r.get("headline")
        if not ticker or not day or not headline:
            continue
        key = (ticker, day, headline)
        if key in seen:
            continue
        seen.add(key)
        by_day = days.setdefault(ticker, {})
        if day in by_day:
            by_day[day]["n"] += 1
            if len(by_day[day]["others"]) < 5:
                by_day[day]["others"].append(headline)
            continue
        impacts = r.get("impacts") or {}
        by_day[day] = {
            "date": day, "headline": headline, "source": r.get("source", ""),
            "url": r.get("url", ""),
            "published_at": r.get("published_at") or r.get("event_at") or "",
            "d1": impacts.get("1"), "d5": impacts.get("5"), "n": 1, "others": [],
        }
    return {t: sorted(rows.values(), key=lambda r: r["date"], reverse=True)[:limit]
            for t, rows in days.items()}
