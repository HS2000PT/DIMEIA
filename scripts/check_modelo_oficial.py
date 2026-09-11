#!/usr/bin/env python3
"""Verifica que as duas árvores continuam conformes com o modelo LaTeX oficial do MEIA/ISEP.

## Porque é que isto é uma porta e não uma nota

O autor pediu para «garantir que cumpre os requisitos do latex oficial modelo fornecido pela
universidade». Uma resposta escrita numa nota envelhece em silêncio: a classe `meia-style.cls`
vive DENTRO de cada árvore, portanto qualquer sessão futura a pode editar sem que nada compare o
resultado com o original. O modelo oficial está arquivado em `archive/modelo-oficial/`, logo a
conformidade é **medível** e não argumentável.

## O que este verificador afirma, e o que não afirma

**Afirma** que as alterações à classe são exactamente as que estão declaradas abaixo, e falha se
aparecer uma que não esteja na lista — o que obriga quem a fizer a justificá-la aqui.

**Não afirma** que o documento cumpre regras que o modelo não codifica. O modelo fixa geometria,
tipo de letra, capa, e a estrutura do *front matter*; não fixa limite de páginas, nem estilo de
citação, nem número de capítulos. Essas verificações vivem noutras portas.

## O estado medido a 2026-09-11

Oito alterações à classe em cada árvore, e **nenhuma toca geometria, margens, tipo de letra ou
espaçamento**. Sete das oito são reparações a defeitos do próprio modelo:

1. **`babel` com as duas línguas** — o modelo carrega `babel` sem opções, o que serve um
   documento monolingue. Este é um par bilingue com um resumo na outra língua em cada árvore.
   É exigência do trabalho, não desvio de gosto.
2. **`\\keywordsother`** — o modelo usa as MESMAS palavras-chave nos dois resumos, e por isso a
   página do *Abstract* inglês imprimia palavras-chave em português. Comando novo, com recuo
   para o comportamento antigo se não for definido.
3. a 5. **três caminhos de imagem da capa** — o modelo escreve
   `{/frontmatter/assets/...}` com **barra inicial**, que é um caminho absoluto a partir da raiz
   do sistema de ficheiros. Não compila em máquina nenhuma onde os ficheiros não estejam na raiz.
   Retirar a barra é a correcção do defeito.
6. **bloco do júri com guarda** — imprime exactamente como o modelo quando os nomes estão
   preenchidos; só se esconde com o campo vazio.
7. e 8. **`\\par` antes do `\\bigskip`** nos dois resumos — no modelo, o `\\bigskip` é espaço
   vertical DENTRO do parágrafo corrente, e as palavras-chave saíam coladas à última frase do
   resumo, a meio da linha.

## A ÚNICA NÃO-CONFORMIDADE A SÉRIO, e é decisão do autor

A opção **`openany`** no `\\documentclass` **não consta da lista de opções do modelo**, cujo
comportamento por omissão é `openright`: cada capítulo abre em página ímpar. Foi acrescentada na
sessão 66 com justificação medida — o documento tinha **17 versos em branco**, o dobro de
qualquer uma das quatro dissertações aprovadas (que têm 7 a 9), e `openany` baixou-os para 3.

⚠️ **Mas as quatro aprovadas mantêm TODAS o `openright`.** O que se ganha são páginas; o que se
perde é a convenção de composição do corpus e do modelo. Não há regra do ISEP encontrada que o
exija — o que há é que nenhuma das quatro o larga. **É uma escolha de forma, e é do autor.**
Este verificador NÃO falha por causa dela: limita-se a dizê-la em voz alta a cada corrida, para
que ela seja uma decisão e não um esquecimento.

Uso:
    python scripts/check_modelo_oficial.py
"""

from __future__ import annotations

import pathlib
import sys

# ⚠️ A GUARDA DE CODIFICACAO, e ela apanhou-me neste proprio ficheiro: sem isto o verificador
# morria com `UnicodeEncodeError` ao imprimir o primeiro aviso, numa consola `cp1252`. E' o
# defeito EXACTO que a sessao 57 corrigiu no `check_all_gates` e a 68 no `check_prontidao_defesa`,
# com o comentario ja' escrito la': «uma porta que rebenta antes de verificar seja o que for e'
# pior do que nao existir». Escrevi a porta e repeti o defeito na mesma passagem.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
OFICIAL = RAIZ / "archive" / "modelo-oficial" / "meia-style.cls"
ARVORES = ("tese-pt", "tese-eng")

# As oito alterações aceites, cada uma identificada por uma marca que tem de estar no ficheiro
# alterado. A chave é a razão; se um `diff` produzir um bloco que nenhuma destas marcas explica,
# a porta falha — e quem alterou tem de acrescentar a razão aqui.
ALTERACOES = {
    "babel com as duas línguas": "shorthands=off",
    "palavras-chave próprias no segundo resumo": r"\keywordsother",
    "caminhos da capa sem a barra inicial (defeito do modelo)": "{frontmatter/assets/",
    "bloco do júri com guarda para nomes vazios": r"\ifx\presidentname\empty",
    "fim de parágrafo antes do espaço, nos dois resumos": r"\par\bigskip\noindent",
}

