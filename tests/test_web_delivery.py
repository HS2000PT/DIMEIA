"""Contratos da leitura leve, paginação e tolerância a falhas do painel."""
import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from api import main as M
from api import services as S
from investigator.web_projection import news_projection


@pytest.fixture
def cache(monkeypatch):
    monkeypatch.setattr(S, "_CACHE", {})
    monkeypatch.setattr(S, "_FAILURES", {})
    monkeypatch.setattr(S, "_KEY_LOCKS", {})


def test_concurrent_reads_load_once(cache):
    entered, release = threading.Event(), threading.Event()
    calls = []

    def read():
        calls.append(1)
        entered.set()
        assert release.wait(3)
        return [42]

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(S.cached, "same", 60, read) for _ in range(5)]
        assert entered.wait(3)
        # A fonte lenta não impede fontes independentes.
        assert S.cached("other", 60, lambda: "ready") == "ready"
        release.set()
        assert [f.result() for f in futures] == [[42]] * 5
    assert len(calls) == 1


def test_failure_retains_data_and_recovers(cache, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(S.time, "monotonic", lambda: clock[0])
    assert S.cached("data", 30, lambda: [1]) == [1]
    clock[0] += 31

    def fail():
        raise OSError("offline")

    assert S.cached("data", 30, fail) == [1]
    assert "data" in S._FAILURES
    assert S.cached("data", 30, lambda: [2]) == [1]
    clock[0] += 16
    assert S.cached("data", 30, lambda: [2]) == [2]
    assert "data" not in S._FAILURES


def test_no_prior_data_is_503_not_empty_success(cache, monkeypatch):
    def fail():
        raise S.DataUnavailable("news")

    monkeypatch.setattr(S, "watchlist", lambda: ["AAPL"])
    monkeypatch.setattr(S, "news_days", lambda _: fail())
    response = TestClient(M.app).get("/api/news/AAPL")
    assert response.status_code == 503
    assert response.headers["retry-after"] == "15"


def test_overview_and_asset_do_not_wait_for_news_or_alerts(monkeypatch):
    def expensive():
        pytest.fail("initial price route requested an independent source")

    row = {"ticker": "AAPL", "closes": [["2026-09-08", 100]],
           "intraday": [[1, 100]], "events": [["2026-09-08", 2, 1]],
           "move": 0.01, "z": 2, "flagged": True}
    monkeypatch.setattr(S, "snapshot", lambda: {"rows": [row]})
    monkeypatch.setattr(S, "watchlist", lambda: ["AAPL"])
    monkeypatch.setattr(S, "market_state", lambda: {})
    monkeypatch.setattr(S, "alerts", expensive)
    monkeypatch.setattr(S, "news_days", lambda _: expensive())
    client = TestClient(M.app)
    brief = client.get("/api/overview").json()["rows"][0]
    assert not {"closes", "intraday", "events"} & brief.keys()
    assert brief["price_day"] == "2026-09-08"
    asset = client.get("/api/asset/AAPL").json()
    assert asset["closes"] == row["closes"]
    assert not {"news", "alerts"} & asset.keys()


def test_cursor_traverses_all_rows_when_new_messages_arrive(monkeypatch):
    rows = [{"ticker": "AAPL", "date": "2026-09-08", "text": str(i)} for i in range(31)]
    monkeypatch.setattr(S, "alerts", lambda: rows)
    client = TestClient(M.app)
    page = client.get("/api/alerts?limit=12&ticker=AAPL").json()
    seen = page["rows"]
    assert page["remaining"] == 19
    rows.append({"ticker": "AAPL", "date": "2026-09-09", "text": "new"})
    while page["next_before"]:
        page = client.get("/api/alerts", params={"limit": 12, "ticker": "AAPL",
                                              "before": page["next_before"]}).json()
        seen = page["rows"] + seen
    assert [r["text"] for r in seen] == [str(i) for i in range(31)]
    assert client.get("/api/alerts?before=invalid").status_code == 409
    assert client.get("/api/alerts?limit=201").status_code == 422


def test_projection_preserves_units_and_deduplicates():
    row = {"ticker": "AAPL", "date": "2026-09-08", "headline": "One", "url": "https://example.com",
           "impacts": {"1": 0.0123, "5": -0.0456}, "embedding": [1, 2, 3]}
    result = news_projection([json.dumps(row), json.dumps(row),
                              json.dumps({**row, "headline": "Two"})])
    day = result["AAPL"][0]
    assert day["d1"] == 0.0123 and day["d5"] == -0.0456
    assert day["url"] == row["url"]
    assert day["n"] == 2 and day["others"] == ["Two"]
    assert "embedding" not in json.dumps(result)
    with pytest.raises(ValueError):
        news_projection([json.dumps(row), "corrupt"])


def test_screener_does_not_drop_late_decisions(cache, monkeypatch):
    monkeypatch.delenv("INVESTIGATOR_OFFLINE", raising=False)
    row = {"date": "2026-09-08", "ticker": "AAPL", "stage": "weak_precedent", "detail": "early"}
    lines = [json.dumps(row)] * 600 + [json.dumps({**row, "stage": "alerted", "detail": "late"})]
    monkeypatch.setattr(S, "_get_json_lines", lambda *a: lines)
    assert {r["stage"] for r in S.screener()} == {"weak_precedent", "alerted"}
    assert len(S.screener()) == 2


def test_news_uses_projection_only(cache, monkeypatch):
    from io import BytesIO

    monkeypatch.delenv("INVESTIGATOR_OFFLINE", raising=False)
    requested = []

    def read(url, **kw):
        requested.append(url)
        return BytesIO(b'{"by_ticker":{"AAPL":[]}}')

    monkeypatch.setattr(S.urllib.request, "urlopen", read)
    assert S.news_days("AAPL") == []
    assert requested == [S.raw_url("dashboard_news.json")]


def test_static_compression_and_no_mascot():
    client = TestClient(M.app)
    r = client.get("/assets/dashboard.js", headers={"Accept-Encoding": "gzip"})
    assert r.headers["content-encoding"] == "gzip"
    assert "max-age=" in r.headers["cache-control"]
    assert not list((M.WEB / "assets").glob("mascote*"))
    for file in (M.WEB / "index.html", M.WEB / "assets/dashboard.js",
                 M.WEB / "assets/dashboard.css"):
        assert "mascote" not in file.read_text(encoding="utf-8").lower()


def test_projection_publish_failure_retries_and_success_is_throttled(monkeypatch, tmp_path):
    from investigator import history_publish
    from scripts import run_alerts as runner

    live = tmp_path / "live.jsonl"
    live.write_text(json.dumps({"ticker": "AAPL", "date": "2026-09-08",
                                "headline": "Recorded headline"}), encoding="utf-8")
    monkeypatch.setattr(runner, "_LIVE_KB", live)
    monkeypatch.setattr(runner, "_BACKFILL_META", tmp_path / "missing.jsonl")
    monkeypatch.setattr(runner, "_NEWS_PROJECTION_AT", None)
    calls = []

    def publish(*args):
        calls.append(1)
        return "failure" if len(calls) == 1 else "[instantaneo-api] publicado dashboard_news.json"

    monkeypatch.setattr(history_publish, "publish_blob", publish)
    runner._write_news_projection_safe()
    assert runner._NEWS_PROJECTION_AT is None
    runner._write_news_projection_safe()
    assert runner._NEWS_PROJECTION_AT is not None
    runner._write_news_projection_safe()
    assert len(calls) == 2
