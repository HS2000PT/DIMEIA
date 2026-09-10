"""Leituras do painel: snapshot, histórico, decisões e projeção de notícias.

O worker calcula; este processo serve valores existentes. Cache por fonte, exclusão
por chave, retenção do último valor válido e erro explícito se nunca houve leitura.
Os motores de IA vivem em investigator e não são carregados por pedidos desta API.
"""

from __future__ import annotations

import json
import os
import pathlib
import threading
import time
import urllib.request
from datetime import UTC, datetime
from typing import Any

RAIZ = pathlib.Path(__file__).resolve().parents[1]
HISTORY_BRANCH = os.getenv("INVESTIGATOR_HISTORY_BRANCH", "alerts-history")
BACKFILL = RAIZ / "data" / "samples" / "backfill_kb_meta.jsonl"


def raw_url(path: str) -> str:
    repo = os.getenv("INVESTIGATOR_HISTORY_REPO", "HS2000PT/DIMEIA")
    return f"https://raw.githubusercontent.com/{repo}/{HISTORY_BRANCH}/{path}"


# ── Cache com TTL (sem framework) ─────────────────────────────────────────────
_CACHE: dict[str, tuple[float, Any]] = {}
_LOCK = threading.Lock()


_KEY_LOCKS: dict[str, threading.Lock] = {}
_FAILURES: dict[str, float] = {}


class DataUnavailable(RuntimeError):
    """A fonte não respondeu; não é uma coleção vazia."""


def cached(key: str, ttl: float, fn):
    """Uma carga por chave; fontes independentes continuam em paralelo.

    Em falha conserva o último valor válido e tenta novamente após 15 s. A idade do
    snapshot é calculada fora desta cache, para os dados antigos nunca parecerem frescos.
    """
    with _LOCK:
        lock = _KEY_LOCKS.setdefault(key, threading.Lock())
    with lock:
        now = time.monotonic()
        hit = _CACHE.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
        if now - _FAILURES.get(key, -float("inf")) < 15:
            if hit:
                return hit[1]
            raise DataUnavailable(key)
        try:
            value = fn()
        except Exception as exc:
            _FAILURES[key] = now
            if hit:
                return hit[1]
            raise DataUnavailable(key) from exc
        _CACHE[key] = (time.monotonic(), value)
        _FAILURES.pop(key, None)
        return value


def _get_json_lines(url: str, timeout: float = 12.0) -> list[str]:
    with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310
        return r.read().decode("utf-8").splitlines()


# ── Watchlist e instantâneo ───────────────────────────────────────────────────

def watchlist() -> list[str]:
    def _load():
        try:
            import yaml
            cfg = yaml.safe_load((RAIZ / "config" / "alerts.yaml").read_text("utf-8")) or {}
            return list(cfg.get("market", {}).get("tickers") or [])
        except Exception:  # noqa: BLE001
            return []
    return cached("watchlist", 300, _load)


def snapshot() -> dict:
    """Lê o instantâneo e calcula a idade em cada pedido, mesmo com cache."""
    from app.snapshot_io import Instantaneo, carregar

    def _load():
        snap = carregar()
        if snap is None:
            raise DataUnavailable("snapshot")
        return snap

    try:
        saved = cached("snapshot", 30, _load)
    except DataUnavailable:
        return {}
    age = max(0.0, (datetime.now(UTC) - saved.gerado_em).total_seconds())
    snap = Instantaneo(saved.linhas, saved.gerado_em, age, saved.remoto, saved.extra)
    return {**snap.extra, "rows": snap.linhas,
            "as_of": snap.gerado_em.isoformat(timespec="seconds"),
            "age_s": round(age, 1), "age_label": snap.idade_legivel,
            "fresh": snap.fresco, "remote": snap.remoto}


def market_state() -> dict:
    """Aberto/fechado + quanto falta para mudar.

    O `detail` ("opens Mon 09:30 EDT") não é decoração: o estudo de percursos registou uma
    pessoa a ler o fecho de ontem como o preço de agora, às 08:02, com o mercado fechado e
    nada no ecrã a dizê-lo. Um painel que mostra números de ontem sem dizer que são de ontem
    está a mentir por omissão.
    """
    def _load():
        try:
            from investigator.market_data.market_hours import us_market_status
            st = us_market_status()
            return {"open": bool(st.is_open), "label": st.label, "detail": st.detail,
                    "minutes_to_change": int(st.minutes_to_change)}
        except Exception:  # noqa: BLE001
            return {"open": False, "label": "unknown", "detail": ""}
    return cached("market_state", 60, _load)


