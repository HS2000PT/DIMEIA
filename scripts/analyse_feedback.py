#!/usr/bin/env python3
"""Analisa os votos do canal e escreve `docs/evaluation/evaluation_feedback.md`.

## As regras estão escritas ANTES de existirem dados, e é essa a razão de este ficheiro existir

Com uma amostra pequena e recolhida em aberto, quem decide as regras depois de ver os números
consegue sempre encontrar um recorte que diga o que quer. As regras abaixo ficam fixadas agora,
com o ficheiro de votos vazio, e o relatório aplica-as sem exceção:

1. **N mínimo para reportar uma proporção: 20 votos efetivos.** Abaixo disso o relatório
   imprime as contagens e escreve, com todas as letras, que não reporta proporção. Uma
   percentagem sobre sete votos é um número que engana quem o lê, incluindo quem o escreveu.
2. **Um voto por pessoa por alerta.** O último substitui o anterior. As mudanças de opinião
   são contadas à parte, porque são interessantes e não são ruído.
3. **Salvaguarda do votante dominante.** Se uma só pessoa representar mais de 40% dos votos
   efetivos, o cálculo é repetido sem essa pessoa. A segunda proporção só é reportada se o
   recorte também tiver os 20 votos mínimos; caso contrário, sai apenas a contagem. Num canal
   pequeno, um leitor entusiasta pode sozinho decidir o resultado.
4. **Nunca se escreve «significativo».** Não há teste de hipótese aqui, e não vai haver com
   este N. Intervalos de Wilson a 95%, e a palavra «piloto» em todo o lado.
5. **Sobreposição de intervalos recusa uma afirmação, nunca a sustenta.** Com intervalos
   sobrepostos escreve-se «não é possível distinguir», e nunca «são iguais».
6. **Só contam votos sobre alertas que existem no histórico partilhado.** Um voto cuja chave
   não corresponde a nenhum alerta entregue não é um voto: é tráfego de teste, uma chave
   antiga, ou alguém a experimentar o endereço. A filtragem é feita na leitura, e o número de
   votos excluídos é reportado — nunca apagado do ficheiro, que é de acrescento e é a prova.
   Se o histórico não estiver disponível, o relatório di-lo e **não** aplica o filtro em
   silêncio.

## O que isto NÃO é

Não é o estudo de utilidade do protocolo moderado (`docs/study/`, `analyse_usefulness.py`).
Esse pergunta se a explicação é compreendida e se calibra a confiança, com sessões conduzidas e
um guião. Este pergunta uma coisa mais estreita: se os alertas que o sistema decidiu enviar
foram considerados úteis por quem os recebeu, sem moderação e sem contexto. São instrumentos
diferentes, com validades diferentes, e o relatório diz isso na primeira linha para que ninguém
os junte.

Uso:
    python scripts/analyse_feedback.py
    python scripts/analyse_feedback.py --votos data/feedback.jsonl
"""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
import sys  # noqa: E402

sys.path.insert(0, str(REPO))

from investigator import feedback_log as FL  # noqa: E402
from investigator.evaluation.proportions import wilson  # noqa: E402

DEFAULT_VOTOS = REPO / "data" / "feedback.jsonl"
DEFAULT_HISTORICO = REPO / "data" / "alerts_history.jsonl"
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_feedback.md"
# O fragmento que a dissertação faz `\\input`. Gerado, e nunca escrito à mão: é a mesma
# disciplina do resto do trabalho — o número aparece no documento porque veio do
# procedimento que o calculou, e não porque alguém o transcreveu.
OUT_TEX = REPO / "tese-v2" / "ch5" / "feedback_auto.tex"

# ── Regras pré-registadas. Alterar qualquer uma destas depois de haver dados é um ato que
#    tem de ficar registado no ESTADO.md, com a data e a razão. ──────────────────────────
N_MINIMO = 20          # votos efetivos abaixo dos quais NÃO se reporta proporção
DOMINANCIA_MAX = 0.40  # acima disto, reporta-se também sem o votante dominante


def _pct(x: float) -> str:
    return "—" if x != x else f"{x * 100:.0f}%"


def _linha_proporcao(rotulo: str, k: int, n: int) -> str:
    if n < N_MINIMO:
        return (f"| {rotulo} | {k} de {n} | não reportada | "
                f"abaixo do mínimo pré-registado de {N_MINIMO} |")
    lo, hi = wilson(k, n)
    return (f"| {rotulo} | {k} de {n} | {_pct(k / n)} | "
            f"IC 95% de Wilson: {_pct(lo)}–{_pct(hi)} |")


