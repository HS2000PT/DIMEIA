"""Recupera linhas de feedback eliminadas por uma substituição antiga da branch de dados.

O commit de origem continua no Git, por isso a recuperação copia exatamente as linhas que
existiam — não reconstrói votos, não altera campos e não cria observações. O destino tem de ser
um ``feedback.jsonl`` dentro de um checkout Git separado. As linhas em falta são acrescentadas;
o analisador ordena-as pelo instante gravado antes de resolver o último voto.

Exemplo:
    python scripts/recover_feedback_history.py \
      --source a9e098cda --target tmp/feedback-recovery/feedback.jsonl --expect 6
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"chave_alerta", "votante", "acao", "at"}


def _git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=30,
        check=False,
    )
    if result.returncode:
        raise SystemExit(f"git {' '.join(args)} falhou: {result.stderr.strip()}")
    return result.stdout


def _validar_linhas(linhas: list[str], origem: str) -> None:
    for numero, linha in enumerate(linhas, 1):
        try:
            carga = json.loads(linha)
        except ValueError as exc:
            raise SystemExit(f"{origem}:{numero} não é JSON válido") from exc
        if not isinstance(carga, dict) or not REQUIRED.issubset(carga):
            raise SystemExit(f"{origem}:{numero} não tem o esquema mínimo de feedback")
        if carga["acao"] not in {"u", "n", "d"}:
            raise SystemExit(f"{origem}:{numero} tem uma ação desconhecida")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="commit que ainda contém as linhas")
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--expect", required=True, type=int, help="número exato esperado")
    args = parser.parse_args()

    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", args.source):
        raise SystemExit("--source tem de ser um identificador de commit hexadecimal")
    target = args.target.resolve()
    if target.name != "feedback.jsonl":
        raise SystemExit("o destino tem de se chamar feedback.jsonl")
    checkout = Path(_git("rev-parse", "--show-toplevel", cwd=target.parent).strip()).resolve()
    if target.parent != checkout:
        raise SystemExit("o destino tem de estar na raiz do checkout da branch de dados")

    antigas = [
        linha
        for linha in _git("show", f"{args.source}:feedback.jsonl", cwd=ROOT).splitlines()
        if linha.strip()
    ]
    atuais = (
        [linha for linha in target.read_text(encoding="utf-8").splitlines() if linha.strip()]
        if target.exists()
        else []
    )
    _validar_linhas(antigas, args.source)
    _validar_linhas(atuais, str(target))

    vistas = set(atuais)
    em_falta = [linha for linha in antigas if linha not in vistas]
    if len(em_falta) != args.expect:
        raise SystemExit(
            f"recusado: encontrei {len(em_falta)} linha(s) em falta, esperava {args.expect}"
        )
    target.write_text("\n".join(atuais + em_falta) + "\n", encoding="utf-8", newline="\n")
    total = len(atuais) + len(em_falta)
    print(f"Recuperadas {len(em_falta)} linhas exatas de {args.source}; total {total}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
