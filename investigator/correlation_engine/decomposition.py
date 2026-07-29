"""Decomposição contemporânea de um movimento: mercado · setor · específico da empresa.

**A pergunta que responde.** Quando uma ação cai 4%, a primeira pergunta de qualquer
investidor é *"é a minha empresa ou é o mercado todo?"*. Nenhuma ferramenta gratuita
responde. Esta função responde com números: `−4,0% = −0,3% mercado · −3,1% setor · −0,6%
específico`. Converte a maioria dos alertas vermelhos de "a tua ação afundou" em "o mercado
caiu, a tua ação não fez nada de invulgar".

**Porque é que NÃO reutiliza `event_study.abnormal_returns`.** São coisas diferentes, e
confundi-las custaria a validade dos congelados:

| | `abnormal_returns` | esta função |
|---|---|---|
| Janela | **futura** (evento → +1/+3/+5 dias) | **hoje**, contemporânea |
| Beta | **implícito = 1,0** | estimado por regressão |
| Serve | rótulo da RQ4 (`triage/dataset.py:102`) | explicação ao utilizador |

`abnormal_returns` é a base dos números congelados da triagem e **não pode ser tocada**.
Além disso, um beta implícito de 1,0 é indefensável para explicar um movimento: o beta da
NVDA face ao setor de semicondutores não é 1,0, por isso um "específico da empresa" calculado
com beta=1 estaria simplesmente errado — e é a primeira coisa que um arguente com formação em
finanças ataca.

**Anti-lookahead.** Os betas são estimados **só** com dados anteriores ao dia explicado. A
decomposição não prevê nada: descreve um movimento já observado.

**Modelo.** Dois fatores, com o setor ortogonalizado contra o mercado (um ETF de setor e o
índice são altamente correlacionados; sem ortogonalizar, os betas ficam instáveis e a
atribuição deixa de ter sentido):

1. regressão `setor ~ mercado` na janela → resíduo = fator de setor PURO;
2. regressão `ticker ~ mercado + setor_puro` na janela → β_mercado, β_setor, α;
3. hoje: mercado = β_m·r_m · setor = β_s·r_s_puro · específico = tudo o resto.

As três componentes **somam exatamente** o movimento observado (o α e o resíduo do dia caem
no específico da empresa, que é onde pertencem: são o que não se explica por mercado ou setor).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Abaixo disto a regressão não é de confiar (poucos graus de liberdade para 2 fatores + α).
MIN_WINDOW = 10

# ── Encolhimento do beta, ponderado pela precisão (Vasicek) ───────────────────
# Um beta estimado em 20 dias é ruidoso: numa janela volátil a AMD deu β=4,43 (medido a
# 2026-07-29). Cortar a régua num limite arbitrário — a 1.ª versão usava ±4 — é o mesmo pecado
# das constantes por justificar que este projeto corrige noutros sítios: em vez de melhorar a
# estimativa, trocava-a silenciosamente por β=1 e atribuía TUDO à empresa.
#
# Um peso FIXO (o clássico 2/3 de Blume) também não serve: encolheria um beta perfeitamente
# estimado, e num caso sem ruído passaria a atribuir à empresa um movimento que é do mercado.
# Verificado nos testes: com ticker = 2× mercado exato, o peso fixo dava β=1,67 em vez de 2,0.
#
# O encolhimento ponderado pela PRECISÃO resolve os dois: pesa o estimado contra o prior pelo
# erro-padrão do próprio estimador (Vasicek 1973). Ajuste tudo-ou-nada nenhum —
#     w = σ²_prior / (σ²_prior + SE²(β̂))
# — com SE→0 (ajuste limpo) w→1 e o beta fica intacto; com SE grande (janela ruidosa) w→0 e
# recai no prior. É adaptativo e é prática padrão em finanças.
# ⚠️ Antes de citar Vasicek/Blume na tese, verificar as referências pelo protocolo §6.4.
PRIOR_BETA_MARKET = 1.0
PRIOR_BETA_SECTOR = 0.0
# Dispersão típica de betas entre ações — grandeza económica (a maioria cai em ~0,5–2,0),
# não um corte arbitrário. Define quanta confiança se dá ao prior.
PRIOR_BETA_SD = 0.5
# Guarda PURAMENTE numérica (explosão por janela degenerada), não juízo económico.
BETA_SANITY = 10.0


def _shrink(beta_raw: float, std_err: float, prior: float,
            prior_sd: float = PRIOR_BETA_SD) -> float:
    """Encolhe `beta_raw` na direção de `prior`, pesando pela precisão da estimativa."""
    if not np.isfinite(std_err) or std_err <= 0:
        return beta_raw  # ajuste exato: nada a encolher
    w = prior_sd**2 / (prior_sd**2 + std_err**2)
    return w * beta_raw + (1.0 - w) * prior


@dataclass(frozen=True)
class MoveDecomposition:
    """Um movimento diário repartido pelas suas fontes. `total` = soma das três componentes."""

    total: float
    market: float
    sector: float
    idiosyncratic: float
    beta_market: float
    beta_sector: float
    window: int
    r_squared: float
    fallback: bool  # True = betas não estimáveis; usou-se β_mercado=1, β_setor=0

    @property
    def idiosyncratic_share(self) -> float:
        """Fração do movimento (em módulo) que é específica da empresa, em [0, 1]."""
        denom = abs(self.market) + abs(self.sector) + abs(self.idiosyncratic)
        return abs(self.idiosyncratic) / denom if denom > 0 else float("nan")

    @property
    def _parts(self) -> dict[str, float]:
        return {"market": self.market, "sector": self.sector, "company": self.idiosyncratic}

    @property
    def driver(self) -> str:
        """A fonte que melhor EXPLICA o movimento observado.

        Não é simplesmente a maior em módulo — e a diferença é real. Medido a 2026-07-29:
        NVDA +0,25% = +0,38% mercado · **−1,54% setor** · +1,41% empresa. A maior componente
        em módulo é o setor, mas o setor puxou ao CONTRÁRIO; dizer "foi o setor" seria falso.
        O que explica um dia positivo são as componentes positivas. Por isso considera-se só
        quem tem o MESMO sinal do movimento total."""
        if self.total == 0:
            return max(self._parts, key=lambda k: abs(self._parts[k]))
        same = {k: abs(v) for k, v in self._parts.items() if v * self.total > 0}
        pool = same or {k: abs(v) for k, v in self._parts.items()}
        return max(pool, key=lambda k: pool[k])

    @property
    def opposed(self) -> list[str]:
        """Componentes que puxaram contra o movimento observado (ordenadas por peso)."""
        against = {k: abs(v) for k, v in self._parts.items() if v * self.total < 0}
        return sorted(against, key=lambda k: against[k], reverse=True)


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
    """OLS com intercepto. Devolve (coeficientes_sem_intercepto, alpha, erros_padrão).

    Os erros-padrão são o que permite encolher pela precisão em vez de por um peso fixo.
    Devolve SE = 0 quando o ajuste é exato (resíduos nulos) ou não há graus de liberdade
    suficientes — nesses casos `_shrink` deixa o beta como está."""
    design = np.column_stack([np.ones(len(x)), x]) if x.ndim > 1 else np.column_stack(
        [np.ones(len(x)), x.reshape(-1, 1)]
    )
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ coef
    dof = len(y) - design.shape[1]
    se = np.zeros(design.shape[1] - 1)
    if dof > 0:
        sigma2 = float(resid @ resid) / dof
        if sigma2 > 0:
            try:
                cov = sigma2 * np.linalg.pinv(design.T @ design)
                se = np.sqrt(np.clip(np.diag(cov)[1:], 0.0, None))
            except np.linalg.LinAlgError:
                se = np.zeros(design.shape[1] - 1)
    return coef[1:], float(coef[0]), se


def decompose_move(
    ticker_returns: np.ndarray,
    market_returns: np.ndarray,
    sector_returns: np.ndarray | None = None,
    window: int = 20,
) -> MoveDecomposition:
    """Reparte o ÚLTIMO retorno da série em mercado, setor e específico da empresa.

    Args:
        ticker_returns: retornos diários do ticker; o ÚLTIMO é o dia a explicar.
        market_returns: retornos do índice (ex.: SPY), alinhados ponto a ponto.
        sector_returns: retornos do ETF de setor (opcional), alinhados. Sem eles, a
            componente de setor é 0 e tudo o que não é mercado vai para específico.
        window: dias ANTERIORES usados para estimar os betas (a mesma janela de 20 do detetor).

    Raises:
        ValueError: séries desalinhadas ou vazias.
    """
    t = np.asarray(ticker_returns, dtype=float)
    m = np.asarray(market_returns, dtype=float)
    if len(t) != len(m):
        raise ValueError(f"Séries desalinhadas: ticker {len(t)}, mercado {len(m)}.")
    if len(t) == 0:
        raise ValueError("Séries vazias.")
    s = None
    if sector_returns is not None:
        s = np.asarray(sector_returns, dtype=float)
        if len(s) != len(t):
            raise ValueError(f"Séries desalinhadas: ticker {len(t)}, setor {len(s)}.")

    total = float(t[-1])
    r_m_today = float(m[-1])
    r_s_today = float(s[-1]) if s is not None else 0.0

    # Janela de estimação: estritamente ANTES do dia explicado (anti-lookahead).
    hist_t, hist_m = t[:-1][-window:], m[:-1][-window:]
    hist_s = s[:-1][-window:] if s is not None else None
    usable = len(hist_t)

    def _fallback(reason_beta_m: float = 1.0) -> MoveDecomposition:
        """Sem estimativa fiável, assume-se β=1 no mercado e nada de setor — e DIZ-SE."""
        market_part = reason_beta_m * r_m_today
        return MoveDecomposition(
            total=total, market=market_part, sector=0.0,
            idiosyncratic=total - market_part,
            beta_market=reason_beta_m, beta_sector=0.0,
            window=usable, r_squared=float("nan"), fallback=True,
        )

    if usable < MIN_WINDOW or np.allclose(hist_m, hist_m[0] if usable else 0.0):
        return _fallback()

    # 1. Fator de setor PURO = resíduo de setor ~ mercado.
    sector_today_pure = 0.0
    hist_s_pure = None
    if hist_s is not None and not np.allclose(hist_s, hist_s[0]):
        (b_sm,), a_sm, _ = _ols(hist_m, hist_s)
        hist_s_pure = hist_s - (a_sm + b_sm * hist_m)
        sector_today_pure = r_s_today - (a_sm + b_sm * r_m_today)

    # 2. Betas do ticker sobre os fatores (já não colineares).
    factors = np.column_stack([hist_m, hist_s_pure]) if hist_s_pure is not None else hist_m
    try:
        betas, alpha, errs = _ols(factors, hist_t)
    except np.linalg.LinAlgError:
        return _fallback()

    beta_m_raw = float(betas[0])
    beta_s_raw = float(betas[1]) if len(betas) > 1 else 0.0
    if not np.isfinite(beta_m_raw):
        return _fallback()
    beta_m = _shrink(beta_m_raw, float(errs[0]), PRIOR_BETA_MARKET)
    beta_s = (
        _shrink(beta_s_raw, float(errs[1]), PRIOR_BETA_SECTOR)
        if len(errs) > 1 and np.isfinite(beta_s_raw)
        else 0.0
    )
    if abs(beta_m) > BETA_SANITY:  # só explosão numérica chega aqui
        return _fallback()
    if abs(beta_s) > BETA_SANITY:
        beta_s = 0.0

    # Recentrar o α para os betas ENCOLHIDOS: o α veio da regressão com os betas brutos, e
    # misturá-lo com betas diferentes descentraria o modelo que efetivamente reportamos.
    sector_hist = beta_s * hist_s_pure if hist_s_pure is not None else 0.0
    alpha = float(np.mean(hist_t) - beta_m * np.mean(hist_m) - np.mean(sector_hist))
    fitted = alpha + beta_m * hist_m + sector_hist
    resid = hist_t - fitted
    var = float(np.var(hist_t))
    r2 = float(1.0 - np.var(resid) / var) if var > 0 else float("nan")

    market_part = beta_m * r_m_today
    sector_part = beta_s * sector_today_pure
    # O α e o resíduo do dia entram no específico: é exatamente o que mercado e setor não
    # explicam. Assim as três componentes somam o movimento observado, por construção.
    return MoveDecomposition(
        total=total, market=float(market_part), sector=float(sector_part),
        idiosyncratic=float(total - market_part - sector_part),
        beta_market=beta_m, beta_sector=beta_s,
        window=usable, r_squared=r2, fallback=False,
    )


def describe(d: MoveDecomposition, ticker: str = "") -> str:
    """Uma linha em linguagem simples para o alerta. Só descreve o observado; nunca prevê."""
    who = f"{ticker} " if ticker else ""
    head = (f"{who}{d.total:+.2%} today = {d.market:+.2%} market"
            f" · {d.sector:+.2%} sector · {d.idiosyncratic:+.2%} company-specific.")
    if d.fallback:
        return head + (" Beta could not be estimated from recent data, so the market share"
                       " assumes beta 1.0 — treat the split as indicative.")
    verdict = {
        "market": "Most of this move came with the whole market, not from the company.",
        "sector": "Most of this move was sector-wide, not specific to the company.",
        "company": "Most of this move was specific to the company.",
    }[d.driver]
    # Quando uma componente puxou ao contrário, dizê-lo: é justamente a informação
    # interessante ("subiu apesar de o setor ter caído") e omiti-la enganaria.
    if "sector" in d.opposed:
        verdict += " The sector moved the other way."
    elif "market" in d.opposed:
        verdict += " The wider market moved the other way."
    return head + " " + verdict