def chaves_do_historico(caminho: str | Path) -> set[str] | None:
    """Chaves dos alertas realmente entregues, ou `None` se o histórico não puder ser lido.

    `None` e conjunto vazio são coisas diferentes e o relatório trata-as como tais: um
    histórico ausente não pode servir de justificação para descartar todos os votos.
    """
    import hashlib

    from investigator.alerts_history import load_jsonl as carregar_historico
    from investigator.explanation_engine.explainer import plain_text

    try:
        entradas = carregar_historico(caminho)
    except Exception:  # noqa: BLE001
        return None
    if not entradas:
        return None

    # ⚠️ A CHAVE É RECALCULADA QUANDO O CAMPO ESTÁ VAZIO, e não é um detalhe.
    #
    # O `key` do histórico só é preenchido para alertas de NOTÍCIA — é a chave de deduplicação
    # entre produtores, e os alertas de mercado não precisam dela. Mas os botões de feedback vão
    # em TODOS os alertas, com a chave calculada da mesma maneira. Resultado da primeira versão:
    # cada voto num alerta de mercado era silenciosamente descartado pela regra 6, por não
    # corresponder a chave nenhuma.
    #
    # Apanhado a 2026-09-01 com os dois primeiros votos reais da recolha — ambos em alertas de
    # mercado (TSLA e AAPL), ambos deitados fora. Recalcular resolve-os aos dois, porque o
    # `news_key` é determinista a partir de (ticker, texto sem tags) e o texto guardado é
    # exatamente esse. Corrigir aqui, e não no que é gravado, deixa o caminho de envio intacto.
    def _chave(e) -> str:
        if e.key:
            return e.key
        return hashlib.sha1(
            f"{e.ticker}|{plain_text(e.text)}".encode()).hexdigest()[:12]

    return {_chave(e) for e in entradas}


def _filtrar_por_historico(
    registos: list[FL.FeedbackRecord],
    chaves_validas: set[str] | None,
) -> tuple[list[FL.FeedbackRecord], int]:
    """Filtra votos inválidos sem remover marcas de retirada.

    A marca ``d`` não pertence a um alerta concreto; eliminá-la por não ter uma chave no
    histórico faria reaparecer precisamente os votos que a pessoa retirou.
    """
    if chaves_validas is None:
        return list(registos), 0
    saida = [
        r
        for r in registos
        if r.acao == FL.RETIRAR or r.chave_alerta in chaves_validas
    ]
    excluidos = sum(
        1
        for r in registos
        if r.acao != FL.RETIRAR and r.chave_alerta not in chaves_validas
    )
    return saida, excluidos


