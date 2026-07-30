"""Taxonomia de tipos de evento sobre os embeddings das manchetes — ADITIVO.

*A lacuna que fecha.* A base de casos são 79k manchetes como vetores achatados. A recuperação
sabe dizer "isto parece-se com aqueles", mas nada no sistema sabe **que tipo de acontecimento**
uma manchete é. É essa lacuna que produz o tema≠direção do Caso 3: sem tipo de evento não há
como restringir a recuperação a precedentes do mesmo género.

*O que este script mede, e o que não mede.* Mede se os embeddings MiniLM — que nunca viram um
rótulo de tipo de evento — organizam por si o fluxo de notícias em grupos que **coincidem** com
uma taxonomia escrita por uma pessoa. Não mede se a taxonomia é "a certa": não existe verdade
fundamental para isso.

*A referência.* A rubrica de palavras-chave em `investigator/historical_kb/taxonomy.py`,
commitada **antes** de qualquer agrupamento ter corrido (o histórico do git é o pré-registo).
É de alta precisão e baixa cobertura de propósito: cala-se quando não sabe. Logo, a pureza é
medida só no subconjunto que a rubrica cobre, e esse número é reportado ao lado da pureza,
porque uma pureza alta sobre poucos itens não diz nada.

*Congelados.* Nada aqui toca em `models/`, no dataset da triagem ou nos .md de avaliação
existentes. Camada descritiva.

Uso:
    python scripts/evaluate_event_taxonomy.py
    python scripts/evaluate_event_taxonomy.py --kmin 6 --kmax 24 --seeds 3
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_rand_score, silhouette_score

from investigator.console import force_utf8_stdout
from investigator.historical_kb.taxonomy import (
    EVENT_TYPES,
    EventTaxonomy,
    l2_normalise,
    majority_labels,
    purity,
    rubric_labels,
)

REPO = Path(__file__).resolve().parents[1]
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_event_taxonomy.md"
OUT_MODEL = REPO / "models" / "event_taxonomy.json"

# Subamostras: a silhueta e o agrupamento hierárquico são O(n²) em memória. Com 78.933
# manchetes, o hierárquico completo pediria ~50 TB. Subamostrar é a prática normal; o que
# não é normal é fazê-lo em silêncio, por isso os tamanhos são constantes visíveis e vão
# para o relatório.
SIL_SAMPLE = 10_000
AGGLO_SAMPLE = 5_000


def _load(dataset: Path, cache: Path) -> tuple[pd.DataFrame, np.ndarray]:
    df = pd.read_csv(dataset)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    emb = np.load(cache)
    if len(df) != len(emb):
        raise SystemExit(
            f"desalinhamento: {len(df)} linhas vs {len(emb)} embeddings. "
            "A cache foi construída sobre as linhas já filtradas por split."
        )
    return df, emb


def _top_terms(headlines: list[str], assignments: np.ndarray, n_clusters: int, top: int = 8):
    """Termos de topo por grupo, por TF-IDF do grupo contra o resto do corpus."""
    vec = TfidfVectorizer(max_features=20_000, stop_words="english", ngram_range=(1, 2))
    matrix = vec.fit_transform(headlines)
    vocab = np.array(vec.get_feature_names_out())
    out: list[tuple[str, ...]] = []
    for k in range(n_clusters):
        mask = assignments == k
        if not mask.any():
            out.append(())
            continue
        mean = np.asarray(matrix[mask].mean(axis=0)).ravel()
        out.append(tuple(vocab[np.argsort(mean)[::-1][:top]]))
    return tuple(out)


def _exemplars(headlines: list[str], emb_n: np.ndarray, centroid: np.ndarray, mask, top: int = 3):
    """As manchetes mais próximas de um centróide — a prova de que o rótulo é honesto."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    sims = emb_n[idx] @ centroid
    return [headlines[idx[i]] for i in np.argsort(sims)[::-1][:top]]


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Taxonomia de tipos de evento (aditivo)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--kmin", type=int, default=6)
    ap.add_argument("--kmax", type=int, default=20)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    dataset = Path(args.dataset)
    cache = dataset.with_name("_cache_triage_minilm.npy")
    if not cache.exists():
        raise SystemExit(
            f"Falta a cache de embeddings ({cache.name}). Corre primeiro um dos scripts de "
            "triagem que a constrói, ou gera-a com o SbertEmbedder."
        )

    df, emb = _load(dataset, cache)
    headlines = df["headline"].astype(str).tolist()
    emb_n = l2_normalise(emb)
    print(f"{len(df):,} manchetes · embeddings {emb.shape}")

    # ── A referência, aplicada antes de olhar para qualquer grupo ─────────────
    reference = rubric_labels(headlines)
    covered = sum(r is not None for r in reference)
    ref_counts = Counter(r for r in reference if r is not None)
    print(f"Rubrica: {covered:,} de {len(df):,} manchetes cobertas ({covered / len(df):.1%})")
    for name, count in ref_counts.most_common():
        print(f"   {name:<18} {count:>7,}")

    # ── Escolha de k pela silhueta ────────────────────────────────────────────
    rng = np.random.default_rng(0)
    sil_idx = rng.choice(len(emb_n), size=min(SIL_SAMPLE, len(emb_n)), replace=False)
    ks = list(range(args.kmin, args.kmax + 1, 2))
    print(f"\nA varrer k em {ks} (silhueta sobre {len(sil_idx):,} pontos)…")
    sweep: list[dict] = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(emb_n)
        assign = km.labels_
        sil = silhouette_score(emb_n[sil_idx], assign[sil_idx], metric="cosine")
        pur, n_eval = purity(assign, reference)
        sweep.append({"k": k, "silhouette": float(sil), "purity": float(pur), "n_eval": n_eval})
        print(f"   k={k:<3} silhueta {sil:+.3f}   pureza {pur:.3f} (n={n_eval:,})")

    best = max(sweep, key=lambda r: r["silhouette"])
    k_star = int(best["k"])
    print(f"\nk* = {k_star} (melhor silhueta {best['silhouette']:+.3f})")

    # ── O modelo final ────────────────────────────────────────────────────────
    km = KMeans(n_clusters=k_star, n_init=10, random_state=0).fit(emb_n)
    assign = km.labels_
    centroids = l2_normalise(km.cluster_centers_)
    labels = majority_labels(assign, reference, k_star)
    terms = _top_terms(headlines, assign, k_star)
    pur, n_eval = purity(assign, reference)

    # ── Estabilidade entre sementes ───────────────────────────────────────────
    print(f"\nEstabilidade ({args.seeds} sementes, ARI contra a semente 0)…")
    aris: list[float] = []
    for seed in range(1, args.seeds + 1):
        other = KMeans(n_clusters=k_star, n_init=10, random_state=seed).fit(emb_n).labels_
        ari = adjusted_rand_score(assign, other)
        aris.append(float(ari))
        print(f"   semente {seed}: ARI {ari:.3f}")

    # ── Alternativa hierárquica, na mesma subamostra ──────────────────────────
    agg_idx = rng.choice(len(emb_n), size=min(AGGLO_SAMPLE, len(emb_n)), replace=False)
    agglo = AgglomerativeClustering(n_clusters=k_star, metric="cosine", linkage="average").fit(
        emb_n[agg_idx]
    )
    agglo_sil = silhouette_score(emb_n[agg_idx], agglo.labels_, metric="cosine")
    agglo_pur, agglo_n = purity(agglo.labels_, [reference[i] for i in agg_idx])
    km_sub_sil = silhouette_score(emb_n[agg_idx], assign[agg_idx], metric="cosine")
    print(
        f"\nHierárquico (n={len(agg_idx):,}): silhueta {agglo_sil:+.3f} vs k-means "
        f"{km_sub_sil:+.3f} na MESMA subamostra; pureza {agglo_pur:.3f} (n={agglo_n:,})"
    )

    # ── Guardar a taxonomia ───────────────────────────────────────────────────
    tax = EventTaxonomy(centroids=centroids, labels=labels, terms=terms)
    OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    tax.save(OUT_MODEL)
    conf = tax.confidence(emb)
    print(f"\nTaxonomia guardada em {OUT_MODEL.relative_to(REPO)}")

    # ── Relatório ─────────────────────────────────────────────────────────────
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    add = lines.append
    add("# Taxonomia de tipos de evento — agrupamento não supervisionado das manchetes")
    add("")
    add(f"> Gerado por `scripts/evaluate_event_taxonomy.py` em {stamp}.")
    add("> **Aditivo.** Não altera `models/` (exceto o artefacto novo `event_taxonomy.json`),")
    add("> o dataset de triagem, nem qualquer .md de avaliação existente.")
    add("")
    add("## A pergunta")
    add("")
    add("Os embeddings MiniLM nunca viram um rótulo de tipo de evento. Organizam mesmo assim o")
    add("fluxo de notícias em grupos que coincidem com uma taxonomia escrita por uma pessoa?")
    add("")
    add("Isto importa para o produto e não só para a curiosidade: sem tipo de evento, a")
    add("recuperação só sabe comparar por semelhança geral, que é exatamente o mecanismo que")
    add("faz uma manchete positiva recuperar um cacho de precedentes negativos (Caso 3).")
    add("")
    add("## Como a referência foi construída (e porque é credível)")
    add("")
    add("A referência é uma **rubrica de palavras-chave** publicada em")
    add("`investigator/historical_kb/taxonomy.py`, escrita a partir da lista de tipos de evento")
    add("e **commitada antes de qualquer agrupamento ter corrido** — o histórico do git é o")
    add("pré-registo. Sem essa ordem, a rubrica podia ter sido afinada até concordar com os")
    add("grupos, e a medição não valeria nada.")
    add("")
    add("A rubrica é de **alta precisão e baixa cobertura** por desenho. Devolve `None` quando")
    add("nenhum padrão dispara e também quando **mais do que um** dispara, porque uma manchete")
    add("que é ao mesmo tempo resultados e ação de analista é genuinamente ambígua.")
    add("")
    add(f"Cobertura: **{covered:,} de {len(df):,}** manchetes (**{covered / len(df):.1%}**).")
    add("Todos os números de pureza abaixo são sobre este subconjunto, e o `n` vai sempre junto.")
    add("")
    add("| Tipo de evento | Manchetes cobertas |")
    add("|---|---:|")
    for name in EVENT_TYPES:
        add(f"| `{name}` | {ref_counts.get(name, 0):,} |")
    add(f"| **(sem rótulo)** | **{len(df) - covered:,}** |")
    add("")
    add("## Escolha de k")
    add("")
    add(f"Silhueta calculada sobre uma subamostra de {SIL_SAMPLE:,} pontos (é O(n²); com")
    add(f"{len(df):,} manchetes a matriz completa não cabe em memória).")
    add("")
    add("| k | Silhueta | Pureza vs rubrica | n avaliado |")
    add("|---:|---:|---:|---:|")
    for row in sweep:
        star = " ←" if row["k"] == k_star else ""
        add(
            f"| {row['k']}{star} | {row['silhouette']:+.3f} | {row['purity']:.3f} "
            f"| {row['n_eval']:,} |"
        )
    add("")
    add(f"**k\\* = {k_star}**, pela silhueta.")
    add("")
    add("## Resultado")
    add("")
    add(f"- **Pureza contra a rubrica: {pur:.3f}** sobre {n_eval:,} manchetes rotuladas.")
    add(f"- **Estabilidade entre sementes:** ARI {np.mean(aris):.3f} ")
    add(f"  (mín {min(aris):.3f}, máx {max(aris):.3f}, {len(aris)} sementes contra a semente 0).")
    add(
        f"- **k-means vs hierárquico** na mesma subamostra de {len(agg_idx):,}: "
        f"silhueta {km_sub_sil:+.3f} vs {agglo_sil:+.3f}; "
        f"pureza {pur:.3f} vs {agglo_pur:.3f}."
    )
    add(
        f"- **Confiança** (cosseno ao centróide atribuído): mediana {np.median(conf):.3f}, "
        f"1.º decil {np.quantile(conf, 0.1):.3f}."
    )
    add("")
    add("### Os grupos")
    add("")
    add("| # | Rótulo | n | Termos de topo (TF-IDF) | Manchete mais próxima do centróide |")
    add("|---:|---|---:|---|---|")
    for k in range(k_star):
        mask = assign == k
        ex = _exemplars(headlines, emb_n, centroids[k], mask, top=1)
        head = ex[0][:70].replace("|", "/") if ex else "—"
        top5 = ", ".join(terms[k][:5]).replace("|", "/")
        add(f"| {k} | `{labels[k]}` | {int(mask.sum()):,} | {top5} | {head} |")
    add("")
    add("## Leitura honesta")
    add("")
    if pur >= 0.6:
        add(f"A pureza de {pur:.3f} está bem acima do que se esperaria por acaso: com")
        add(f"{len(ref_counts)} tipos presentes e a distribuição desequilibrada acima, atribuir")
        add("tudo ao tipo mais frequente daria")
        add(f"{max(ref_counts.values()) / covered:.3f}. Os embeddings estão a recuperar")
        add("estrutura de tipo de evento que ninguém lhes ensinou.")
    else:
        add(f"A pureza de {pur:.3f} é modesta. Comparar com a linha de base trivial: atribuir")
        add(f"tudo ao tipo mais frequente daria {max(ref_counts.values()) / covered:.3f}.")
        add("Reportado tal como caiu.")
    add("")
    add("Três limitações que não se devem esconder:")
    add("")
    add("1. **A referência é uma rubrica, não um humano.** Mede-se concordância entre dois")
    add("   métodos, não concordância com a verdade. A rubrica erra onde a linguagem é")
    add("   indireta, e essas manchetes contam contra os grupos mesmo quando os grupos estão")
    add("   certos.")
    add("2. **A cobertura é parcial** — a pureza nada diz sobre as manchetes que a rubrica não")
    add("   apanha, que são a maioria.")
    add("3. **k foi escolhido pela silhueta, não pela pureza.** De propósito: escolher k por")
    add("   pureza seria afinar o método não supervisionado contra a sua própria avaliação.")
    add("")
    add("## Para que serve, no produto")
    add("")
    add("A taxonomia guardada (`models/event_taxonomy.json`) é NumPy puro: produto interno e")
    add("argmax, sem scikit-learn em produção. Dá duas coisas que não existiam:")
    add("")
    add("1. Um **tipo de evento** por alerta (\"isto é um item regulatório\").")
    add("2. Recuperação **filtrável por tipo**, que ataca diretamente o tema≠direção: comparar")
    add("   um item regulatório com precedentes regulatórios, e não com tudo o que se lhe")
    add("   pareça.")
    add("")
    add("O campo `confidence` existe para o produto poder **recusar** mostrar um tipo quando a")
    add("manchete não se parece com nenhum grupo. Um rótulo sem confiança é pior do que rótulo")
    add("nenhum.")
    add("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Relatório escrito em {OUT_MD.relative_to(REPO)}")

    summary = {
        "k": k_star,
        "silhouette": best["silhouette"],
        "purity": pur,
        "n_eval": n_eval,
        "coverage": covered / len(df),
        "ari_mean": float(np.mean(aris)),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
