"""Todo o número da PROSA e das TABELAS da tese, e onde ele aparece nas fontes.

⚠️ POR QUE E QUE ISTO EXISTE, e em que difere do `check_tese_numeros.py`. Aquele verifica uma
lista curada de 53 números contra o ficheiro que os produz: garante que os que estão na lista
estão certos, e nada diz sobre os que não estão. Este faz o inverso — varre o documento inteiro
e pergunta, de cada número, se ele existe em ALGUMA fonte. O que interessa é o resto: os números
que a tese afirma e que nenhum ficheiro sustenta.

O QUE E EXCLUIDO, e porquê. As coordenadas de TikZ não são afirmações: são posições de desenho,
e uma varredura ingénua enche-se delas (a primeira versão devolveu 94 falsos positivos). Também
saem os ambientes de código e os índices de equação.

⚠️ O QUE ESTA PORTA NAO GARANTE, e fica medido em vez de suposto (2026-09-10). Enumerados os
900 valores da forma `0,NNN`, apenas **429 estão ausentes** das fontes: ou seja um número
inventado com três casas tem cerca de **52% de probabilidade de encontrar par por
coincidência** e passar. A porta apanha com fiabilidade os números **retirados** e as gralhas
que caem na metade livre — é para isso que serve — e **não é prova de que todo o número do
documento foi verificado**. Essa garantia é do `check_tese_numeros.py`, que compara uma lista
curada contra o ficheiro que a produz.

⚠️ E ESTEVE CEGO ATE 2026-09-10, o que é a razão de este aviso existir. Extraía apenas
decimais com PONTO enquanto a árvore canónica escreve `$2{,}173$`, com vírgula em modo
matemático: declarava «todos os números têm origem» depois de examinar **60**, quando a prosa e
as tabelas contêm **263**. A contribuição nova (QI4) estava inteira do lado invisível. É a mesma
classe que a sessão 63 corrigiu no `check_tese_numeros`, e sobreviveu aqui por não haver um
único teste sobre este ficheiro. Há agora: `tests/test_auditar_numeros.py`.

    python scripts/auditar_numeros.py
"""

from __future__ import annotations

import glob
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
B = chr(92)

# ambientes que NAO sao prosa nem tabela: o que la esta dentro sao coordenadas ou codigo
NAO_PROSA = ("tikzpicture", "lstlisting", "verbatim", "equation", "equation*", "align", "align*",
             "aligned", "array")