def relatorio(registos: list[FL.FeedbackRecord],
              chaves_validas: set[str] | None = None) -> str:
    # Regra 6: votos sobre alertas que não existem não são votos.
    registos, excluidos = _filtrar_por_historico(registos, chaves_validas)
    amostra_verificada = chaves_validas is not None

    efetivos = FL.votos_efetivos(registos)
    resumo = FL.resumo(registos)
    n = len(efetivos)
    uteis = sum(1 for r in efetivos.values() if r.acao == FL.UTIL)

    por_pessoa = Counter(v for v, _ in efetivos)
    dominante, n_dominante = (por_pessoa.most_common(1) or [("", 0)])[0]
    fracao_dominante = (n_dominante / n) if n else 0.0

    L: list[str] = []
    L.append("# Feedback do canal — piloto não moderado")
    L.append("")
    L.append("> **O que este documento é, e o que não é.** Mede se os alertas que o sistema "
             "decidiu enviar foram considerados úteis por quem os recebeu, através de dois "
             "botões na própria mensagem. Não é o estudo de utilidade do protocolo moderado "
             "(`docs/study/`), que pergunta se a explicação é compreendida e se calibra a "
             "confiança. São instrumentos diferentes e não se somam.")
    L.append("")
    L.append("> **Todas as regras de análise foram fixadas antes de existirem dados** e estão "
             "no cabeçalho de `scripts/analyse_feedback.py`. Nenhuma foi alterada depois.")
    L.append("")
    L.append(f"> Gerado por `scripts/analyse_feedback.py` a "
             f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.")
    L.append("")
    if chaves_validas is None:
        L.append("> ⚠️ **O filtro do histórico não foi aplicado**, por o histórico partilhado "
                 "não estar disponível. Os números abaixo incluem, se existirem, votos sobre "
                 "alertas que o canal nunca entregou — tráfego de teste ou chaves antigas. "
                 "Correr de novo com o histórico presente antes de citar qualquer valor.")
        L.append("")
    elif excluidos:
        L.append(f"> **{excluidos} voto(s) excluído(s)** por não corresponderem a nenhum alerta "
                 f"do histórico partilhado. Não foram apagados do ficheiro, que é de acrescento "
                 f"e é a prova; foram ignorados na contagem.")
        L.append("")

    if not registos:
        L.append("## Ainda não há votos")
        L.append("")
        L.append("O ficheiro de votos está vazio. Não há nada a reportar, e a ausência de "
                 "dados não é um resultado de zero por cento — é a ausência de dados.")
        L.append("")
        return "\n".join(L) + "\n"

    L.append("## Dimensão da amostra")
    L.append("")
    L.append("| Medida | Valor |")
    L.append("|---|---|")
    L.append(f"| Votos válidos registados | {resumo['votos_brutos']} |")
    L.append(f"| Votos efetivos (um por pessoa e alerta) | {resumo['votos_efetivos']} |")
    L.append(f"| Pessoas distintas | {resumo['pessoas']} |")
    L.append(f"| Alertas votados | {resumo['alertas_votados']} |")
    L.append(f"| Mudanças de voto | {resumo['mudancas_de_voto']} |")
    L.append(f"| Cliques repetidos sem mudança | {resumo['repeticoes_iguais']} |")
    if resumo["retiradas"]:
        L.append(f"| Retiradas de participação | {resumo['retiradas']} |")
    L.append("")

    L.append("## Resultado")
    L.append("")
    L.append("| Recorte | Contagem | Proporção | Nota |")
    L.append("|---|---|---|---|")
    if amostra_verificada:
        L.append(_linha_proporcao("Alertas considerados úteis", uteis, n))
    else:
        L.append(f"| Alertas considerados úteis | {uteis} de {n} | não reportada | "
                 "filtro do histórico indisponível |")

    if fracao_dominante > DOMINANCIA_MAX and n:
        sem = {k: v for k, v in efetivos.items() if k[0] != dominante}
        uteis_sem = sum(1 for r in sem.values() if r.acao == FL.UTIL)
        if amostra_verificada:
            L.append(_linha_proporcao("O mesmo, sem o votante dominante", uteis_sem, len(sem)))
        else:
            L.append(f"| O mesmo, sem o votante dominante | {uteis_sem} de {len(sem)} | "
                     "não reportada | filtro do histórico indisponível |")
    L.append("")

    if fracao_dominante > DOMINANCIA_MAX:
        sem_n = n - n_dominante
        if n >= N_MINIMO and amostra_verificada:
            dominio = f"{_pct(fracao_dominante)} dos votos efetivos"
        else:
            dominio = f"{n_dominante} dos {n} votos efetivos"
        if sem_n >= N_MINIMO and amostra_verificada:
            leitura = ("A segunda linha reporta o cálculo sem essa pessoa; se as duas linhas "
                       "divergirem, essa é a leitura a reter.")
        else:
            leitura = (f"Sem essa pessoa restam {sem_n} votos, abaixo do mínimo de "
                       f"{N_MINIMO}; a segunda linha mostra apenas a contagem e nenhuma "
                       "proporção desse recorte é reportada.")
        L.append(f"⚠️ **Salvaguarda do votante dominante aplicada.** Uma só pessoa forneceu "
                 f"{dominio}, excedendo o limite pré-registado de {_pct(DOMINANCIA_MAX)}. "
                 f"{leitura}")
        L.append("")

    if not amostra_verificada:
        L.append("**Nenhuma proporção é reportada.** O histórico partilhado não esteve "
                 "disponível para confirmar que cada voto corresponde a um alerta entregue. "
                 "As contagens são provisórias e não podem ser citadas como resultado.")
    elif n < N_MINIMO:
        L.append(f"**Nenhuma proporção é reportada.** Há {n} votos efetivos e a regra "
                 f"pré-registada exige {N_MINIMO}. As contagens acima são o resultado, e são "
                 f"tudo o que esta amostra sustenta.")
    else:
        lo, hi = wilson(uteis, n)
        L.append(f"A proporção de alertas considerados úteis é de {_pct(uteis / n)}, com "
                 f"intervalo de confiança de Wilson a 95% entre {_pct(lo)} e {_pct(hi)}. "
                 f"A largura deste intervalo é a medida honesta do que {n} votos permitem "
                 f"afirmar, e é por isso que é reportada ao lado do valor central e nunca "
                 f"depois dele.")
    L.append("")

    L.append("## Ameaças à validade, e nenhuma delas é resolúvel com mais votos")
    L.append("")
    L.append("- **Autosseleção.** Vota quem quer. Quem acha um alerta indiferente tende a não "
             "carregar em nada, o que empurra a amostra para os dois extremos.")
    L.append("- **Ausência de contrafactual.** Não há um grupo que receba a variação de preço "
             "sem explicação, portanto nada aqui atribui a utilidade à explicação em si.")
    L.append("- **Utilidade percebida não é decisão melhor.** É a hipótese fundadora do "
             "trabalho, e continua por testar: um alerta pode agradar e conduzir a uma "
             "decisão pior.")
    L.append("- **Canal público.** Não se sabe quem são as pessoas, nem se são investidores "
             "particulares, que é o público que a dissertação assume.")
    L.append("")
    return "\n".join(L) + "\n"


def fragmento_latex(registos: list[FL.FeedbackRecord],
                    chaves_validas: set[str] | None = None) -> str:
    """A subsecção da dissertação, gerada a partir dos mesmos votos que o relatório.

    **Escrita para ser correta com qualquer N, incluindo zero.** Abaixo do mínimo pré-registado
    diz quantos votos houve e que não reporta proporção; acima, reporta com o intervalo de
    Wilson. Assim a dissertação pode compilar hoje, com a recolha a decorrer, sem afirmar nada
    que os dados não sustentem, e passa a estar certa no dia em que os votos cheguem — sem
    ninguém ter de reescrever o parágrafo.
    """
    registos, excluidos = _filtrar_por_historico(registos, chaves_validas)
    amostra_verificada = chaves_validas is not None

    efetivos = FL.votos_efetivos(registos)
    r = FL.resumo(registos)
    n = len(efetivos)
    uteis = sum(1 for v in efetivos.values() if v.acao == FL.UTIL)
    dias = sorted({v.at[:10] for v in efetivos.values()})
    periodo = (f"entre {dias[0]} e {dias[-1]}" if len(dias) > 1
               else (f"em {dias[0]}" if dias else "sem qualquer voto registado"))

    L = ["% GERADO por scripts/analyse_feedback.py — NÃO EDITAR À MÃO.",
         "% Correr o script outra vez depois de a recolha fechar; o texto acompanha os dados.",
         r"\subsection{Utilidade percebida dos alertas entregues}",
         r"\label{sec:av_feedback}", ""]

    # ⚠️ «cada alerta», e não «cada alerta de notícia»: os botões vão nos alertas de mercado
    # também, e os dois primeiros votos reais da recolha foram precisamente em alertas de
    # mercado. A redação anterior descrevia o sistema de forma errada no próprio documento.
    L.append("O canal passou a acompanhar cada alerta entregue com dois botões, "
             "\\emph{útil} e \\emph{não ajudou}, e a registar o voto de quem carrega. "
             "As regras de análise foram fixadas antes de existir um único voto e não foram "
             "alteradas depois: mínimo de vinte votos efetivos para reportar qualquer proporção, "
             "um voto por pessoa e por alerta com o último a substituir o anterior, "
             "salvaguarda que repete o cálculo sem o votante dominante quando este representa "
             "mais de quarenta por cento dos votos, sempre sujeita ao mesmo mínimo, e intervalos "
             "de confiança de Wilson, apropriados a proporções com amostras pequenas.")
    if amostra_verificada:
        L.append("Contaram apenas votos sobre alertas presentes no registo partilhado.")
    else:
        L.append("O registo partilhado não esteve disponível nesta execução. As contagens são "
                 "por isso provisórias e nenhuma proporção pode ser reportada até o filtro ser "
                 "aplicado.")
    L.append("")

    if n == 0:
        L.append("A recolha decorre à data de escrita e não contém votos efetivos. "
                 "A ausência de dados não é um resultado de zero por cento, e por isso nada é "
                 "reportado aqui; o mecanismo, as regras e as ameaças à validade abaixo ficam "
                 "estabelecidos para que a medição, quando existir, não dependa de decisões "
                 "tomadas depois de ver os números.")
    else:
        L.append(f"Foram registados {r['votos_brutos']} votos válidos {periodo}, "
                 f"que correspondem a {n} votos efetivos de {r['pessoas']} "
                 f"{'pessoa' if r['pessoas'] == 1 else 'pessoas distintas'}, "
                 f"sobre {r['alertas_votados']} alertas."
                 + (f" {r['mudancas_de_voto']} votos foram posteriormente alterados pela mesma "
                    f"pessoa, e apenas o último de cada par conta."
                    if r['mudancas_de_voto'] else "")
                 + (f" {excluidos} votos foram excluídos por não corresponderem a nenhum alerta "
                    f"do registo partilhado." if excluidos else ""))
        L.append("")
        if not amostra_verificada:
            L.append("O histórico partilhado não esteve disponível para confirmar que cada "
                     "voto corresponde a um alerta entregue. \\textbf{Nenhuma proporção é "
                     "reportada}; as contagens acima são provisórias e não podem ser citadas "
                     "como resultado.")
        elif n < N_MINIMO:
            L.append(f"A amostra fica abaixo do mínimo de {N_MINIMO} votos efetivos fixado no "
                     f"protocolo, pelo que \\textbf{{nenhuma proporção é reportada}}. "
                     f"As contagens acima são o resultado, e são tudo o que esta amostra "
                     f"sustenta. Uma percentagem sobre {n} votos daria ao leitor uma precisão "
                     f"que os dados não têm.")
        else:
            lo, hi = wilson(uteis, n)
            L.append(f"Dos {n} votos efetivos, {uteis} classificaram o alerta como útil, "
                     f"ou seja {uteis / n * 100:.0f}\\%, com intervalo de confiança de Wilson a "
                     f"95\\% entre {lo * 100:.0f}\\% e {hi * 100:.0f}\\%. A largura deste "
                     f"intervalo é a medida honesta do que {n} votos permitem afirmar.")
            por_pessoa = Counter(v for v, _ in efetivos)
            dom, nd = por_pessoa.most_common(1)[0]
            if nd / n > DOMINANCIA_MAX:
                sem = {k: v for k, v in efetivos.items() if k[0] != dom}
                us = sum(1 for v in sem.values() if v.acao == FL.UTIL)
                L.append("")
                L.append(f"Uma única pessoa representa {nd / n * 100:.0f}\\% dos votos efetivos, "
                         f"acima do limite de {DOMINANCIA_MAX * 100:.0f}\\% fixado no protocolo. "
                         f"Excluindo-a, restam {len(sem)} votos, dos quais {us} classificam o "
                         "alerta como útil.")
                if len(sem) < N_MINIMO:
                    L.append(f"Este recorte também fica abaixo do mínimo de {N_MINIMO}; nenhuma "
                             "segunda proporção é reportada e a amostra não sustenta uma leitura "
                             "independente do votante dominante.")
                else:
                    lo2, hi2 = wilson(us, len(sem))
                    L.append(f"A proporção sem essa pessoa é de "
                             f"{us / len(sem) * 100:.0f}\\%, com intervalo entre "
                             f"{lo2 * 100:.0f}\\% e {hi2 * 100:.0f}\\%. É esta a leitura a "
                             "reter.")
    L.append("")
    L.append("Quatro limitações acompanham este resultado e nenhuma delas se resolve com mais "
             "votos. A primeira é a autosseleção: vota quem quer, e quem considera um alerta "
             "indiferente tende a não carregar em nada, o que empurra a amostra para os "
             "extremos. A segunda é a ausência de contrafactual, uma vez que nenhum grupo "
             "recebeu a variação de preço sem a explicação que a acompanha; nada aqui atribui "
             "a utilidade à explicação em si. A terceira é a distância entre utilidade "
             "percebida e decisão melhor, que é a hipótese fundadora deste trabalho e "
             "permanece por testar. A quarta é o desconhecimento de quem vota: o canal é "
             "público e não se sabe se quem responde pertence ao público que a dissertação "
             "assume.")
    L.append("")
    return "\n".join(L)


def _juntar_linhas_da_branch(remotas: list[str], caminho: str | Path) -> int:
    """Guarda a união ordenada branch+local e devolve o total de linhas."""
    destino = Path(caminho)
    locais = (
        [linha for linha in destino.read_text(encoding="utf-8").splitlines() if linha.strip()]
        if destino.exists()
        else []
    )
    vistas: set[str] = set()
    juntas: list[str] = []
    for linha in remotas + locais:
        if linha not in vistas:
            vistas.add(linha)
            juntas.append(linha)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(juntas) + ("\n" if juntas else ""), encoding="utf-8")
    return len(juntas)


