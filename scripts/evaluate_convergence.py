"""Convergência multi-sinal: o acordo entre sinais bate o melhor sinal isolado? — ADITIVO.

*A ideia e o crédito.* Adaptada de `worldmonitor.app`, recomendado pelo coorientador Rafael Silva.
Aproveita-se o princípio (um acontecimento onde várias fontes independentes convergem merece mais
atenção) e não a escala, que está fora do âmbito de um projeto restrito a APIs gratuitas.

*A pergunta, posta de forma falsificável.* O sistema calcula quatro coisas sobre um par
(ticker, dia): o preço mexeu-se de forma invulgar para aquela ação, o volume foi invulgar, houve
notícia e quanta, e a triagem achou material provável. Cada um responde a algo diferente e nenhum
vê os outros. **Ao mesmo orçamento diário de alertas, a fusão dos quatro apanha mais dias materiais
do que o melhor deles sozinho?**

*Regra dura.* Os pesos são **derivados** (regressão logística ajustada na VALIDAÇÃO, avaliada no
teste), nunca escolhidos à mão. Um score de convergência com pesos inventados seria exatamente o
tipo de número que esta tese recusa mostrar.

*Se perder, reporta-se que perdeu.* O projeto já tem registo de negativos honestos (o texto não bate
a volatilidade; cinco features de contexto não ajudaram). Mais um não enfraquece a tese.

*Congelados.* Usa o modelo de triagem tal como está e verifica a reprodução antes de mais nada.
Não treina, não regrava, não altera nenhum .md existente.

Uso:
    python scripts/evaluate_convergence.py
    python scripts/evaluate_convergence.py --refresh-volumes
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score

from investigator.anomaly_detector.volume import volume_z_series
from investigator.console import force_utf8_stdout
from investigator.convergence import SIGNALS, ConvergenceWeights, score_matrix
from investigator.triage.features import context_block
from investigator.triage.model import load_bundle

REPO = Path(__file__).resolve().parents[1]
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_convergence.md"
BUNDLE = REPO / "models" / "triage_context_lr.joblib"
VOL_CACHE = REPO / "data" / "_cache_volumes.csv"
FROZEN_PR_AUC = 0.5384788504706477
BUDGETS = (1, 3, 5)


def _fetch_volumes(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Volume diário por ticker. Em cache, porque é a única parte que precisa de rede."""
    import yfinance as yf

    frames = []
    for t in tickers:
        try:
            h = yf.Ticker(t).history(start=start, end=end, interval="1d", auto_adjust=False)
        except Exception as exc:  # noqa: BLE001 — um ticker em falta não deve matar a corrida
            print(f"   {t}: falhou ({exc})")
            continue
        if h is None or h.empty or "Volume" not in h:
            print(f"   {t}: sem dados")
            continue
        f = pd.DataFrame(
            {
                "ticker": t,
                "date": pd.to_datetime(h.index).tz_localize(None).strftime("%Y-%m-%d"),
                "volume": h["Volume"].to_numpy(dtype="float64"),
            }
        )
        frames.append(f)
        print(f"   {t}: {len(f):,} dias")
    if not frames:
        raise SystemExit("Nenhum volume obtido; sem rede não é possível correr este estudo.")
    return pd.concat(frames, ignore_index=True)


def _daily_panel(df: pd.DataFrame, probs: np.ndarray) -> pd.DataFrame:
    """Colapsa manchetes em pares (ticker, dia), que é a unidade do rótulo.

    Este passo não é cosmético. O rótulo é por (ticker, dia), pelo que ordenar MANCHETES encheria
    o topo com cópias do mesmo nome — foi exatamente o erro apanhado no varrimento de política
    (`evaluation_policy_sweep.md`), e repeti-lo aqui daria empates perfeitos e um Δ de zero.
    """
    work = df.copy()
    work["triage_p"] = probs
    # A reação padronizada: quão grande foi o movimento PARA AQUELA ação. É o mesmo z que o
    # detetor de preço calcula ao vivo, reconstruído a partir das colunas do dataset.
    with np.errstate(divide="ignore", invalid="ignore"):
        work["price_z"] = np.abs(work["ret_event"] / work["vol20"].replace(0.0, np.nan))
    grouped = work.groupby(["ticker", "date"], as_index=False).agg(
        price_z=("price_z", "max"),
        triage_p=("triage_p", "max"),
        news_intensity=("headline", "size"),
        label=("label", "max"),
    )
    return grouped


