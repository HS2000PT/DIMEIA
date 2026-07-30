"""Event-type taxonomy over headline embeddings.

*Porquê existe.* A base de casos é uma pilha achatada de vetores. A recuperação sabe dizer
"isto parece-se com aqueles", mas nada no sistema sabe **que tipo de acontecimento** uma
manchete é. Essa lacuna é a causa direta do problema tema≠direção documentado no Caso 3: sem
tipo de evento não há maneira de dizer "compara este item regulatório contra precedentes
regulatórios", só "contra o que se parece com ele".

*Âmbito.* Esta camada é **descritiva**. Não toca no proxy de setor que sustenta os números
congelados de recuperação (RQ2), nem no dataset de triagem (RQ4). Acrescenta um rótulo; não
altera nenhum já existente.

*Duas peças, de propósito separadas:*

1. **A rubrica** (`RUBRIC`, `rubric_label`) — regras de palavra-chave, transparentes e de alta
   precisão, que devolvem `None` quando não têm confiança. Serve de **referência independente**
   contra a qual os agrupamentos não supervisionados são medidos. Foi escrita a partir da lista
   de tipos de evento **antes** de qualquer agrupamento correr, e a ordem dos commits prova-o.
2. **A taxonomia aprendida** (`EventTaxonomy`) — centróides obtidos por agrupamento sobre os
   embeddings, com um rótulo por grupo. É esta que generaliza para manchetes que a rubrica não
   apanha.

A rubrica é de propósito **alta precisão e baixa cobertura**: prefere não responder a responder
mal, porque o seu trabalho é servir de referência, não de classificador.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# ── A taxonomia ───────────────────────────────────────────────────────────────
# Oito tipos que cobrem o que o fluxo de notícias financeiras de facto contém. Escolhidos
# para serem accionáveis: cada um responde de forma diferente à pergunta "isto interessa-me?".
EVENT_TYPES: tuple[str, ...] = (
    "earnings",  # resultados trimestrais publicados
    "guidance",  # perspetivas futuras da própria empresa
    "analyst",  # ações de analistas: subidas/descidas de recomendação, preços-alvo
    "product",  # lançamentos, produtos, parcerias comerciais
    "legal_regulatory",  # processos, reguladores, investigações, multas
    "ma",  # fusões, aquisições, participações, cisões
    "personnel",  # mudanças de liderança
    "macro_market",  # macro, Fed, índices, resumos de mercado
)

UNMATCHED = "unmatched"

# ── A rubrica de referência (pré-registada) ───────────────────────────────────
# Alta precisão de propósito. Cada padrão foi escolhido para ser quase inequívoco: uma
# manchete que contenha "downgrades to sell" é uma ação de analista e mais nada. Casos
# ambíguos ficam deliberadamente por apanhar (`None`), porque uma referência que adivinha
# não é uma referência.
RUBRIC: tuple[tuple[str, str], ...] = (
    (
        "earnings",
        r"\b(q[1-4]\s*(20\d\d|earnings|results)|quarterly results|earnings (report|call|beat|miss|"
        r"season|preview|recap)|reports? (q[1-4]|first|second|third|fourth)[- ]quarter|eps of|"
        r"beats? (on )?(eps|earnings|estimates)|misses? (on )?(eps|earnings|estimates)|"
        r"earnings per share)\b",
    ),
    (
        "guidance",
        r"\b(raises? (fy|full[- ]year|20\d\d)? ?(guidance|outlook|forecast)|"
        r"cuts? (fy|full[- ]year)? ?(guidance|outlook|forecast)|"
        r"lowers? (guidance|outlook|forecast)|"
        r"(guidance|outlook) (raised|cut|lowered|lifted)|"
        r"issues? (upbeat|weak|soft|strong) (guidance|outlook|forecast)|"
        r"reaffirms? (guidance|outlook))\b",
    ),
    (
        "analyst",
        r"\b(upgrades?|downgrades?|price target|pt raised|pt lowered|initiates? coverage|"
        r"reiterates? (buy|sell|hold|neutral|outperform|underperform)|"
        r"(maintains?|assumes?) (buy|sell|hold|neutral|outperform|underperform)|"
        r"analyst (ratings?|actions?)|(raises?|lowers?) price target|"
        r"to (outperform|underperform|overweight|underweight)|street ratings?)\b",
    ),
    (
        "product",
        r"\b(launch(es|ed|ing)?|unveil(s|ed|ing)?|introduces?|debuts?|rolls? out|"
        r"announces? (the )?(new|availability)|releases? (the )?new|"
        r"partners? with|partnership with|teams? up with)\b",
    ),
    (
        "legal_regulatory",
        r"\b(lawsuit|sues?|sued|litigation|class action|securities fraud|investigat(es|ion|ing)|"
        r"probe[sd]?|subpoena|antitrust|sec (charges?|filing|probe|investigation)|ftc|doj|"
        r"regulators?|fined?|settlement|settles? (with|charges)|court (rules?|ruling)|"
        r"judge (rules?|ruled)|recall(s|ed|ing)?|fda (approval|rejects?|warning))\b",
    ),
    (
        "ma",
        r"\b(acquires?|acquisition|to buy|merger|merges? with|takeover|buyout|"
        r"stake in|majority stake|spin[- ]?off|divests?|divestiture|"
        r"agrees? to (buy|acquire|sell)|deal to (buy|acquire))\b",
    ),
    (
        "personnel",
        r"\b((ceo|cfo|coo|cto|chairman|president|executive)s? (steps? down|resigns?|departs?|"
        r"to (leave|retire)|named|appointed|hired?)|names? (new )?(ceo|cfo|coo|cto|president)|"
        r"appoints? (new )?(ceo|cfo|coo|cto|president|chairman)|"
        r"(resignation|departure) of (ceo|cfo|chairman))\b",
    ),
    (
        "macro_market",
        r"\b(federal reserve|the fed\b|fomc|interest rates?|inflation|cpi report|jobs report|"
        r"nonfarm payrolls|gdp|market (wrap|recap|update|close)|close update|"
        r"(wall street|stocks?|markets?) (open|close|rally|slide|slump|gain|fall)|"
        r"dow (jones)?|s&p 500|nasdaq composite|treasury yields?|"
        r"the market in 5 minutes)\b",
    ),
)

_COMPILED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern, re.IGNORECASE)) for name, pattern in RUBRIC
)


def rubric_label(headline: str) -> str | None:
    """Rótulo de referência para uma manchete, ou ``None`` se a rubrica não tiver confiança.

    Devolve ``None`` também quando **mais do que um** tipo dispara: uma manchete que é ao
    mesmo tempo resultados e ação de analista é genuinamente ambígua, e uma referência que
    resolve ambiguidades por ordem de lista está a inventar precisão que não tem.
    """
    if not headline:
        return None
    hits = [name for name, pattern in _COMPILED if pattern.search(headline)]
    if len(hits) == 1:
        return hits[0]
    return None


def rubric_labels(headlines: Iterable[str]) -> list[str | None]:
    """A rubrica aplicada a muitas manchetes."""
    return [rubric_label(h) for h in headlines]


# ── Álgebra dos embeddings ────────────────────────────────────────────────────
def l2_normalise(matrix: np.ndarray) -> np.ndarray:
    """Linhas com norma 1, para que o produto interno seja o cosseno.

    Linhas de norma zero ficam a zero em vez de gerar NaN: um vetor nulo não tem direção,
    e propagar NaN partiria silenciosamente o agrupamento a jusante.
    """
    arr = np.asarray(matrix, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"esperava uma matriz 2-D, recebi shape {arr.shape}")
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    safe = np.where(norms > 0.0, norms, 1.0)
    return arr / safe


# ── A taxonomia aprendida ─────────────────────────────────────────────────────
@dataclass(frozen=True)
class EventTaxonomy:
    """Centróides agrupados, cada um com um rótulo de tipo de evento.

    ``centroids`` está normalizado por L2, pelo que atribuir é um produto interno seguido de
    um argmax, sem dependências para lá do NumPy. É isto que permite ao produto usar a
    taxonomia sem carregar o scikit-learn.
    """

    centroids: np.ndarray  # (n_clusters, dim), normalizado por L2
    labels: tuple[str, ...]  # rótulo de tipo de evento por grupo
    terms: tuple[tuple[str, ...], ...] = ()  # termos de topo por grupo (proveniência)

    def __post_init__(self) -> None:
        if self.centroids.ndim != 2:
            raise ValueError(f"os centróides têm de ser 2-D, recebi {self.centroids.shape}")
        if len(self.labels) != self.centroids.shape[0]:
            raise ValueError(
                f"{len(self.labels)} rótulos para {self.centroids.shape[0]} centróides"
            )
        unknown = set(self.labels) - set(EVENT_TYPES)
        if unknown:
            raise ValueError(f"rótulos fora da taxonomia: {sorted(unknown)}")

    @property
    def n_clusters(self) -> int:
        return int(self.centroids.shape[0])

    def assign(self, embeddings: np.ndarray) -> np.ndarray:
        """Índice do grupo mais próximo por linha (cosseno)."""
        arr = np.atleast_2d(np.asarray(embeddings, dtype=np.float64))
        if arr.shape[1] != self.centroids.shape[1]:
            raise ValueError(
                f"dimensão do embedding {arr.shape[1]} != dimensão dos centróides "
                f"{self.centroids.shape[1]}"
            )
        return np.argmax(l2_normalise(arr) @ self.centroids.T, axis=1)

    def label_of(self, embeddings: np.ndarray) -> list[str]:
        """Rótulo de tipo de evento por linha."""
        return [self.labels[i] for i in self.assign(embeddings)]

    def confidence(self, embeddings: np.ndarray) -> np.ndarray:
        """Similaridade do cosseno ao centróide atribuído, em [-1, 1].

        Existe para que o produto possa recusar-se a mostrar um tipo de evento quando a
        manchete não se parece com nenhum grupo. Um rótulo sem confiança é pior do que
        rótulo nenhum.
        """
        arr = np.atleast_2d(np.asarray(embeddings, dtype=np.float64))
        return np.max(l2_normalise(arr) @ self.centroids.T, axis=1)

    # ── Persistência ──────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "centroids": self.centroids.tolist(),
            "labels": list(self.labels),
            "terms": [list(t) for t in self.terms],
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict()), encoding="utf-8")

    @classmethod
    def from_dict(cls, payload: dict) -> EventTaxonomy:
        return cls(
            centroids=np.asarray(payload["centroids"], dtype=np.float64),
            labels=tuple(payload["labels"]),
            terms=tuple(tuple(t) for t in payload.get("terms", ())),
        )

    @classmethod
    def load(cls, path: str | Path) -> EventTaxonomy:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


# ── Métricas de concordância ──────────────────────────────────────────────────
def purity(assignments: Sequence[int], reference: Sequence[str | None]) -> tuple[float, int]:
    """Pureza dos grupos contra rótulos de referência, ignorando os ``None``.

    Para cada grupo toma-se o rótulo de referência mais frequente entre os seus membros
    rotulados; a pureza é a fração de itens rotulados que caem no rótulo maioritário do seu
    próprio grupo. Devolve ``(pureza, n_avaliados)`` — o segundo valor importa tanto como o
    primeiro, porque uma pureza alta sobre 12 itens não diz nada.
    """
    pairs = [(c, r) for c, r in zip(assignments, reference, strict=True) if r is not None]
    if not pairs:
        return 0.0, 0
    by_cluster: dict[int, dict[str, int]] = {}
    for cluster, ref in pairs:
        by_cluster.setdefault(cluster, {})
        by_cluster[cluster][ref] = by_cluster[cluster].get(ref, 0) + 1
    correct = sum(max(counts.values()) for counts in by_cluster.values())
    return correct / len(pairs), len(pairs)


def majority_labels(
    assignments: Sequence[int],
    reference: Sequence[str | None],
    n_clusters: int,
    fallback: str = "macro_market",
) -> tuple[str, ...]:
    """Rótulo maioritário da referência por grupo, para nomear grupos a partir da rubrica.

    Grupos sem nenhum membro rotulado recebem ``fallback``. Isso é uma escolha visível e não
    um acidente: um grupo que a rubrica nunca toca é, na prática, ruído de fluxo de mercado.
    """
    counts: dict[int, dict[str, int]] = {i: {} for i in range(n_clusters)}
    for cluster, ref in zip(assignments, reference, strict=True):
        if ref is None:
            continue
        counts[cluster][ref] = counts[cluster].get(ref, 0) + 1
    out: list[str] = []
    for i in range(n_clusters):
        if counts[i]:
            out.append(max(counts[i].items(), key=lambda kv: (kv[1], kv[0]))[0])
        else:
            out.append(fallback)
    return tuple(out)
