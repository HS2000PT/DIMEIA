"""Estado dos treinos QI4 em curso. Sem dependencias externas."""
import glob
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cauda(caminho, n=6):
    try:
        with open(caminho, encoding="utf-8", errors="replace") as fh:
            linhas = fh.read().splitlines()
    except OSError as erro:
        return [f"(nao legivel: {erro})"]
    return linhas[-n:] if linhas else ["(vazio)"]


def main():
    padroes = sys.argv[1:] or ["logs/*.log", "logs/*.txt"]
    achados = []
    for padrao in padroes:
        achados.extend(sorted(glob.glob(os.path.join(RAIZ, padrao))))
    if not achados:
        print("nenhum log encontrado para", padroes)
        return
    agora = time.time()
    for caminho in achados:
        idade = (agora - os.path.getmtime(caminho)) / 60.0
        tam = os.path.getsize(caminho)
        rel = os.path.relpath(caminho, RAIZ)
        print(f"=== {rel} | {tam} bytes | ultima escrita ha {idade:.1f} min ===")
        for linha in cauda(caminho):
            print("   ", linha)
        print()


if __name__ == "__main__":
    main()
