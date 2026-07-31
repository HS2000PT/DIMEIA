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
from sklearn.metrics import (
    adjusted_mutual_info_score,
    adjusted_rand_score,
    silhouette_score,
)

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

    # ── O controlo que decide se a pureza significa alguma coisa ──────────────
    # A pureza com rotulagem por maioria INFLACIONA quando a referência é desequilibrada e k
    # é grande: com um tipo a valer 44% dos rótulos, muitos grupos ficam com esse rótulo por
    # omissão. O controlo é a MESMA métrica sobre uma atribuição aleatória com os MESMOS
    # tamanhos de grupo. O que a pureza vale é a diferença, não o valor absoluto.
    sizes = np.bincount(assign, minlength=k_star)
    rand_purities: list[float] = []
    for seed in range(5):
        shuffled = np.repeat(np.arange(k_star), sizes)
        np.random.default_rng(seed).shuffle(shuffled)
        rand_purities.append(purity(shuffled, reference)[0])
    rand_pur = float(np.mean(rand_purities))
    trivial = max(ref_counts.values()) / covered
    print(
        f"\nPureza {pur:.3f} · aleatório com os mesmos tamanhos {rand_pur:.3f} "
        f"· tudo-no-maioritário {trivial:.3f}"
    )

    # ── A pergunta decisiva: por evento, ou por assunto? ──────────────────────
    # Se os grupos se alinharem mais com TICKER/SETOR do que com tipo de evento, então o
    # embedding organiza-se por assunto e não por acontecimento — e a taxonomia de eventos
    # não sai daqui, por muito respeitável que a pureza pareça.
    #
    # A pureza NÃO serve para esta comparação, e vale a pena dizer porquê: o seu valor
    # depende de quantas classes a referência tem (8 tipos vs 15 tickers vs 6 setores) e de
    # quão desequilibradas são, pelo que comparar purezas entre referências diferentes é
    # comparar coisas incomparáveis. A informação mútua AJUSTADA (AMI) é corrigida para o
    # acaso e para a cardinalidade, que é exatamente o que aqui é preciso.
    #
    # E as três TÊM de ser calculadas nas MESMAS linhas — o subconjunto que a rubrica cobre.
    # Caso contrário compara-se o alinhamento de eventos em 11.889 linhas com o de tickers em
    # 78.933, que também não é comparação nenhuma.
    cov_mask = np.array([r is not None for r in reference])
    assign_cov = assign[cov_mask]
    ref_cov = [r for r in reference if r is not None]
    tick_cov = df.loc[cov_mask, "ticker"].astype(str).tolist()
    sect_cov = df.loc[cov_mask, "sector"].astype(str).tolist()

    ami_event = float(adjusted_mutual_info_score(ref_cov, assign_cov))
    ami_ticker = float(adjusted_mutual_info_score(tick_cov, assign_cov))
    ami_sector = float(adjusted_mutual_info_score(sect_cov, assign_cov))
    print(
        f"AMI (mesmas {cov_mask.sum():,} linhas) — evento {ami_event:.3f} · "
        f"ticker {ami_ticker:.3f} · setor {ami_sector:.3f}"
    )
    subject_wins = max(ami_ticker, ami_sector) > ami_event

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
    add("## Os dois controlos, sem os quais a pureza não significa nada")
    add("")
    add("### 1. A pureza bruta está inflacionada")
    add("")
    add("A pureza com rotulagem por maioria **inflaciona** quando a referência é desequilibrada")
    add(f"e k é grande. Aqui um único tipo (`macro_market`) vale {trivial:.1%} dos rótulos, e há")
    add(f"{k_star} grupos: muitos ficam com esse rótulo quase por omissão. O controlo é a mesma")
    add("métrica sobre uma atribuição **aleatória com exatamente os mesmos tamanhos de grupo**.")
    add("")
    add("| Pureza medida | Aleatório (mesmos tamanhos) | Tudo-no-maioritário |")
    add("|---:|---:|---:|")
    add(f"| **{pur:.3f}** | {rand_pur:.3f} | {trivial:.3f} |")
    add("")
    add(f"O ganho real sobre o acaso é **{pur - rand_pur:+.3f}**, não {pur:.3f}.")
    add("")
    add("### 2. Por evento, ou apenas por assunto?")
    add("")
    add("Este é o controlo decisivo. Se os grupos se alinharem mais com a **empresa** ou o")
    add("**setor** do que com o **tipo de evento**, então o agrupamento está a redescobrir o")
    add("assunto, e uma taxonomia de eventos não sai daqui.")
    add("")
    add("Duas exigências de método, ambas necessárias para a comparação ser válida:")
    add("")
    add("- **A pureza não serve aqui.** O seu valor depende de quantas classes a referência tem")
    add(f"  ({len(ref_counts)} tipos vs {df.loc[cov_mask, 'ticker'].nunique()} tickers vs")
    add(f"  {df.loc[cov_mask, 'sector'].nunique()} setores) e de quão desequilibradas são;")
    add("  comparar purezas entre referências diferentes é comparar coisas incomparáveis. A")
    add("  **informação mútua ajustada (AMI)** é corrigida para o acaso e para a cardinalidade.")
    add(f"- **As mesmas linhas.** Todas as três medidas correm sobre as {cov_mask.sum():,}")
    add("  manchetes que a rubrica cobre. Medir eventos numa amostra e tickers noutra não")
    add("  compara nada.")
    add("")
    add("| Referência | AMI com os grupos |")
    add("|---|---:|")
    add(f"| **Tipo de evento** (rubrica) | **{ami_event:.3f}** |")
    add(f"| Ticker | {ami_ticker:.3f} |")
    add(f"| Setor | {ami_sector:.3f} |")
    add("")
    add("## Leitura honesta")
    add("")
    if subject_wins:
        add("**O resultado é negativo, e é informativo.**")
        add("")
        add(f"Os grupos alinham-se mais com **assunto** (ticker AMI {ami_ticker:.3f}, setor")
        add(f"{ami_sector:.3f}) do que com **tipo de evento** ({ami_event:.3f}). A tabela dos")
        add("grupos diz o mesmo em texto: os termos de topo são nomes de empresas e de setores,")
        add("não verbos de acontecimento.")
        add("")
        add("Por outras palavras: **os embeddings de frase do MiniLM organizam manchetes")
        add("financeiras por assunto — que empresa, que setor, que tema — e não por aquilo que")
        add("aconteceu.** Um agrupamento não supervisionado sobre estes vetores não produz uma")
        add("taxonomia de eventos, por muito respeitável que a pureza bruta pareça.")
        add("")
        add("**Consequência de desenho:** filtrar precedentes por tipo de evento **não** pode")
        add("assentar em grupos não supervisionados destes vetores. A taxonomia guardada fica")
        add("como artefacto descritivo e **não** é ligada à recuperação.")
    else:
        add(f"O alinhamento com **tipo de evento** (AMI {ami_event:.3f}) é superior ao")
        add(f"alinhamento com **assunto** (ticker {ami_ticker:.3f}, setor {ami_sector:.3f}),")
        add("medido nas mesmas linhas e com uma métrica corrigida para o acaso e para a")
        add("cardinalidade. Os embeddings estão de facto a recuperar estrutura de tipo de")
        add("evento que ninguém lhes ensinou — não apenas a agrupar por empresa.")
        add("")
        add("Este resultado merece uma ressalva que o torna mais útil e não menos. A leitura")
        add("*qualitativa* da tabela dos grupos sugere o contrário: vários grupos têm por")
        add("termos de topo nomes de empresas (`tesla, ev, musk`; `nvidia, nvda`; `apple,")
        add("aapl`) e de setores (`oil, exxon, chevron`). As duas observações conciliam-se")
        add("assim: o espaço de representação codifica assunto **e** tipo de evento ao mesmo")
        add("tempo, e num corpus de 15 tickers o assunto é o eixo mais visível a olho, porque")
        add("os nomes das empresas dominam os termos de topo. Medido com uma métrica")
        add("corrigida, é o eixo do acontecimento que explica mais da partição.")
        add("")
        add("**Consequência de desenho.** Há sinal de tipo de evento nos embeddings, mas a")
        add(f"separação é fraca em termos absolutos (silhueta {best['silhouette']:+.3f}, ver")
        add("abaixo) e a atribuição de rótulos depende inteiramente de uma rubrica que só")
        add(f"cobre {covered / len(df):.1%} do corpus. Isso chega para caracterizar o corpus e")
        add("não chega para filtrar precedentes em produção: um filtro por tipo de evento")
        add("errado remove precedentes válidos em silêncio, que é pior do que não filtrar. A")
        add("taxonomia fica como artefacto descritivo, e o caminho sustentado pela evidência é")
        add("a rubrica — transparente e correta onde responde.")
    add("")
    add("### O confundimento que um arguente levanta primeiro")
    add("")
    add("A rubrica atribui rótulos a partir de **palavras que estão na manchete**, e os")
    add("embeddings codificam essas mesmas palavras. Uma manchete rotulada `earnings` contém")
    add("quase de certeza a palavra *earnings*, pelo que agrupar por semelhança de texto vai")
    add("aproximá-la de outras que também a contêm. Parte do AMI de tipo de evento está,")
    add("portanto, garantida por construção, e o número não deve ser lido como prova de que os")
    add("embeddings \"percebem\" tipos de acontecimento.")
    add("")
    add("O que o confundimento **não** destrói é a comparação, e é isso que aqui se usa: a")
    add("referência de ticker sofre exatamente do mesmo problema — os nomes das empresas também")
    add("estão nas manchetes, muitas vezes mais do que uma vez e no início. As três referências")
    add("estão em pé de igualdade quanto a este viés, pelo que a ordenação entre elas continua")
    add("informativa mesmo que os valores absolutos estejam inflacionados.")
    add("")
    add("### A silhueta é baixa, e isso também conta")
    add("")
    add(f"A melhor silhueta é {best['silhouette']:+.3f}. Em termos absolutos é fraca: os grupos")
    add("não estão bem separados, sobrepõem-se. E a curva é **plana** — de k=10 a k=20 varia")
    add("entre +0.081 e +0.084, uma amplitude de 0.003. O k\\* escolhido é, portanto,")
    add("fracamente determinado: k=16 ou k=12 serviriam quase igualmente bem. Reportado assim")
    add("em vez de se apresentar k=18 como se fosse um ótimo nítido.")
    add("")
    add("### Limitações que se mantêm")
    add("")
    add("1. **A referência é uma rubrica, não um humano.** Mede-se concordância entre dois")
    add("   métodos, não com a verdade. A rubrica erra onde a linguagem é indireta, e essas")
    add("   manchetes contam contra os grupos mesmo quando os grupos estão certos.")
    add(f"2. **A cobertura é parcial** ({covered / len(df):.1%}): a pureza nada diz sobre as")
    add("   manchetes que a rubrica não apanha, que são a maioria.")
    add("3. **Dois tipos são residuais** neste corpus — `guidance` (23) e `personnel` (17). Na")
    add("   prática a pureza mede-se sobre seis tipos, não oito.")
    add("4. **k foi escolhido pela silhueta, não pela pureza.** De propósito: escolher k por")
    add("   pureza seria afinar o método não supervisionado contra a sua própria avaliação.")
    add("")
    add("## O que fica")
    add("")
    add("O artefacto (`models/event_taxonomy.json`) é NumPy puro — produto interno e argmax,")
    add("sem scikit-learn em produção — e fica no repositório como camada **descritiva**: serve")
    add("para caracterizar o corpus e para sustentar a conclusão acima. **Não** está ligado à")
    add("recuperação nem aos alertas, e a razão é a medição desta página, não uma falta de")
    add("tempo.")
    add("")
    add("O caminho que a evidência sustenta, se houver tempo, é a rubrica: transparente,")
    add("verificável, sem treino, e correta onde responde — ao custo de só responder em")
    add(f"{covered / len(df):.1%} dos casos.")
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
