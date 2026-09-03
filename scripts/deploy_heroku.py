"""Implanta no Heroku pela API de Sources/Builds.

## Porque é que não é `git push heroku`

O Heroku deixou de aceitar autenticação básica por git nesta conta, e o `git push heroku`
está bloqueado desde a sessão 51. O caminho que funciona é o oficial e tem três passos:
pedir um slot de origem, carregar um tarball, e criar um *build* que aponta para ele.

## A regra de segurança que este script implementa

O tarball sai de `git archive HEAD` — **nunca do directório de trabalho**. É isso que garante
que o `.env`, as chaves e qualquer ficheiro não versionado ficam de fora por construção, em
vez de dependerem de uma lista de exclusões que alguém tem de manter certa.

USO
---
    python scripts/deploy_heroku.py                 # implanta o HEAD
    python scripts/deploy_heroku.py --dry-run       # só mostra o que faria
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

# ⚠️ A consola do Windows e cp1252 e rebenta a imprimir simbolos. Aconteceu na implantacao de
# 2026-08-20: o build tinha SUCEDIDO e o script morreu na linha que imprimia o sucesso, com um
# rasto de excepcao que se le como implantacao falhada. E a setima vez que esta classe aparece
# neste projecto, e aqui e das piores: leva alguem a implantar outra vez sem precisar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import tempfile
import time
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
APP = "investigator"
API = "https://api.heroku.com"


def _run(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ,
                          check=True).stdout.strip()


def _token() -> str:
    """Token do Heroku, do `.env` primeiro e da CLI depois.

    O valor NUNCA e impresso, nem no caminho de erro. Este projecto ja teve duas fugas de
    credencial da mesma familia (sessoes 44 e 51), e nas duas ninguem imprimiu a chave de
    proposito: imprimiu-se a EXCEPCAO, e a mensagem trazia o URL com o segredo dentro. A
    API do Heroku leva o token num cabecalho `Authorization` e nao no URL, o que fecha essa
    porta, mas a regra fica escrita para nao ser reaberta por distraccao.

    A ordem e deliberada. O `.env` e o cofre que o projecto ja usa para as outras chaves,
    esta gitignored, e nao obriga a ter a CLI instalada, que era o que faltava na maquina
    onde esta funcao passou a ser precisa.
    """
    import os

    import investigator.config  # noqa: F401  (o import corre o load_dotenv do projecto)

    do_env = (os.environ.get("HEROKU_API_KEY") or "").strip()
    if do_env:
        print("  token lido do .env")
        return do_env
    # `shell=True` no Windows: o `heroku` e um `.cmd`, e o `CreateProcess` nao o encontra
    # sem passar pelo interpretador de comandos. Sem isto sai `WinError 2`.
    out = subprocess.run("heroku auth:token", capture_output=True, text=True, cwd=RAIZ,
                         shell=True)  # noqa: S602 (comando fixo, sem input do utilizador)
    # `heroku auth:token` sai com codigo 1 E imprime o token na mesma. Nao se verifica o
    # codigo de saida: verifica-se o TOKEN.
    for linha in (out.stdout + "\n" + out.stderr).splitlines():
        linha = linha.strip()
        if linha.startswith("HRKU-") or (len(linha) > 30 and " " not in linha):
            return linha
    raise SystemExit(
        "sem token do Heroku." + chr(10)
        + "  Opcao A (recomendada, nao precisa da CLI): poe a chave no .env, que esta"
        + " gitignored, numa linha HEROKU_API_KEY=..." + chr(10)
        + "  Obtem-se em https://dashboard.heroku.com/account -> API Key -> Reveal."
        + chr(10) + "  Opcao B: instala a CLI do Heroku e corre `heroku login`."
    )


def _api(token: str, method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method, headers={
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read().decode()[:400]}") from e


def _put(url: str, blob: bytes) -> int:
    req = urllib.request.Request(url, data=blob, method="PUT",
                                 headers={"Content-Type": ""})
    with urllib.request.urlopen(req, timeout=600) as r:  # noqa: S310
        return r.status


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    sha = _run("git", "rev-parse", "--short", "HEAD")
    sujo = _run("git", "status", "--porcelain")
    if sujo:
        print("⚠️  árvore suja — o tarball sai do HEAD e NÃO inclui estas alterações:")
        print("   " + "\n   ".join(sujo.splitlines()[:8]))

    print(f"a implantar {sha} em {APP}")
    if args.dry_run:
        return 0

    token = _token()
    print("  token ok")

    tmp = pathlib.Path(tempfile.mkdtemp()) / "src.tar.gz"
    _run("git", "archive", "--format=tar.gz", "-o", str(tmp), "HEAD")
    blob = tmp.read_bytes()
    print(f"  tarball {len(blob) / 1e6:.1f} MB (de git archive: sem .env por construção)")

    src = _api(token, "POST", f"/apps/{APP}/sources")
    print("  slot de origem ok")

    code = _put(src["source_blob"]["put_url"], blob)
    print(f"  upload {code}")

    build = _api(token, "POST", f"/apps/{APP}/builds", {
        "source_blob": {"url": src["source_blob"]["get_url"], "version": sha},
    })
    bid = build["id"]
    print(f"  build {bid} -> {build['status']}")

    inicio = time.time()
    while True:
        time.sleep(10)
        # ⚠️ UM TEMPO ESGOTADO A CONSULTAR NÃO É UM BUILD FALHADO. A 2026-08-20 a leitura de
        # uma destas consultas expirou, o script morreu com um rasto de excepção e a
        # implantação **tinha corrido bem** — a página nova já estava no ar. Um rasto que se
        # lê como falha leva alguém a implantar outra vez, ou pior, a desfazer o que resultou.
        # A consulta é de leitura pura, portanto repetir é seguro.
        try:
            b = _api(token, "GET", f"/apps/{APP}/builds/{bid}")
        except Exception as e:  # noqa: BLE001
            print(f"  [{time.time() - inicio:5.0f}s] consulta falhou ({type(e).__name__}), "
                  f"a repetir — o build continua no Heroku")
            continue
        st = b["status"]
        print(f"  [{time.time() - inicio:5.0f}s] {st}")
        if st != "pending":
            if st == "succeeded":
                rel = (b.get("release") or {}).get("id", "?")
                print(f"\n✅ build OK — release {rel}")
                return 0
            print(f"\n❌ build {st} — {b.get('output_stream_url', '')}")
            return 1
        if time.time() - inicio > 900:
            print("\n⏱️  timeout à espera do build")
            return 1


if __name__ == "__main__":
    sys.exit(main())