def _ler_branch_por_git(ficheiros: tuple[str, ...]) -> dict[str, list[str]] | None:
    """Lê um instantâneo coerente da branch quando a API autenticada não está configurada."""
    fetch = subprocess.run(
        ["git", "fetch", "--quiet", "origin",
         "+refs/heads/alerts-history:refs/remotes/origin/alerts-history"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if fetch.returncode != 0:
        return None
    resolve = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/remotes/origin/alerts-history^{commit}"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    snapshot = resolve.stdout.strip()
    if resolve.returncode != 0 or not snapshot:
        return None
    saida: dict[str, list[str]] = {}
    for ficheiro in ficheiros:
        show = subprocess.run(
            ["git", "show", f"{snapshot}:{ficheiro}"],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if show.returncode != 0:
            return None
        saida[ficheiro] = [linha for linha in show.stdout.splitlines() if linha.strip()]
    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--votos", default=str(DEFAULT_VOTOS))
    ap.add_argument("--historico", default=str(DEFAULT_HISTORICO))
    ap.add_argument("--sem-filtro", action="store_true",
                    help="não filtrar pelo histórico (o relatório assinala-o)")
    ap.add_argument("--out", default=str(OUT_MD))
    ap.add_argument("--out-tex", default=str(OUT_TEX))
    ap.add_argument("--da-branch", action="store_true",
                    help="descarrega feedback.jsonl e alerts_history.jsonl da branch de dados "
                         "antes de analisar (é lá que vivem os dados de produção)")
    args = ap.parse_args()

    # ⚠️ O ficheiro local só tem os votos desta máquina. Os votos reais chegam pelo Telegram a
    # um dyno do Heroku com disco efémero, e o sítio onde ficam é a branch de dados. Analisar o
    # ficheiro local e dizer «N votos» seria contar uma amostra que não é a amostra.
    if args.da_branch:
        from investigator.history_publish import fetch_jsonl

        votos_remotos = fetch_jsonl("feedback.jsonl")
        historico_remoto = fetch_jsonl("alerts_history.jsonl")
        origem = "API autenticada"
        if votos_remotos is None or historico_remoto is None:
            por_git = _ler_branch_por_git(("feedback.jsonl", "alerts_history.jsonl"))
            if por_git is not None:
                votos_remotos = por_git["feedback.jsonl"]
                historico_remoto = por_git["alerts_history.jsonl"]
                origem = "git origin/alerts-history"
        if votos_remotos is None or historico_remoto is None:
            print("[feedback] ERRO: não consegui ler votos e histórico da branch; "
                  "os relatórios existentes não foram substituídos.")
            return 2
        if not historico_remoto:
            print("[feedback] ERRO: a branch não contém histórico; "
                  "não é possível validar os votos.")
            return 2
        total_votos = _juntar_linhas_da_branch(votos_remotos, args.votos)
        total_historico = _juntar_linhas_da_branch(historico_remoto, args.historico)
        print(f"[feedback] branch ({origem}): {len(votos_remotos)} voto(s); "
              f"local depois da junção: {total_votos}.")
        print(f"[feedback] histórico da branch: {len(historico_remoto)} linha(s); "
              f"local depois da junção: {total_historico}.")

    registos = FL.load_jsonl(args.votos)
    chaves = None if args.sem_filtro else chaves_do_historico(args.historico)
    if chaves is None and not args.sem_filtro:
        print(f"[feedback] ⚠️ histórico ilegível em {args.historico}: filtro NÃO aplicado.")
    texto = relatorio(registos, chaves)
    saida = Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(f"[feedback] {len(registos)} voto(s) lido(s) de {args.votos}")
    print(f"[feedback] relatório escrito em {saida}")

    tex = Path(args.out_tex)
    tex.parent.mkdir(parents=True, exist_ok=True)
    tex.write_text(fragmento_latex(registos, chaves), encoding="utf-8")
    print(f"[feedback] fragmento da dissertação escrito em {tex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
