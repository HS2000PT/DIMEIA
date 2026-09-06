"""Os materiais de estudo ensinam algum número que a dissertação já retirou?

⚠️ **PORQUE EXISTE, e é a metade cega de uma porta que já existia.** O `check_materiais`
exige que todo o **decimal** dos materiais tenha par na tese. Isso deixa passar duas classes
inteiras, e as duas morderam a 2026-09-06:

1. **Os inteiros.** «84% das decisões», «944 títulos → 42 alertas», «22:1», «~1 s até
   entregar». O `RX_RESULTADO` do outro verificador nem olha para eles, e sobreviveram em
   cinco documentos — incluindo o slide do guia intitulado *«a pergunta mais dura, e a tua
   melhor resposta»*, ou seja na frase que o autor decora para dizer em voz alta.
2. **Os valores que continuam na tese noutro sentido.** O `0,064` e o `0,385` **têm** par:
   a tese declara-os em voz alta como a janela **anterior e mais curta**, que é o tratamento
   correcto. O guia citava-os como se fossem *o* resultado. Uma porta que compara valores
   não consegue ver a diferença; esta compara **afirmações**.

O que faz é estreito de propósito: uma lista explícita do que foi retirado, com o que dizer
em vez disso. Não tenta adivinhar.

**A isenção é o mecanismo que o torna utilizável.** Um número retirado PODE e DEVE aparecer
nos materiais — dentro de um aviso. O `LEIA-ME-PRIMEIRO` tem uma tabela inteira deles, e os
slides têm o frame *«onde me enganei»*, que é dos melhores momentos da defesa. Uma ocorrência
é aceite se houver uma marca de aviso perto dela.

⚠️ **O QUE ISTO NÃO GARANTE.** A isenção é por proximidade, logo uma marca de aviso escrita
por outra razão a menos de 400 caracteres cala um achado verdadeiro. É um falso negativo
possível e conhecido; a alternativa era não ter porta nenhuma, e a lista é curta o bastante
para se reler à mão quando cresce.

    python scripts/check_numeros_retirados.py
    python scripts/check_numeros_retirados.py --autoteste
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# (identificador, padrão, o que dizer em vez disso, porque foi retirado)
RETIRADOS: list[tuple[str, str, str, str]] = [
    ("quase-4x", r"quase\s+(?:4|quatro)\s*(?:×|x|vezes)|quadrupl",
     "1,67× (de 0,379 para 0,632)",
     "o chão de 0,163 ordenava por ordem alfabética das empresas; ao acaso a sério é 0,379"),
    ("84-por-cento", r"\b84\s*(?:\\)?%",
     "48% dos títulos distintos",
     "contar decisões infla a fração, e na direção que convinha à conclusão: o sistema "
     "repontua o mesmo título a cada ciclo de sessenta segundos"),
    # ⚠️ SÓ o `0,064` e o `6,1×`. O `0,385` sozinho é TAMBÉM a prevalência do rótulo por
    # bloco (0,385 / 0,470 / 0,378), que não tem relação nenhuma com isto e aparece em
    # quatro documentos: apanhá-lo dava quatro acusações sobre texto correcto. Na
    # afirmação retirada os dois aparecem sempre juntos, logo o inequívoco chega.
    ("amplitude-antiga", r"0(?:[.,]|\{,\})064\b|6(?:[.,]|\{,\})1\s*(?:×|x)\b",
     "0,072 dentro, 0,392 entre, 5,4×",
     "janela de 36 925 decisões; a de 4 366 é a anterior e mais curta, e a tese diz isso"),
    ("funil-antigo", r"\b944\b|\b22\s*:\s*1\b|22 para 1|22-to-1",
     "743 títulos distintos → 15 alertas, cerca de 1 para 50",
     "a janela antiga contava avaliações de um lado e casos cumulativos do outro"),
    ("amd-963", r"\b963\b", "máximo de 0,472 na Apple; a AMD ultrapassou o piso em todas",
     "963 de 963 era a contagem da AMD na janela de 4 366"),
    ("latencia-antiga", r"\b158\s*min|~?\s*2[,.]5\s*h\b|\b1\s*s\b(?![\w-])|\b1 segundo\b",
     "353 minutos até detetar, 5 segundos até entregar",
     "o 1 s era a era do agendador, com n=28; a medição actual são 278 alertas"),
    ("live-0667", r"0(?:[.,]|\{,\})667\s*(?:vs|contra|/)\s*0(?:[.,]|\{,\})455",
     "0,589 contra 0,617",
     "eram 12 decisões; com 825 o sinal inverte-se"),
    ("onnx-20-23", r"\b20\s+(?:de|of)\s+23\b",
     "o Apêndice A afirma o formato de execução, e chega",
     "retirado por n pequeno de mais, e a tese curta não contém esse teste"),
]

# ⚠️ Uma ocorrência dentro de um aviso é o uso CERTO, não um defeito. Sem esta lista o
# verificador acusaria a própria tabela dos números retirados do `LEIA-ME-PRIMEIRO`.
MARCAS = (
    "não digas", "nao digas", "não dizer", "nao dizer", "não diga", "não cites", "nao cites",
    "não citar", "nao citar", "retirad", "withdrawn", "do not say", "don't say", "❌",
    "enganei", "engano", "onde me enganei", "era a medição antiga", "era a medicao antiga",
    "i had written", "eu tinha escrito", "já não", "ja nao", "deixou de", "janela anterior",
    # a correcção citada ao lado do erro é o uso certo: o quizz ensina-a assim.
    "1,67", "1.67", "ganho anunciado", "0,379", "0.379",
)
JANELA = 400


# ⚠️ O REGISTO DOS NÚMEROS RETIRADOS NÃO SE VERIFICA A SI PRÓPRIO. O `LEIA-ME-PRIMEIRO`
# existe precisamente para os nomear, numa tabela de «não digas / diz»: acusá-lo seria
# acusar a solução. É o único ficheiro fora do corpus, e é-o por nome e com a razão à
# vista, não por uma regra genérica que amanhã cale outra coisa.
REGISTO = "LEIA-ME-PRIMEIRO.md"


def corpus() -> list[pathlib.Path]:
    """Os materiais por onde o autor estuda, e mais nada. A tese não entra aqui."""
    padroes = (
        "tese-pt/slides/*.tex", "tese-eng/slides/*.tex", "tese-pt/guia/*.tex",
        "tese-pt/guia_construir/*.tex", "tese-pt/quiz/*.html", "docs/defence/*.md",
        "paper/*.tex",
    )
    fora: list[pathlib.Path] = []
    for p in padroes:
        fora.extend(sorted(RAIZ.glob(p)))
    return [f for f in fora if f.name != REGISTO]


def isento(texto: str, inicio: int, fim: int) -> bool:
    """Há uma marca de aviso à volta desta ocorrência?"""
    volta = texto[max(0, inicio - JANELA):fim + JANELA].lower()
    return any(m in volta for m in MARCAS)


def achados(textos: dict[str, str]) -> list[tuple[str, int, str, str, str]]:
    """(ficheiro, linha, identificador, contexto, o que dizer em vez disso)."""
    fora = []
    for nome, t in textos.items():
        for ident, padrao, em_vez, _porque in RETIRADOS:
            for m in re.finditer(padrao, t, re.I):
                if isento(t, m.start(), m.end()):
                    continue
                ln = t[: m.start()].count("\n") + 1
                ctx = re.sub(r"\s+", " ", t[max(0, m.start() - 52):m.end() + 40]).strip()
                fora.append((nome, ln, ident, ctx, em_vez))
    return sorted(fora)


def autoteste() -> bool:
    """Planta os dois sentidos: o número nu dispara, o número avisado não."""
    casos = [
        ("limpo dispara?", {"a.md": "A triagem sobe de 0,379 para 0,632, ou seja 1,67 vezes."},
         False),
        ("84% nu", {"a.md": "Em 84% das decisões o resultado estava determinado."}, True),
        ("84% dentro de um aviso",
         {"a.md": "⚠️ Não digas «84% das decisões»: foi retirado, diz 48% dos títulos."}, False),
        ("funil antigo nu", {"a.md": "944 títulos relevantes, 42 alertas, uma razão de 22:1."},
         True),
        ("latência antiga nua", {"a.md": "O alerta chega em ~1 s desde a deteção."}, True),
        ("quadruplica nu", {"a.md": "A triagem quase quadruplica a precisão."}, True),
        ("quadruplica avisado",
         {"a.md": "Onde me enganei: eu tinha escrito que quase quadruplica a precisão."}, False),
        ("amplitude antiga nua", {"a.md": "A pontuação varia 0,064 dentro e 0,385 entre."}, True),
        ("20 de 23 nu", {"a.md": "Top-3 idênticos em 20 de 23 consultas."}, True),
        # ⚠️ Os dois casos abaixo são falsos positivos que ESTE verificador teve na
        # primeira corrida, sobre texto correcto. Ficam no autoteste para não voltarem.
        ("prevalência do rótulo, que não é a amplitude",
         {"a.md": "Prevalência por bloco: 0,385 / 0,470 / 0,378, sem tendência."}, False),
        ("a correção citada ao lado do erro",
         {"a.md": "A linha de base reduziu o ganho anunciado de quase quatro vezes "
                  "para 1,67 vezes."}, False),
    ]
    ok = True
    for nome, textos, espera in casos:
        disparou = bool(achados(textos))
        if disparou != espera:
            ok = False
        marca = "OK  " if disparou == espera else "FALHA"
        print(f"  {marca} {nome}: {'esperado disparo' if espera else 'esperado silêncio'}")
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

    # ⚠️ Recusar-se a validar sem corpus, pela razão de sempre: não encontrar nada e aprovar
    # tudo têm o mesmo aspecto no ecrã.
    ficheiros = corpus()
    if len(ficheiros) < 8:
        print(f"\nERRO: só encontrei {len(ficheiros)} materiais em {RAIZ}. "
              "Não é seguro validar sem corpus.")
        return 2

    textos = {f.relative_to(RAIZ).as_posix(): f.read_text(encoding="utf-8", errors="replace")
              for f in ficheiros}
    print(f"\nMateriais: {len(textos)} ficheiros · afirmações retiradas na lista: "
          f"{len(RETIRADOS)}\n")

    fora = achados(textos)
    if fora:
        porque = {i: (v, r) for i, _p, v, r in RETIRADOS}
        for nome, ln, ident, ctx, em_vez in fora:
            print(f"  !!  {nome}:{ln}  [{ident}]")
            print(f"        ...{ctx}...")
            print(f"        diz em vez disso: {em_vez}")
            print(f"        porquê: {porque[ident][1]}")
        print(f"\nFALHA: {len(fora)} afirmação(ões) que a dissertação retirou, ensinadas sem "
              "aviso.\nUm número que ele decora e a tese não imprime é um número que ele vai "
              "citar sem o poder mostrar.")
        return 1

    print("ok  nenhum número retirado é ensinado como facto.")
    print("    (os que aparecem estão todos dentro de avisos, que é o uso certo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