# Linhas do modelo que NUNCA podem mudar: é aqui que vive a conformidade visível ao júri.
INTOCAVEIS = ("\\RequirePackage{geometry}", "inner=", "outer=", "\\RequirePackage{mathpazo}")


def _opcao_activa(principal: pathlib.Path, opcao: str) -> bool:
    r"""A opção está na LISTA do `\documentclass`, e não em qualquer sítio do ficheiro.

    ⚠️ A PRIMEIRA VERSÃO PROCURAVA A PALAVRA NO FICHEIRO INTEIRO, e isso tornou-a errada no
    momento exacto em que ela passou a importar: quando o autor decidiu retirar a opção, o
    comentário que explica a remoção ficou a conter a palavra, e a porta continuou a reportar
    uma não-conformidade já resolvida. É a metade «grita de mais» do par que este repositório
    documenta — e um padrão a acertar numa palavra dentro de um comentário é o falso positivo
    que já foi pago cinco vezes antes desta.

    Lê-se só a lista de opções, com os comentários LaTeX retirados primeiro.
    """
    try:
        bruto = principal.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    linhas = bruto.replace(chr(13), "").split(chr(10))
    limpas = [("" if ln.lstrip().startswith("%") else ln.split("%", 1)[0]) for ln in linhas]
    texto = chr(10).join(limpas)
    i = texto.find(chr(92) + "documentclass[")
    if i < 0:
        return False
    j = texto.find("]", i)
    lista = texto[i:j] if j > i else texto[i:]
    return any(x.strip() == opcao for x in lista.split(","))


def normaliza(p: pathlib.Path) -> list[str]:
    return p.read_text(encoding="utf-8", errors="replace").replace("\r", "").splitlines()


def main() -> int:
    if not OFICIAL.exists():
        print(f"FALHA: o modelo oficial não está em {OFICIAL.relative_to(RAIZ)}.")
        print("       Sem ele não há contra o que comparar, e esta porta não pode aprovar nada.")
        return 1

    base = normaliza(OFICIAL)
    problemas = 0
    print(f"modelo oficial: {OFICIAL.relative_to(RAIZ)} ({len(base)} linhas)\n")

    for arvore in ARVORES:
        cls = RAIZ / arvore / "meia-style.cls"
        if not cls.exists():
            print(f"FALHA {arvore}: não tem meia-style.cls.")
            problemas += 1
            continue
        nosso = normaliza(cls)
        texto = "\n".join(nosso)

        import difflib
        blocos = [g for g in difflib.SequenceMatcher(None, base, nosso).get_opcodes()
                  if g[0] != "equal"]
        explicados, orfaos = 0, []
        for _op, i1, i2, j1, j2 in blocos:
            trecho = "\n".join(nosso[j1:j2]) + "\n".join(base[i1:i2])
            razao = next((r for r, marca in ALTERACOES.items() if marca in trecho), None)
            if razao:
                explicados += 1
            else:
                orfaos.append((i1 + 1, "\n".join(nosso[j1:j2])[:120]))

        print(f"  {arvore}: {len(blocos)} bloco(s) alterado(s), {explicados} com razão declarada")
        for linha, amostra in orfaos:
            print(f"    FALHA  linha ~{linha}: alteração SEM razão declarada neste ficheiro")
            print(f"           {amostra!r}")
            problemas += 1

        for marca in INTOCAVEIS:
            if sum(marca in ln for ln in nosso) != sum(marca in ln for ln in base):
                print(f"    FALHA  «{marca}» mudou — é geometria ou tipo de letra, e o júri vê")
                problemas += 1

        # A não-conformidade declarada, dita a cada corrida e sem fazer falhar.
        principal = RAIZ / arvore / "main.tex"
        if principal.exists() and _opcao_activa(principal, "openany"):
            print("    ⚠️  `openany` está activo, e NÃO consta das opções do modelo (que abre")
            print("        cada capítulo à direita). Poupa páginas em branco; afasta-se da")
            print("        convenção das quatro dissertações aprovadas, que a mantêm todas.")
            print("        Decisão do autor — ver o cabeçalho deste ficheiro.")
        if "\\RequirePackage{geometry}" not in texto:
            print("    FALHA  a classe deixou de carregar `geometry`")
            problemas += 1

    print()
    if problemas:
        print(f"{problemas} problema(s) de conformidade com o modelo oficial.")
        return 1
    print("Conforme: todas as alterações à classe têm razão declarada, e a geometria, as")
    print("margens e o tipo de letra do modelo estão intactos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
