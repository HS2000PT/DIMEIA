"""Gera o kit executável do estudo de utilidade (RQ3) — estímulos reais, prontos a usar.

**Porque existe.** `docs/design/usefulness_study.md` desenha o estudo ao pormenor, mas correr
o estudo ainda exigia escolher alertas à mão, construir as versões A/B, contrabalançar ordens
e desenhar folhas de resposta. Esse atrito é a razão de o estudo nunca ter sido corrido — e a
utilidade da RQ3 é a ÚNICA linha "ainda em aberto" do Cap. 6. Este script remove o atrito:
um comando produz o caderno do facilitador, os estímulos e as folhas de recolha.

**Zero fabricação.** Os estímulos são alertas REAIS lidos da branch de dados `alerts-history`
— exatamente os que o canal Telegram enviou. A condição **A** é o FACTO nu (ver `_bare_fact`:
para mercado é a 1.ª linha; para notícia é o cabeçalho + a manchete, porque cortar na 1.ª linha
deixaria a condição A sem conteúdo e a B ganharia por omissão); a condição **B** é o alerta
completo, tal como saiu. Nada é escrito à mão, nada é embelezado.

**Seleção.** 3 alertas de mercado + 3 de notícia, e **pelo menos um caso tema≠direção**
(manchete sem sinal negativo mas precedentes que caíram) — é o estímulo mais duro e o que
melhor mede a calibração de confiança, que é o risco de produto central.

Uso:
    python scripts/build_usefulness_pack.py                 # 8 participantes
    python scripts/build_usefulness_pack.py --participants 10 --seed 7
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from investigator.console import force_utf8_stdout

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "study"
DEFAULT_URL = (
    "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/alerts_history.jsonl"
)


def _history(url: str) -> list:
    from investigator.alerts_history import fetch_remote

    return fetch_remote(url)


def _bare_fact(text: str, kind: str) -> str:
    """Condição A: o FACTO nu, sem explicação, precedentes ou avisos.

    Onde vive o facto depende do tipo, e confundi-lo invalidaria o estudo:
    - **mercado**: a 1.ª linha JÁ é o facto ("📉 AMD · -8,64% today");
    - **notícia**: a 1.ª linha é só um cabeçalho ("📰 News alert for TSLA"), e o facto é a
      MANCHETE, na linha seguinte. Cortar na 1.ª linha deixaria a condição A sem conteúdo
      nenhum — e a condição B ganharia por omissão, medindo nada.
    """
    linhas = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if not linhas:
        return text.strip()[:120]
    if kind == "news" and len(linhas) > 1:
        return f"{linhas[0]}\n{linhas[1]}"
    return linhas[0]


def _is_theme_direction_case(text: str) -> bool:
    """Precedentes que caíram todos — o caso em que 'tema semelhante' NÃO significa
    'direção semelhante'. É o estímulo que testa se o utilizador percebe que aquilo não é
    uma previsão."""
    return "shown cases moved down" in text or "moved in BOTH directions" in text


def _select(entries: list, seed: int) -> list[dict]:
    """3 mercado + 3 notícia, com pelo menos um caso tema≠direção. Determinístico."""
    rng = random.Random(seed)
    market = [e for e in entries if e.kind == "market" and len(e.text) > 80]
    news = [e for e in entries if e.kind == "news" and len(e.text) > 200]
    hard = [e for e in news if _is_theme_direction_case(e.text)]

    if len(market) < 3 or len(news) < 3:
        raise SystemExit(
            f"[!] histórico insuficiente (mercado={len(market)}, notícia={len(news)}).\n"
            "    O estudo precisa de alertas reais — correr quando o canal tiver mais história."
        )

    escolhidos: list = []
    if hard:  # garantir o caso duro
        escolhidos.append(rng.choice(hard))
    restantes = [e for e in news if e not in escolhidos]
    escolhidos += rng.sample(restantes, 3 - len(escolhidos))
    escolhidos += rng.sample(market, 3)

    out = []
    for i, e in enumerate(escolhidos, start=1):
        out.append({
            "id": f"S{i}",
            "kind": e.kind,
            "ticker": e.ticker,
            "date": e.date,
            "hard": _is_theme_direction_case(e.text),
            "A": _bare_fact(e.text, e.kind),
            "B": e.text.strip(),
        })
    return out


def _assign(stimuli: list[dict], n_participants: int) -> list[dict]:
    """Contrabalanço: metade A→B, metade B→A, e alertas DIFERENTES em cada condição
    (senão o participante limitava-se a lembrar-se do primeiro)."""
    metade = len(stimuli) // 2
    grupo1, grupo2 = stimuli[:metade], stimuli[metade:]
    plano = []
    for p in range(1, n_participants + 1):
        a_primeiro = p % 2 == 1
        plano.append({
            "participant": f"P{p:02d}",
            "order": "A→B" if a_primeiro else "B→A",
            "cond1": {"condition": "A" if a_primeiro else "B",
                      "stimuli": [s["id"] for s in (grupo1 if a_primeiro else grupo2)]},
            "cond2": {"condition": "B" if a_primeiro else "A",
                      "stimuli": [s["id"] for s in (grupo2 if a_primeiro else grupo1)]},
        })
    return plano


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Kit executável do estudo de utilidade (RQ3)")
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--participants", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    entries = _history(args.url)
    if not entries:
        print("[!] sem histórico (rede em baixo ou branch vazia). Nada gerado.")
        return 1
    print(f"{len(entries)} alertas reais no histórico partilhado.")

    stimuli = _select(entries, args.seed)
    plano = _assign(stimuli, args.participants)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Estímulos ──────────────────────────────────────────────────────────
    L = [
        "# Study stimuli — real alerts, condition A vs B",
        "",
        "> Generated by `scripts/build_usefulness_pack.py`. Every stimulus is a **real alert**",
        "> the Telegram channel sent. Condition **A** is its first line only (the bare fact);",
        "> condition **B** is the alert exactly as delivered. Nothing here was written by hand.",
        "",
        "**Facilitator: do not explain anything while the participant reads.** The point is",
        "whether the alert explains itself.",
        "",
    ]
    for s in stimuli:
        marca = "  ⟵ **theme ≠ direction case**" if s["hard"] else ""
        L += [f"## {s['id']} — {s['ticker']} · {s['date']} · {s['kind']}{marca}", "",
              "**Condition A (bare fact)**", "", "```", s["A"], "```", "",
              "**Condition B (full alert)**", "", "```", s["B"], "```", "", "---", ""]
    (OUT_DIR / "stimuli.md").write_text("\n".join(L), encoding="utf-8")

    # ── 2. Plano de contrabalanço ─────────────────────────────────────────────
    P = ["# Counterbalancing plan", "",
         "Half the participants see A first, half see B first, and the two conditions use",
         "**different** alerts — otherwise the second condition would just be recall.", "",
         "| Participant | Order | Condition 1 | Condition 2 |", "|---|---|---|---|"]
    for row in plano:
        P.append(f"| {row['participant']} | {row['order']} | "
                 f"{row['cond1']['condition']}: {', '.join(row['cond1']['stimuli'])} | "
                 f"{row['cond2']['condition']}: {', '.join(row['cond2']['stimuli'])} |")
    (OUT_DIR / "counterbalancing.md").write_text("\n".join(P), encoding="utf-8")

    # ── 3. Folha de recolha (CSV pronto a preencher) ──────────────────────────
    cab = ("participant,order,condition,stimulus,"
           "p1_detected,p1_why,p1_not_prediction,q1_clear,q2_complete,"
           "q3_actionable,q4_calibrated,q5_preference,open_comment")
    linhas = [cab]
    for row in plano:
        for cond in ("cond1", "cond2"):
            for sid in row[cond]["stimuli"]:
                linhas.append(f"{row['participant']},{row['order']},"
                              f"{row[cond]['condition']},{sid},,,,,,,,,")
    (OUT_DIR / "responses_template.csv").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    # ── 4. Guião do facilitador ───────────────────────────────────────────────
    guiao = f"""# Facilitator script ({args.participants} participants, ~15 min each)