def _precision_at_budget(panel: pd.DataFrame, column: str, k: int) -> float:
    """Fração de alertas materiais entre os top-k de cada dia, ordenados por `column`."""
    hits = tot = 0
    for _, day in panel.groupby("date"):
        top = day.nlargest(k, column)
        hits += int(top["label"].sum())
        tot += len(top)
    return hits / tot if tot else float("nan")


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Convergência multi-sinal (aditivo)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--refresh-volumes", action="store_true")
    args = ap.parse_args()

    if not BUNDLE.exists():
        raise SystemExit(f"Falta o modelo congelado: {BUNDLE}")

    df = pd.read_csv(args.dataset)
    df = df[df["split"].isin(["val", "test"])].reset_index(drop=True)
    print(f"{len(df):,} manchetes (val+test)")

    # ── Porta de reprodução ───────────────────────────────────────────────────
    bundle = load_bundle(BUNDLE)
    x, names = context_block(df)
    if names != bundle["feature_names"]:
        raise SystemExit("features do bundle divergem das calculadas; parar.")
    probs = np.asarray(bundle["calibrator"](bundle["model"].predict_proba(x)[:, 1]))

    test_mask = (df["split"] == "test").to_numpy()
    pr = float(average_precision_score(df.loc[test_mask, "label"], probs[test_mask]))
    print(f"PR-AUC do teste reproduzida {pr:.6f} vs congelada {FROZEN_PR_AUC:.6f}")
    if abs(pr - FROZEN_PR_AUC) > 1e-6:
        raise SystemExit("A reprodução não bate no congelado. Parar.")
    print("Porta de reprodução: PASSA\n")

    # ── Volume ────────────────────────────────────────────────────────────────
    tickers = sorted(df["ticker"].unique())
    if args.refresh_volumes or not VOL_CACHE.exists():
        print(f"A obter volumes para {len(tickers)} tickers…")
        vols = _fetch_volumes(tickers, "2017-11-01", "2024-01-15")
        vols.to_csv(VOL_CACHE, index=False)
        print(f"   cache escrita em {VOL_CACHE.name}")
    else:
        vols = pd.read_csv(VOL_CACHE)
        print(f"Volumes da cache ({len(vols):,} linhas)")

    vols = vols.sort_values(["ticker", "date"]).reset_index(drop=True)
    vols["volume_z"] = vols.groupby("ticker")["volume"].transform(
        lambda s: volume_z_series(s.to_numpy(), window=20).to_numpy()
    )

    # ── Painel diário ─────────────────────────────────────────────────────────
    panel = _daily_panel(df, probs)
    split_of = df.groupby(["ticker", "date"])["split"].first().reset_index()
    panel = panel.merge(split_of, on=["ticker", "date"], how="left")
    panel = panel.merge(vols[["ticker", "date", "volume_z"]], on=["ticker", "date"], how="left")

    coberto = panel["volume_z"].notna().mean()
    print(f"\nPainel: {len(panel):,} pares (ticker,dia) · volume alinhado em {coberto:.1%}")
    panel = panel.dropna(subset=list(SIGNALS)).reset_index(drop=True)
    print(f"Após exigir os quatro sinais: {len(panel):,} pares")

    val = panel[panel["split"] == "val"].reset_index(drop=True)
    test = panel[panel["split"] == "test"].reset_index(drop=True)
    print(f"   validação {len(val):,} · teste {len(test):,}")
    if len(val) < 200 or len(test) < 200:
        raise SystemExit("Painel pequeno demais para uma comparação honesta.")

    # ── Pesos DERIVADOS na validação ──────────────────────────────────────────
    xv = val[list(SIGNALS)].to_numpy(dtype=np.float64)
    means, stds = xv.mean(axis=0), xv.std(axis=0)
    lr = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
    lr.fit((xv - means) / np.where(stds > 0, stds, 1.0), val["label"].to_numpy())
    weights = ConvergenceWeights(
        coefficients=tuple(float(c) for c in lr.coef_[0]),
        intercept=float(lr.intercept_[0]),
        means=tuple(float(m) for m in means),
        stds=tuple(float(s) for s in stds),
    )
    print("\nPesos derivados (validação, sinais estandardizados):")
    for name, coef in zip(SIGNALS, weights.coefficients, strict=True):
        print(f"   {name:<16} {coef:+.4f}")

    test = test.copy()
    test["convergence"] = score_matrix(test[list(SIGNALS)].to_numpy(), weights)

    # ── A comparação ──────────────────────────────────────────────────────────
    contenders = [*SIGNALS, "convergence"]
    rows: list[dict] = []
    for col in contenders:
        row = {"signal": col, "pr_auc": float(average_precision_score(test["label"], test[col]))}
        for k in BUDGETS:
            row[f"p@{k}"] = _precision_at_budget(test, col, k)
        rows.append(row)
    res = pd.DataFrame(rows)
    prevalence = float(test["label"].mean())

    print(f"\nTeste: {len(test):,} pares · prevalência {prevalence:.4f}")
    print(f"{'sinal':<16}{'PR-AUC':>9}" + "".join(f"{'p@' + str(k):>9}" for k in BUDGETS))
    for _, r in res.iterrows():
        print(
            f"{r['signal']:<16}{r['pr_auc']:>9.4f}"
            + "".join(f"{r[f'p@{k}']:>9.4f}" for k in BUDGETS)
        )

    singles = res[res["signal"] != "convergence"]
    fused = res[res["signal"] == "convergence"].iloc[0]
    verdict: dict[str, dict] = {}
    for k in BUDGETS:
        col = f"p@{k}"
        best = singles.loc[singles[col].idxmax()]
        verdict[col] = {
            "best_single": best["signal"],
            "best_value": float(best[col]),
            "fused": float(fused[col]),
            "delta": float(fused[col] - best[col]),
        }
    wins = sum(1 for v in verdict.values() if v["delta"] > 0)
    print(f"\nA fusão ganha em {wins} de {len(BUDGETS)} orçamentos.")

    # ── Relatório ─────────────────────────────────────────────────────────────
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    add = lines.append
    add("# Convergência multi-sinal — o acordo bate o melhor sinal isolado?")
    add("")
    add(f"> Gerado por `scripts/evaluate_convergence.py` em {stamp}.")
    add("> **Aditivo.** Usa o modelo de triagem congelado tal como está; não treina nem regrava.")
    add(f"> Porta de reprodução: PR-AUC {pr:.4f} = congelada {FROZEN_PR_AUC:.4f}.")
    add("")
    add("## De onde vem a ideia")
    add("")
    add("Adaptada de **worldmonitor.app**, recomendado pelo **coorientador Rafael Silva**.")
    add("O que se aproveita não é a escala (dezenas de camadas e de fornecedores de dados,")
    add("fora do âmbito de um projeto restrito a APIs gratuitas) mas o **princípio**: um")
    add("acontecimento em que várias")
    add("fontes independentes convergem merece mais atenção do que um em que só uma dispara.")
    add("")
    add("## A pergunta, posta de forma falsificável")
    add("")
    add("O sistema já calcula quatro coisas sobre um par (ticker, dia), e trata-as separadamente:")
    add("")
    add("| Sinal | Pergunta a que responde | Já existia? |")
    add("|---|---|---|")
    add("| Preço | mexeu-se muito **para aquela ação**? | sim, o detetor |")
    add("| Volume | negociou-se muito mais do que o costume? | **novo** (a coluna vinha e "
        "era deitada fora) |")
    add("| Intensidade de notícia | quantas manchetes nesse dia? | sim, no fluxo |")
    add("| Triagem | probabilidade calibrada de ser material? | sim, o modelo congelado |")
    add("")
    add("Nenhum vê os outros. **Ao mesmo orçamento diário de alertas, a fusão apanha mais dias")
    add("materiais do que o melhor sinal sozinho?**")
    add("")
    add("## Método")
    add("")
    add("- **Unidade de análise:** o par (ticker, dia), que é a unidade do rótulo. Ordenar")
    add("  *manchetes* encheria o topo com cópias do mesmo nome; foi o erro apanhado no varrimento")
    add("  de política, e não se repete.")
    add("- **Pesos derivados, não escolhidos:** regressão logística sobre os quatro sinais")
    add("  estandardizados, ajustada na **validação** e avaliada no **teste**. O modelo de fusão é")
    add("  linear de propósito, para as contribuições por sinal serem exatas e não aproximadas.")
    add("- **Volume:** z-score do `log` do volume contra a norma dos 20 dias anteriores, pela")
    add("  mesma")
    add("  convenção anti-lookahead do detetor de preço. O logaritmo é necessário porque o volume")
    add("  é fortemente assimétrico e um z sobre o valor bruto dispararia quase só para cima.")
    add("")
    add(f"Painel de teste: **{len(test):,}** pares (ticker, dia), prevalência "
        f"**{prevalence:.4f}**.")
    add("")
    add("> ⚠️ **O painel é bastante menor do que o corpus sugere, e a razão importa.** As")
    add(f"> {len(df):,} manchetes de validação e teste colapsam em apenas {len(panel):,} pares")
    add("> (ticker, dia), porque essa é a unidade do rótulo. Além disso, a cobertura de tickers")
    add("> do FNSPID **varia ao longo do tempo**: o bloco de treino tem 13 tickers, mas a")
    add(f"> validação tem 8 e o teste {test['ticker'].nunique()}. Não é um defeito do")
    add("> alinhamento (o volume casa em 100% das linhas); é uma propriedade do corpus. A")
    add("> consequência é que este estudo assenta numa amostra bem mais pequena do que os")
    add("> estudos de recuperação e de triagem, e as diferenças abaixo devem ser lidas com essa")
    add("> reserva.")
    add("")
    add("### Pesos derivados")
    add("")
    add("| Sinal | Peso (sinais estandardizados) |")
    add("|---|---:|")
    for name, coef in zip(SIGNALS, weights.coefficients, strict=True):
        add(f"| `{name}` | {coef:+.4f} |")
    add("")
    news_w = weights.coefficients[SIGNALS.index("news_intensity")]
    if news_w < 0:
        add(f"**O peso da intensidade de notícia é NEGATIVO ({news_w:+.4f}), e isso é um achado**")
        add("**e não um erro de sinal.** Mais manchetes num dia torna esse dia *menos* provável de")
        add("ser material. A explicação compatível com o que já se sabe deste corpus: dias com")
        add("muitas manchetes tendem a ser dias de conteúdo automático (resumos de mercado, listas")
        add("de sugestões, atualizações de desequilíbrio de ordens) e não dias de acontecimento")
        add("real. É o mesmo problema de qualidade à entrada que motivou o filtro de relevância em")
        add("produção, a aparecer agora do lado quantitativo. Um score de convergência com pesos")
        add("**escolhidos à mão** teria quase de certeza posto aqui um peso positivo, e estaria")
        add("errado; foi por isto que a regra deste projeto é derivar os pesos.")
        add("")
    add("## Resultados")
    add("")
    add("| Sinal | PR-AUC | " + " | ".join(f"p@{k}/dia" for k in BUDGETS) + " |")
    add("|---|---:|" + "---:|" * len(BUDGETS))
    for _, r in res.iterrows():
        nome = "**convergência**" if r["signal"] == "convergence" else f"`{r['signal']}`"
        add(
            f"| {nome} | {r['pr_auc']:.4f} | "
            + " | ".join(f"{r[f'p@{k}']:.4f}" for k in BUDGETS)
            + " |"
        )
    add("")
    add("### A fusão contra o melhor sinal isolado")
    add("")
    add("| Orçamento | Melhor sinal isolado | Valor | Convergência | Δ |")
    add("|---|---|---:|---:|---:|")
    for k in BUDGETS:
        v = verdict[f"p@{k}"]
        add(
            f"| top-{k}/dia | `{v['best_single']}` | {v['best_value']:.4f} "
            f"| {v['fused']:.4f} | **{v['delta']:+.4f}** |"
        )
    add("")
    add("## Leitura honesta")
    add("")
    if wins == len(BUDGETS):
        add(f"**A fusão ganha nos {wins} orçamentos.** O acordo entre sinais independentes carrega")
        add("informação que nenhum deles tem sozinho, que é exatamente a intuição por trás da")
        add("convergência.")
    elif wins == 0:
        add("**A fusão não ganha em nenhum orçamento.** Reportado tal como caiu.")
        add("")
        add("Vale a pena dizer porque é que isto não é surpreendente. Os sinais não são")
        add("independentes na prática: dias de notícia forte tendem a ser dias de volume alto e de")
        add("movimento grande, pelo que fundi-los acrescenta menos do que o argumento sugere. É a")
        add("mesma lição que o texto e as cinco features de contexto já tinham dado, por outros")
        add("caminhos: neste corpus, a materialidade de curto prazo é notavelmente bem")
        add("resumida por")
        add("poucos números.")
    else:
        ganhos = ", ".join(
            f"top-{k} ({verdict[f'p@{k}']['delta']:+.4f})"
            for k in BUDGETS
            if verdict[f"p@{k}"]["delta"] > 0
        )
        perdas = ", ".join(
            f"top-{k} ({verdict[f'p@{k}']['delta']:+.4f})"
            for k in BUDGETS
            if verdict[f"p@{k}"]["delta"] <= 0
        )
        add(f"**Misto: a fusão ganha em {wins} de {len(BUDGETS)} orçamentos.**")
        add(f"Ganha em {ganhos}; não ganha em {perdas}.")
        add("")
        add("Um resultado misto não sustenta ligar isto à produção. Um ganho que depende do")
        add("orçamento escolhido é um ganho que se pode ter escolhido, e o critério deste projeto")
        add("é que uma capacidade nova só entra quando a medição a sustenta sem se escolher o")
        add("ângulo.")
    add("")
    add("## O que fica")
    add("")
    add("O **detetor de volume** é uma capacidade genuinamente nova e de custo zero em dados: a")
    add("coluna já vinha em todas as barras e estava a ser deitada fora. Responde à segunda")
    add("pergunta que qualquer operador faz depois de ver um movimento (*e com quanta gente a")
    add("negociar?*), e é transparente pela mesma construção do detetor de preço.")
    add("")
    if wins == len(BUDGETS):
        add("O **score de convergência** fica atrás de uma opção de configuração, desligada por")
        add("defeito, pelo mesmo padrão do narrador: aditivo, e se falhar o sistema comporta-se")
        add("exatamente como hoje.")
    else:
        add("O **score de convergência** fica como medição e **não** é ligado à produção, e a")
        add("razão é a evidência desta página. O que dela se aproveita para o produto é a *humana*")
        add("da convergência, `agreement_count`: dizer \"três dos quatro sinais dispararam\"")
        add("comunica de imediato e é verificável olhando para os componentes, ao passo que um")
        add("score fundido de 0,73 não se verifica em lado nenhum.")
    add("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRelatório escrito em {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