# ⚠️ NUMEROS QUE SAO AFIRMACOES DA TESE MAS NAO TEM (NEM PODEM TER) FICHEIRO DE AVALIACAO POR TRAS.
# Cada um foi rastreado a mao a 2026-08-22 e a razao esta escrita. A lista existe para que a saida
# do varrimento seja ACCIONAVEL: sem ela sao vinte e seis nomes de que ninguem se lembra porque
# estao la, e um numero novo e verdadeiramente sem fonte passaria despercebido no meio deles.
# Acrescentar aqui exige escrever a razao. Se a razao nao se escrever, o numero e um defeito.
JUSTIFICADOS: dict[str, str] = {
    # Cada entrada e um numero que a tese afirma e que nenhum ficheiro de avaliacao
    # sustenta, com a razao pela qual isso esta certo. A lista e podada sempre que o
    # verificador diz que uma entrada deixou de corresponder a alguma coisa: uma
    # justificacao que ja nao justifica nada e folclore, e a lista perde autoridade.

    # (a) nao sao afirmacoes: composicao e versoes de bibliotecas
    "1.08": "\\arraystretch da matriz de evidencia, medida de composicao",
    # ⚠️ "3.11" (matplotlib) e "3.12" (Python) foram RETIRADAS a 2026-09-10: o proprio
    # verificador passou a acusa-las de nao corresponderem a nada, porque ganharam fonte
    # quando `docs/design/` entrou nas pastas lidas. Uma justificacao que ja nao justifica
    # nada e folclore, e a lista perde autoridade -- e a regra esta escrita no topo.

    # (a2) contagens citadas da literatura: nao sao medicoes deste trabalho, logo nenhum
    # ficheiro de avaliacao as pode sustentar. A fonte e a publicacao citada ao lado.
    "20904": "investidores do estudo de Liu et al. (2023), citado no Cap. 2",

    # (a3) propriedades do corpus fixado, declaradas na 3.2 e verificaveis no manifesto
    "1704": ("titulos exatamente repetidos que o FNSPID entrega e que nao foram removidos; "
             "propriedade do corpus fixado por sha256, declarada na 3.2"),

    # (a4) tempo de maquina de um treino, registado em log gitignored
    "35386": ("segundos do braco de controlo da QI4 (data/_qi4_c4.log, gitignored); "
              "e tempo de maquina e nao um resultado, e o log declara-o ao lado dos passos"),

    # (b) contagens de producao, datadas, que crescem com o sistema
    "11445": "casos da base viva na branch de dados; instantaneo datado (Cap. 4)",

    # (c) o funil de um dia, com ficheiro proprio
    "1194": "funil por porta, docs/evaluation/funil_por_porta.md",
    # (d) aritmetica que a propria figura mostra
    "4727": ("soma das eliminacoes da Figura do funil (2994+1194+269+249+21); "
             "a legenda enuncia-a para que o leitor a possa refazer, e 5060-4727=333"),

    # ─────────────────────────────────────────────────────────────────────────────────────
    # (e) ACRESCENTADAS A 2026-09-10, quando o verificador deixou de estar cego a virgula.
    #     Passou a examinar 263 numeros em vez de 60, e estes sete apareceram. Nenhum e um
    #     defeito: quatro sao aritmetica que a tese faz a' frente do leitor, um e' calculado
    #     no exemplo trabalhado, e dois nao sao afirmacoes -- sao o FORMATO do alerta.
    # ─────────────────────────────────────────────────────────────────────────────────────

    # (e1) diferencas que a propria frase enuncia com os dois operandos ao lado
    "0.143": ("ganho do sistema sobre a alternativa realista na 5.4: 0,632 - 0,489, e a frase "
              "imprime os dois operandos antes da diferenca, para o leitor a refazer"),
    "0.336": ("margem ate' ao oraculo na 5.4: 0,968 - 0,632, e a frase di-lo por extenso "
              "(«A margem entre 0,632 e 0,968 e' de 0,336»)"),
    "0.235": ("indice de Brier de quem anuncia a prevalencia, na tabela das metricas: "
              "0,378 x 0,622 = 0,2351, com os dois fatores publicados no mesmo capitulo. "
              "A tabela escreve «cerca de», que e' a leitura honesta de um valor derivado"),

    # (e2) propriedade da amostragem da QI4, medida sobre os dados reais
    "0.289": ("desvio-padrao do alvo depois da amostragem estratificada da QI4 (3.5), medido "
              "sobre os dados reais e reportado ao lado da media de 0,499. E' o desvio de uma "
              "uniforme (1/raiz(12) = 0,2887), e e' isso que a frase conclui: a construcao "
              "produziu a distribuicao pretendida. Sem ele, a correcao do alvo triangular "
              "ficaria afirmada e nao mostrada"),

    # (e3) calculado no exemplo trabalhado, a partir da serie de precos fixada
    "2.725": ("desvio-padrao dos vinte dias anteriores no exemplo da Tesla (3.3), de onde sai "
              "z = +7,61. A sessao 66 refez a divisao: com 2,72 dava 7,63, e o valor exato e' "
              "2,7246. A tese imprime tres casas porque e' a conta que convida a refazer"),

    # (e4) NAO SAO AFIRMACOES: e' a forma da linha do alerta, nao uma medicao
    "2.11": ("exemplo do FORMATO da linha de repartição no Cap. 4 («NFLX -2,11% hoje = -0,08% "
             "mercado · -0,32% setor · -1,71% da propria empresa»). A sessao 61 rastreou os 26 "
             "numeros sem ficheiro e classificou dois como exemplo de formato: sao estes"),
    "1.71": "a parcela da propria empresa do mesmo exemplo de formato; ver a entrada de 2.11",
}




def prosa_e_tabelas(texto: str) -> str:
    for amb in NAO_PROSA:
        texto = re.sub(B + B + r"begin\{" + amb + r"\*?\}.*?" + B + B + r"end\{" + amb + r"\*?\}",
                       " ", texto, flags=re.S)
    texto = re.sub(r"(?m)^\s*%.*$", " ", texto)          # comentarios de linha inteira
    texto = re.sub(r"(?<!" + B + B + r")%.*", " ", texto)  # comentarios em fim de linha
    return texto


