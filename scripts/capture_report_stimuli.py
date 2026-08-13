"""capture_report_stimuli.py — congela relatórios reais de produção como estímulos do bloco C.

## Porque é que isto não pode ser gerado ao vivo durante o estudo

O relatório é escrito por um LLM e **não é determinístico**. Gerar durante a sessão daria a cada
participante um texto diferente, e a comparação entre condições deixaria de medir a condição para
passar a medir a variação entre chamadas ao modelo. Um estímulo de estudo tem de ser **o mesmo para
toda a gente**, e é por isso que se captura uma vez e se congela.

Captura-se, para cada activo pedido:

- o **relatório** (`POST /api/report`), com o campo `source` — que diz se saiu **gerado** ou da
  **composição determinística**. Um estímulo que caiu no chão determinístico **não testa a camada
  generativa**, e vai marcado para a análise o poder separar em vez de os misturar;
- o **pacote de evidência** (`GET /api/evidence`), porque a hipótese H5 (a travessia
  frase → facto) tem de poder ser feita **em papel** se não houver ecrã.

Nada é reescrito nem embelezado: o que se grava é o que a API devolveu, com o carimbo de quando.

USO
---
    python scripts/capture_report_stimuli.py --base https://investigator-....herokuapp.com
    python scripts/capture_report_stimuli.py --base http://127.0.0.1:8000 --tickers NVDA,XOM
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.console import force_utf8_stdout  # noqa: E402

SAIDA = RAIZ / "docs" / "study"
TIMEOUT = 90


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8"))


def _post(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="raiz da API (produção ou local)")
    ap.add_argument("--tickers", default="", help="lista separada por vírgulas; vazio = watchlist")
    ap.add_argument("--max", type=int, default=4, help="quantos activos capturar")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    try:
        overview = _get(f"{base}/api/overview")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"não consegui falar com {base}: {type(e).__name__}: {e}")
        return 2

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    else:
        # Os mais movimentados primeiro: são os que dão um relatório com alguma coisa lá dentro.
        linhas = sorted(overview.get("rows", []),
                        key=lambda r: -abs(float(r.get("z") or 0)))
        tickers = [r["ticker"] for r in linhas[: args.max]]
    tickers = tickers[: args.max]

    SAIDA.mkdir(parents=True, exist_ok=True)
    capturados: list[dict] = []
    for t in tickers:
        try:
            rep = _post(f"{base}/api/report", {"scope": "asset", "ticker": t})
            ev = _get(f"{base}/api/evidence?scope=asset&ticker={t}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  {t}: falhou ({type(e).__name__}) — saltado")
            continue
        capturados.append({"ticker": t, "report": rep, "evidence": ev})
        origem = rep.get("source", "?")
        n_sec = len(rep.get("sections", []) or [])
        print(f"  {t}: {n_sec} secções · source={origem}")

    if not capturados:
        print("nada capturado — nenhum estímulo escrito.")
        return 1

    carimbo = datetime.now(UTC).isoformat(timespec="seconds")
    bruto = SAIDA / "report_stimuli.json"
    bruto.write_text(json.dumps(
        {"captured_at": carimbo, "base": base, "items": capturados},
        ensure_ascii=False, indent=1), encoding="utf-8")

    # ⚠️ A regra é a do próprio código (`Report.was_generated`: `source != "deterministic"`), e não
    # uma adivinha minha sobre a cadeia. A primeira versão procurava "generat" no `source` e
    # reportou **0 gerados** para três relatórios cujo `source` era `groq+guarded` — ou seja,
    # gerados e aprovados pela guarda. Um verificador que inventa o seu próprio predicado mede outra
    # coisa; apanhado a correr contra produção.
    gerados = [c for c in capturados
               if str(c["report"].get("source", "")).strip() != "deterministic"]
    L = [
        "# Estímulos do bloco C — relatórios ancorados, congelados",
        "",
        f"> Capturados de `{base}` a {carimbo}. **Não editar.** Gerados por um LLM e portanto "
        "não reproduzíveis: é exactamente por isso que ficam congelados aqui em vez de serem "
        "gerados durante a sessão.",
        "",
        f"- Activos capturados: **{len(capturados)}**",
        f"- Dos quais **realmente gerados**: **{len(gerados)}** "
        f"(os restantes caíram na composição determinística e **não testam a camada generativa** "
        "— separar na análise, nunca misturar)",
        "",
        "⚠️ **Antes da sessão:** escolher **três frases com âncora** por participante e escrevê-las "
        "na folha de recolha. A H5 mede se a pessoa consegue abrir o facto citado e julgar se ele "
        "sustenta a frase, **sem ajuda**.",
        "",
    ]
    for c in capturados:
        rep, ev = c["report"], c["evidence"]
        L += [f"## {c['ticker']} · source: `{rep.get('source', '?')}`", ""]
        for sec in rep.get("sections", []) or []:
            titulo = sec.get("title") or sec.get("key") or "secção"
            L += [f"**{titulo}**", "", sec.get("text", "").strip(), ""]
        L += ["<details><summary>Pacote de evidência (para a travessia de H5)</summary>", ""]
        for f in ev.get("facts", []) or []:
            L.append(f"- `[{f['id']}]` *{f['origin']}* — {f['label']}: {f['value']}")
        L += ["", "</details>", ""]
    (SAIDA / "report_stimuli.md").write_text("\n".join(L), encoding="utf-8")

    print(f"\n[ok] {len(capturados)} estímulos ({len(gerados)} gerados)")
    print(f"     {bruto.relative_to(RAIZ)}")
    print(f"     {(SAIDA / 'report_stimuli.md').relative_to(RAIZ)}")
    if len(gerados) < len(capturados):
        print("\n⚠️ Nem todos foram gerados. Voltar a correr mais tarde dá outra amostra — e a "
              "taxa em si é um dado (a tese reporta 5/6 em produção).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
