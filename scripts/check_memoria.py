"""Os dois ficheiros de continuidade dizem em que sessão vamos, e dizem o mesmo?

O projeto mantém DOIS ficheiros de memória persistente, o `CLAUDE.md` e o `AGENTS.md`, lidos
por agentes diferentes no início de cada sessão. Não são cópias um do outro — medido a
2026-09-06: partilham 3473 das 4129 linhas, e o bloco `## Estado Atual` só coincide nas
primeiras 185, a partir das quais divergem por escrito. Este verificador **não** exige que
sejam iguais, porque não são e nunca foram.

O que exige é o pedaço que tem de ser igual, e que se sabe que derrapa.

⚠️ **PORQUE EXISTE, e é um defeito medido e não hipotético.** A 2026-09-06 o `AGENTS.md`
declarava «Sessão nº: 61 · Última atualização: 2026-08-23» com o Estado Atual acima dessa linha
já na sessão 65. O bloco do topo era espelhado a cada sessão e o rodapé não, pelo que um agente
que lesse o rodapé para saber onde estava ficava **cinco sessões atrás**, com o resto do
ficheiro a contradizê-lo. Nada disparava: são duas linhas de texto válido.

Três regras, e a terceira é a que apanha o caso em que os DOIS rodapés ficam para trás ao mesmo
tempo, que a comparação entre ficheiros sozinha deixaria passar:

1. a linha `- **Sessão nº:**` é idêntica nos dois ficheiros;
2. a linha `- **Última atualização:**` é idêntica nos dois, e é uma data que existe e não está
   no futuro;
3. em CADA ficheiro, o número do rodapé é o do cabeçalho de sessão mais alto do documento.

    python scripts/check_memoria.py
    python scripts/check_memoria.py --autoteste
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FICHEIROS = ("CLAUDE.md", "AGENTS.md")

RX_SESSAO = re.compile(r"^- \*\*Sessão nº:\*\*.*$", re.M)
RX_DATA = re.compile(r"^- \*\*Última atualização:\*\*.*$", re.M)
# Só cabeçalhos de sessão, e não a prosa: há linhas de corpo com «SESSÃO 40» lá dentro, e
# apanhá-las faria o verificador comparar contra um número que ninguém escreveu como estado.
RX_CABECALHO = re.compile(r"^- \*\*[^A-Za-z\n]*SESSÃO\s+(\d+)", re.M)
RX_NUMERO = re.compile(r"Sessão nº:\*\*\s*(\d+)")
RX_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def linha(texto: str, rx: re.Pattern[str]) -> str | None:
    """A única linha que corresponde, ou None se não houver exactamente uma."""
    achados = rx.findall(texto)
    return achados[0] if len(achados) == 1 else None


def sessao_do_rodape(texto: str) -> int | None:
    ln = linha(texto, RX_SESSAO)
    if ln is None:
        return None
    m = RX_NUMERO.search(ln)
    return int(m.group(1)) if m else None


def sessao_mais_alta(texto: str) -> int | None:
    numeros = [int(n) for n in RX_CABECALHO.findall(texto)]
    return max(numeros) if numeros else None


def data_do_rodape(texto: str) -> dt.date | None:
    ln = linha(texto, RX_DATA)
    if ln is None:
        return None
    m = RX_ISO.search(ln)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def achados(textos: dict[str, str], hoje: dt.date) -> list[str]:
    """As falhas encontradas. Lista vazia quer dizer que as três regras passam."""
    fora: list[str] = []
    nomes = list(textos)

    # regra 1 e 2: as duas linhas são as mesmas nos dois ficheiros
    for rotulo, rx in (("Sessão nº", RX_SESSAO), ("Última atualização", RX_DATA)):
        valores = {n: linha(textos[n], rx) for n in nomes}
        em_falta = [n for n, v in valores.items() if v is None]
        if em_falta:
            fora.append(f"{rotulo}: linha ausente ou repetida em {', '.join(em_falta)}")
            continue
        if len(set(valores.values())) > 1:
            fora.append(f"{rotulo}: diverge entre os ficheiros")
            for n in nomes:
                fora.append(f"    {n}: {valores[n]}")

    # regra 2b: a data existe e não está no futuro
    for n in nomes:
        d = data_do_rodape(textos[n])
        if d is None:
            if not any("Última atualização" in f for f in fora):
                fora.append(f"Última atualização: {n} não traz uma data AAAA-MM-DD válida")
        elif d > hoje:
            fora.append(f"Última atualização: {n} está no futuro ({d})")

    # regra 3: o rodapé acompanha o cabeçalho mais recente DO PRÓPRIO ficheiro
    for n in nomes:
        rodape, topo = sessao_do_rodape(textos[n]), sessao_mais_alta(textos[n])
        if topo is None:
            fora.append(f"{n}: não encontrei nenhum cabeçalho de sessão. Não é seguro validar.")
        elif rodape is None:
            fora.append(f"{n}: não encontrei o número de sessão no rodapé.")
        elif rodape != topo:
            fora.append(f"{n}: o rodapé diz sessão {rodape} e o registo mais recente é a {topo}")
    return fora


def autoteste() -> bool:
    """Planta cada defeito e exige que dispare. Sem isto, '0 achados' não vale nada."""
    hoje = dt.date(2026, 9, 6)
    bom = ("- **🆕 SESSÃO 66 (2026-09-06): o que aconteceu.**\n"
           "- **🆕 SESSÃO 65 (2026-09-05): o que aconteceu antes.**\n"
           "- **Sessão nº:** 66 (uma frase)\n"
           "- **Última atualização:** 2026-09-06\n")
    casos = [
        ("limpo dispara?", {"A.md": bom, "B.md": bom}, False),
        ("rodapés divergentes",
         {"A.md": bom, "B.md": bom.replace("Sessão nº:** 66", "Sessão nº:** 61")}, True),
        ("datas divergentes",
         {"A.md": bom, "B.md": bom.replace("atualização:** 2026-09-06",
                                           "atualização:** 2026-08-23")}, True),
        ("os DOIS rodapés para trás",
         {"A.md": bom.replace("Sessão nº:** 66", "Sessão nº:** 65"),
          "B.md": bom.replace("Sessão nº:** 66", "Sessão nº:** 65")}, True),
        ("data no futuro",
         {"A.md": bom.replace("atualização:** 2026-09-06", "atualização:** 2027-01-01"),
          "B.md": bom.replace("atualização:** 2026-09-06", "atualização:** 2027-01-01")}, True),
        ("rodapé ausente",
         {"A.md": bom, "B.md": bom.replace("- **Sessão nº:** 66 (uma frase)\n", "")}, True),
    ]
    ok = True
    for nome, textos, espera in casos:
        disparou = bool(achados(textos, hoje))
        marca = "OK  " if disparou == espera else "FALHA"
        if disparou != espera:
            ok = False
        esperado = "esperado disparo" if espera else "esperado silêncio"
        print(f"  {marca} {nome}: {esperado}")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--autoteste", action="store_true", help="só o controlo negativo")
    args = p.parse_args()

    print("Controlo negativo do detector:")
    if not autoteste():
        print("\n⚠️  O DETECTOR ESTÁ PARTIDO. Qualquer 'nenhum achado' abaixo não vale nada.")
        return 2
    if args.autoteste:
        return 0

    # ⚠️ Recusar-se a validar sem corpus. Um verificador que não encontra os ficheiros e sai a
    # zero é indistinguível de um que os leu e não achou nada — foi assim que o
    # `verify_bibliography` da sessão 65 dizia «26 entradas em 1 ficheiros».
    textos: dict[str, str] = {}
    for nome in FICHEIROS:
        f = RAIZ / nome
        if not f.exists():
            print(f"\nERRO: {nome} não existe em {RAIZ}. Não é seguro validar sem corpus.")
            return 2
        textos[nome] = f.read_text(encoding="utf-8", errors="replace")

    print(f"\nContinuidade: {' e '.join(FICHEIROS)}\n")
    for nome in FICHEIROS:
        print(f"  {nome}: rodapé na sessão {sessao_do_rodape(textos[nome])}, "
              f"registo mais recente a {sessao_mais_alta(textos[nome])}, "
              f"data {data_do_rodape(textos[nome])}")

    fora = achados(textos, dt.date.today())
    print()
    if fora:
        for f in fora:
            print(f"  !! {f}")
        print("\nFALHA: quem ler o rodapé fica noutra sessão que não a do registo acima dele.")
        return 1
    print("ok  os dois ficheiros declaram a mesma sessão, e é a do registo mais recente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