def numeros(texto: str) -> set[str]:
    """Decimais com 2+ casas e inteiros com separador de milhar: os que sao afirmacoes.

    ⚠️ A VIRGULA E A FORMA EM QUE ESTA TESE ESCREVE TODOS OS RESULTADOS, e este verificador
    esteve cego a ela. A arvore canonica e PT-PT e escreve `$2{,}173$` em modo matematico, o que
    outra porta exige; este extrator procurava so `\\d+\\.\\d{2,}`, com PONTO. Consequencia
    medida a 2026-09-10: declarava «todos os numeros tem origem» depois de examinar 60, quando a
    prosa e as tabelas contem 212 decimais com virgula que ele nunca extraia -- entre eles a
    contribuicao nova por inteiro.

    E' a MESMA classe que a sessao 63 corrigiu no `check_tese_numeros` («a tese escreve os
    decimais com virgula e o verificador procurava 36.8»). Foi corrigida la e nunca aqui.

    Os decimais com virgula sao normalizados para a forma com PONTO, porque e' assim que os
    artefactos de `docs/evaluation/` os escrevem e assim que as chaves de JUSTIFICADOS estao.
    """
    fora = set(re.findall(r"\b\d+\.\d{2,}\b", texto))

    # `$2{,}173$` -> "2.173". O `{,}` e' a virgula decimal em modo matematico.
    fora |= {f"{inteiro}.{casas}"
             for inteiro, casas in re.findall(r"\b(\d+)\{,\}(\d{2,})\b", texto)}

    # milhares: `36\,925` -> "36925"
    fora |= {m.replace(B + ",", "").replace(",", "")
             for m in re.findall(r"\b\d{1,3}" + B + B + r",\d{3}\b", texto)}
    return fora


def _valores_das_fontes(fontes: str) -> list[tuple[str, int]]:
    """Todos os decimais das fontes, com o numero de casas, para o teste de arredondamento."""
    fora = []
    for m in re.finditer(r"\b\d+[.,](\d+)\b", fontes):
        fora.append((m.group(0).replace(",", "."), len(m.group(1))))
    return fora


def arredonda_de(alvo: str, fontes_num: list[tuple[str, int]]) -> str | None:
    """A fonte publica o mesmo valor com MAIS casas, e arredonda para o alvo?

    ⚠️ POR QUE E' QUE ISTO E' LEGITIMO e nao um afrouxamento. Os relatorios publicam quatro
    casas e a tese escreve tres: o `porta_colapso_direcao_v2` publica `0,9936` e a tese escreve
    `0{,}994`. Sao o MESMO valor, e exigir a cadeia exacta reportava-o como sem fonte -- foi o
    que aconteceu a 2026-09-10 com quatro numeros do diagnostico de degeneracao, que e'
    precisamente a evidencia que torna a QI4 um resultado e nao uma montagem falhada.

    E' estreito de proposito: exige que a fonte tenha MAIS casas do que o alvo e que arredonde
    EXACTAMENTE para ele. Nao aceita vizinhanca, nao aceita tolerancia, e nao aceita uma fonte
    com menos casas (senao `0,5` justificaria `0,499` e `0,503` ao mesmo tempo).
    """
    if "." not in alvo:
        return None
    casas = len(alvo.split(".")[1])
    for bruto, n in fontes_num:
        if n <= casas:
            continue
        try:
            if f"{round(float(bruto), casas):.{casas}f}" == alvo:
                return bruto
        except ValueError:
            continue
    return None


