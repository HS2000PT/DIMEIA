"""Avalia os braços da QI4 no mesmo arnês, com as duas métricas que a pergunta exige.

    python -m scripts.avaliar_qi4 \\
        --modelo base=all-MiniLM-L6-v2 \\
        --modelo magnitude=data/qi4_modelos/magnitude \\
        --modelo direcao=data/qi4_modelos/direcao \\
        --out docs/evaluation/evaluation_qi4.md

Todos os modelos vêem as **mesmas consultas** (a semente fixa a amostragem antes de qualquer
modelo entrar), o que torna as comparações emparelhadas. O acaso é calculado uma vez por
repetição, com a mesma máscara, e serve de referência às duas métricas.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.qi4 import avaliacao as A
from investigator.qi4 import colapso as C

REPO = Path(__file__).resolve().parents[1]


def codificar(caminho: str, textos: list[str], lote: int = 256) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    m = SentenceTransformer(caminho)
    v = m.encode(textos, batch_size=lote, normalize_embeddings=True,
                 convert_to_numpy=True, show_progress_bar=False)
    return np.asarray(v, dtype="float32")


def vizinhos_ao_acaso(consultas: np.ndarray, tickers: np.ndarray, datas: np.ndarray | None,
                      k: int, rng: np.random.Generator) -> np.ndarray:
    """`k` candidatos elegíveis ao acaso por consulta — a referência das duas métricas."""
    elegivel = A.mascara(consultas, tickers, datas,
                         datas[consultas] if datas is not None else None)
    saida = np.empty((len(consultas), k), dtype="int64")
    for i in range(len(consultas)):
        pool = np.flatnonzero(elegivel[i])
        if len(pool) < k:
            # Nao se chega aqui com o lote filtrado por `consultas_viaveis`. Se se chegar, e
            # defeito de quem chamou: `replace=True` sobre um conjunto pequeno inventaria
            # repeticoes e sobre um conjunto vazio nao tem sentido nenhum.
            raise ValueError(
                f"consulta {consultas[i]} tem {len(pool)} candidatos elegiveis para k={k}; "
                "filtrar o lote com A.consultas_viaveis antes de medir"
            )
        saida[i] = rng.choice(pool, size=k, replace=False)
    return saida


def medir(vetores: np.ndarray, consultas: np.ndarray, tickers: np.ndarray,
          setores: np.ndarray, grandeza: np.ndarray, datas: np.ndarray | None,
          k: int) -> tuple[float, float]:
    viz = A.topo_k(vetores, consultas, tickers, k=k, datas=datas)
    return (A.comparabilidade(grandeza[consultas], grandeza[viz]),
            A.precisao_setor(consultas, viz, setores))


def ms(v: list[float]) -> tuple[float, float]:
    a = np.asarray(v, dtype="float64")
    return float(a.mean()), float(a.std(ddof=1)) if len(a) > 1 else 0.0


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Avaliação dos braços da QI4")
    ap.add_argument("--dataset", default=str(REPO / "data" / "qi4_dataset.csv"))
    ap.add_argument("--modelo", action="append", required=True,
                    help="nome=caminho; repetir por cada braço")
    ap.add_argument("--bloco", default="test")
    ap.add_argument("--horizonte", type=int, default=3)
    ap.add_argument("--consultas", type=int, default=500)
    ap.add_argument("--repeticoes", type=int, default=5)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--causal", action="store_true",
                    help="exige que o precedente seja anterior à consulta (o que a produção faz)")
    ap.add_argument("--out", default=str(REPO / "data" / "_arquivo" / "_qi4_avaliacao.md"))
    args = ap.parse_args()

    coluna = f"abn_h{args.horizonte}"
    df = pd.read_csv(args.dataset).dropna(subset=[coluna])
    df = df[df["split"] == args.bloco].reset_index(drop=True)
    textos = df["headline"].astype(str).tolist()
    tickers = df["ticker"].to_numpy()
    setores = df["sector"].to_numpy()
    grandeza = df[coluna].abs().to_numpy(dtype="float64")
    datas = df["date"].to_numpy().astype(str) if args.causal else None
    print(f"Bloco {args.bloco}: {len(df):,} manchetes · {len(set(tickers))} empresas "
          f"· protocolo {'causal' if args.causal else 'simétrico'}")

    # As consultas são sorteadas ANTES de qualquer modelo: todos veem exactamente as mesmas.
    lotes = [A.amostrar_consultas(len(df), args.consultas, seed=args.seed + r)
             for r in range(args.repeticoes)]

    # E são filtradas ANTES também, pela mesma razão: uma consulta sem `k` candidatos elegíveis
    # não tem resposta possível, e o filtro não depende de modelo nenhum, pelo que aplicá-lo
    # aqui mantém os braços emparelhados. O que não se pode é filtrar em silêncio.
    sorteadas = sum(len(c) for c in lotes)
    lotes = [c[A.consultas_viaveis(c, tickers, datas, args.k)] for c in lotes]
    viaveis = sum(len(c) for c in lotes)
    excluidas = sorteadas - viaveis
    if excluidas:
        print(f"⚠ excluídas {excluidas} de {sorteadas} consultas ({excluidas / sorteadas:.2%}) "
              f"por terem menos de k={args.k} candidatos elegíveis "
              f"({'protocolo causal' if args.causal else 'protocolo simétrico'})")
    else:
        print(f"{viaveis} consultas, nenhuma excluída (todas com ≥ k={args.k} elegíveis)")
    if not viaveis:
        print("ERRO: nenhuma consulta viável — nada a medir.")
        return 1

    acaso_c, acaso_p = [], []
    for r, consultas in enumerate(lotes):
        viz = vizinhos_ao_acaso(consultas, tickers, datas, args.k,
                                np.random.default_rng(args.seed + 1000 + r))
        acaso_c.append(A.comparabilidade(grandeza[consultas], grandeza[viz]))
        acaso_p.append(A.precisao_setor(consultas, viz, setores))

    modelos = dict(m.split("=", 1) for m in args.modelo)
    resultados: dict[str, dict] = {}
    for nome, caminho in modelos.items():
        print(f"\n{nome}: a codificar {len(textos):,} manchetes…", flush=True)
        v = codificar(caminho, textos)

        # A porta que faltou na primeira tentativa: um modelo colapsado produz uma tabela
        # plausível e sem valor nenhum. Mede-se ANTES de calcular qualquer métrica.
        perfil = C.perfil(v[:1500])
        marca = "COLAPSADO" if perfil["colapsou"] else "ok"
        print(f"  dispersão [{marca}]: cosseno entre manchetes diferentes "
              f"{perfil['cosseno_medio']:.4f} · norma do vetor médio "
              f"{perfil['norma_do_vetor_medio']:.4f}")
        if perfil["colapsou"]:
            print(f"  ⚠️  {nome} perdeu a capacidade de distinguir manchetes. "
                  "As métricas abaixo NÃO são interpretáveis.")

        comp, prec = [], []
        for consultas in lotes:
            c, p = medir(v, consultas, tickers, setores, grandeza, datas, args.k)
            comp.append(c)
            prec.append(p)
        cm, cs = ms(comp)
        pm, ps = ms(prec)
        resultados[nome] = {"caminho": caminho, "comparabilidade": cm, "comp_dp": cs,
                            "precisao": pm, "prec_dp": ps, "dispersao": perfil,
                            "comp_por_repeticao": comp, "prec_por_repeticao": prec}
        print(f"  comparabilidade {cm * 100:.3f} pp (±{cs * 100:.3f}) · "
              f"precisão@{args.k} {pm:.3f} (±{ps:.3f})")

    am, asd = ms(acaso_c)
    apm, apsd = ms(acaso_p)
    print(f"\nacaso: comparabilidade {am * 100:.3f} pp (±{asd * 100:.3f}) · "
          f"precisão@{args.k} {apm:.3f} (±{apsd:.3f})")
    return escrever(args, df, resultados, (am, asd), (apm, apsd), (sorteadas, viaveis))


def _linha_populacao(populacao: tuple[int, int], args) -> str:
    """Declara a população medida. Um denominador que muda em silêncio é o defeito, não a
    solução: uma consulta sem `k` candidatos elegíveis não tem resposta possível, e antes desta
    correção recebia os primeiros índices por ordem como se fossem vizinhos."""
    sorteadas, viaveis = populacao
    fora = sorteadas - viaveis
    if not fora:
        return (f"- **População:** {viaveis} consultas medidas, **nenhuma excluída** — todas "
                f"tinham pelo menos k={args.k} candidatos elegíveis.")
    return (f"- **População:** {viaveis} de {sorteadas} consultas medidas; **{fora} excluídas "
            f"({fora / sorteadas:.2%})** por terem menos de k={args.k} candidatos elegíveis. "
            "No protocolo causal são as consultas do início do bloco, que não têm passado "
            "dentro dele. O filtro é o mesmo em todos os braços e não depende de modelo "
            "nenhum, pelo que as comparações continuam emparelhadas.")


def escrever(args, df: pd.DataFrame, resultados: dict, acaso_c: tuple,
             acaso_p: tuple, populacao: tuple[int, int]) -> int:
    """Grava o relatório. O nome de cada braço aparece tal como foi passado na linha de comando."""
    am, asd = acaso_c
    apm, apsd = acaso_p
    protocolo = "causal (precedente anterior à consulta)" if args.causal else "simétrico"

    L = [
        "# evaluation_qi4.md — Ajuste do codificador por materialidade comparável (QI4)",
        "",
        "> Gerado por `scripts/avaliar_qi4.py`. **Não editar à mão.**",
        "",
        f"- **Bloco:** `{args.bloco}` · {len(df):,} manchetes · "
        f"{df['ticker'].nunique()} empresas.",
        f"- **Protocolo:** {protocolo}; nunca a própria empresa; "
        f"{args.consultas} consultas × {args.repeticoes} repetições; k={args.k}; "
        f"horizonte +{args.horizonte}d.",
        "- **Consultas idênticas para todos os braços** (sorteadas antes de qualquer modelo), "
        "logo as comparações são emparelhadas.",
        _linha_populacao(populacao, args),
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC · seed {args.seed}.",
        "",
        "## As duas métricas",
        "",
        "**Comparabilidade de materialidade** — diferença média, em pontos percentuais, entre a "
        "grandeza do movimento da consulta e a dos precedentes devolvidos. **Menor é melhor.** "
        "É a métrica do objectivo do ajuste.",
        "",
        "**Precisão@k por setor** — a métrica da §5.3. Está aqui para mostrar o que o ajuste "
        "custa, ou não, em relevância temática. **Maior é melhor.**",
        "",
        f"| Braço | Comparabilidade (pp) | Precisão@{args.k} | Cosseno entre manchetes "
        "diferentes |",
        "|---|---:|---:|---:|",
    ]
    for nome, r in resultados.items():
        d = r["dispersao"]
        marca = " ⚠️ **COLAPSADO**" if d["colapsou"] else ""
        L.append(f"| {nome} | {r['comparabilidade'] * 100:.3f} ± {r['comp_dp'] * 100:.3f} "
                 f"| {r['precisao']:.3f} ± {r['prec_dp']:.3f} "
                 f"| {d['cosseno_medio']:.4f}{marca} |")
    L.append(f"| **acaso** | {am * 100:.3f} ± {asd * 100:.3f} | {apm:.3f} ± {apsd:.3f} | — |")
    if any(r["dispersao"]["colapsou"] for r in resultados.values()):
        L += ["", "> ⚠️ **Pelo menos um braço colapsou.** Um codificador que mapeia todas as "
              "manchetes para o mesmo vetor produz uma tabela plausível e sem significado. "
              "As linhas marcadas não são interpretáveis. Ver "
              "`investigator/qi4/colapso.py`."]
    L += [
        "",
        "## Leitura",
        "",
        "A comparabilidade só é informativa contra o acaso: um valor baixo obtido por devolver "
        "sempre movimentos pequenos não seria mérito nenhum, e é o acaso que o denuncia. "
        "A precisão por setor tem de ser lida ao lado, porque um codificador pode melhorar "
        "numa à custa da outra — e se melhorar, é preciso dizer quanto custou.",
        "",
        "```json",
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "caminho"}
                    for k, v in resultados.items()}, indent=2, ensure_ascii=False),
        "```",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nEscrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
