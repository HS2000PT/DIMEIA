"""Evidência do narrador — o contrato de dados entre os motores e a linguagem.

**A propriedade que importa.** A afirmação central do narrador é *"o LLM escreve a língua,
nunca os factos"*. Para essa afirmação ser MENSURÁVEL (e não só um slogan), todos os números
que o texto gerado PODE conter têm de ser enumeráveis mecanicamente a partir da evidência.
É isso que `allowed_number_strings()` faz: devolve o conjunto fechado de grafias numéricas
legítimas. Qualquer número no texto gerado fora deste conjunto é, por definição, invenção —
detetável por um verificador puro, sem juízo humano.

Consequência de desenho: os campos numéricos guardam-se JÁ FORMATADOS como vão aparecer
("-8.50", não -0.085013). O LLM copia grafias, não reformata floats — reformatação é a via
mais comum de "alucinação por arredondamento" (o modelo escreve 8.5 ou 8,50 ou 8.501) e
eliminá-la à nascença é mais robusto do que tolerá-la no verificador.

Puro: sem rede, sem LLM, sem dependências além da stdlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


def fmt_pct(value: float) -> str:
    """Formata um retorno fracionário como percentagem com sinal ("-0.085" → "-8.50").

    Uma ÚNICA função de formatação para toda a evidência: é ela que garante que a grafia
    no prompt, no template e no conjunto permitido é a MESMA.
    """
    return f"{value * 100:+.2f}"


def fmt_num(value: float) -> str:
    """Número simples com 2 casas e sinal quando negativo (z-scores, similaridades)."""
    return f"{value:+.2f}" if value < 0 else f"{value:.2f}"


@dataclass(frozen=True)
class Precedent:
    """Um caso histórico recuperado — os factos exatos que o retrieval devolveu."""

    headline: str
    date: str  # ISO
    days_ago: int
    similarity: str  # já formatado, ex.: "0.64"
    impact_pct: str  # já formatado, ex.: "-6.38"


@dataclass(frozen=True)
class AlertEvidence:
    """Tudo o que os motores apuraram sobre UM evento — e NADA mais.

    O narrador recebe isto e só isto. Campos opcionais a None/[] significam "o motor não
    produziu este facto" — o texto não pode então falar dele.
    """

    ticker: str
    date: str  # ISO, dia do evento
    kind: str  # "market" | "news"

    # Movimento e deteção (mercado; também presente em notícias quando há barra do dia)
    move_pct: str | None = None  # ex.: "-8.50"
    z_score: str | None = None  # ex.: "-1.82"
    threshold: str | None = None  # ex.: "1.5"
    window_days: int | None = None  # ex.: 20

    # Decomposição contemporânea (correlation_engine/decomposition.py)
    market_pct: str | None = None
    sector_pct: str | None = None
    company_pct: str | None = None
    driver: str | None = None  # "market" | "sector" | "company"
    decomposition_fallback: bool = False  # True = beta assumido 1.0 (dizê-lo é obrigatório)

    # Notícia + precedentes (retrieval)
    headline: str | None = None
    precedents: list[Precedent] = field(default_factory=list)
    horizon_days: int | None = None  # ex.: 5
    up_count: int | None = None  # quantos precedentes subiram
    down_count: int | None = None

    # Triagem aprendida (RQ4)
    triage_prob_pct: str | None = None  # ex.: "63" (por cento, inteiro — como o produto mostra)

    def evidence_texts(self) -> list[str]:
        """Textos NÃO-numéricos vindos de fora (manchetes): citáveis pelo narrador.

        Servem para a isenção do léxico proibido — uma palavra como "buy" numa manchete
        real citada não é conselho NOSSO. Ver core.check_faithfulness.
        """
        out = [self.headline or ""]
        out += [p.headline for p in self.precedents]
        return [t for t in out if t]

    def field_number_strings(self) -> set[str]:
        """Grafias numéricas dos CAMPOS calculados pelos motores — permitidas em qualquer
        ponto do texto gerado.

        Inclui, para cada valor, as variantes de grafia inofensivas (sem sinal, sem zeros
        finais): "−8.50" pode legitimamente aparecer como "8.5" no meio de uma frase. O que
        NUNCA entra é um valor que não esteja na evidência.
        """
        raw: set[str] = set()

        def add(s: str | None) -> None:
            if not s:
                return
            v = s.lstrip("+-")
            raw.add(v)
            if "." in v:
                stripped = v.rstrip("0").rstrip(".")
                if stripped:
                    raw.add(stripped)

        for s in (self.move_pct, self.z_score, self.threshold, self.market_pct,
                  self.sector_pct, self.company_pct, self.triage_prob_pct):
            add(s)
        for p in self.precedents:
            add(p.similarity)
            add(p.impact_pct)
            raw.add(str(p.days_ago))
        for n in (self.window_days, self.horizon_days, self.up_count, self.down_count):
            if n is not None:
                raw.add(str(n))
        raw.add(str(len(self.precedents)))

        # Partes de datas da evidência ("2026-07-28" → 2026, 07, 7, 28): uma narração pode
        # legitimamente dizer "July 28". Nada disto abre porta a números de mercado inventados.
        for d in [self.date] + [p.date for p in self.precedents]:
            for part in re.findall(r"\d+", d or ""):
                raw.add(part)
                raw.add(part.lstrip("0") or "0")

        return raw

    def text_number_strings(self) -> set[str]:
        """Grafias numéricas vindas de MANCHETES — permitidas SÓ dentro de aspas.

        A distinção é deliberada e é uma defesa contra injeção: uma manchete maliciosa
        ("TSLA will rise 400%") entra na evidência como texto, e sem esta separação o "400"
        ficaria automaticamente legítimo em qualquer ponto da narração. Confinar os números
        de manchete a citações força o texto gerado a ASSINALAR que está a repetir a fonte
        ("the headline claims '...400%...'") em vez de afirmar o número com a nossa voz.
        """
        raw: set[str] = set()
        for t in self.evidence_texts():
            for n in re.findall(r"\d+(?:\.\d+)?", t):
                raw.add(n)
                if "." in n:
                    stripped = n.rstrip("0").rstrip(".")
                    if stripped:
                        raw.add(stripped)
        return raw
