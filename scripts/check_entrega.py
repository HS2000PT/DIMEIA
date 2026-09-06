"""A porta única: está pronto para entregar?

Corre tudo o que se pode verificar por máquina e diz, numa linha, o que falta. O que
sobrar depois disto é humano: a leitura final, a conversa com o orientador, e os cliques.

    python scripts/check_entrega.py

Sai com 0 quando tudo o que é verificável passa.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
# Os materiais de estudo passaram de `tese/` para `materiais/` a 2026-09-05,
# quando as tres arvores supersedas foram arquivadas. A prosa canonica e tese-v2.
TESE = RAIZ / "tese-pt"

# ⚠️ O TERCEIRO CAMPO SÃO ARGUMENTOS, e existe por uma distinção que a porta não fazia.
# Uma pendência HUMANA é um item real que NENHUM trabalho no repositório pode fechar: os
# nomes do júri só existem depois de o ISEP o designar. Misturada com os defeitos, deixava
# a porta permanentemente vermelha — e uma porta que nunca fica verde é uma porta que se
# deixa de ler, que é o defeito que este projecto já pagou cinco vezes.
#
# O contrato é uma linha que começa por `aviso `: quem a imprime declara um item humano, e
# esta porta recolhe-a numa secção própria em vez de a contar como falha. O item continua
# VISÍVEL; o que muda é onde aparece, e o veredicto final diz que ele impede a entrega.
VERIFICADORES = [
    ("dissertação canónica", "check_tese_pt.py", ["--permitir-pendencias-humanas"]),
    ("números contra a fonte", "check_tese_numeros.py", []),
    # O de cima verifica uma lista curada contra o ficheiro que a produz: garante que os que estão
    # na lista estão certos, e nada diz sobre os que não estão. Este faz o inverso, e é por isso
    # que os dois coexistem: varre o documento inteiro e exige que TODO o número afirmado tenha
    # origem, ou uma justificação escrita.
    ("todo o número tem origem", "auditar_numeros.py", []),
    ("escapes de LaTeX comidos", "check_tex_escapes.py", []),
    ("apêndice: cada número onde diz estar", "check_apendice_xref.py", []),
    ("materiais de estudo alinhados", "check_materiais.py", []),
    # ⚠️ A METADE CEGA DO DE CIMA. Ele compara VALORES decimais, logo nao ve nem os
    # inteiros («84% das decisoes», «944 -> 42», «~1 s») nem os valores que continuam
    # na tese noutro sentido (o `0,064` esta la, declarado como a janela anterior). A
    # 2026-09-06 quatro afirmacoes retiradas viviam em cinco documentos por causa
    # disso, uma delas na resposta modelo do slide «a pergunta mais dura».
    ("números que a tese retirou", "check_numeros_retirados.py", []),
    # ⚠️ O deck ingles existe desde 2026-09-06, para a audiencia do artigo, e tem de ser
    # conferido contra a arvore INGLESA. Corrido sobre ela, encontrou logo o travessao
    # que a passagem daquele dia tinha corrigido so do lado portugues.
    ("materiais EN alinhados", "check_materiais.py", ["tese-eng"]),
    ("flutuantes referenciados", "check_floats.py", []),
    ("escrita: PT-PT e um termo por conceito", "check_escrita.py", []),
    # O guia de construção promete código verbatim. Sem esta porta a promessa vale o que valer
    # a memória de quem o escreveu, e o código muda: um excerto correcto hoje deixa de o ser.
    ("guia de construção: código verbatim", "check_guia_codigo.py", []),
    # O artigo e a dissertação são lidos pelas mesmas pessoas, e a 2026-09-04 o artigo
    # afirmava o que a dissertação tinha retirado -- sem que nada falhasse. Esta porta
    # exige que todo o número do artigo tenha fonte e que os resultados estreitados na
    # tese apareçam no artigo com a mesma ressalva.
    ("artigo alinhado com a dissertação", "check_artigo_numeros.py", []),
    # A politica linguistica admite duas configuracoes; o que nao admite e uma figura
    # metade em cada. A 2026-09-04 duas das mais importantes do Cap. 4 estavam assim.
    ("figuras PT: uma so língua por figura", "check_figuras_lingua.py", []),
    # ⚠️ A ARVORE INGLESA PRECISA DA MESMA PORTA. Com duas arvores, um verificador que
    # so olha para uma deixa metade do corpus sem guarda -- que e a classe de cegueira
    # que esta porta existe para nao ter.
    ("figuras EN: uma so língua por figura", "check_figuras_lingua.py", ["tese-eng"]),
    # ⚠️ E AS DUAS PORTAS ACIMA COMPARAM CONTRA VOCABULARIO, logo uma expressao que
    # nenhuma lista preveja e invisivel: foi assim que `promotion gate` atravessou uma
    # figura portuguesa. Esta nao sabe vocabulario nenhum -- pergunta se o mesmo texto
    # desenhado aparece nas duas arvores, o que so acontece se nao tiver sido traduzido.
    ("figuras: nada por traduzir entre as árvores", "check_figuras_paridade.py", []),
    # ⚠️ A porta acima compara o texto DESENHADO; esta compara a PROSA — as frases com
    # citação nas duas árvores, à procura de uma ressalva que se perca na tradução. Até
    # 2026-09-06 comparava as árvores arquivadas e dizia «0 candidatos» sobre documentos
    # que nunca serão entregues.
    ("tradução: nenhuma ressalva perdida", "check_bilingual_parity.py", []),
    # ⚠️ Cada arvore imprime DOIS resumos — o da sua lingua e a traducao —, logo ha
    # quatro textos e dois conteudos. A sessao 56 encontrou o resumo portugues a
    # divergir entre as duas teses, e nenhuma das duas falhava a compilar.
    ("os quatro resumos dizem o mesmo", "check_resumos.py", []),
    # A cadeia de cada questao: enunciada, medida, delimitada e respondida -- e a
    # conclusao a nao citar valores que os resultados nao produziram.
    ("questões: enunciada, medida, respondida", "check_qi_cadeia.py", []),
    # Os dois ficheiros de continuidade declaram a mesma sessao, e e' a do registo mais
    # recente de cada um. O rodape do AGENTS.md ficou cinco sessoes atras do seu proprio
    # topo sem nada disparar: sao duas linhas de texto valido.
    ("continuidade: os dois ficheiros de memória", "check_memoria.py", []),
]

# ⚠️ A DISSERTAÇÃO A ENTREGAR É `tese-pt/`, e esta lista apontava para `tese/`. Corrigido a
# 2026-09-04. Os materiais de estudo — slides, guia, guia de construção — nunca foram movidos
# e continuam em `tese/`; a dissertação foi. Uma porta que confere o documento errado dá
# garantia falsa sobre o que vai ser entregue E grita por defeitos que não contam, que é a
# combinação que faz alguém deixar de a ler.
TESE_V2 = RAIZ / "tese-pt"

PDFS = [
    ("dissertação (canónica)", TESE_V2 / "main.pdf", TESE_V2 / "main.tex"),
    ("slides", TESE / "slides" / "main.pdf", TESE / "slides" / "main.tex"),
    ("guia", TESE / "guia" / "main.pdf", TESE / "guia" / "main.tex"),
    ("guia de construção", TESE / "guia_construir" / "main.pdf",
     TESE / "guia_construir" / "main.tex"),
]


def paginas(pdf: pathlib.Path) -> str:
    try:
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, timeout=120)
        m = re.search(r"Pages:\s*(\d+)", r.stdout.decode("utf-8", "replace"))
        return m.group(1) if m else "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


def registo_sujo(log: pathlib.Path) -> list[str]:
    """Erros e referências por resolver no `.log` do LaTeX.

    Um PDF existir não quer dizer que esteja bem: o LaTeX escreve-o mesmo depois de erros, e o
    que sai para a página é lixo tipográfico que só se vê a olhar. As referências indefinidas
    são piores, porque saem como `??` e ninguém repara numa página cheia de texto.

    As faltas de tipo de letra não contam: são cosméticas e o template do ISEP produz três.
    """
    if not log.exists():
        return [f"registo de compilação em falta: {log.name}"]
    linhas = log.read_text(encoding="utf-8", errors="replace").splitlines()
    erros = [x.strip() for x in linhas if x.startswith("! ")]
    indefinidas = [x.strip() for x in linhas
                   if "undefined" in x.lower() and "Font shape" not in x]
    return erros + indefinidas


def main() -> int:
    falhas = 0

    print("=== os PDF existem e têm páginas ===")
    for nome, pdf, tex in PDFS:
        if not pdf.exists():
            print(f"  !!  {nome}: {pdf.name} NÃO EXISTE — compila antes de entregar")
            falhas += 1
            continue
        if tex.exists() and tex.stat().st_mtime > pdf.stat().st_mtime:
            print(f"  !!  {nome}: o .tex é MAIS RECENTE do que o .pdf — recompila")
            falhas += 1
            continue
        # ⚠️ E O REGISTO DE COMPILAÇÃO, que esta porta não olhava. O LaTeX **recupera** de quase
        # tudo: um `\ref` partido por um escape produz três erros, imprime lixo na página, e
        # **escreve o PDF na mesma**. A porta dizia "ok, 118 páginas" sobre um documento com
        # erros dentro. Apanhado a 2026-08-20, no próprio dia em que causei um.
        problemas = registo_sujo(pdf.with_suffix(".log"))
        if problemas:
            print(f"  !!  {nome}: {len(problemas)} problema(s) no registo de compilação")
            for x in problemas[:3]:
                print(f"        {x[:78]}")
            falhas += 1
            continue
        print(f"  ok  {nome}: {paginas(pdf)} páginas, compila limpo, mais recente do que a fonte")

    print("\n=== os verificadores ===")
    humanas: list[str] = []
    for descricao, script, extra in VERIFICADORES:
        p = RAIZ / "scripts" / script
        if not p.exists():
            print(f"  !!  {descricao}: {script} não existe")
            falhas += 1
            continue
        r = subprocess.run([sys.executable, str(p), *extra], capture_output=True,
                           cwd=RAIZ, timeout=1800)
        saida = r.stdout.decode("utf-8", "replace")
        humanas.extend(x.strip()[6:].strip() for x in saida.splitlines()
                       if x.strip().startswith("aviso "))
        if r.returncode == 0:
            print(f"  ok  {descricao}")
        else:
            cmd = " ".join([f"python scripts/{script}", *extra]).strip()
            print(f"  !!  {descricao}  ->  {cmd}")
            falhas += 1

    print("\n=== marcadores de trabalho por acabar no que vai ser entregue ===")
    # ⚠️ SEM re.I, e é o ponto todo: em português "todo" é uma palavra corrente, e um
    # \bTODO\b insensível a maiúsculas acusa dezassete frases perfeitamente normais. É a
    # quinta vez que esta classe de falso positivo aparece neste projecto.
    padrao = re.compile(r"\[A definir\]|\bTODO\b|\bFIXME\b|\bXXX\b")
    achados = []
    for f in sorted(TESE.rglob("*.tex")):
        if "build" in f.parts:
            continue
        for n, linha in enumerate(f.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            if linha.lstrip().startswith("%"):
                continue
            if padrao.search(linha):
                achados.append(f"{f.relative_to(RAIZ)}:{n}  {linha.strip()[:64]}")
    if achados:
        for x in achados:
            print(f"  !!  {x}")
        falhas += len(achados)
    else:
        print("  ok  nenhum")

    print("\n=== a data não muda sozinha ===")
    # ⚠️ Só fora de comentários: os dois ficheiros EXPLICAM em comentário porque é que o
    # \today saiu, e um verificador que lê comentários acusa a própria explicação.
    def sem_comentarios(p: pathlib.Path) -> str:
        return "\n".join(x for x in p.read_text(encoding="utf-8").split("\n")
                         if not x.lstrip().startswith("%"))

    main_tex = sem_comentarios(TESE / "main.tex")
    fm = sem_comentarios(TESE / "frontmatter" / "frontmatter.tex")
    if "\\today" in main_tex or "\\today" in fm:
        print("  !!  ainda há \\today: a data muda a cada compilação, e numa declaração "
              "assinada isso é pior do que na capa")
        falhas += 1
    else:
        print("  ok  fixada")

    # ⚠️ SECÇÃO PRÓPRIA, E NÃO SILÊNCIO. Um item humano não é um defeito, mas continua a
    # impedir a entrega. Escondê-lo para a porta ficar verde seria trocar um problema
    # visível por um esquecido.
    print(f"\n=== pendências humanas: {len(humanas)} ===")
    for x in humanas:
        print(f"  ..  {x}")
    if not humanas:
        print("  ok  nenhuma")

    print()
    if falhas:
        print(f"FALTA RESOLVER: {falhas}")
        return 1
    print("Tudo o que se verifica por máquina está feito.")
    if humanas:
        print("⚠️  E NÃO ESTÁ PRONTO A ENTREGAR: as pendências humanas acima continuam por")
        print("    fechar, e nenhuma delas se resolve com trabalho no repositório.")
    print("O resto é humano: a leitura final, a redação da declaração de IA e a licença")
    print("com o orientador, os agradecimentos, e rodar as credenciais. "
          "Está no docs/planos/CHECKLIST.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
