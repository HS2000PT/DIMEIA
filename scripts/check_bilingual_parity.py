"""Paridade EN<->PT nas frases que carregam citações.

O QUE ISTO PROCURA
------------------
Já está verificado, por contagem, que as duas teses têm as mesmas 129 instâncias de citação e
as mesmas 59 chaves. Isso não é o risco. **O risco é a tradução endurecer a afirmação**: se o
inglês diz *"suggests"* e o português diz *"demonstra"*, a citação passa a sustentar mais do que
aguenta — e é a versão PT que o júri português lê.

O mesmo defeito tem uma segunda forma, mais silenciosa: um *hedge* que simplesmente **desaparece**
na tradução ("in this corpus", "preliminary", "approximately"). A frase fica verdadeira em geral
e falsa em particular, que é a maneira mais fácil de um trabalho honesto passar a parecer
exagerado sem ninguém ter mentido.

O QUE ISTO **NÃO** É
--------------------
Não é um juiz. É um filtro: reduz 129 instâncias às poucas que valem leitura humana. Um
disparo é um candidato, não um veredicto.

O CONTROLO NEGATIVO, E PORQUÊ ESTÁ AQUI DENTRO
----------------------------------------------
Um detector que não encontra nada pode estar a funcionar ou pode estar partido, e as duas coisas
lêem-se exactamente da mesma maneira no ecrã. Por isso `--autoteste` planta um endurecimento e um
*hedge* perdido e **exige que o detector dispare nos dois**, e que fique calado numa tradução
fiel. Se o autoteste falhar, o resultado "0 achados" não vale nada e o script diz isso.

Isto não é zelo: a primeira versão deste código apanhava `causa` dentro de *causal*,
*causalmente* e *causar*, e acusou cinco frases perfeitamente fiéis — uma delas dizia
"podem causar", que é o *hedge* oposto ao que estava a ser reportado.

USO
---
    python scripts/check_bilingual_parity.py
    python scripts/check_bilingual_parity.py --autoteste
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PAT = re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")

# Marcas de CAUTELA. Uma frase que as perde na tradução ficou mais forte.
HEDGE_EN = [
    "suggest", "may", "might", "could", "appears", "seems", "indicate", "associated",
    "tends", "likely", "preliminary", "broadly", "roughly", "approximately", "typically",
    "often", "generally", "rather than", "arguably", "partly", "largely", "mostly",
]
HEDGE_PT = [
    "sugere", "pode", "poderia", "parece", "indica", "associad", "tende", "provavel",
    "preliminar", "aproximadamente", "tipicamente", "frequentemente", "geralmente",
    "em parte", "por regra", "cerca de", "em vez de", "sobretudo", "largamente",
]
# Marcas de FORÇA. Uma frase que as ganha na tradução ficou mais forte.
FORTE_EN = [
    # "proof" e "prove" precisam de entrada própria: o `\b...\w*\b` não liga uma à outra, e
    # sem isto o PT "prova" disparava contra o EN "proof", que diz exactamente o mesmo.
    "demonstrate", "prove", "proof", "guarantee", "always", "never", "confirms",
    "necessarily", "establishes",
]
FORTE_PT = [
    "demonstra", "prova", "garante", "sempre", "nunca", "obriga", "confirma",
    "necessariamente", "implica",
]


def conta(frase: str, marcas: list[str]) -> int:
    """Conta marcas com FRONTEIRA DE PALAVRA (ver docstring do módulo)."""
    b = frase.lower()
    return sum(1 for t in marcas if re.search(r"\b" + re.escape(t.strip()) + r"\w*\b", b))


def endurece(en: str, pt: str) -> bool:
    """O PT afirma mais do que o EN?"""
    return (conta(en, HEDGE_EN) - conta(pt, HEDGE_PT)) >= 2 or (
        conta(pt, FORTE_PT) - conta(en, FORTE_EN)
    ) >= 1


def frases_com_citacao(caminho: pathlib.Path) -> dict[str, str]:
    texto = re.sub(r"(?m)^\s*%.*$", "", caminho.read_text(encoding="utf-8"))
    plano = " ".join(texto.split())
    saida: dict[str, str] = {}
    for m in PAT.finditer(plano):
        ini = plano.rfind(".", 0, m.start())
        fim = plano.find(".", m.end())
        frase = plano[ini + 1 : fim if fim > 0 else len(plano)].strip()
        for chave in m.group(1).split(","):
            saida.setdefault(chave.strip(), frase)
    return saida


def autoteste() -> bool:
    casos = [
        ("endurecimento plantado", True,
         "The survey suggests that text may indicate materiality",
         "O survey demonstra que o texto indica materialidade"),
        ("tradução fiel", False,
         "The survey suggests that text may indicate materiality",
         "O survey sugere que o texto pode indicar materialidade"),
        ("hedge perdido", True,
         "This holds approximately and typically in this corpus",
         "Isto verifica-se neste corpus"),
    ]
    ok = True
    for nome, esperado, en, pt in casos:
        obtido = endurece(en, pt)
        estado = "OK  " if obtido == esperado else "FALHA"
        if obtido != esperado:
            ok = False
        print(f"  {estado} {nome}: esperado {'disparo' if esperado else 'silêncio'}")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--autoteste", action="store_true", help="só o controlo negativo")
    args = p.parse_args()

    print("Controlo negativo do detector:")
    if not autoteste():
        print("\n⚠️  O DETECTOR ESTÁ PARTIDO. Qualquer '0 achados' abaixo não vale nada.")
        return 2
    if args.autoteste:
        return 0

    # ASCII de propósito: a consola do Windows usa cp1252 e uma seta Unicode aqui rebentava
    # o script DEPOIS de o controlo negativo passar, que é o pior sítio possível para rebentar.
    # ⚠️ A DIRECCAO INVERTEU-SE COM A REESCRITA. Este verificador nasceu quando a tese
    # canonica era a INGLESA e o risco era a traducao portuguesa endurecer o verbo. Hoje a
    # canonica e a PORTUGUESA (`tese-pt/`) e a inglesa (`tese-eng/`) e que e traduzida, pelo
    # que o risco mudou de lado: uma ressalva perdida no caminho para a arvore que acompanha
    # o artigo. Ate 2026-09-06 comparava as arvores ARQUIVADAS, e imprimia «0 candidatos
    # sobre 89 chaves» -- saude sobre documentos que nunca serao entregues.
    print("\nAssimetrias PT->EN nas frases com citacao:\n")
    total = candidatos = 0
    faltam = []
    for n in ("ch1", "ch2", "ch3", "ch4", "ch5", "ch6"):
        pt = RAIZ / "tese-pt" / n / f"chapter{n[-1]}.tex"
        en = RAIZ / "tese-eng" / n / f"chapter{n[-1]}.tex"
        if not (en.exists() and pt.exists()):
            # ⚠️ Saltar em silencio era o que permitia dizer «0 candidatos sobre 0 chaves»
            # com exit 0 se o corpus nao estivesse la.
            faltam.append(n)
            continue
        fe, fp = frases_com_citacao(en), frases_com_citacao(pt)
        for chave in sorted(set(fe) & set(fp)):
            total += 1
            if endurece(fe[chave], fp[chave]):
                candidatos += 1
                print(f"[{n}] {chave}")
                print(f"   PT: {fp[chave][:240]}")
                print(f"   EN: {fe[chave][:240]}\n")

    if faltam:
        print("ERRO: capitulos em falta em tese-pt/ ou tese-eng/: "
              + ", ".join(faltam)
              + ". Um verificador que nao ve o corpus tem de ser indistinguivel de "
              "um que falha.")
        return 2
    print(f"{candidatos} candidato(s) a leitura humana, sobre {total} chaves comparadas")
    return 1 if candidatos else 0


if __name__ == "__main__":
    sys.exit(main())
