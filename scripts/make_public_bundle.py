"""Monta um BUNDLE PÚBLICO limpo (app + tese + código) a partir dos ficheiros versionados.

Parte de `git ls-files` — por isso **nunca** inclui `.env`, segredos ou os corpora grandes
(estão gitignored) — remove os caminhos só-internos (planeamento, memória de continuidade,
material de estudo privado), copia o resto para uma pasta de saída, faz um scan de segredos e,
opcionalmente, inicia um repositório git novo com **1 commit**. **Nunca faz push.**

Ver `docs/design/public_bundle.md` para o manifesto (o que entra, o que fica de fora, e porquê).

Uso:
    python scripts/make_public_bundle.py --out ../InvestiGator-public
    python scripts/make_public_bundle.py --out ../InvestiGator-public --git  # git init + 1 commit
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from investigator.console import force_utf8_stdout

REPO = Path(__file__).resolve().parents[1]

# Caminhos SÓ-INTERNOS (ficam de fora do bundle público). Ver o manifesto para a justificação.
EXCLUDE_PREFIXES = (
    "progress/",          # planeamento multi-sessão (PLANO_V2/TRACKER/SESSIONS + _historico/)
    ".claude/",           # settings + planos internos
    "docs/internal/",     # ROOT_PROMPT + proposta ao orientador
    "docs/_archive/",     # análises antigas de fase inicial
    "docs/defence/",      # caderno de defesa + guia rápido (estudo privado)
    "slides/",            # slides de defesa + guia de estudo (preparação privada)
    # Materiais do estudo de utilidade: os estímulos vêm de um canal público, mas o guião do
    # facilitador contém o CRITÉRIO DE CORREÇÃO. Publicá-los ANTES de correr o estudo deixaria
    # um participante encontrar as respostas, o que enviesaria a única medição humana da tese.
    # Depois de o estudo estar corrido, isto deve ser publicado com os resultados (é o que
    # torna o piloto reproduzível) — remover esta linha nessa altura.
    "docs/study/",
)
EXCLUDE_FILES = {
    "CLAUDE.md",          # memória de continuidade (processo interno)
    "docs/planos/CHECKLIST.md",       # lista de tarefas interna
    "archive/reports/RELATORIO_FINAL.md", # relatório interno para o orientador
}

# Padrões de segredo (defesa em profundidade — os ficheiros versionados já não têm .env).
SECRET_PATTERNS = [
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),          # token de bot Telegram
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9]{20,}"),
]
# Ficheiros onde placeholders são esperados (não alarmar).
SECRET_SCAN_SKIP = {".env.example"}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True)
    return [ln for ln in out.stdout.splitlines() if ln.strip()]


def keep(path: str) -> bool:
    if path in EXCLUDE_FILES:
        return False
    return not any(path.startswith(p) for p in EXCLUDE_PREFIXES)


def scan_secrets(files: list[Path]) -> list[str]:
    hits: list[str] = []
    for f in files:
        if f.name in SECRET_SCAN_SKIP or f.suffix in {".png", ".pdf", ".jpg", ".joblib", ".onnx"}:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                hits.append(f"{f}: {pat.pattern[:40]}")
                break
    return hits


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Monta o bundle público (app + tese + código)")
    ap.add_argument("--out", required=True, help="pasta de saída (fora do repo)")
    ap.add_argument("--git", action="store_true", help="git init + 1 commit no bundle (sem push)")
    ap.add_argument("--force", action="store_true", help="sobrescrever a pasta de saída se existir")
    args = ap.parse_args()

    out = Path(args.out).resolve()
    if REPO in out.parents or out == REPO:
        print(f"ERRO: a saída {out} está dentro do repo. Escolhe uma pasta irmã.")
        return 2
    if out.exists() and any(out.iterdir()):
        if not args.force:
            print(f"ERRO: {out} existe e não está vazia. Usa --force para sobrescrever.")
            return 2
        shutil.rmtree(out)

    files = [f for f in tracked_files() if keep(f)]
    excluded = sum(1 for f in tracked_files() if not keep(f))
    copied: list[Path] = []
    for rel in files:
        src = REPO / rel
        if not src.exists():
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst)

    print(f"Copiados {len(copied)} ficheiros ({excluded} internos excluídos) -> {out}")

    hits = scan_secrets(copied)
    if hits:
        print("\n⚠️  SCAN DE SEGREDOS encontrou possíveis segredos — REVER antes de publicar:")
        for h in hits[:20]:
            print("   ", h)
        print("Bundle deixado no sítio para inspeção; NÃO foi feito git init.")
        return 1
    print("Scan de segredos: limpo.")

    # Aviso de licença (o código ainda não tem licença — decisão com o orientador).
    if not (out / "LICENSE").exists():
        print("\n⚠️  Sem LICENSE no bundle. Adiciona uma licença ANTES de publicar "
              "(decisão com o Prof. Luís Gomes).")

    if args.git:
        subprocess.run(["git", "init", "-q"], cwd=out, check=True)
        subprocess.run(["git", "add", "-A"], cwd=out, check=True)
        subprocess.run(["git", "commit", "-q", "-m",
                        "Initial public release of InvestiGator"], cwd=out, check=True)
        print(f"\nRepositório git iniciado com 1 commit em {out} (sem remote, sem push).")

    print("\nPróximos passos (teus cliques):")
    print("  1. Adicionar LICENSE (com o orientador).")
    print("  2. Criar o repo público VAZIO no GitHub.")
    print(f"  3. cd {out} && git remote add origin <URL> && git push -u origin main")
    print("  Ver docs/design/public_bundle.md para o manifesto completo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
