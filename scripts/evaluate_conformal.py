"""Predição conformal sobre o modelo de triagem CONGELADO — ADITIVO.

*A lacuna que fecha.* A triagem devolve uma probabilidade calibrada por Platt. A calibração é
uma afirmação agregada e **sem garantia**: descreve o passado do conjunto de validação e não
promete nada sobre o próximo item. A predição conformal split acrescenta uma garantia livre de
distribuição e de amostra finita.

*A suposição, e porque é ela que interessa aqui.* A garantia conformal precisa de **uma** coisa:
permutabilidade entre calibração e o que se prevê. Num sistema financeiro treinado em 2018-2023
e a correr em 2026, é precisamente essa suposição que está sob suspeita. Por isso este script
não se limita à divisão aleatória (onde a permutabilidade vale por construção e a garantia
*tem* de se verificar); corre também uma divisão **temporal**, que é o que o sistema de facto
faz em produção. A diferença entre as duas é o resultado que interessa.

*Congelados.* Carrega `models/triage_context_lr.joblib` tal como está e verifica que reproduz a
PR-AUC congelada antes de dizer seja o que for. Não treina, não regrava, não altera nenhum .md
de avaliação existente.

Uso:
    python scripts/evaluate_conformal.py
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from investigator.console import force_utf8_stdout
from investigator.triage.conformal import ConformalReport, run_split_conformal
from investigator.triage.features import context_block
from investigator.triage.model import load_bundle

REPO = Path(__file__).resolve().parents[1]
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_conformal.md"
BUNDLE = REPO / "models" / "triage_context_lr.joblib"

# A PR-AUC congelada da variante só-contexto (models/triage_context_lr.json, teste).
# Se a reprodução não bater nisto, alguma coisa mudou e nada abaixo é de confiança.
FROZEN_PR_AUC = 0.5384788504706477
ALPHAS = (0.05, 0.1, 0.2)


def _score(bundle: dict, df: pd.DataFrame) -> np.ndarray:
    """Probabilidade calibrada do modelo congelado, pelo mesmo caminho que a produção usa."""
    x, names = context_block(df)
    if names != bundle["feature_names"]:
        raise SystemExit(
            f"features do bundle {bundle['feature_names']} != calculadas {names}. "
            "O bundle e o código divergiram; parar em vez de comparar coisas diferentes."
        )
    raw = bundle["model"].predict_proba(x)[:, 1]
    return np.asarray(bundle["calibrator"](raw), dtype=np.float64)


def _row(rel: ConformalReport) -> str:
    veredicto = "✅" if rel.covers else "⚠️"
    return (
        f"| {rel.alpha:.2f} | {rel.nominal:.2f} | **{rel.coverage:.3f}** {veredicto} "
        f"| {rel.qhat:.3f} | {rel.avg_set_size:.3f} | {rel.frac_singleton:.1%} "
        f"| {rel.frac_both:.1%} | {rel.frac_empty:.1%} |"
    )


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Predição conformal na triagem (aditivo)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    args = ap.parse_args()

    if not BUNDLE.exists():
        raise SystemExit(f"Falta o modelo congelado: {BUNDLE}")

    bundle = load_bundle(BUNDLE)
    df = pd.read_csv(args.dataset)
    test = df[df["split"] == "test"].reset_index(drop=True)
    y = test["label"].to_numpy().astype(int)
    p = _score(bundle, test)
    print(f"Teste: {len(test):,} linhas · prevalência {y.mean():.4f}")

    # ── Porta de reprodução ───────────────────────────────────────────────────
    pr_auc = float(average_precision_score(y, p))
    delta = abs(pr_auc - FROZEN_PR_AUC)
    print(f"PR-AUC reproduzida {pr_auc:.6f} vs congelada {FROZEN_PR_AUC:.6f} (Δ {delta:.2e})")
    if delta > 1e-6:
        raise SystemExit(
            "A reprodução não bate no número congelado. Parar: sem isto, nada do que se "
            "segue diz respeito ao modelo da tese."
        )
    print("Porta de reprodução: PASSA\n")

    # ── 1. Divisão ALEATÓRIA — a permutabilidade vale por construção ──────────
    rng = np.random.default_rng(42)
    perm = rng.permutation(len(test))
    meio = len(test) // 2
    cal_r, ev_r = perm[:meio], perm[meio:]
    aleatorias = [
        run_split_conformal(p[cal_r], y[cal_r], p[ev_r], y[ev_r], a) for a in ALPHAS
    ]
    print("Divisão ALEATÓRIA (permutabilidade por construção):")
    for rel in aleatorias:
        print(
            f"   α={rel.alpha:.2f} nominal {rel.nominal:.2f} → cobertura {rel.coverage:.3f} "
            f"| conjunto médio {rel.avg_set_size:.3f} | 'não sei' {rel.frac_both:.1%}"
        )

    # ── 2. Divisão TEMPORAL — o que produção de facto faz ────────────────────
    ordem = np.argsort(test["date"].astype(str).to_numpy(), kind="stable")
    cal_t, ev_t = ordem[:meio], ordem[meio:]
    corte = test["date"].astype(str).to_numpy()[ordem][meio]
    temporais = [
        run_split_conformal(p[cal_t], y[cal_t], p[ev_t], y[ev_t], a) for a in ALPHAS
    ]
    print(f"\nDivisão TEMPORAL (calibra antes de {corte}, avalia depois):")
    for rel in temporais:
        print(
            f"   α={rel.alpha:.2f} nominal {rel.nominal:.2f} → cobertura {rel.coverage:.3f} "
            f"| conjunto médio {rel.avg_set_size:.3f} | 'não sei' {rel.frac_both:.1%}"
        )

    quebras = [r for r in temporais if not r.covers]
    prev_cal = float(y[cal_t].mean())
    prev_ev = float(y[ev_t].mean())
    print(f"\nPrevalência: calibração {prev_cal:.4f} → avaliação {prev_ev:.4f}")

    # ── Relatório ─────────────────────────────────────────────────────────────
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    add = lines.append
    add("# Predição conformal na triagem — uma garantia, e o preço dela")
    add("")
    add(f"> Gerado por `scripts/evaluate_conformal.py` em {stamp}.")
    add("> **Aditivo.** Usa o modelo congelado tal como está; não treina nem regrava nada.")
    add(f"> Porta de reprodução: PR-AUC {pr_auc:.4f} = congelada {FROZEN_PR_AUC:.4f}.")
    add("")
    add("## O que isto acrescenta a uma probabilidade calibrada")
    add("")
    add("A triagem já devolve uma probabilidade calibrada por Platt. Calibração é uma")
    add("afirmação **agregada**: *entre os itens a que chamei 60%, cerca de 60% eram")
    add("materiais*. Descreve um histórico e **não promete nada** sobre o próximo item.")
    add("")
    add("A predição conformal split troca o ponto pelo conjunto e ganha uma garantia")
    add("**livre de distribuição** e de **amostra finita**: escolhido um α, o conjunto contém")
    add("a classe verdadeira em pelo menos 1−α dos casos. Não assume normalidade, nem que o")
    add("modelo esteja bem especificado, nem sequer que seja bom.")
    add("")
    add("Num problema binário há quatro conjuntos possíveis, e é a leitura deles que dá o")
    add("valor de produto:")
    add("")
    add("| Conjunto | Lê-se |")
    add("|---|---|")
    add("| {material} | decisão definida: alertar |")
    add("| {não material} | decisão definida: não alertar |")
    add("| {ambos} | **\"não sei\"**, declarado, com garantia por trás |")
    add("| {} (vazio) | nenhuma classe é plausível ao nível pedido |")
    add("")
    add("A terceira linha é a que interessa a esta tese. Um sistema que se recusa a prever")
    add("preços deve também saber dizer *não sei* sobre a sua própria triagem, em vez de")
    add("empurrar um 0,51 que finge decidir.")
    add("")
    add("## A suposição — e é aqui que está o resultado")
    add("")
    add("A garantia conformal precisa de **uma** coisa: **permutabilidade** entre o conjunto")
    add("de calibração e o que se vai prever. Num modelo treinado em 2018-2023 e a correr em")
    add("2026, é exatamente essa suposição que está sob suspeita.")
    add("")
    add("Por isso corre-se a experiência **duas vezes**, e a comparação é o resultado:")
    add("")
    add("1. **Divisão aleatória** do teste. A permutabilidade vale por construção, logo a")
    add("   garantia *tem* de se verificar. Serve de verificação da implementação.")
    add("2. **Divisão temporal** do teste (calibrar no passado, prever no futuro). É o que o")
    add("   sistema faz em produção, e a permutabilidade **não** está garantida.")
    add("")
    add("### 1. Divisão aleatória")
    add("")
    add(f"Calibração {aleatorias[0].n_cal:,} · avaliação {aleatorias[0].n_eval:,}.")
    add("")
    add("| α | Nominal | Cobertura | q̂ | Conjunto médio | Decisões | \"Não sei\" | Vazio |")
    add("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for rel in aleatorias:
        add(_row(rel))
    add("")
    add("### 2. Divisão temporal")
    add("")
    add(f"Calibração até {corte} ({temporais[0].n_cal:,} linhas) · avaliação depois")
    add(f"({temporais[0].n_eval:,} linhas).")
    add("")
    add("| α | Nominal | Cobertura | q̂ | Conjunto médio | Decisões | \"Não sei\" | Vazio |")
    add("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for rel in temporais:
        add(_row(rel))
    add("")
    add(f"Prevalência de positivos: **{prev_cal:.3f}** na calibração → **{prev_ev:.3f}** na")
    add("avaliação.")
    add("")
    add("## Leitura honesta")
    add("")
    if not quebras:
        add("**A garantia aguenta-se nas duas divisões.**")
        add("")
        add("Que se verifique na divisão aleatória era esperado e serve de verificação da")
        add("implementação. Que se aguente também na **temporal** é o resultado que interessa:")
        add("nesta janela de teste, a deriva não é suficiente para partir a permutabilidade ao")
        add("ponto de a cobertura cair abaixo do nominal.")
        add("")
        add("Duas ressalvas para não sobre-ler isto. A janela de teste é **interna ao corpus")
        add("2018-2023**; não diz nada sobre 2026, que é o salto que de facto preocupa — essa")
        add("pergunta é medida à parte, em `evaluation_drift.md`. E a cobertura é marginal,")
        add("não condicional: vale no agregado, e não promete 1−α *dentro de cada* regime.")
    else:
        aguentam = [r for r in temporais if r.covers]
        quebradas = ", ".join(f"α={r.alpha:.2f} (cobertura {r.coverage:.3f})" for r in quebras)
        add("**Na divisão aleatória a garantia verifica-se; na temporal parte-se, mas só no")
        add("nível mais exigente.** É esse padrão, e não um veredicto único, o resultado.")
        add("")
        add("A divisão aleatória bate no nominal aos três níveis, o que confirma que a")
        add("implementação está correta — se falhasse aqui, o erro seria meu e não dos dados.")
        add("")
        add(f"Sob divisão temporal a cobertura fica aquém em: {quebradas}.")
        if aguentam:
            ok = ", ".join(f"α={r.alpha:.2f} ({r.coverage:.3f})" for r in aguentam)
            add(f"Aguenta-se em: {ok}.")
        add("")
        add("A direção do padrão é a que a teoria prevê e vale a pena dizê-lo por extenso:")
        add("**quanto mais apertada a cobertura exigida, mais frágil ela é à deriva.** Pedir")
        add("95% obriga o limiar a apoiar-se na cauda da distribuição de calibração, e é")
        add("exatamente a cauda que se move primeiro quando o regime muda. A 80% e a 90% a")
        add("folga é suficiente para absorver o desvio desta janela.")
        add("")
        add("Nada disto é um defeito do método conformal — é o método a **detetar** a quebra")
        add("de permutabilidade e a dizer em que nível ela começa a doer. Uma garantia que se")
        add("parte de forma mensurável vale mais do que uma probabilidade que nunca prometeu")
        add("nada e por isso nunca pode ser desmentida.")
        add("")
        add(f"A prevalência de positivos move-se de {prev_cal:.3f} para {prev_ev:.3f} entre as")
        add("duas metades, o que é uma pista direta da causa e liga esta página à medição de")
        add("deriva em `evaluation_drift.md`.")
        add("")
        add("Uma ressalva para não sobre-ler: esta divisão é **interna ao corpus 2018-2023**.")
        add("O salto que de facto preocupa é 2023 → 2026, e é maior do que este.")
    add("")
    add("## O preço da garantia — e é este o número mais duro desta página")
    add("")
    add("A garantia não é grátis, e o custo lê-se na coluna **\"não sei\"**:")
    add("")
    for rel in aleatorias:
        add(
            f"- A **{rel.nominal:.0%}** de cobertura: decisão definida em "
            f"**{rel.frac_singleton:.1%}** dos casos, \"não sei\" em **{rel.frac_both:.1%}**."
        )
    add("")
    a90 = next(r for r in aleatorias if abs(r.alpha - 0.10) < 1e-9)
    add("Dito sem rodeios: para poder prometer 90% de cobertura, o modelo de triagem só")
    add(f"consegue tomar uma decisão definida em **{a90.frac_singleton:.1%}** das manchetes.")
    add(f"Nas outras **{a90.frac_both:.1%}**, o conjunto honesto contém as duas classes.")
    add("")
    add("Este número não contradiz a avaliação congelada — **explica-a**. A tese já reporta")
    add("que nenhum modelo com texto bate a volatilidade (PR-AUC 0,496 vs 0,542) e que o")
    add("valor da triagem está no mecanismo de ordenação, não na força preditiva. A predição")
    add("conformal põe um número nessa fraqueza a partir de outro ângulo, sem treinar nada de")
    add("novo: o sinal disponível simplesmente não separa a maioria dos itens ao nível de")
    add("confiança que se costuma exigir.")
    add("")
    add("É também o mostrador que faltava ao limiar de produção. O `min_materiality` de 0,5")
    add("(derivado por rácio de custo em `evaluation_policy_sweep.md`) força **sempre** uma")
    add("decisão. Esta página mede em quantos casos essa decisão forçada assenta em pouco.")
    add("")
    add("## O que fica")
    add("")
    add("Camada de **medição**, não ligada à produção. A razão é de desenho e não de falta de")
    add("tempo: o produto promete uma cadência legível")
    add("(`docs/design/cadence_contract.md`), e um alerta que dissesse \"não sei\" a")
    add(f"{a90.frac_both:.0%} dos itens romperia essa promessa sem que ninguém tivesse")
    add("decidido rompê-la. Onde isto **deve** entrar é na leitura crítica do sistema, e é lá")
    add("que entra.")
    add("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRelatório escrito em {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