def main() -> int:
    corpo = ""
    # A ARVORE E A CANONICA. Este verificador apontava para `tese/`, que foi superseda:
    # reportava ok sobre um documento que nao e entregue, ou seja garantia falsa na
    # porta. E os NOMES dos ficheiros mudam com a arvore -- apontar a arvore certa sem
    # corrigir a lista deixa-o a ler o frontmatter e mais nada, que e o defeito que a
    # sessao 63 pagou e quase mandou corrigir uma tese que estava certa.
    for f in sorted(glob.glob(str(RAIZ / "tese-pt" / "ch*" / "chapter*.tex"))) + \
             sorted(glob.glob(str(RAIZ / "tese-pt" / "appendices" / "*.tex"))) + \
             [str(RAIZ / "tese-pt" / "frontmatter" / "frontmatter.tex")]:
        corpo += prosa_e_tabelas(open(f, encoding="utf-8", errors="replace").read())

    fontes = ""
    # ⚠️ `docs/design/` ENTRA, e a razao e' concreta: o resultado da QI4 -- a contribuicao nova --
    # vive em `docs/design/qi4_resultado_2026-09-09.md` e em `porta_colapso_direcao_v2_*.md`, e
    # nao em `docs/evaluation/`. Sem esta linha, 19 dos valores que a tese afirma sobre a QI4
    # ficariam sem fonte reconhecivel: a porta acusaria o capitulo mais recente por um defeito
    # que e' dela. Os manifestos `*_manifest.json` entram pela mesma razao (fixam os corpora).
    for padrao in ("docs/evaluation/*.md", "docs/evaluation/*.csv", "docs/decisions/*.md",
                   "docs/design/*.md", "docs/design/*.json",
                   "config/*.yaml"):
        for f in glob.glob(str(RAIZ / padrao)):
            fontes += open(f, encoding="utf-8", errors="replace").read()
    for f in glob.glob(str(RAIZ / "investigator" / "**" / "*.py"), recursive=True):
        fontes += open(f, encoding="utf-8", errors="replace").read()

    # ⚠️ A OUTRA METADE DA MESMA CEGUEIRA, e corrigir so uma deixa a porta meio cega.
    # Os alvos extraidos da tese sao normalizados para a forma com PONTO (`$2{,}173$` -> "2.173"),
    # mas os relatorios de `docs/design/` sao Markdown escrito em PORTUGUES e escrevem os
    # decimais com VIRGULA -- 148 deles so nos dois documentos da QI4. Sem esta normalizacao, um
    # valor que esta' no artefacto continuaria a ser reportado como sem fonte, e a correcao
    # anterior teria movido o defeito em vez de o fechar.
    # A copia acrescentada nao substitui a original: uma fonte pode legitimamente escrever as
    # duas formas, e apagar uma delas perderia acertos.
    fontes += re.sub(r"(?<=\d),(?=\d)", ".", fontes)

    alvos = sorted(numeros(corpo))
    fontes_num = _valores_das_fontes(fontes)
    sem_fonte = []
    por_arredondamento: dict[str, str] = {}
    for n in alvos:
        variantes = {n, n.rstrip("0").rstrip("."), n.replace(".", ","),
                     f"{n[:-3]},{n[-3:]}" if n.isdigit() and len(n) > 3 else n}
        if any(v and v in fontes for v in variantes):
            continue
        # A fonte publica mais casas do que a tese imprime? Entao esta' sustentado.
        bruto = arredonda_de(n, fontes_num)
        if bruto:
            por_arredondamento[n] = bruto
            continue
        sem_fonte.append(n)

    novos = [n for n in sem_fonte if n not in JUSTIFICADOS]
    mortos = [n for n in JUSTIFICADOS if n not in sem_fonte]

    print(f"números de prosa e tabelas: {len(alvos)}")
    print(f"  com fonte na cadeia exacta: "
          f"{len(alvos) - len(sem_fonte) - len(por_arredondamento)}")
    print(f"  sustentados por ARREDONDAMENTO de um valor publicado com mais casas: "
          f"{len(por_arredondamento)}")
    print(f"sem ocorrência em nenhuma fonte: {len(sem_fonte)}")
    print(f"  dos quais rastreados à mão e justificados: {len(sem_fonte) - len(novos)}")
    print(f"  SEM ORIGEM CONHECIDA: {len(novos)}\n")

    if mortos:
        print("⚠️  Justificações que já não correspondem a nada (o número saiu da tese ou")
        print("    ganhou fonte). Apagar da lista, para ela não virar folclore:")
        print("      " + "  ".join(sorted(mortos)) + "\n")

    if novos:
        print("  " + "  ".join(novos))
        print("\n⚠️  Cada um destes é um número que a tese afirma e que nenhum ficheiro sustenta.")
        print("    Ou ganha fonte, ou ganha uma linha em JUSTIFICADOS com a razão escrita.")
        return 1

    print("Todos os números da prosa e das tabelas têm origem conhecida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
