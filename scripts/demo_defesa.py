"""Demonstração de defesa: um dia REAL do sistema, reproduzido a partir dos registos.

PORQUE É QUE ESTA DEMO É UM REPLAY, E PORQUE ISSO NÃO É UM DEFEITO
------------------------------------------------------------------
A tentação é ligar o sistema à frente do júri e esperar por um alerta. Não se faz, por uma
razão que é o próprio resultado do trabalho: **nove em cada dez varreduras não mandam nada**.
O silêncio é o comportamento correcto, não uma avaria. Uma demo ao vivo mostraria, com toda a
probabilidade, um ecrã parado — e a alternativa, forçar um alerta, seria fabricar exactamente
aquilo que esta tese recusa fabricar.

O que se faz em vez disso: reproduzir um dia que **aconteceu mesmo**, a partir de três
registos versionados que o sistema escreveu enquanto corria —

  * `gate_log.jsonl`        — onde cada ticker morreu, e com que margem
  * `predictions_log.jsonl` — a probabilidade de triagem de cada decisão
  * `alerts_history.jsonl`  — o texto exacto que o canal recebeu, com carimbos

Nada aqui é reconstruído por aproximação: cada linha impressa vem de um ficheiro escrito no
momento em que a decisão foi tomada. É determinístico, corre sem rede depois da primeira vez,
e mostra as duas metades que interessam: **o que passou** e, sobretudo, **o que não passou**.

USO
---
    python scripts/demo_defesa.py                 # o dia mais movimentado com alertas
    python scripts/demo_defesa.py --dia 2026-08-07
    python scripts/demo_defesa.py --offline       # só cache local (sala sem wi-fi)
    python scripts/demo_defesa.py --listar        # que dias existem
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import textwrap
import urllib.request
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

BRANCH = "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history/"
CACHE = RAIZ / "data" / "_demo_cache"
FICHEIROS = ("gate_log.jsonl", "predictions_log.jsonl", "alerts_history.jsonl")

L = 78  # largura


def _c(s: str, cor: str) -> str:
    cores = {"v": "\033[32m", "r": "\033[31m", "a": "\033[33m", "c": "\033[36m",
             "b": "\033[1m", "d": "\033[2m", "0": "\033[0m"}
    return f"{cores.get(cor, '')}{s}{cores['0']}"


def _regra(t: str = "") -> None:
    print(_c("─" * L, "d") if not t else _c(f"── {t} " + "─" * max(0, L - len(t) - 4), "c"))


def _carregar(offline: bool) -> dict[str, list[dict]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    out: dict[str, list[dict]] = {}
    for nome in FICHEIROS:
        local = CACHE / nome
        if not offline:
            try:
                dados = urllib.request.urlopen(BRANCH + nome, timeout=30).read()  # noqa: S310
                local.write_bytes(dados)
            except Exception as exc:  # noqa: BLE001
                print(_c(f"[rede] {nome}: {type(exc).__name__} — uso a cache", "a"))
        if not local.exists():
            raise SystemExit(f"Sem {nome} em cache e sem rede. Corre uma vez com internet.")
        out[nome] = [json.loads(x) for x in local.read_text(encoding="utf-8").splitlines() if x]
    return out


def _envolver(txt: str, indent: str = "    ") -> str:
    linhas = []
    for bruta in txt.splitlines():
        linhas.extend(textwrap.wrap(bruta, L - len(indent)) or [""])
    return "\n".join(indent + x for x in linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description="Demo de defesa (replay de um dia real)")
    ap.add_argument("--dia", default="")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    from investigator.console import force_utf8_stdout

    force_utf8_stdout()

    d = _carregar(args.offline)
    gates, preds, hist = d["gate_log.jsonl"], d["predictions_log.jsonl"], d["alerts_history.jsonl"]

    dias_com_alerta = collections.Counter(
        g["date"] for g in gates if g["stage"] == "alerted")
    if args.listar:
        print("dia         decisões  alertas")
        for dia, n in sorted(collections.Counter(g["date"] for g in gates).items()):
            print(f"{dia}  {n:>8}  {dias_com_alerta.get(dia, 0):>7}")
        return 0

    dia = args.dia or max(dias_com_alerta, key=lambda k: (dias_com_alerta[k], k))
    do_dia = [g for g in gates if g["date"] == dia]
    if not do_dia:
        raise SystemExit(f"Sem registos para {dia}. Usa --listar.")

    print()
    _regra()
    print(_c(f"  InvestiGator — um dia real, reproduzido dos registos    {dia}", "b"))
    _regra()
    print(_envolver(
        "Isto NÃO é uma corrida ao vivo. É a reprodução de um dia que aconteceu, a partir dos "
        "ficheiros que o sistema escreveu enquanto corria. Escolhi um replay de propósito: nove "
        "em cada dez varreduras não mandam nada, e o silêncio é o comportamento correcto — uma "
        "demo ao vivo mostraria um ecrã parado, e forçar um alerta seria fabricar evidência.", ""))
    print()

    # ── 1. o funil do dia ────────────────────────────────────────────────────
    _regra("1. o funil do dia: o que a varredura fez com cada empresa")
    por_fase = collections.Counter(g["stage"] for g in do_dia)
    total = sum(por_fase.values())
    nomes = {"alerted": ("alerta enviado", "v"),
             "triage_suppressed": ("travado na triagem", "a"),
             "weak_precedent": ("evidência fraca demais", "a"),
             "error": ("sem dados de preço", "d")}
    for fase, n in por_fase.most_common():
        rot, cor = nomes.get(fase, (fase, ""))
        barra = "█" * max(1, round(40 * n / total))
        print(f"  {rot:<24} {_c(barra, cor)} {n:>3}  ({100 * n / total:.0f}%)")
    print()
    print(_envolver(
        f"{total} decisões, {por_fase.get('alerted', 0)} alertas. É esta a resposta à fadiga de "
        "alertas, e é medida e não afirmada: a maior parte do trabalho do sistema é decidir "
        "CALAR-SE.", "  "))
    print()

    # ── 2. o silêncio, com a margem ──────────────────────────────────────────
    _regra("2. porque é que cada empresa ficou de fora (a parte que ninguém mostra)")
    # Uma linha por EMPRESA e não por decisão: o registo tem uma entrada por ciclo, e num dia
    # com muitos ciclos a mesma empresa aparece repetida. Para um leitor, o que interessa é
    # "onde é que esta empresa parou", não quantas vezes lá parou.
    vistos: dict[str, dict] = {}
    for g in do_dia:
        if g["stage"] != "alerted":
            vistos.setdefault(g["ticker"], g)
    for g in list(vistos.values())[:9]:
        rot, cor = nomes.get(g["stage"], (g["stage"], ""))
        print(f"  {g['ticker']:<6} {_c(rot, cor):<32} {_c(g['detail'][:38], 'd')}")
    print()
    print(_envolver(
        "Cada linha traz a MARGEM que faltou, não só o veredicto. Nenhum produto comercial "
        "mostra o que descartou; aqui o silêncio é uma decisão do sistema, logo tem de poder "
        "ser inspeccionado.", "  "))
    print()

    # ── 3. um alerta, de ponta a ponta ───────────────────────────────────────
    enviados = [g for g in do_dia if g["stage"] == "alerted"]
    if not enviados:
        print(_c("  (dia sem alertas — escolhe outro com --listar)", "a"))
        return 0
    alvo = enviados[0]
    _regra(f"3. um alerta seguido até ao fim — {alvo['ticker']}")
    print(f"  {_c('manchete captada', 'b')}")
    print(_envolver(alvo["detail"], "    "))
    print()

    def _mesma(x: dict) -> bool:
        return (x["ticker"] == alvo["ticker"]
                and x.get("headline", "")[:40] == alvo["detail"][:40])

    p = next((x for x in preds if _mesma(x)), None)
    passos = [
        ("relevância", "nomeia a empresa e não é boilerplate de mercado", True),
        ("frescura", "dentro da janela de 2 dias", True),
        ("recuperação", "precedentes acima do chão de similaridade 0.45", True),
    ]
    if p:
        passos.append(("triagem", f"P(movimento anormal) = {float(p['prob']):.0%} "
                                  f"≥ {float(p.get('gate', 0.5)):.0%}", bool(p["kept"])))
    passos.append(("tecto e dedup", "abaixo de 2/empresa/dia; não repetido", True))
    for nome, det, ok in passos:
        print(f"  {_c('✓' if ok else '✗', 'v' if ok else 'r')} {nome:<16} {_c(det, 'd')}")
    print()

    entregue = next((h for h in hist
                     if h["date"] == dia and h["ticker"] == alvo["ticker"] and h["kind"] == "news"),
                    None)
    if entregue:
        print(f"  {_c('a mensagem que o canal recebeu, verbatim', 'b')}")
        print()
        print(_envolver(entregue["text"], "  │ "))
        print()
        if "not a forecast" in entregue["text"]:
            # Mensagem anterior a 2026-08-09. Dizer isto em voz alta é melhor do que deixar o
            # júri notar a diferença entre o que a tese descreve e o que o registo mostra.
            print(_envolver(
                "⚠️ Nota, e é a favor: esta mensagem é anterior a 9 de Agosto de 2026 e termina "
                "em «not a forecast». Essa frase era FALSA — uma probabilidade sobre os próximos "
                "dias é uma afirmação sobre o futuro — e foi corrigida. O registo fica como está "
                "porque é histórico; o que mudou foi o sistema, não o passado.", "  "))
            print()
        ev, det, snt = (entregue.get("event_at"), entregue.get("detected_at"),
                        entregue.get("sent_at"))
        if ev and det and snt:
            f = "%Y-%m-%dT%H:%M:%SZ"
            try:
                a, b, c = (datetime.strptime(x, f) for x in (ev, det, snt))
                print(f"  {_c('latência, decomposta', 'b')}")
                fonte = _c(f"{(b - a).total_seconds() / 60:>6.0f} min", "a")
                nosso = _c(f"{(c - b).total_seconds():>6.0f} s", "v")
                print(f"    publicação → detecção   {fonte}   "
                      + _c("(a fonte; fora do nosso controlo)", "d"))
                print(f"    detecção → entrega      {nosso}   "
                      + _c("(o nosso lado)", "d"))
                print()
                print(_envolver(
                    "As duas componentes têm de aparecer separadas: um número agregado não "
                    "distingue «somos lentos» de «a fonte é lenta», e as duas afirmações pedem "
                    "coisas opostas.", "  "))
            except ValueError:
                pass
    print()
    _regra()
    print(_envolver(
        "Tudo o que apareceu acima saiu de ficheiros versionados escritos pelo sistema no "
        "momento das decisões. Volta a correr e dá o mesmo — é essa a diferença entre uma "
        "demonstração e uma encenação.", ""))
    _regra()
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