## Before you start
- Print or open `stimuli.md`. Keep `counterbalancing.md` beside you.
- Copy `responses_template.csv` to `responses.csv` and fill it as you go.
- Recruit adults with **no** finance or AI background. Colleagues and family are the right
  profile — they are the actual target user.

## Consent (read aloud, ~20 s)
> "You'll see a few financial alerts. You don't need to know anything about markets. For each
> one I'll ask what you understood. There are no wrong answers about you — I'm testing the
> alerts, not you. It's anonymous, and you can stop at any time."

## Per participant
1. Look up their row in `counterbalancing.md`.
2. **Condition 1** — show each listed stimulus in that condition, then ask:
   - *"What did the system detect here?"* → score `p1_detected` 1 if correct, else 0
   - *"Why was this flagged?"* → `p1_why` 1/0
   - *"Is this a prediction of what happens next?"* → `p1_not_prediction` 1 if they say **NO**
   - Then the five 1–5 statements (Q1–Q5 in `usefulness_study.md` §4).
3. **Condition 2** — same, with the other stimuli.
4. Ask once at the end: *"What was missing or confusing?"* → `open_comment`.

## Do not
- Do not explain, hint, or fill silence. If they ask what something means, say
  *"whatever it means to you"* and move on. That silence **is** the measurement.

## When done
    python scripts/analyse_usefulness.py

That writes `docs/evaluation/evaluation_usefulness.md` — the Case Study 5 table.
"""
    (OUT_DIR / "facilitator_script.md").write_text(guiao, encoding="utf-8")

    duros = sum(1 for s in stimuli if s["hard"])
    print(f"\n[ok] {len(stimuli)} estímulos ({duros} tema≠direção) · "
          f"{args.participants} participantes")
    for f in ("stimuli.md", "counterbalancing.md", "responses_template.csv",
              "facilitator_script.md"):
        print(f"     docs/study/{f}")
    print("\nPróximo passo é humano: recrutar 6–10 pessoas e preencher responses.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
