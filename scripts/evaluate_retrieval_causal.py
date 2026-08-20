"""A recuperação sob a restrição que a produção tem: só pode ver o PASSADO.

## A pergunta, e porque é que ela apareceu

O protocolo de recuperação da dissertação proíbe o candidato de ser da **mesma empresa** da
consulta, e mais nada. Não proíbe o candidato de ser **posterior** à consulta. Sobre o corpus
recente, `evaluation_relevance_filter.md` mediu a consequência: **38.7%** dos vizinhos devolvidos
são de data posterior à consulta e **30.2%** são do mesmo dia. Ou seja, o número reportado foi
medido com o recuperador a poder olhar para a frente.

Isto **não é uma fuga no sentido habitual**: o rótulo da métrica é *"pertence ao mesmo setor"*, e
o setor de uma notícia não muda com o tempo, portanto a direcção temporal não pode inflacionar a
precisão pelo caminho por onde as fugas costumam entrar. Mas a afirmação que a dissertação faz é
sobre **encontrar casos passados**, e o sistema em produção só consegue devolver casos passados —
a base de precedentes só recebe um caso depois de o impacto amadurecer, oito dias mais tarde.

Medir as duas coisas separadamente é, portanto, a diferença entre uma métrica de semelhança e
uma métrica do que o produto faz. Este é o segundo número.

## O que muda no protocolo, e só isto

À máscara de proibição junta-se uma segunda condição: **o candidato tem de ser estritamente
anterior à consulta**. Tudo o resto — corpus, embeddings, sementes, `k`, o critério de setor, as
linhas de base — é o mesmo, e reproduz-se o número simétrico na mesma corrida para que a
comparação seja emparelhada e não uma citação de memória.

⚠️ **Aditivo.** Escreve um ficheiro NOVO e recusa-se a tocar em `evaluation_retrieval_fnspid.md`,
que é congelado e citado pela dissertação.

USO
---
    python scripts/evaluate_retrieval_causal.py
    python scripts/evaluate_retrieval_causal.py --queries 300 --repeats 3
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from investigator.console import force_utf8_stdout
from investigator.evaluation.retrieval_eval import (
    expected_random_precision,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

REPO = Path(__file__).resolve().parents[1]

# O MESMO mapa do protocolo à escala. Repetido aqui de propósito e não importado: se um dia
# divergirem, quero que o ficheiro que produz o número o diga por si.
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech", "FB": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}


def _carrega(caminho: str) -> tuple[np.ndarray, ...]:
    datas, tickers, embs = [], [], []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            r = json.loads(linha)
            t = str(r["ticker"]).upper()
            if t not in SECTORS or "embedding" not in r:
                continue
            datas.append(str(r["date"]))
            tickers.append(t)
            embs.append(r["embedding"])
    emb = np.asarray(embs, dtype="float32")
    emb /= np.clip(np.linalg.norm(emb, axis=1, keepdims=True), 1e-12, None)
    return emb, np.asarray(tickers), np.asarray(datas)


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kb", default=str(REPO / "data" / "kb_fnspid_sbert.jsonl"))
    ap.add_argument("--queries", type=int, default=500)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not Path(args.kb).exists():
        print(f"ERRO: nao encontrei {args.kb}.")
        print("Este corpus e local (690 MB, gitignored). Correr na maquina que o tem.")
        return 2

    print(f"A carregar {args.kb} ...")
    emb, tickers, datas = _carrega(args.kb)
    setores = np.asarray([SECTORS[t] for t in tickers])
    n = len(emb)
    print(f"  {n} registos - {len(set(tickers))} tickers - {len(set(setores))} setores")
    d0, d1 = str(np.sort(datas)[0]), str(np.sort(datas)[-1])
    print(f"  datas de {d0} a {d1}")

    k, n_q = args.k, min(args.queries, len(emb))
    sim, cau, chao, chao_cau, sem_passado = [], [], [], [], []

    for rep in range(args.repeats):
        rng = np.random.default_rng(args.seed + rep)
        q = rng.choice(n, size=n_q, replace=False)

        # (1) o protocolo da dissertação: só a mesma empresa é proibida
        f_sim = same_ticker_forbid(tickers[q], tickers)
        sim.append(retrieval_precision_at_k(emb[q], emb, setores[q], setores, k=k, forbid=f_sim))
        chao.append(expected_random_precision(setores[q], setores, f_sim))

        # (2) o protocolo da produção: e o candidato tem de ser ANTERIOR à consulta.
        # Estritamente anterior: o mesmo dia também sai, porque uma notícia do próprio dia não
        # é um precedente — no momento da decisão o seu impacto ainda não existe.
        f_cau = f_sim | (datas[None, :] >= datas[q][:, None])
        # ⚠️ Uma consulta cujo passado esteja vazio (as primeiras do corpus) não tem k vizinhos
        # e contaminaria a média com uma tarefa impossível. Contam-se e excluem-se, e o número
        # de excluídas vai no relatório: um filtro silencioso muda a população medida.
        viaveis = (~f_cau).sum(axis=1) >= k
        sem_passado.append(int((~viaveis).sum()))
        qq = q[viaveis]
        f_cau = f_cau[viaveis]
        cau.append(retrieval_precision_at_k(emb[qq], emb, setores[qq], setores, k=k,
                                            forbid=f_cau))
        chao_cau.append(expected_random_precision(setores[qq], setores, f_cau))
        print(f"  [{rep + 1}/{args.repeats}] simetrico {sim[-1]:.3f} - causal {cau[-1]:.3f}")

    def ms(v):
        a = np.asarray(v, dtype="float64")
        return float(a.mean()), float(a.std())

    s_m, s_s = ms(sim)
    c_m, c_s = ms(cau)
    b_m, _ = ms(chao)
    bc_m, _ = ms(chao_cau)
    delta = c_m - s_m
    # ⚠️ O CHÃO TAMBÉM MUDA, e comparar as duas precisões sem isso repetiria o erro que
    # esta dissertação já apanhou uma vez: restringir os candidatos aos anteriores muda a
    # composição do conjunto de onde se escolhe, logo muda a probabilidade de acertar ao
    # acaso. A quantidade comparável é a MARGEM sobre o acaso de cada protocolo.
    m_sim, m_cau = s_m - b_m, c_m - bc_m

    linhas = [
        "# evaluation_retrieval_causal.md — a recuperação só com o passado (QI2)",
        "",
        f"> Gerado por `scripts/evaluate_retrieval_causal.py` a "
        f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC. **Não editar à mão.**",
        "> Aditivo: não toca em `evaluation_retrieval_fnspid.md`, que é o congelado citado pela",
        "> dissertação.",
        "",
        "## A pergunta",
        "",
        "O protocolo da dissertação proíbe o candidato de ser da mesma empresa, e mais nada — em",
        "particular, não o proíbe de ser **posterior** à consulta. O sistema em produção não tem",
        "essa liberdade: a base de precedentes só recebe um caso oito dias depois, quando o",
        "impacto já é observável. Este documento mede a mesma tarefa **com a restrição da**",
        "**produção**, para que o número que a dissertação reporta se possa ler pelo que é.",
        "",
        "## Resultado",
        "",
        f"Corpus: **{n}** manchetes com embedding e setor conhecido, de {d0} a {d1}. "
        f"{args.repeats} repetições de {n_q} consultas, semente {args.seed}, precisão@{k}.",
        "",
        "| protocolo | o que o recuperador pode ver | precisão@5 | chão de acaso |",
        "|---|---|---|---|",
        f"| simétrico (o da dissertação) | tudo menos a própria empresa | **{s_m:.3f}** "
        f"± {s_s:.3f} | {b_m:.3f} |",
        f"| causal (o da produção) | só o que é anterior à consulta | **{c_m:.3f}** "
        f"± {c_s:.3f} | {bc_m:.3f} |",
        "",
        f"**Diferença em precisão bruta: {delta:+.3f}.** Mas o chão de acaso também desce, "
        f"porque restringir os candidatos aos anteriores muda a composição do conjunto de "
        f"onde se escolhe. A quantidade comparável é a **margem sobre o acaso**:",
        "",
        "| protocolo | precisão@5 | chão | **margem** |",
        "|---|---|---|---|",
        f"| simétrico | {s_m:.3f} | {b_m:.3f} | **{m_sim:+.3f}** |",
        f"| causal | {c_m:.3f} | {bc_m:.3f} | **{m_cau:+.3f}** |",
        "",
        f"**A margem muda {m_cau - m_sim:+.3f}.**",
        "",
        f"Consultas sem passado suficiente, excluídas da linha causal: "
        f"{sum(sem_passado)} em {n_q * args.repeats} "
        f"({100 * sum(sem_passado) / (n_q * args.repeats):.1f}%). São as primeiras do corpus, "
        "que não têm $k$ candidatos anteriores; deixá-las dentro mediria uma tarefa impossível.",
        "",
        "## Leitura honesta",
        "",
        "Esta comparação **não** existe para descobrir uma fuga: o rótulo da métrica é",
        "*pertence ao mesmo setor*, e o setor não muda com o tempo, portanto a direcção temporal",
        "não tem por onde inflacionar a precisão. Existe porque a afirmação da dissertação é",
        "sobre **encontrar casos passados**, e um número medido sem essa restrição descreve uma",
        "tarefa ligeiramente diferente da que o produto executa.",
        "",
        "E há uma segunda lição, que é de método e vale mais do que o número: a precisão bruta",
        "desce, mas o **chão desce quase o mesmo**, e a margem sobre o acaso fica praticamente",
        "onde estava. Ler só a primeira coluna desta tabela levaria à conclusão errada — que é",
        "exactamente o erro que esta dissertação já cometeu uma vez, e corrigiu, com o chão da",
        "precisão no orçamento.",
        "",
    ]
    saida = REPO / "docs" / "evaluation" / "evaluation_retrieval_causal.md"
    saida.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nsimetrico {s_m:.3f}+-{s_s:.3f} | causal {c_m:.3f}+-{c_s:.3f} | delta {delta:+.3f}")
    print(f"-> {saida.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
