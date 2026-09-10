"""Substitui o bloco de retoma do docs/contexto/ESTADO_ATUAL.md, preservando terminacoes de linha.

Uso: python scripts\\_patch_estado.py <ficheiro_com_o_texto_novo>
O texto novo substitui tudo entre o inicio do documento e a linha `---` que fecha o bloco
de retoma (a primeira ocorrencia de uma linha com apenas `---` seguida de `## 0.`).
"""
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ALVO = RAIZ / "docs/contexto/ESTADO_ATUAL.md"
MARCA = "\n---\n\n## 0."


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: _patch_estado.py <ficheiro_com_o_texto_novo>")
        return 2
    novo = pathlib.Path(sys.argv[1]).read_bytes().decode("utf-8").replace("\r\n", "\n")
    bruto = ALVO.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    texto = bruto.replace("\r\n", "\n")
    i = texto.find(MARCA)
    if i < 0:
        print("ABORTADO: nao encontrei a marca de fim do bloco de retoma")
        return 1
    resultado = novo.rstrip("\n") + texto[i:]
    ALVO.write_bytes((resultado.replace("\n", "\r\n") if crlf else resultado).encode("utf-8"))
    print("docs/contexto/ESTADO_ATUAL.md actualizado; terminacoes:", "CRLF" if crlf else "LF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
