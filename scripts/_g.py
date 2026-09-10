"""grep minimo, seguro contra o quoting do PowerShell/cmd.

Uso: python scripts\\_g.py <ficheiro> <regex> [<regex> ...] [--ctx N] [--cs]
Varios regex sao combinados com OU. Nunca escrever '|' na linha de comandos:
o cmd interpreta-o como pipe. Passar padroes separados por espaco.
"""
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("uso: _g.py <ficheiro> <regex> [<regex> ...] [--ctx N] [--cs]")
        raise SystemExit(2)
    contexto = 0
    sinal = re.IGNORECASE
    padroes = []
    caminho = args[0]
    i = 1
    while i < len(args):
        a = args[i]
        if a == "--ctx":
            contexto = int(args[i + 1])
            i += 2
        elif a == "--cs":
            sinal = 0
            i += 1
        else:
            padroes.append(a)
            i += 1
    rx = re.compile("|".join(f"(?:{p})" for p in padroes), sinal)
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        linhas = fh.read().splitlines()
    mostradas = set()
    for n, linha in enumerate(linhas):
        if rx.search(linha):
            for j in range(max(0, n - contexto), min(len(linhas), n + contexto + 1)):
                if j not in mostradas:
                    mostradas.add(j)
                    marca = ">" if j == n else " "
                    print(f"{j + 1:6d}{marca} {linhas[j]}")
            if contexto:
                print("   ---")
    if not mostradas:
        print("(sem correspondencias)")


if __name__ == "__main__":
    main()