# ── Notícias captadas ─────────────────────────────────────────────────────────

def news_by_ticker() -> dict[str, list[dict]]:
    """Lê exclusivamente a projeção sem embeddings, criada pelo worker.

    Não há fallback remoto para a base de IA: voltaria a pôr 42 MB no pedido do leitor.
    Sem projeção em produção, a rota devolve indisponibilidade e a página permite repetir.
    """
    def _load():
        if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
            from investigator.web_projection import news_projection

            if BACKFILL.exists():
                with BACKFILL.open(encoding="utf-8") as f:
                    return news_projection(f)
            return {}
        with urllib.request.urlopen(raw_url("dashboard_news.json"), timeout=12) as r:  # noqa: S310
            payload = json.load(r)
        if not isinstance(payload.get("by_ticker"), dict):
            raise DataUnavailable("news projection")
        return payload["by_ticker"]
    return cached("news_by_ticker", 900, _load)


def news_days(ticker: str, limit: int = 400) -> list[dict]:
    return news_by_ticker().get(ticker.upper(), [])[:limit]


# ── Alertas enviados e funil de gates ─────────────────────────────────────────

def _chave(h) -> str:
    """A chave de um alerta a partir de (ticker, texto sem tags), igual à do `news_key`."""
    import hashlib

    try:
        from investigator.explanation_engine.explainer import plain_text

        texto = plain_text(getattr(h, "text", "") or "")
    except Exception:  # noqa: BLE001
        texto = getattr(h, "text", "") or ""
    return hashlib.sha1(
        f"{getattr(h, 'ticker', '')}|{texto}".encode()).hexdigest()[:12]


def alerts() -> list[dict]:
    def _load():
        if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
            return []
        from investigator.alerts_history import parse_jsonl_lines

        hist = parse_jsonl_lines(_get_json_lines(raw_url("alerts_history.jsonl")))
        out = []
        for h in hist:
            out.append({
                "date": getattr(h, "date", ""),
                "ticker": getattr(h, "ticker", ""),
                "kind": getattr(h, "kind", ""),
                "text": getattr(h, "text", ""),
                "event_at": getattr(h, "event_at", "") or "",
                "sent_at": getattr(h, "sent_at", "") or "",
                # ⚠️ A CHAVE, que é o que liga um alerta aos votos que recebeu. Sem ela o painel
                # mostra os votos como zero e ninguém percebe porquê: a chave existe no registo,
                # e era este dicionário que a deitava fora.
                # Recalculada quando o campo está vazio — só os alertas de NOTÍCIA a trazem
                # gravada, e os botões vão em todos. É a mesma correção que a regra 6 da análise
                # da dissertação levou.
                "key": getattr(h, "key", "") or _chave(h),
            })
        return out
    return cached("alerts", 60, _load)


def screener() -> list[dict]:
    """Cada nome que a varredura olhou e o portão que o parou, com a MARGEM que faltou.

    Nenhum produto comercial mostra o que descartou. O silêncio é uma decisão deste sistema,
    e uma decisão tem de ser inspeccionável — é a mesma ideia do "porque é que esta mensagem
    está no spam?" do Gmail, aplicada a alertas financeiros.
    """
    def _load():
        if os.environ.get("INVESTIGATOR_OFFLINE") == "1":
            return []
        rows: list[dict] = []
        for line in _get_json_lines(raw_url("gate_log.jsonl"), 15):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            # `detail` é o campo que transforma uma contagem numa explicação: guarda o
            # número que justificou a paragem ("sim 0.31 < 0.45"). É a MARGEM, e é o que
            # nenhum produto comercial mostra.
            rows.append({
                "date": r.get("date", ""), "ticker": r.get("ticker", ""),
                "stage": r.get("stage", ""), "detail": r.get("detail", ""),
            })
        # Um registo por empresa/etapa no último dia disponível, escolhido do fim.
        # Cortar as primeiras 400 linhas de um dia perdia as decisões das horas seguintes.
        day = max((r["date"] for r in rows), default="")
        latest: dict[tuple, dict] = {}
        for row in reversed(rows):
            if row["date"] == day:
                latest.setdefault((row["ticker"], row["stage"]), row)
        return list(latest.values())
    return cached("screener", 120, _load)
