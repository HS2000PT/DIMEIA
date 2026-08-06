"""Leitura do instantâneo pré-computado — a camada que torna a v4 rápida.

A v3 chama `_snapshot(t)` por cada um dos doze tickers na página de entrada, e cada chamada puxa
um ano de preços **pela rede**. São doze idas à rede antes da primeira pintura, e é aí que vivem
os ~5,5 s de carga a frio: medido, o parse do *backfill* custa 0,30 s e o import do pandas 0,97 s,
portanto o resto é espera de rede.

Aqui a página **lê um ficheiro**. Medido: construir a frio 4,92 s · calcular com a cache HTTP
quente 0,870 s · **ler o instantâneo 0,011 s**, num ficheiro de 2,4 KB.

**Falha aberto, e é a decisão de desenho mais importante deste módulo.** Sem instantâneo, ou com
um instantâneo velho, a app **não** mostra um ecrã vazio nem números inventados: devolve `None` e
quem chama decide (a v4 cai no cálculo ao vivo). Um painel que mostra dados silenciosamente
velhos é pior do que um painel que diz que não sabe.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CAMINHO = RAIZ / "data" / "samples" / "dashboard_snapshot.json"

# Acima disto o instantâneo deixa de ser "agora". O worker corre a 60 s; 90 s dá margem para um
# ciclo lento sem deixar passar um ficheiro genuinamente parado (critério P3).
IDADE_MAXIMA_S = 90


@dataclass(frozen=True)
class Instantaneo:
    linhas: list[dict]
    gerado_em: datetime
    idade_s: float

    @property
    def fresco(self) -> bool:
        return self.idade_s <= IDADE_MAXIMA_S

    @property
    def idade_legivel(self) -> str:
        """Idade em palavras. O ecrã tem de mostrar isto (P3): um número sem idade é um número
        que o leitor assume actual, e assumir é o modo de falha que este projecto evita."""
        s = int(self.idade_s)
        if s < 60:
            return f"{s}s ago"
        if s < 3600:
            return f"{s // 60}m ago"
        return f"{s // 3600}h ago"


def carregar(caminho: pathlib.Path | None = None,
             agora: datetime | None = None) -> Instantaneo | None:
    """Lê o instantâneo. Devolve `None` em qualquer falha — nunca levanta, nunca inventa."""
    p = caminho or CAMINHO
    try:
        bruto = json.loads(p.read_text(encoding="utf-8"))
        gerado = datetime.fromisoformat(bruto["generated_at"])
        if gerado.tzinfo is None:
            gerado = gerado.replace(tzinfo=UTC)
        linhas = [x for x in bruto.get("rows", []) if x.get("ticker")]
        if not linhas:
            return None
        ref = agora or datetime.now(UTC)
        return Instantaneo(
            linhas=linhas,
            gerado_em=gerado,
            idade_s=max(0.0, (ref - gerado).total_seconds()),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


def resumo_do_dia(linhas: list[dict], limiar: float = 1.5) -> str:
    """A frase que responde ao dia ANTES de qualquer cartão (critério C1).

    Sem números técnicos e sem previsão: conta quantas se destacaram e quantas não. É a versão
    executável de "responde à pergunta antes de mostrar os dados".
    """
    if not linhas:
        return "No data for today yet."
    total = len(linhas)
    destacadas = [r for r in linhas if abs(float(r.get("z") or 0.0)) >= limiar]
    n = len(destacadas)
    if n == 0:
        return f"Nothing stood out today. All {total} moved within their usual range."
    nomes = ", ".join(r["ticker"] for r in sorted(
        destacadas, key=lambda r: -abs(float(r.get("z") or 0.0)))[:3])
    if n == 1:
        return f"One name stood out today: {nomes}. The other {total - 1} were ordinary."
    return f"{n} of {total} stood out today: {nomes}. The rest moved within their usual range."


def tira_distribuicao(count: int | None, n: int | None, largura: int = 132,
                      altura: int = 14) -> str:
    """A raridade **vista**, não lida (critério C3).

    A contagem empírica ("52 dos últimos 250 dias moveram-se tanto ou mais") já é honesta, mas é
    uma frase. Aqui é uma tira: uma marca por dia, as que excederam acesas. O leitor vê a
    proporção sem ler um número e sem precisar de estatística nenhuma.

    Não é um histograma nem uma distribuição ajustada — é a contagem, desenhada. Nada aqui
    assume normalidade, que é precisamente a razão pela qual o projecto conta em vez de converter
    o z-score numa probabilidade.
    """
    if not n or count is None:
        return ""
    marcas = 60  # resolução da tira; o `n` real vai no rótulo
    acesas = max(0, min(marcas, round(marcas * count / n)))
    largura_marca = largura / marcas
    partes = []
    for i in range(marcas):
        cor = "var(--strip-on)" if i < acesas else "var(--strip-off)"
        x = i * largura_marca
        partes.append(
            f'<rect x="{x:.2f}" y="0" width="{max(0.9, largura_marca - 1):.2f}" '
            f'height="{altura}" rx="1" fill="{cor}"/>'
        )
    return (f'<svg class="strip" width="{largura}" height="{altura}" '
            f'viewBox="0 0 {largura} {altura}" aria-hidden="true">{"".join(partes)}</svg>')
