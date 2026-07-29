"""Sonda de saúde dos fornecedores de LLM — correr ANTES de depender deles (e antes da defesa).

**Porque existe.** Os free tiers de LLM mudam sem aviso. A sondagem de 2026-07-29 desmentiu a
suposição inicial: o Gemini, escolhido como principal por reputação de free tier generoso,
devolveu **404** nos modelos 2.5 ("no longer available to new users") e **429 à primeira
chamada** nos 2.0 — numa chave acabada de criar. O Groq respondeu em 0,57 s. A ordem de
preferência foi invertida **por medição**, não por opinião.

Uma demo de defesa não pode morrer num rate limit. Este script responde a "o meu narrador vai
funcionar daqui a uma hora?" sem adivinhar.

Uso:
    python scripts/probe_llm.py            # sonda os fornecedores configurados
    python scripts/probe_llm.py --all      # tenta também modelos alternativos
"""

from __future__ import annotations

import argparse
import json
import time

import requests

from investigator import config
from investigator.console import force_utf8_stdout

# Ordem de preferência, fixada pela sondagem de 2026-07-29 (ver docs/design/keys.md).
GROQ_PRIMARY = "llama-3.3-70b-versatile"
GEMINI_FALLBACK = "gemini-flash-lite-latest"  # nome estável; evita os "-preview"

GROQ_ALTERNATIVES = ["llama-3.1-8b-instant", "openai/gpt-oss-20b"]
GEMINI_ALTERNATIVES = ["gemini-3.1-flash-lite-preview", "gemini-flash-latest"]

# Pedido realista: o narrador recebe números e devolve UMA frase. Serve também de teste de
# fidelidade rápido — a resposta não pode conter números fora do input.
PROBE_PROMPT = """You are a financial alert narrator. Write ONE short sentence for a retail
investor. Use ONLY these numbers. Never add a number that is not listed. Never predict, never
advise.

ticker: AMD
total_move_pct: -8.50
market_component_pct: 0.61
sector_component_pct: -3.60
company_component_pct: -5.51
"""
# Números que PODEM aparecer. Qualquer outro é sinal de invenção.
ALLOWED_NUMBERS = {"8.50", "8.5", "0.61", "3.60", "3.6", "5.51"}


def _numbers_in(text: str) -> set[str]:
    import re

    return set(re.findall(r"\d+\.?\d*", text))


def call_groq(model: str, prompt: str, timeout: float = 45.0) -> tuple[float, str, str]:
    """Devolve (segundos, estado, texto_ou_erro). Nunca levanta."""
    t0 = time.time()
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0, "max_tokens": 200},
            timeout=timeout,
        )
        dt = time.time() - t0
        if not r.ok:
            return dt, str(r.status_code), _err(r.text)
        return dt, "ok", r.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        return time.time() - t0, "erro", f"{type(exc).__name__}: {exc}"


def call_gemini(model: str, prompt: str, timeout: float = 45.0) -> tuple[float, str, str]:
    t0 = time.time()
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": config.GEMINI_API_KEY},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0, "maxOutputTokens": 400}},
            timeout=timeout,
        )
        dt = time.time() - t0
        if not r.ok:
            return dt, str(r.status_code), _err(r.text)
        try:
            return dt, "ok", r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            # Modelos de raciocínio devolvem 200 sem texto quando gastam o orçamento a "pensar".
            return dt, "sem-texto", "200 sem conteúdo (modelo de raciocínio?)"
    except Exception as exc:  # noqa: BLE001
        return time.time() - t0, "erro", f"{type(exc).__name__}: {exc}"


def _err(body: str) -> str:
    try:
        return json.loads(body).get("error", {}).get("message", body)[:120]
    except json.JSONDecodeError:
        return body[:120]


def _report(label: str, dt: float, status: str, text: str) -> bool:
    ok = status == "ok"
    if not ok:
        print(f"  ✗ {label:38} {dt:5.2f}s  [{status}] {text}")
        return False
    extra = _numbers_in(text) - ALLOWED_NUMBERS
    flag = "" if not extra else f"  ⚠ números fora do input: {sorted(extra)}"
    print(f"  ✓ {label:38} {dt:5.2f}s  {text[:90]}{flag}")
    return True


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Sonda de saúde dos fornecedores de LLM")
    ap.add_argument("--all", action="store_true", help="tenta também modelos alternativos")
    args = ap.parse_args()

    presentes = config.narrator_providers()
    print(f"Fornecedores com chave: {presentes or '(nenhum)'}")
    if not presentes:
        print("\nSem chaves → o narrador usa o texto por template determinístico.")
        print("Isto NÃO é uma falha: o sistema é fail-open por desenho.")
        return 0

    saudavel = False
    if config.GROQ_API_KEY:
        print("\nGroq (principal):")
        saudavel |= _report(GROQ_PRIMARY, *call_groq(GROQ_PRIMARY, PROBE_PROMPT))
        if args.all:
            for m in GROQ_ALTERNATIVES:
                _report(m, *call_groq(m, PROBE_PROMPT))

    if config.GEMINI_API_KEY:
        print("\nGemini (reserva):")
        saudavel |= _report(GEMINI_FALLBACK, *call_gemini(GEMINI_FALLBACK, PROBE_PROMPT))
        if args.all:
            for m in GEMINI_ALTERNATIVES:
                _report(m, *call_gemini(m, PROBE_PROMPT))

    print()
    if saudavel:
        print("[ok] Pelo menos um fornecedor responde — o narrador tem caminho.")
    else:
        print("[!] NENHUM fornecedor respondeu. O sistema degrada para o texto por template")
        print("    (continua a funcionar), mas a demo do narrador não vai correr.")
    return 0 if saudavel else 1


if __name__ == "__main__":
    raise SystemExit(main())
