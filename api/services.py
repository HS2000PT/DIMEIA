"""Acesso a dados para a API — os mesmos motores, sem o Streamlit à volta.

## Porque é que este ficheiro existe em vez de reaproveitar `app/dashboard.py`

Porque as funções de lá estão decoradas com `@st.cache_data`, e esse decorador **importa o
Streamlit e exige uma sessão**. A lógica era boa e está reutilizada tal como estava; o que
mudou foi a cache, que passa a ser um dicionário com TTL em vez de uma dependência de
framework. É o que permite ao processo web deixar de ser um servidor de Streamlit.

## A decisão de desenho que interessa: o que é caro sai do caminho crítico

A v4 teve de **retirar** os precedentes da página porque carregar o modelo semântico mais a
base de casos custava ~7 s à carga a frio, contra um critério que pede menos de 2,5 s. Numa
página monolítica isso é uma escolha entre a capacidade e a velocidade.

Com uma API deixa de ser uma escolha: `/api/asset/{t}` responde com o que é barato e o
cliente pede `/api/precedents/{t}` **depois de pintar**. A capacidade volta ao produto sem
pagar o custo onde ele se nota. É a razão técnica mais concreta para separar o servidor do
cliente, e é a mesma razão pela qual a recuperação — a terceira pergunta da tese — pode
finalmente viver no ecrã principal.
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
BACKFILL = RAIZ / "data" / "samples" / "backfill_kb.jsonl"


def raw_url(path: str) -> str:
    repo = os.getenv("INVESTIGATOR_HISTORY_REPO", "HS2000PT/DIMEIA")
    return f"https://raw.githubusercontent.com/{repo}/{HISTORY_BRANCH}/{path}"


# ── Cache com TTL (sem framework) ─────────────────────────────────────────────
_CACHE: dict[str, tuple[float, Any]] = {}
_LOCK = threading.Lock()


def cached(key: str, ttl: float, fn):
    """Memoiza `fn()` por `ttl` segundos.

    O lock protege o dicionário, não a chamada: duas chamadas simultâneas com a cache fria
    podem ambas executar `fn`. É deliberado — segurar o lock durante uma ida à rede
    serializaria todos os pedidos da app atrás do mais lento.
    """
    now = time.time()
    with _LOCK:
        hit = _CACHE.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
    value = fn()
    with _LOCK:
        _CACHE[key] = (now, value)
    return value


def _get_json_lines(url: str, timeout: float = 20.0) -> list[str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310
            return r.read().decode("utf-8", "replace").splitlines()
    except Exception:  # noqa: BLE001
        return []


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
    """A grelha pré-computada pelo worker. Nunca levanta; devolve `{}` se não houver."""
    def _load():
        from app.snapshot_io import carregar
        snap = carregar()
        if not snap:
            return {}
        return {
            # `**snap.extra` primeiro, para os campos calculados aqui mandarem sobre os do
            # ficheiro em caso de colisão de nome.
            **snap.extra,
            "rows": snap.linhas,
            "as_of": snap.gerado_em.isoformat(timespec="seconds"),
            "age_s": round(snap.idade_s, 1),
            "age_label": snap.idade_legivel,
            "fresh": snap.fresco,
            "remote": snap.remoto,
        }
    return cached("snapshot", 30, _load)


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

def _absorb(lines, out: dict[str, list[dict]], seen: set) -> None:
    for line in lines:
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        key = (r.get("ticker"), r.get("date"), (r.get("headline") or "")[:80])
        if key in seen:
            continue
        seen.add(key)
        imp = r.get("impacts") or {}
        out.setdefault(r.get("ticker", "?"), []).append({
            "date": r.get("date", ""),
            "headline": r.get("headline", ""),
            "source": r.get("source", ""),
            "published_at": r.get("published_at") or r.get("event_at") or "",
            "url": r.get("url", ""),
            "d1": imp.get("1"),
            "d5": imp.get("5"),
        })


def news_by_ticker() -> dict[str, list[dict]]:
    """Notícias com impacto medido, por ticker. Local primeiro, base viva depois.

    A ordem é a mesma do painel anterior e pela mesma razão: se a rede falhar perde-se as
    últimas semanas e mantém-se o ano reconstruído, em vez de se perder tudo.
    """
    def _load():
        out: dict[str, list[dict]] = {}
        seen: set = set()
        if BACKFILL.exists():
            try:
                with BACKFILL.open(encoding="utf-8") as fh:
                    _absorb(fh, out, seen)
            except OSError:
                pass
        if os.environ.get("INVESTIGATOR_OFFLINE") != "1":
            _absorb(_get_json_lines(raw_url("live_kb.jsonl"), 25), out, seen)
        for v in out.values():
            v.sort(key=lambda r: r["date"], reverse=True)
        return out
    return cached("news_by_ticker", 900, _load)


def news_days(ticker: str, limit: int = 400) -> list[dict]:
    """Uma entrada por DIA — a unidade em que o impacto existe.

    Seis manchetes do mesmo dia partilham exactamente os mesmos +1d/+5d, portanto no gráfico
    seriam seis marcas indistinguíveis no mesmo sítio. A contagem das outras vai em `n`.
    """
    rows = news_by_ticker().get(ticker.upper(), [])
    by_day: dict[str, dict] = {}
    for r in rows:
        d = r["date"]
        if d not in by_day:
            by_day[d] = {**r, "n": 1, "others": []}
        else:
            by_day[d]["n"] += 1
            if len(by_day[d]["others"]) < 5:
                by_day[d]["others"].append(r["headline"])
    return sorted(by_day.values(), key=lambda r: r["date"], reverse=True)[:limit]


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
        try:
            from investigator.alerts_history import fetch_remote
            hist = fetch_remote(raw_url("alerts_history.jsonl")) or []
        except Exception:  # noqa: BLE001
            return []
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
        rows.sort(key=lambda r: r["date"], reverse=True)
        return rows[:400]
    return cached("screener", 120, _load)


# ── Recuperação semântica (caro — fora do caminho crítico) ────────────────────

_ENGINE: dict[str, Any] = {}


def _retrieval_engine():
    if "engine" not in _ENGINE:
        from investigator.main import product_retrieval
        _ENGINE["engine"] = product_retrieval(
            auto_download=os.environ.get("INVESTIGATOR_OFFLINE") != "1")
    return _ENGINE["engine"]


def _retrieval_kbs(kb_path: str):
    if "kbs" not in _ENGINE:
        from investigator.historical_kb.knowledge_base import HistoricalKB
        from investigator.live_kb import fetch_remote_records
        kbs = []
        if os.environ.get("INVESTIGATOR_OFFLINE") != "1":
            try:
                vivos = fetch_remote_records(raw_url("live_kb.jsonl"))
                if vivos:
                    kbs.append(HistoricalKB(vivos))
            except Exception:  # noqa: BLE001
                pass
        kbs.append(HistoricalKB.load(kb_path, lean=True))
        _ENGINE["kbs"] = kbs
    return _ENGINE["kbs"]


def precedents(ticker: str, top_k: int = 4, query: str | None = None) -> dict | None:
    """*Já aconteceu antes, e o que se seguiu?* — a terceira pergunta da tese.

    Os casos vêm de **outras empresas também**: é essa a aposta da RQ2 (P@5 0,595 à escala),
    e por isso cada linha diz de quem é. O desfecho é **medido** com a regra de alinhamento
    sem lookahead, nunca projectado.
    """
    t = ticker.upper()
    key = f"prec:{t}:{top_k}:{(query or '')[:60]}"

    def _load():
        q = query
        q_date = ""
        if not q:
            dias = news_days(t, limit=1)
            if not dias:
                return None
            q, q_date = dias[0]["headline"], dias[0]["date"]
        try:
            from investigator.live_kb import merged_precedents
            kb_path, embedder = _retrieval_engine()
            casos = merged_precedents(q, _retrieval_kbs(str(kb_path)), embedder,
                                      top_k=top_k, today=datetime.now(UTC).date())
        except Exception:  # noqa: BLE001
            return None
        if not casos:
            return None
        linhas, up, down = [], 0, 0
        for rec, sim in casos:
            imp = rec.impacts.get("5")
            if imp is not None and imp == imp:
                up += imp > 0
                down += imp < 0
            else:
                imp = None
            linhas.append({"ticker": rec.ticker, "date": rec.date,
                           "headline": rec.headline,
                           "impact_pct": None if imp is None else round(float(imp), 2),
                           "similarity": round(float(sim), 3)})
        return {"query": q, "query_date": q_date, "cases": linhas, "up": up, "down": down,
                "semantic": bool(getattr(embedder, "semantic", False))}

    return cached(key, 900, _load)


def triage_score(ticker: str, headline: str = "") -> dict | None:
    """A pontuação do modelo treinado (RQ4) — probabilidade calibrada de movimento anormal.

    ⚠️ **O que este número é, e a tese diz o mesmo:** estima se o mercado *reage*, nunca em que
    *direcção*. Não é uma previsão de preço, e a interface tem de o dizer sempre que o mostra.

    Fail-open em todas as etapas: sem modelo, sem preços, ou com furos na série, devolve
    `None` e o produto diz que não sabe — em vez de mostrar um número que não existe.
    """
    def _load():
        try:
            from investigator.market_data.prices import get_price_history
            from investigator.triage.infer import load_context_bundle, score_latest
            bundle = load_context_bundle()
            if not bundle:
                return None
            close = get_price_history(ticker.upper(), period="6mo")["Close"]
            out = score_latest(bundle, close, headline, ticker.upper())
            if out is None:
                return None
            prob, contribs = out
            return {
                "prob": float(prob),
                "contributions": [{"name": n, "weight": round(float(w), 3)}
                                  for n, w in contribs[:5]],
                "for_headline": bool(headline),
            }
        except Exception:  # noqa: BLE001
            return None
    return cached(f"triage:{ticker}:{headline[:60]}", 600, _load)
