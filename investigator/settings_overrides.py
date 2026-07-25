"""Overrides de definições editáveis pelo ADMIN (painel da app) que chegam aos alertas.

Puro e defensivo: define QUAIS os parâmetros seguros de ajustar, valida/limita a valores
sãos, e funde-os sobre a config base (`alerts.yaml`). O runner aplica isto de forma
FAIL-OPEN — qualquer erro ⇒ ignora os overrides e comporta-se como sempre —, por isso um
override malformado nunca pode partir o pipeline de alertas nem inundar o canal.

Importante: a avaliação da tese continua congelada e separada (threshold 3.0 em
`docs/evaluation/`); estes são parâmetros de IMPLANTAÇÃO, divulgados e ajustáveis.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass


@dataclass(frozen=True)
class Tunable:
    key: str            # id do override (o que a UI/ficheiro usam)
    path: tuple         # caminho na config (ex.: ("market", "threshold"))
    label: str
    kind: str           # "float" | "int" | "bool"
    lo: float = 0.0
    hi: float = 1.0
    help: str = ""


# Parâmetros de IMPLANTAÇÃO seguros de expor ao admin. Limites conservadores para o canal
# nunca ser inundado nem silenciado por engano.
TUNABLES: list[Tunable] = [
    Tunable("market_threshold", ("market", "threshold"), "Market anomaly |z| threshold",
            "float", 0.8, 5.0,
            "Lower = more frequent market alerts. Thesis evaluation stays frozen at 3.0."),
    Tunable("market_enabled", ("market", "enabled"), "Market alerts on", "bool"),
    Tunable("news_enabled", ("news", "enabled"), "News alerts on", "bool"),
    Tunable("news_min_similarity", ("news", "min_similarity"), "Precedent similarity floor",
            "float", 0.20, 0.80,
            "Lower = show weaker-but-more precedents. Below this, alerts are suppressed."),
    Tunable("news_min_materiality", ("news", "min_materiality"), "Learned-triage gate p",
            "float", 0.0, 1.0,
            "Lower = the triage model lets more news through (more alerts, more noise)."),
    Tunable("news_max_per_ticker", ("news", "max_per_ticker_per_day"),
            "Max news alerts per ticker/day", "int", 1, 10,
            "Anti-fatigue cap."),
    Tunable("news_recency_half_life", ("news", "recency_half_life_days"),
            "Recency half-life (days)", "int", 30, 1000,
            "How fast older precedents lose ranking weight."),
]

_BY_KEY = {t.key: t for t in TUNABLES}


def _coerce(t: Tunable, value):
    """Converte e LIMITA um valor aos limites do tunable. Levanta em valor inconvertível."""
    if t.kind == "bool":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}
    num = float(value)
    if num != num:  # NaN
        raise ValueError("NaN")
    num = max(t.lo, min(t.hi, num))
    return int(round(num)) if t.kind == "int" else num


def validate_overrides(raw: dict | None) -> dict:
    """Filtra a chaves conhecidas e limita cada valor. Ignora o resto (nunca levanta por
    chave desconhecida ou valor mau — fail-open); devolve só overrides sãos."""
    if not isinstance(raw, dict):
        return {}
    clean: dict = {}
    for key, value in raw.items():
        t = _BY_KEY.get(key)
        if t is None:
            continue
        try:
            clean[key] = _coerce(t, value)
        except (TypeError, ValueError):
            continue
    return clean


def merge_overrides(base_cfg: dict, raw_overrides: dict | None) -> dict:
    """Devolve uma CÓPIA da config base com os overrides válidos aplicados nos caminhos certos.
    Não muta a base. Overrides inválidos são descartados (fail-open)."""
    cfg = copy.deepcopy(base_cfg) if base_cfg else {}
    clean = validate_overrides(raw_overrides)
    for key, value in clean.items():
        section, leaf = _BY_KEY[key].path
        cfg.setdefault(section, {})
        if not isinstance(cfg[section], dict):
            cfg[section] = {}
        cfg[section][leaf] = value
    return cfg


def current_values(cfg: dict) -> dict:
    """Valores efetivos atuais dos tunables (para pré-preencher o formulário do admin)."""
    out: dict = {}
    for t in TUNABLES:
        section, leaf = t.path
        val = (cfg.get(section) or {}).get(leaf)
        if val is not None:
            try:
                out[t.key] = _coerce(t, val)
            except (TypeError, ValueError):
                pass
    return out
