"""Cada excerto do guia de construção existe VERBATIM no ficheiro que ele diz ser a fonte.

⚠️ POR QUE É QUE ESTA PORTA EXISTE. O `tese/guia_construir/` promete uma coisa e só uma: que o
código que mostra é o código que está no repositório, não uma versão simplificada para ensinar. O
aluno vai decorá-lo para o defender perante um júri que pode abrir o repositório, e um excerto
errado é pior do que excerto nenhum, porque ele defende com confiança uma coisa que não existe.

Sem esta porta, a promessa vale o que valer a memória de quem escreveu o guia. Pior: o código
vive e muda, portanto um excerto correcto hoje deixa de o ser sem que nada avise.

⚠️ A VERIFICAÇÃO É EM DUAS PASSAGENS, e a segunda existe por causa de um defeito real.
A primeira exige que cada linha do excerto exista no ficheiro. A segunda exige que os blocos
sejam **contíguos e pela ordem certa**. Escrevi a primeira sozinha, e ela deu VERBATIM a um
excerto que colava duas funções saltando uma terceira sem marcar o corte: cada linha existia, o
bloco não. Um estudante que decorasse aquilo aprenderia que `abnormal_returns` vem logo a seguir a
`post_event_returns`, e nunca saberia que `mean_impact` existe.

Onde há um corte, ele tem de estar marcado com uma linha `# ...`. Um corte por marcar é o defeito
que esta porta apanha.

    python scripts/check_guia_codigo.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
GUIA = RAIZ / "tese-pt" / "guia_construir" / "main.tex"
B = chr(92)
CORTE = "# ..."


def blocos(texto: str) -> list[tuple[str, str]]:
    """Devolve (ficheiro_fonte, codigo) para cada lstlisting precedido de \\fonte{...}."""
    padrao = re.compile(
        re.escape(B + "fonte{") + r"([^}]+)\}\s*"
        + re.escape(B + "begin{lstlisting}") + r"(.*?)"
        + re.escape(B + "end{lstlisting}"),
        re.S,
    )
    return [(m.group(1), m.group(2)) for m in padrao.finditer(texto)]


def main() -> int:
    if not GUIA.exists():
        print(f"nao existe: {GUIA}")
        return 1
    texto = GUIA.read_text(encoding="utf-8")
    achados = blocos(texto)

    # Um lstlisting sem \fonte escapa a esta porta por inteiro, e e o modo mais facil de a
    # contornar sem querer. Conta-los e comparar e o que fecha esse buraco.
    total_listagens = texto.count(B + "begin{lstlisting}")
    if total_listagens != len(achados):
        print(f"FALHA  {total_listagens - len(achados)} excerto(s) sem \\fonte{{...}} antes,")
        print("       logo nao sao verificados por ninguem. Marcar a fonte de todos.")
        return 1

    falhas = 0
    for fonte_rel, codigo in achados:
        alvo = RAIZ / fonte_rel
        nome = fonte_rel.split("/")[-1]
        if not alvo.exists():
            print(f"FALHA  {nome}: o ficheiro nao existe")
            falhas += 1
            continue
        origem = alvo.read_text(encoding="utf-8")

        segmentos = [s.strip("\n") for s in codigo.split(CORTE)]
        segmentos = [s for s in segmentos if s.strip()]
        pos, mau = 0, None
        for i, seg in enumerate(segmentos):
            onde = origem.find(seg, pos)
            if onde < 0:
                mau = i + 1
                break
            pos = onde + len(seg)
        if mau is not None:
            # Distingue "nao existe" de "existe mas fora de ordem", porque as correccoes diferem:
            # a primeira e um excerto mal copiado, a segunda e um corte por marcar.
            existe = origem.find(segmentos[mau - 1]) >= 0
            porque = ("existe no ficheiro mas NAO nesta ordem: falta um `# ...` a marcar o corte"
                      if existe else "nao existe no ficheiro")
            print(f"FALHA  {nome}: segmento {mau} de {len(segmentos)} {porque}")
            falhas += 1
            continue

        linha = origem[:origem.find(segmentos[0])].count("\n") + 1
        print(f"  ok   {nome:<22} {len(segmentos)} segmento(s), a partir da linha {linha}")

    # O \verifica{...} de cada fase promete um comando que se pode correr. Um teste renomeado ou
    # apagado deixaria a promessa em pe sem nada avisar, e o aluno so descobriria a correr.
    alvos = re.findall(re.escape(B + "verifica{") + r"([^}]+)\}", texto)
    for bruto in alvos:
        caminho = bruto.replace(B + "_", "_").split()[-1]
        if not (RAIZ / caminho).exists():
            print(f"FALHA  \\verifica aponta para {caminho}, que nao existe")
            falhas += 1

    if falhas:
        print(f"\n{falhas} problema(s): o guia ja nao corresponde ao repositorio.")
        return 1
    print(f"\n{len(achados)} excertos verbatim e contiguos, "
          f"{len(alvos)} comandos de verificacao que existem.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
