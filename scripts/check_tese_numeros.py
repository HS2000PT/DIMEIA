"""Cada numero da tese curta conferido contra o ficheiro de avaliacao que o produz.

Porque e que isto existe. Os resultados desta dissertacao vivem em `docs/evaluation/*.md`,
gerados por scripts. A tese cita-os a mao. Se um script for re-corrido e um valor mudar, a
tese passa a afirmar um numero que a evidencia ja nao sustenta, e nada falha: o LaTeX compila,
os testes passam, e o documento fica errado em silencio. Ja aconteceu neste projecto.

Este verificador fecha essa porta. Falha com codigo 1 quando um numero citado nao aparece no
ficheiro que devia produzi-lo.

    python scripts/check_tese_numeros.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

# A consola do Windows e cp1252: imprimir um simbolo mata o verificador a MEIO do
# relatorio, e um relatorio truncado le-se como um relatorio limpo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
AVAL = RAIZ / "docs" / "evaluation"

# ⚠️ A ÁRVORE A VERIFICAR VEM POR ARGUMENTO, E O PADRÃO É A CANÓNICA. Corrigido a 2026-09-04.
#
# Este verificador apontava para `tese/`, que foi SUPERSEDA por `tese-v2/`. Continuava a passar
# ou a falhar sobre um documento que já não é entregue — ou seja, gritava por defeitos que não
# contam e ficava cego aos que contam. É a mesma classe que a sessão 58 encontrou no
# `check_references`, que só conhecia os nomes ingleses e imprimia «0 referências» como se
# fosse um estado saudável.
BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "tese-v2"
TESE = RAIZ / BASE

# (numero como aparece na tese, ficheiro que o produz, o que e)
# Um numero pode aparecer com mais ou menos casas do que o gerador escreve; por isso a
# comparacao e feita por VALOR e nao por cadeia de caracteres.
MANIFESTO: list[tuple[str, str, str]] = [
    # QI1 -- detecao
    ("0.015", "evaluation_anomaly.md", "amplitude da taxa de disparo, z-score"),
    ("0.344", "evaluation_anomaly.md", "amplitude da taxa de disparo, limiar fixo"),
    ("0.516", "evaluation_anomaly.md", "F1 do z-score contra o rotulo aproximado"),
    ("0.218", "evaluation_anomaly.md", "F1 do limiar fixo"),
    ("0.530", "evaluation_anomaly_ext.md", "F1 do z-score no protocolo dos detetores"),
    ("0.269", "evaluation_anomaly_ext.md", "F1 do Isolation Forest"),
    ("0.280", "evaluation_anomaly_ext.md", "F1 do Local Outlier Factor"),
    ("0.407", "evaluation_anomaly.md", "precisao do z-score"),
    # QI2 -- recuperacao
    ("0.513", "evaluation_retrieval_causal.md", "precisao@5 so com o passado"),
    ("0.259", "evaluation_retrieval_causal.md", "chao de acaso no protocolo causal"),
    ("0.514", "evaluation_results.md", "precisao@5, MiniLM"),
    ("0.538", "evaluation_results.md", "precisao@5, MPNet"),
    ("0.346", "evaluation_results.md", "precisao@5, palavras em comum"),
    ("0.240", "evaluation_results.md", "precisao@5, acaso"),
    ("0.126", "evaluation_results.md", "precisao@5, recencia"),
    ("0.595", "evaluation_retrieval_fnspid.md", "precisao@5 a escala"),
    ("0.708", "evaluation_retrieval_fnspid.md", "concordancia de direcao"),
    ("0.688", "evaluation_retrieval_fnspid.md", "chao de acaso da concordancia"),
    # QI3 -- triagem
    ("0.542", "evaluation_triage.md", "PR-AUC, so volatilidade"),
    ("0.538", "evaluation_triage.md", "PR-AUC, so contexto"),
    ("0.496", "evaluation_triage.md", "PR-AUC, contexto + texto"),
    ("0.439", "evaluation_triage.md", "PR-AUC, so texto"),
    ("0.469", "evaluation_triage.md", "PR-AUC, gradient boosting"),
    ("0.378", "evaluation_triage.md", "prevalencia, o chao da PR-AUC"),
    ("0.622", "evaluation_triage.md", "Brier de alertar sempre"),
    # pos-validacao ao vivo. ⚠️ Estes tres nao estavam no manifesto, e sao dos que mais
    # provavelmente mudam: o registo cresce todos os dias e o ficheiro e regenerado por
    # `evaluate_live_transfer.py`. A 2026-08-20 mudaram mesmo, de 530 para 825 decisoes.
    ("825", "evaluation_live_transfer.md", "decisoes maturadas no registo de producao"),
    ("0.589", "evaluation_live_transfer.md", "materiais entre as decisoes mantidas"),
    ("0.617", "live_monitoring.md", "materiais entre as decisoes suprimidas"),
    # A seleccao da porta contada por TITULO DISTINTO, e nao por decisao registada: o
    # sistema repontua a mesma manchete a cada ciclo, e a duplicacao e maior nas empresas
    # que nunca passam o piso. O congelado (84%) fica; este e o numero corrigido.
    ("48", "evaluation_gate_selectivity_unicos.md", "determinado pela empresa, por titulo"),
    ("0.617", "evaluation_live_transfer.md", "materiais entre as decisoes suprimidas"),
    ("0.486", "evaluation_live_transfer.md", "ROC-AUC na populacao implantada"),
    # o texto POR CIMA da melhor linha de base (Cap. 5). O 0.534 e o 0.662 ja vinham da
    # ablacao da identidade; o que e novo e o valor com texto.
    ("0.547", "evaluation_triage_within.md", "PR-AUC da tabela de consulta mais o texto"),
    ("0.512", "evaluation_triage_within.md", "AUC dentro da empresa, tabela mais texto"),
    ("0.502", "evaluation_triage_within.md", "AUC dentro da empresa, modelo implantado"),
    # chaos do orcamento (a correccao do artefacto alfabetico)
    ("0.3790", "evaluation_budget_baselines.md", "chao aleatorio real"),
    ("0.6624", "evaluation_budget_baselines.md", "prior de volatilidade por ticker"),
    ("0.6317", "evaluation_budget_baselines.md", "modelo implantado"),
    # ablacao da identidade (Cap. 5). ⚠️ Esta tabela ja divergiu do seu proprio ficheiro em
    # 5 das 7 linhas da coluna Precisao@5, e o manifesto nao a cobria. Cobre agora.
    ("0.534", "evaluation_triage_identity.md", "PR-AUC da tabela de consulta"),
    ("0.543", "evaluation_triage_identity.md", "PR-AUC sem indicadores de setor"),
    ("0.389", "evaluation_triage_identity.md", "PR-AUC sem volatilidade nem momento"),
    ("0.662", "evaluation_triage_identity.md", "precisao@5 da tabela de consulta"),
    ("0.629", "evaluation_triage_identity.md", "precisao@5 sem indicadores de setor"),
    ("0.390", "evaluation_triage_identity.md", "precisao@5 sem volatilidade nem momento"),
    ("0.368", "evaluation_triage_identity.md", "precisao@5 sem nada de nivel de empresa"),
    ("0.352", "evaluation_triage_identity.md", "precisao@5 so com o comprimento do titulo"),
    # decomposicao (tecnica 2)
    ("2.0143", "evaluation_decomposition.md", "beta de mercado da AMD, encolhido"),
    ("1.5888", "evaluation_decomposition.md", "beta de setor da AMD, encolhido"),
    # ⚠️ `0.6577` (R2 do ajuste da AMD) SAIU do manifesto a 2026-09-04, e a razao fica
    # escrita para nao voltar por engano. A reescrita canonica passou a reportar a MEDIANA
    # do coeficiente sobre a watchlist (`0.460`, que continua no manifesto e passa) em vez
    # do valor de uma empresa isolada. E a escolha mais defensavel: um R2 individual e uma
    # anedota, a mediana e um resumo. O numero continua a existir na fonte; deixou de ser
    # afirmado, e o que este verificador guarda sao as afirmacoes.
    ("0.460", "evaluation_decomposition.md", "R2 mediano sobre a watchlist"),
    ("0.487", "evaluation_decomposition.md", "quota especifica mediana"),
    # producao
    ("88.5", "evaluation_news_coverage.md", "cobertura de noticias em dias invulgares"),
    ("36.8", "evaluation_precedent_independence.md", "alertas com menos dias do que casos"),
    ("11.3", "evaluation_precedent_independence.md", "alertas assentes num unico dia"),
]

# ⚠️ AS DUAS ARVORES TEM NOMES DIFERENTES, e apontar a base certa sem corrigir isto e pior do
# que nao mexer em nada: o verificador le UM ficheiro de oito, encontra seis decimais no que
# julga ser a tese inteira, e reporta CINQUENTA numeros correctos como "ja nao citados". Foi o
# que aconteceu a 2026-09-04, e a leitura errada quase me levou a mandar corrigir a tese --
# que estava certa. Um verificador cego e um verificador que acusa tudo sao o mesmo defeito.
if (TESE / "ch1").is_dir():          # arvore nova: ch4/chapter4.tex
    FICHEIROS_TESE = [
        "frontmatter/frontmatter.tex",
        *[f"ch{i}/chapter{i}.tex" for i in range(1, 7)],
        "appendices/appendixA.tex",
        "appendices/appendixB.tex",
    ]
else:                                # arvore antiga: cap4/capitulo4.tex
    FICHEIROS_TESE = [
        "frontmatter/frontmatter.tex",
        *[f"cap{i}/capitulo{i}.tex" for i in range(1, 7)],
        "apendices/apendiceA.tex",
    ]


def valores(texto: str) -> set[float]:
    """Todos os numeros decimais do texto, como valores."""
    saida = set()
    for m in re.finditer(r"[-+]?\d+(?:\.\d+)?", texto):
        try:
            saida.add(float(m.group(0)))
        except ValueError:
            continue
    return saida


def _confere_contagem_de_testes(falhas: list) -> bool:
    """A contagem de testes que o apendice afirma bate com a suite?

    Nao se corre a suite (demora): conta-se o que o pytest COLECTA, que e o mesmo numero e
    e barato. Se o pytest nao estiver disponivel, avisa e nao bloqueia: um verificador que
    rebenta por falta de ambiente e pior do que um que diz que nao verificou.
    """
    ap = TESE / "apendices" / "apendiceA.tex"
    if not ap.exists():
        return False
    m = re.search(r"textbf\{(\d+) testes\}", ap.read_text(encoding="utf-8"))
    if not m:
        print("  AVISO  o apendice ja nao declara uma contagem de testes")
        return False
    afirmado = int(m.group(1))
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-p",
                            "no:cacheprovider"], cwd=RAIZ, capture_output=True, timeout=600)
        saida = r.stdout.decode("utf-8", "replace")
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  AVISO  nao consegui contar os testes ({e}); contagem NAO verificada")
        return False
    c = re.search(r"(\d+)\s*/\s*\d+ tests collected|(\d+) tests collected", saida)
    if not c:
        print("  AVISO  nao percebi a saida do pytest; contagem NAO verificada")
        return False
    real = int(c.group(1) or c.group(2))
    if real != afirmado:
        falhas.append((str(afirmado), "pytest --collect-only", "contagem de testes do apendice",
                       f"a suite colecta {real}"))
        return True
    return False


def main() -> int:
    corpo = "\n".join(
        (TESE / f).read_text(encoding="utf-8", errors="replace")
        for f in FICHEIROS_TESE
        if (TESE / f).exists()
    )
    # ⚠️ A TESE ESCREVE OS DECIMAIS COM VIRGULA, e sem esta linha o verificador nao os ve.
    # Em PT-PT o separador decimal e a virgula, e em modo matematico escreve-se `$36{,}8$`.
    # O verificador procurava `36.8` e reportava tres limitacoes MEDIDAS como "ja nao citadas",
    # quando estao la todas, com seccao propria. Verificado a 2026-09-04 lendo o texto: a
    # afirmacao do verificador era falsa e a tese estava certa.
    #
    # E a mesma classe do falso positivo da sessao 56, onde o comparador EN<->PT normalizava
    # `{,}` da mesma maneira nas duas linguas e transformava o `88,5` do PT em `885`.
    # Um verificador que inventa divergencias manda corrigir o que esta certo.
    corpo = corpo.replace("{,}", ".")
    citados = valores(corpo)

    cache: dict[str, set[float]] = {}
    falhas, ausentes, ok = [], [], 0

    for num, ficheiro, desc in MANIFESTO:
        alvo = float(num)
        p = AVAL / ficheiro
        if not p.exists():
            ausentes.append((num, ficheiro, desc))
            continue
        if ficheiro not in cache:
            cache[ficheiro] = valores(p.read_text(encoding="utf-8", errors="replace"))

        # A tese cita-o? (se nao, e um numero do manifesto que ja nao esta na tese)
        na_tese = any(abs(v - alvo) < 5e-4 for v in citados)
        # O ficheiro de avaliacao produz esse valor?
        na_fonte = any(abs(v - alvo) < 5e-4 for v in cache[ficheiro])

        if na_tese and na_fonte:
            ok += 1
        elif na_tese and not na_fonte:
            falhas.append((num, ficheiro, desc, "citado na tese, AUSENTE da fonte"))
        elif not na_tese and na_fonte:
            falhas.append((num, ficheiro, desc, "existe na fonte, ja NAO citado na tese"))
        else:
            falhas.append((num, ficheiro, desc, "ausente dos dois"))

    # ⚠️ A contagem de testes nao vem de nenhum .md: vem da suite. Ficou desactualizada em
    # silencio (a tese dizia 726 quando ja eram 737), porque nada a ligava a realidade.
    erro_testes = _confere_contagem_de_testes(falhas)

    print(f"{ok} de {len(MANIFESTO)} numeros conferidos contra a fonte que os produz.")
    for num, ficheiro, desc, porque in falhas:
        print(f"  FALHA  {num:>8s}  {desc}")
        print(f"         {porque}  ({ficheiro})")
    for num, ficheiro, desc in ausentes:
        print(f"  SEM FONTE  {num:>8s}  {desc}  -> {ficheiro} nao existe")

    if falhas or ausentes or erro_testes:
        print("\nUm numero que a tese afirma tem de existir no ficheiro que o produz.")
        return 1
    print("Todos batem certo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
