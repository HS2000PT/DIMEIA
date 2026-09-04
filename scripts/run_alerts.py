"""Runner de alertas agendado — varre uma watchlist e envia alertas explicáveis para o Telegram.

Lê `config/alerts.yaml` (definições não-secretas) e reutiliza as funções já validadas do
InvestiGator. Corre na **stack leve** (sem torch). Seguro por defeito: se o Telegram não estiver
configurado, imprime os alertas e sai com código 0 — assim um job agendado fica verde antes de
definires os segredos.

Uso:
    python scripts/run_alerts.py            # varre + envia (se o Telegram estiver configurado)
    python scripts/run_alerts.py --dry-run  # varre + imprime apenas, nunca envia

Pensado para ser chamado por `.github/workflows/alerts.yml` (cron) — ver docs/design/going_live.md.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path

import yaml

# Permitir correr como `python scripts/run_alerts.py` a partir da raiz do repo.
from investigator.alerts_history import utc_stamp
from investigator.console import force_utf8_stdout

_CONFIG = Path(__file__).resolve().parents[1] / "config" / "alerts.yaml"
_STATE = Path(__file__).resolve().parents[1] / "data" / "alerts_state.json"
# No workflow, INVESTIGATOR_HISTORY_PATH aponta para o checkout da branch `alerts-history`
# (ver .github/workflows/alerts.yml); localmente cai num ficheiro gitignored inofensivo.
_HISTORY = Path(os.environ.get(
    "INVESTIGATOR_HISTORY_PATH",
    str(Path(__file__).resolve().parents[1] / "data" / "alerts_history.jsonl"),
))
# KB VIVA: vive ao lado do histórico partilhado (mesma branch de dados `alerts-history`),
# por isso é publicada/lida pelos mesmos mecanismos (workflow + VM + app via raw URL).
_LIVE_PENDING = _HISTORY.parent / "live_pending.jsonl"
_LIVE_KB = _HISTORY.parent / "live_kb.jsonl"
# Base reconstruída do último ano, em formato compacto (metadados + matriz float32).
_AMOSTRAS = Path(__file__).resolve().parents[1] / "data" / "samples"
_BACKFILL_META = _AMOSTRAS / "backfill_kb_meta.jsonl"
_BACKFILL_VEC = _AMOSTRAS / "backfill_kb_vec.npy"
# FUNIL DE GATES: também na branch partilhada — acumula entre corridas para se poder medir
# quantas varreduras cada ticker perdeu em cada etapa (ver investigator/gate_log.py).
_GATE_LOG = _HISTORY.parent / "gate_log.jsonl"
# LOG DE PREDIÇÕES (loop de pós-validação M5.5): também na branch partilhada, para PERSISTIR
# entre corridas do Actions (o runner é efémero — antes o log era gitignored em data/ e nunca
# acumulava na nuvem; o loop de pós-fecho só corria no PC do aluno). Agora `git add -A` do
# workflow publica-o e o post_validate corre em cima dele ao fecho.
_PRED_LOG = _HISTORY.parent / "predictions_log.jsonl"


# ── Estado entre corridas (intradiário, anti-duplicado) ───────────────────────
# Com o cron a correr de 30 em 30 min durante o mercado, o runner tem de se lembrar do que
# JÁ alertou hoje (o job do Actions é efémero; o workflow persiste este ficheiro via cache).
def load_state(path: str | Path = _STATE, today: date | None = None) -> dict:
    """Lê o estado; se for de outro dia, zera as marcas do dia mas PRESERVA o offset do bot."""
    import json

    today = today or date.today()
    state = {"date": today.isoformat(), "alerted_market": [], "alerted_news": [],
             "news_count": {}, "news_words": {}, "opening_sent": False, "summary_sent": False,
             # Sem informação nenhuma sobre o dia, o defeito é «não sei» e não «não saiu nada».
             # Quem sabe é o `run_once`, depois de tentar ler o histórico partilhado.
             "memoria_do_dia": False,
             "desfechos_anotados": False, "bot_offset": None}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        state["bot_offset"] = raw.get("bot_offset")
        if raw.get("date") == today.isoformat():
            state["alerted_market"] = list(raw.get("alerted_market", []))
            state["alerted_news"] = list(raw.get("alerted_news", []))
            state["news_count"] = dict(raw.get("news_count", {}))
            # Palavras de conteúdo do que já saiu hoje, para apanhar a mesma história escrita
            # por outro meio. Ausente em estados antigos ⇒ `.get` com defeito, nunca KeyError.
            state["news_words"] = {k: list(v) for k, v in (raw.get("news_words") or {}).items()}
            state["opening_sent"] = bool(raw.get("opening_sent", False))
            state["summary_sent"] = bool(raw.get("summary_sent", False))
            # Sem esta linha a marca não sobrevivia ao reinício do dyno DENTRO do mesmo dia, e
            # a anotação corria de novo — sem estragar nada (é idempotente e só edita quando há
            # novidade), mas a puxar preços de doze empresas outra vez, de graça.
            state["desfechos_anotados"] = bool(raw.get("desfechos_anotados", False))
    except (OSError, ValueError):
        pass  # sem estado (1.ª corrida do dia/da cache) → começa limpo
    return state


def save_state(state: dict, path: str | Path = _STATE) -> None:
    import json

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def news_key(ticker: str, text: str) -> str:
    """Chave estável de um alerta de notícia, calculada sobre o texto SEM tags (plain_text)
    — assim a VM, o Actions e o histórico partilhado produzem sempre a mesma chave."""
    import hashlib

    from investigator.explanation_engine.explainer import plain_text

    return hashlib.sha1(f"{ticker}|{plain_text(text)}".encode()).hexdigest()[:12]


# Palavras vazias EN+PT. "as" serve as duas línguas, por isso aparece uma vez só — estava
# escrita duas vezes e o conjunto engolia a repetição em silêncio (apanhado pelo ruff).
def sem_segredos(texto: object) -> str:
    """Mascara credenciais em texto que vai para o registo.

    ⚠️ **Isto é uma correcção de fuga, não higiene.** A 2026-08-06, ao verificar uma implantação,
    apareceu isto nos registos do Heroku, centenas de vezes:

        [saltar noticias JNJ] HTTPError: 503 ... for url:
        https://finnhub.io/api/v1/company-news?symbol=JNJ&from=...&token=<A CHAVE INTEIRA>

    A mensagem de uma `HTTPError` inclui o URL do pedido, e o URL leva o token. Ou seja: bastava
    a API responder com erro — e respondeu 503 a tudo nesse dia — para a chave ficar escrita no
    registo, legível por quem tenha acesso à aplicação. O código nunca imprimiu a chave de
    propósito; imprimiu **a excepção**, e a chave vinha lá dentro.

    É a segunda fuga desta família neste projecto (a primeira, na sessão 44, expôs a chave da
    AlphaVantage por o filtro de saída só mascarar cadeias com mais de 30 caracteres). A lição é
    a mesma: **nunca imprimir uma excepção de rede em bruto.**
    """
    import re

    s = str(texto)
    # Qualquer parâmetro de query com cheiro a credencial, seja qual for o nome.
    s = re.sub(r"([?&](?:token|key|apikey|api_key|apiKey|access_token)=)[^&\s]+",
               r"\1<REDACTED>", s, flags=re.I)
    return s


# ⚠️ A regra da quase-repetição vive agora em `investigator/dedup.py`, porque o caminho dos
# PRECEDENTES precisava exactamente da mesma e uma biblioteca não deve importar de um script.
# Estes nomes ficam como re-exportação: são a API que os testes e o resto do runner já usavam.
from investigator.dedup import content_words as conteudo  # noqa: E402
from investigator.dedup import is_near_duplicate  # noqa: E402


def quase_repetida(manchete: str, anteriores: list[list[str]], limiar: float = 0.6) -> bool:
    """A mesma história, escrita por outro meio? Ver `investigator.dedup.is_near_duplicate`."""
    return is_near_duplicate(manchete, anteriores, limiar)


def seed_state_from_shared_history(state: dict, entries: list, today: str) -> None:
    """Puro: semeia o estado com o que QUALQUER produtor já enviou hoje.

    Com dois produtores possíveis (a VM em modo --watch e o cron do Actions como rede de
    segurança), o estado local de cada um não chega — o histórico partilhado (branch
    `alerts-history`) é a memória comum que impede alertas duplicados no canal.

    ⚠️ **Este é o único sítio onde o runner descobre o que já saiu hoje depois de um reinício.**
    O `data/alerts_state.json` vive no disco do dyno, que é efémero: cada arranque começa com o
    contador do dia a zero. Se esta função não semear — porque a rede falhou, porque a
    publicação do produtor anterior ainda não chegou à branch, ou porque o URL não está
    configurado — o processo não fica a saber que já enviou nada; fica a **acreditar que não
    enviou nada**, que é outra coisa.

    Foi o que aconteceu entre 25 e 29 de agosto de 2026: o registo mostra rajadas de exactamente
    cinco alertas de notícia, aos segundos coincidentes com arranques (00:03, 07:38, 13:04,
    22:24 no dia 26), num dia com orçamento de cinco. Vinte alertas, e as mesmas cinco empresas
    quatro vezes. O orçamento não foi violado por uma decisão errada: foi violado por um
    contador que voltou ao princípio quatro vezes.
    """
    for e in entries:
        if e.date != today:
            continue
        if e.kind == "market" and e.ticker not in state["alerted_market"]:
            state["alerted_market"].append(e.ticker)
        elif e.kind == "news":
            k = e.key or news_key(e.ticker, e.text)
            if k not in state["alerted_news"]:
                state["alerted_news"].append(k)
                state["news_count"][e.ticker] = state["news_count"].get(e.ticker, 0) + 1
        elif e.kind == "summary":
            state["summary_sent"] = True
        elif e.kind == "open":
            state["opening_sent"] = True


def _noticias_de_todas_as_fontes(ticker: str, start: str, end: str, cfg_news: dict) -> list:
    """Junta as fontes configuradas e devolve manchetes **sem repetições**.

    ⚠️ Somar fontes só vale a pena porque foi medido que se completam, e não porque "mais é
    melhor" (`docs/evaluation/evaluation_news_sources.md`): sobre a watchlist e três dias, as
    três juntas dão **970** manchetes relevantes distintas contra as **432** do Finnhub sozinho.
    O Polygon traz mais exclusivas do que o Finnhub, e a Alpha Vantage é a **mais fresca** (9,3 h
    de mediana contra 15,8 h), que é o que ataca a queixa de os alertas chegarem tarde.

    A deduplicação é por manchete normalizada. É o mínimo defensável: a mesma história publicada
    por dois sítios com títulos diferentes continua a passar como duas, e isso é uma limitação
    conhecida — a detecção por significado existe no sistema e está registada como o passo
    seguinte.

    Fail-open por fonte: uma fonte que falhe ou não tenha chave é ignorada com aviso, e as
    outras respondem. É a mesma razão pela qual os preços vêm de uma cadeia e não de uma fonte.
    """
    import re

    from investigator.news_fetcher.fetcher import (
        fetch_alphavantage_news,
        fetch_finnhub_company_news,
        fetch_polygon_news,
    )

    extra = [f.strip().lower() for f in (cfg_news.get("extra_sources") or [])]
    fontes: list[tuple[str, object]] = [
        ("finnhub", lambda: fetch_finnhub_company_news(ticker, start, end)),
    ]
    if "alphavantage" in extra:
        fontes.append(("alphavantage", lambda: fetch_alphavantage_news(ticker)))
    if "polygon" in extra:
        fontes.append(("polygon", lambda: fetch_polygon_news(ticker)))

    vistos: set[str] = set()
    juntas: list = []
    contagem: dict[str, int] = {}
    for nome, fn in fontes:
        try:
            itens = fn()
        except Exception as exc:  # noqa: BLE001 — uma fonte em baixo não pode calar o sistema
            print(f"[noticias {ticker}] fonte {nome} indisponível (ignorada): "
                  f"{type(exc).__name__}: {sem_segredos(exc)}")
            continue
        novos = 0
        for it in itens:
            chave = re.sub(r"[^a-z0-9 ]+", " ", it.headline.lower()).strip()
            if chave and chave not in vistos:
                vistos.add(chave)
                juntas.append(it)
                novos += 1
        contagem[nome] = novos
    if len(contagem) > 1:
        detalhe = " · ".join(f"{k} +{v}" for k, v in contagem.items())
        print(f"[noticias {ticker}] {len(juntas)} manchetes distintas ({detalhe})")
    return juntas


def _movimento_de_hoje(ticker: str) -> tuple[float | None, str | None]:
    """O retorno do último dia e uma leitura em palavras da sua raridade. Fail-open total.

    Existe porque um alerta de notícia falava de manchetes passadas e nunca dizia o que a acção
    estava a fazer **agora** — o facto mais simples e o único que permite julgar, num relance,
    se a notícia interessa. A frase de raridade usa a mesma contagem empírica do painel (quantos
    dos últimos dias se moveram pelo menos isto), e não uma probabilidade: converter o z-score
    numa probabilidade exigiria normalidade, que os retornos não têm.
    """
    try:
        from investigator.anomaly_detector.frequency import empirical_exceedance
        from investigator.market_data.prices import get_price_history

        closes = get_price_history(ticker)["Close"].dropna()
        if len(closes) < 2:
            return None, None
        retornos = closes.pct_change().dropna()
        ret = float(retornos.iloc[-1])
        nota = None
        try:
            exc = empirical_exceedance(retornos)
            if exc is not None:
                # A contagem diz as duas coisas conforme o caso: "3 of the last 249" lê-se
                # como raro e "220 of the last 249" lê-se como banal, sem precisar de
                # adjectivo nenhum. O número fica sempre, que é a lição do defeito antigo em
                # que um movimento no top 2% do ano foi descrito como "an ordinary day".
                nota = f"{exc.count} of the last {exc.n} days moved at least as much"
        except Exception:  # noqa: BLE001 — a nota é um extra, nunca um requisito
            nota = None
        return ret, nota
    except Exception:  # noqa: BLE001
        return None, None


def filter_new_alerts(market: list[tuple[str, str]], news: list[tuple[str, str]],
                      state: dict, max_per_ticker: int = 2,
                      materiality: dict[str, float] | None = None,
                      headlines: dict[str, str] | None = None,
                      ladder: list[float] | None = None,
                      suppressed: dict[str, tuple[str, str]] | None = None,
                      daily_budget: int | None = None
                      ) -> list[tuple[str, str]]:
    """Puro: mantém só o que ainda NÃO foi alertado hoje e marca-o no estado.

    Notícias têm um TETO por ticker por dia (`max_per_ticker`, config
    `news.max_per_ticker_per_day`) — anti-fadiga: 12 alertas/dia do mesmo ticker treinam
    o utilizador a ignorar o canal.

    ⚠️ **CORRECÇÃO DE UM DEFEITO NA PRÓPRIA CORRECÇÃO ANTERIOR (2026-08-07).**
    A 2026-08-05 acrescentou-se aqui uma ordenação por materialidade e escreveu-se que "o tecto
    passa a ser servido por importância em vez de por ordem de chegada". **Não passou.** A
    ordenação vale dentro de uma chamada, e `scan_news` emite **no máximo um alerta por ticker
    por ciclo** (escolhe `latest`, a manchete relevante mais recente). Duas notícias do MESMO
    ticker nunca coexistem no mesmo lote, portanto a ordenação **nunca** pode reordenar duas
    candidatas que disputam o mesmo tecto — o tecto é por ticker. Ao longo do dia a quota
    continuava a ser gasta pela ordem de chegada, que era exactamente o defeito a corrigir.

    O teste que a validava passava a comparar três manchetes NVDA numa só chamada, um cenário
    que a produção não sabe produzir. Um teste verde sobre um cenário impossível é
    indistinguível de uma correcção que funciona.

    **O que a ordenação faz de facto, e fica escrito como o que é:** ordena a ORDEM DE ENTREGA
    entre tickers diferentes dentro de um ciclo — o canal mostra primeiro a mais material. É um
    benefício pequeno e real; não é o controlo do tecto.

    **O controlo global do tecto é `daily_budget`**. A `ladder` (config
    `news.materiality_ladder`) encarece apenas alertas adicionais do mesmo ticker: com orçamento
    ligado, o primeiro slot fica livre e o segundo exige a segunda posição da escada. Assim a
    triagem não volta a excluir empresas inteiras por outra porta.

    ⚠️ **O que isto NÃO resolve, e não há algoritmo online que resolva:** o primeiro slot é
    gasto na primeira manchete que passe o gate, porque no momento da decisão a notícia da
    tarde ainda não existe. Não se pode reservar quota para uma história que ainda não se viu,
    e não se pode retirar um alerta já entregue. O que se pode é tornar cada slot extra mais
    caro, e é isso que está feito.

    Os dois valores guardados na configuração são **derivados**, não escolhidos: são os τ* do
    varrimento de política (`docs/evaluation/evaluation_policy_sweep.md`) sob custos crescentes
    de falso alarme. R=1 dá τ*=0,49 e R=0,5 dá τ*=0,64. Com `daily_budget`, 0,49 fica apenas como
    proveniência: o primeiro alerta de cada ticker não tem piso e o SEGUNDO exige 0,64, onde a
    fadiga é o risco dominante. Um limiar de "notícia de última hora" acima disso **não é
    implementável com este modelo** e por isso não foi inventado: o score máximo observado no
    conjunto de teste está entre 0,65 e 0,66 (a τ=0,66 não dispara nada), logo qualquer piso de
    0,7+ seria código morto com aparência de rigor.

    `materiality` é um canal lateral `{news_key: P(material)}`, o mesmo padrão que `event_times`
    já usava, para não mudar a forma dos tuplos `(ticker, texto)` que atravessam o runner.
    **Sem triagem ligada (o defeito por defeito), o dicionário vem vazio, a `ladder` não tem
    score para aplicar e a ordem de chegada é preservada** — o comportamento antigo é o caso
    particular deste.

    ⚠️ `suppressed` é o canal lateral de SAÍDA `{ticker: (etapa, detalhe)}`, e existe por causa
    de um defeito que só se via no ecrã: estas três supressões acontecem **depois** do
    `scan_news`, que é onde o funil é registado, portanto nada as registava. O `gate_log` dizia
    `alerted` e o screener traduzia para **"Alert sent"** — afirmando ao utilizador que um
    alerta saiu quando não saiu. Quem chama reconcilia o funil com isto.
    """
    keep: list[tuple[str, str]] = []
    for ticker, text in market:
        if ticker not in state["alerted_market"]:
            state["alerted_market"].append(ticker)
            keep.append((ticker, text))
        else:
            print(f"[{ticker}] já alertado hoje — sem repetição.")

    if materiality:
        # `sorted` é estável: entre iguais (e entre as que não têm score) a ordem de chegada
        # mantém-se. As sem score ficam atrás porque não há evidência de materialidade para
        # lhes dar a quota — e isso fica dito no log, não em silêncio.
        news = sorted(news, key=lambda tt: -materiality.get(news_key(tt[0], tt[1]), -1.0))
        ordem = ", ".join(
            f"{t} {materiality.get(news_key(t, x), float('nan')):.0%}" for t, x in news[:6]
        )
        # Dito como o que é: isto ordena a ENTREGA entre tickers. O tecto (que é por ticker) é
        # controlado pela `ladder` abaixo. A mensagem anterior afirmava o contrário.
        print(f"[noticias] ordem de entrega por materialidade: {ordem}")

    vistas: dict[str, list[list[str]]] = state.setdefault("news_words", {})
    for ticker, text in news:
        k = news_key(ticker, text)
        if k in state["alerted_news"]:
            print(f"[noticias {ticker}] já alertada hoje — sem repetição.")
            # Sem esta linha o funil continuava a dizer `alerted` a cada ciclo de 60 s para
            # uma manchete já entregue. As três supressões abaixo registavam-se e esta não.
            if suppressed is not None:
                suppressed[ticker] = ("already_sent", "same headline already delivered today")
            continue
        # A quase-repetição compara MANCHETES. Sem manchete no canal lateral não se compara
        # nada: falha aberto, porque suprimir um alerta por engano é pior do que repetir um.
        manchete = (headlines or {}).get(k, "")
        if manchete and quase_repetida(manchete, vistas.get(ticker, [])):
            print(f"[noticias {ticker}] a mesma história noutras palavras — sem repetição.")
            if suppressed is not None:
                suppressed[ticker] = ("duplicate_story", "same story, other words")
            continue
        # ⚠️ ORÇAMENTO GLOBAL DO DIA, e vem ANTES do tecto por ticker de propósito.
        # O tecto por ticker limita cada empresa mas não limita o total: com doze empresas a
        # dois alertas cada, o pior caso são vinte e quatro mensagens num dia. O que o
        # utilizador sente é o total, não a distribuição.
        # A ordem entre candidatas já foi decidida acima, por materialidade — que é a única
        # coisa para que o score do modelo tem informação: ordenar ENTRE empresas.
        # ⚠️ NÃO dizer que é a mesma política que a dissertação avalia. Não é, e o docstring
        # desta função explica porquê: a métrica ordena o dia INTEIRO e depois escolhe cinco
        # (offline), e aqui os cinco lugares gastam-se por ordem de chegada (online), porque a
        # notícia da tarde ainda não existe. São da mesma família; a avaliada é um limite
        # superior desta. A tese diz isso na Secção do veredicto da QI3.
        if daily_budget is not None:
            # ⚠️ Falha FECHADA, e só esta porta. Todo o resto do runner falha aberto de
            # propósito — suprimir por falta de informação seria decidir com base em nada. Aqui
            # é o contrário: ENVIAR por falta de informação é que é decidir com base em nada, e
            # o custo do erro não é simétrico. Não enviar um alerta hoje perde-se um alerta;
            # enviar sem saber o que já saiu enche o canal e ensina o leitor a ignorá-lo, que é
            # a única coisa que este trabalho não pode dar-se ao luxo de fazer.
            if not state.get("memoria_do_dia", True):
                if suppressed is not None:
                    suppressed[ticker] = ("daily_budget", "day's count unknown this cycle")
                continue
            total_hoje = sum(state["news_count"].values())
            if total_hoje >= daily_budget:
                print(f"[noticias {ticker}] orçamento do dia gasto "
                      f"({total_hoje}/{daily_budget}) — sem mais alertas hoje.")
                if suppressed is not None:
                    suppressed[ticker] = ("daily_budget",
                                          f"budget {daily_budget}/day spent")
                continue

        ja_hoje = state["news_count"].get(ticker, 0)
        if ja_hoje >= max_per_ticker:
            print(f"[noticias {ticker}] teto diário atingido ({max_per_ticker}) "
                  "— sem mais alertas deste ticker hoje.")
            if suppressed is not None:
                suppressed[ticker] = ("daily_cap", f"cap {max_per_ticker}/day reached")
            continue
        # Piso escalonado: cada slot seguinte do mesmo ticker no mesmo dia custa mais. Falha
        # ABERTO em duas situações, de propósito: sem `ladder` configurada, e sem score para
        # esta manchete (triagem desligada, ou modelo ausente). Suprimir um alerta por falta de
        # informação seria decidir com base em nada.
        #
        # ⚠️ COM ORÇAMENTO LIGADO, O PRIMEIRO SLOT NÃO TEM PISO, e isto foi apanhado num
        # dry-run: tirar o veto da triagem em `scan_news` não bastava, porque a escada é
        # **outro limiar sobre o mesmo score** e reproduzia o mesmo defeito — a AAPL, cujo
        # score está sempre à volta de 0.46, continuava a não conseguir alertar nunca, agora
        # travada aqui em vez de lá.
        # A escada foi derivada quando o score era a porta; passando o controlo de volume para
        # o orçamento, ela mantém o papel para que continua a servir — tornar cada alerta
        # EXTRA da MESMA empresa mais caro, que é anti-fadiga e não selecção de empresas.
        primeiro_slot_livre = daily_budget is not None and ja_hoje == 0
        piso = (None if primeiro_slot_livre
                else ladder[ja_hoje] if ladder and ja_hoje < len(ladder) else None)
        p = (materiality or {}).get(k)
        if piso is not None and p is not None and p < piso:
            print(f"[noticias {ticker}] alerta nº{ja_hoje + 1} do dia exige "
                  f"P≥{piso:.0%} e esta tem {p:.0%} — quota guardada.")
            if suppressed is not None:
                suppressed[ticker] = ("ladder_floor", f"P {p:.2f} < floor {piso:.2f}")
            continue
        state["alerted_news"].append(k)
        state["news_count"][ticker] = state["news_count"].get(ticker, 0) + 1
        if manchete:
            vistas.setdefault(ticker, []).append(sorted(conteudo(manchete)))
        keep.append((ticker, text))
    return keep


# Chaves (news_date, ticker, headline) já escritas no registo. O varrimento repontua a mesma
# manchete de 60 em 60 segundos: sem esta guarda a mediana era de 78 linhas por título distinto
# e o máximo 1406 (`registo_decisoes_auditoria.md`). Escrever a duplicação faz o peso de cada
# empresa passar a ser a frequência com que o sistema a republica, e não a frequência com que
# ela aparece nas notícias — e o ficheiro é republicado inteiro a cada ciclo, logo o custo é de
# publicação. Uma linha por título, e a contagem de ciclos vive no `gate_log`, que é onde a
# pergunta "onde é gasto o tempo do sistema" se responde.
_DECISOES_VISTAS: tuple[str, set[tuple[str, str, str]]] | None = None


def _seed_decision_keys() -> set[tuple[str, str, str]]:
    """Lê o registo uma vez e devolve as chaves já escritas (vazio se não houver ficheiro).

    A cache é indexada pelo CAMINHO do registo. Guardá-la sem o caminho faria uma troca de
    ficheiro herdar as chaves do anterior e suprimir escritas legítimas em silêncio — que é
    exactamente a classe de defeito que esta guarda existe para não introduzir.

    Fail-open: um registo ilegível não pode impedir o varrimento de correr.
    """
    global _DECISOES_VISTAS
    chave_ficheiro = str(_PRED_LOG)
    if _DECISOES_VISTAS is not None and _DECISOES_VISTAS[0] == chave_ficheiro:
        return _DECISOES_VISTAS[1]
    vistas: set[tuple[str, str, str]] = set()
    try:
        from investigator.triage.postval import read_log

        for r in read_log(_PRED_LOG):
            vistas.add((str(r.get("news_date")), str(r.get("ticker")), str(r.get("headline"))))
    except Exception as exc:  # noqa: BLE001
        print(f"[postval] semente do registo falhou (ignorada): "
              f"{type(exc).__name__}: {sem_segredos(exc)}")
    _DECISOES_VISTAS = (chave_ficheiro, vistas)
    return vistas


def _log_decision_safe(news_date: str, ticker: str, headline: str,
                       scored: tuple | None, gate: float | None, kept: bool,
                       feature_snapshot: dict | None = None,
                       model_info: dict | None = None,
                       stage: str | None = None) -> None:
    """Regista a decisão de notícia para o loop de pós-validação (M5.5, `scripts/
    post_validate.py`). Ficheiro local gitignored; uma falha aqui NUNCA pára o runner."""
    try:
        from investigator.triage.postval import log_decision

        chave = (str(news_date), str(ticker), str(headline))
        vistas = _seed_decision_keys()
        if chave in vistas:
            return
        log_decision(_PRED_LOG, news_date=news_date, ticker=ticker, headline=headline,
                     prob=(float(scored[0]) if scored is not None else None),
                     gate=(gate if scored is not None else None), kept=kept,
                     feature_snapshot=feature_snapshot, model_info=model_info,
                     stage=stage)
        vistas.add(chave)
    except Exception as exc:  # noqa: BLE001
        print(f"[postval] registo falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def _registar_candidatas_safe(relevantes: list, latest, ticker: str, bundle,
                              gate: float | None, max_age: int, hoje,
                              close=None) -> None:
    """Regista TODA a manchete relevante que o ciclo NÃO escolheu, com a porta onde morreu.

    Decisão R1 do contrato de dados. Antes disto o registo só recebia a sobrevivente das portas
    — o varrimento pontua uma manchete por empresa por ciclo, a mais recente relevante — e um
    candidato treinado nesse registo herda o enviesamento que a dissertação já dá como a causa
    de o modelo não ajudar em produção: quando é invocado, os filtros elementares já removeram
    grande parte do que ele foi treinado para remover.

    A `latest` NÃO é registada aqui; é registada a jusante, com a porta real onde acabou.

    ⚠️ A série de preços vem de FORA, já obtida, e isso não é detalhe. A primeira versão
    ia buscá-la aqui, o que somava uma segunda busca por empresa e por ciclo — doze chamadas
    por minuto a mais. Em produção o efeito foi imediato e não aparecia em teste nenhum: o
    yfinance começou a devolver séries de 14 dias em vez do histórico completo, `vol20` saiu
    NaN, e a triagem DEIXOU DE PONTUAR NO SISTEMA INTEIRO — 139 linhas `[triagem]` antes da
    implantação, zero depois. O `_hist_cached` já existia precisamente com este aviso escrito
    no docstring; o que faltou foi usá-lo.

    ⚠️ Fixados a empresa e o dia, oito das nove entradas são constantes: só `headline_len`
    separa duas manchetes da mesma empresa no mesmo ciclo. Registá-las todas é o que torna essa
    afirmação mensurável a partir do registo, em vez de discutível.

    Fail-open em todos os passos: nada aqui pode travar um alerta.
    """
    outras = [it for it in relevantes if it is not latest]
    if not outras:
        return
    snapshot_de = {}
    if bundle is None:
        close = None
    for it in outras:
        etapa = "stale" if not news_is_fresh(it.date, hoje, max_age) else "not_latest"
        scored = None
        snapshot = None
        if close is not None:
            try:
                from investigator.triage.infer import score_latest_with_snapshot

                resultado = score_latest_with_snapshot(bundle, close, it.headline, ticker)
                if resultado is not None:
                    scored, snapshot = resultado
            except Exception as exc:  # noqa: BLE001
                snapshot_de.setdefault("erro", f"{type(exc).__name__}: {sem_segredos(exc)}")
        # `model_info` SO quando houve pontuacao. Registar a identidade do modelo numa linha
        # que ele nao pontuou afirma mais do que aconteceu, e a auditoria leria essas linhas
        # como classe A quando nao sao.
        _log_decision_safe(it.date, ticker, it.headline, scored, gate,
                           kept=False, feature_snapshot=snapshot,
                           model_info=(bundle.get("_model_info")
                                       if (bundle is not None and scored is not None) else None),
                           stage=etapa)
    if "erro" in snapshot_de:
        print(f"[postval {ticker}] pontuacao de candidata falhou (ignorada): "
              f"{snapshot_de['erro']}")


def load_config(path: str | Path = _CONFIG) -> dict:
    """Carrega o ficheiro de definições YAML (base, sem overrides)."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _local_overrides() -> dict:
    """Overrides do operador no disco (VM/PC): `config/alerts_overrides.yaml`. Fail-open."""
    p = _CONFIG.parent / "alerts_overrides.yaml"
    if not p.exists():
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:  # noqa: BLE001
        return {}


def _branch_overrides(cfg: dict) -> dict:
    """Overrides definidos no PAINEL DE ADMIN da app, publicados na branch partilhada
    (`alerts_overrides.json`, ao lado do histórico). Fail-open: rede/404/JSON mau ⇒ {}."""
    url = ((cfg.get("public") or {}).get("history_url")) or ""
    if not url:
        return {}
    try:
        import json

        import requests

        r = requests.get(url.rsplit("/", 1)[0] + "/alerts_overrides.json", timeout=5)
        if r.status_code == 404:
            return {}
        r.raise_for_status()
        return json.loads(r.text) or {}
    except Exception:  # noqa: BLE001
        return {}


def effective_config(path: str | Path = _CONFIG) -> dict:
    """Config base + overrides (operador local, depois admin da app). O admin ganha o desempate.
    Estritamente FAIL-OPEN e limitado a valores sãos (`settings_overrides`): um override mau
    nunca altera o comportamento nem inunda o canal."""
    from investigator.settings_overrides import merge_overrides

    cfg = load_config(path)
    cfg = merge_overrides(cfg, _local_overrides())
    cfg = merge_overrides(cfg, _branch_overrides(cfg))
    return cfg


def news_is_fresh(news_date: str, today: date, max_age_days: int = 2) -> bool:
    """Puro: só alertamos notícias recentes.

    O scan apanha "a mais recente da última semana"; sem este filtro a MESMA manchete
    podia alertar dias a fio (spam = fadiga de alertas). 2 dias por defeito cobre o
    fim de semana (notícia de sábado ainda alerta na segunda).
    """
    try:
        d = date.fromisoformat(str(news_date)[:10])
    except ValueError:
        return False
    return 0 <= (today - d).days <= max_age_days


def bar_is_fresh(last_bar: date, today: date) -> bool:
    """Puro: só perguntamos "hoje é anómalo?" se a última barra de preços é de HOJE.

    Evita dois defeitos reais: repetir num feriado de segunda o alerta da barra de sexta
    (já enviado na sexta) e "avaliar" dados estagnados quando o mercado não abriu.
    """
    return last_bar >= today


def build_market_alerts(results: list[tuple[str, object]]) -> list[str]:
    """Puro: dado [(ticker, AnomalyResult)], devolve os textos de alerta só das anomalias."""
    from investigator.explanation_engine.explainer import explain_anomaly

    return [explain_anomaly(ticker, res) for ticker, res in results if res.is_anomaly]


def _hist_cached(ticker: str, cache: dict) -> object:
    """UMA busca de preços por ticker por ciclo (fecho + intradiário partilham a cadeia
    de fallback de `get_price_history` — sem isto, cada ciclo duplicava as chamadas)."""
    if ticker not in cache:
        from investigator.market_data.prices import get_price_history

        cache[ticker] = get_price_history(ticker)
    return cache[ticker]


def collect_market_results(cfg: dict, cache: dict | None = None) -> list[tuple[str, object]]:
    """Busca preços e avalia cada ticker; devolve [(ticker, AnomalyResult)] dos dias frescos.

    Base tanto dos alertas de anomalia como do resumo diário de fecho — uma só passagem
    pelos preços por corrida.
    """
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.market_data.prices import log_returns

    m = cfg.get("market", {})
    if not m.get("enabled", False):
        return []
    cache = {} if cache is None else cache
    window = int(m.get("window", 20))
    threshold = float(m.get("threshold", 3.0))
    require_fresh = bool(m.get("require_fresh_bar", True))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            hist = _hist_cached(ticker, cache)
            last_bar = hist.index[-1].date()
            if require_fresh and not bar_is_fresh(last_bar, date.today()):
                print(f"[{ticker}] última barra é de {last_bar} (sem sessão nova hoje) "
                      "— sem avaliação (anti-duplicado).")
                continue
            returns = log_returns(hist["Close"])
            results.append((ticker, detect_latest(returns, window=window, threshold=threshold)))
        except Exception as exc:  # noqa: BLE001  (um ticker/rede a falhar não pode parar a varredura)
            print(f"[saltar {ticker}] {type(exc).__name__}: {sem_segredos(exc)}")
    return results


def scan_market(cfg: dict) -> list[tuple[str, str]]:
    """Deteta anomalias e devolve pares (ticker, texto de alerta)."""
    results = collect_market_results(cfg)
    # Mesmo filtro e mesma ordem de build_market_alerts (puro, testado) → zip alinha por construção.
    tickers_anomalos = [t for t, r in results if r.is_anomaly]
    return list(zip(tickers_anomalos, build_market_alerts(results), strict=True))


def build_daily_summary(results: list[tuple[str, object]], threshold: float) -> str:
    """Puro: a mensagem única de fecho — o batimento cardíaco diário do canal.

    Sem isto, em dias calmos o canal ficava mudo sobre o mercado e o utilizador não via o
    detetor a trabalhar. Uma mensagem por dia: cada ticker com o movimento e o z-score,
    anomalias destacadas; honesto quando não há nenhuma.
    """
    if not results:
        return ""
    from investigator.explanation_engine.explainer import direction_icon

    ordenados = sorted(results, key=lambda tr: -tr[1].score_magnitude)
    linhas = ["📊 <b>Daily close summary</b>"]
    # Hierarquia visual (UX 2026-07-12): movers em destaque, um por linha; os calmos
    # (<1% e sem anomalia) comprimidos numa linha só — 10 linhas monótonas não se leem.
    # A seta segue SEMPRE o sinal do movimento (direction_icon, fonte única): anomalias
    # levam 📈 (sobe, verde) / 📉 (desce, vermelho); os movers normais as setas finas ⬆/⬇.
    calmos: list[str] = []
    for ticker, r in ordenados:
        estatistica = (f"z {r.z_score:+.2f}" if not r.zero_variance
                       else f"flat {r.window}-day baseline")
        if r.is_anomaly:
            icon = direction_icon(r.last_return)
            linhas.append(f"{icon} {ticker}: {r.last_return * 100:+.2f}% ({estatistica})")
        elif abs(r.last_return) >= 0.01:
            seta = "⬆" if r.last_return > 0 else "⬇"
            linhas.append(f"{seta} {ticker}: {r.last_return * 100:+.2f}% ({estatistica})")
        else:
            calmos.append(f"{ticker} {r.last_return * 100:+.1f}%")
    if calmos:
        linhas.append("• Quiet: " + " · ".join(calmos))
    n_anom = sum(1 for _, r in results if r.is_anomaly)
    if n_anom:
        linhas.append(
            f"{n_anom} anomaly(ies) today (|z| ≥ {threshold:g}, or a move after a flat "
            "baseline); alerted above."
        )
    else:
        linhas.append(f"No anomalies today (threshold |z| ≥ {threshold:g}); a normal day.")
    linhas.append("<i>An observed snapshot of the watchlist, not advice.</i>")
    return "\n".join(linhas)


def build_opening_note(results: list[tuple[str, object]]) -> str:
    """Puro: a mensagem de ABERTURA — como a watchlist está a abrir vs o fecho de ontem.

    O par matinal do resumo de fecho (o aluno pediu "um alerta de abertura"): dá o pulso da
    manhã (gaps overnight + primeiros minutos da sessão) a partir dos resultados INTRADIÁRIOS
    (cotação ao vivo vs fecho anterior). Sem previsão — só o que já se observa.
    """
    if not results:
        return ""
    from investigator.explanation_engine.explainer import direction_icon

    ordenados = sorted(results, key=lambda tr: -abs(tr[1].last_return))
    linhas = ["🔔 <b>Market open · watchlist snapshot</b>"]
    calmos: list[str] = []
    for ticker, r in ordenados:
        if abs(r.last_return) >= 0.01:
            icon = direction_icon(r.last_return)
            linhas.append(f"{icon} {ticker}: {r.last_return * 100:+.2f}% vs yesterday's close")
        else:
            calmos.append(f"{ticker} {r.last_return * 100:+.1f}%")
    if calmos:
        linhas.append("• Flat at the open: " + " · ".join(calmos))
    linhas.append("<i>How the US session is opening vs yesterday's close. "
                  "An observed snapshot, not advice.</i>")
    return "\n".join(linhas)


def maybe_opening_note(state: dict, results: list[tuple[str, object]],
                       hour_utc: int) -> str | None:
    """Puro: a nota de abertura na 1.ª corrida da janela de abertura (14–15 UTC), 1×/dia.

    A janela cobre verão (abertura 13:30 UTC ⇒ já aberto às 14h) e inverno (abertura 14:30 ⇒
    aberto às 15h). Marca `opening_sent` (partilhado entre corridas e produtores, como o resumo).
    """
    if hour_utc not in (14, 15) or state.get("opening_sent") or not results:
        return None
    state["opening_sent"] = True
    return build_opening_note(results)


def maybe_daily_summary(state: dict, results: list[tuple[str, object]],
                        threshold: float, hour_utc: int) -> str | None:
    """Puro: devolve o resumo de fecho na 1.ª corrida com hora UTC ≥ 21, uma vez por dia.

    Marca `summary_sent` no estado (partilhado entre corridas e, via histórico, entre
    produtores). Sem resultados frescos (mercado fechado) não há nada a resumir.
    """
    if hour_utc < 21 or state.get("summary_sent") or not results:
        return None
    state["summary_sent"] = True
    return build_daily_summary(results, threshold)


def maybe_anotar_desfechos(state: dict, hour_utc: int, *, dry_run: bool = False) -> int:
    """Uma vez por dia, depois do fecho americano, anexa a cada alerta recente o que a ação
    veio a fazer a +1, +3 e +5 sessões.

    **Porque corre aqui e não num agendador à parte.** O `worker` já é um processo permanente
    com ciclo de 60 s e já tem este padrão para o resumo de fecho: uma marca no estado
    partilhado e uma guarda de hora. Um agendador seria mais uma peça a manter, a pagar e a
    falhar em silêncio, para fazer o que uma guarda de duas linhas faz.

    **22 UTC e não 21**, que é a hora do resumo de fecho: a anotação precisa das barras de
    fecho do próprio dia, e as fontes gratuitas só as consolidam mais tarde. Correr as duas na
    mesma hora daria uma anotação sistematicamente atrasada de um dia.

    Fail-open, como tudo neste caminho: nada aqui pode impedir um alerta de sair.
    """
    if hour_utc < 22 or state.get("desfechos_anotados"):
        return 0
    state["desfechos_anotados"] = True
    try:
        import importlib.util

        caminho = Path(__file__).resolve().parent / "anotar_desfechos.py"
        spec = importlib.util.spec_from_file_location("anotar_desfechos", caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.anotar_tudo(_HISTORY, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        print(f"[desfechos] anotação falhou (ignorada): {type(exc).__name__}: {sem_segredos(exc)}")
        return 0


def apply_materiality(text: str, scored: tuple | None, gate: float) -> str | None:
    """Puro: aplica o gate da triagem aprendida a um alerta de notícia (ML_PLAN M5).

    `scored` = (probabilidade, contribuições) do modelo só-contexto, ou None quando não foi
    possível pontuar (sem histórico suficiente) — nesse caso FAIL-OPEN: o alerta segue como
    sempre, sem linha. Devolve None se o gate suprimir o alerta; caso contrário o texto com
    a linha de materialidade (honesta: "triage evidence, not a forecast").
    """
    if scored is None:
        return text
    from investigator.triage.explain import materiality_line

    prob, contribs = scored
    if prob < gate:
        return None
    return text + "\n" + materiality_line(prob, contribs)


def precedents_are_strong(precedents: list, min_similarity: float) -> bool:
    """Puro: há pelo menos um precedente com similaridade ≥ chão?

    Evidência fraca (sim ~0,35-0,45) parecia aleatória ao utilizador — com razão. Sem um
    precedente forte, é mais honesto NÃO alertar do que mostrar vizinhos irrelevantes.
    """
    return any(score >= min_similarity for _, score in precedents)


def scan_news(cfg: dict, event_times: dict[str, str] | None = None,
              gate_log: list | None = None,
              materiality: dict[str, float] | None = None,
              headlines: dict[str, str] | None = None) -> list[tuple[str, str]]:
    """Opcional: notícias recentes por ticker -> pares (ticker, alerta) (best-effort).

    Qualidade primeiro (revisão 2026-07-11, sobre 27 alertas reais): (1) filtro de
    RELEVÂNCIA — a manchete tem de mencionar a empresa e não pode ser boilerplate de
    mercado; (2) chão de SIMILARIDADE — sem um precedente forte, não há alerta; (3) o
    gate de materialidade regista o P de cada ticker no log (diagnóstico visível).

    `materiality` é um canal lateral opcional `{news_key: P(material)}` que o `filter_new_alerts`
    usa para servir o tecto diário por importância em vez de por ordem de chegada. Mesmo padrão
    do `event_times`: não muda a forma dos tuplos que atravessam o runner.
    """
    n = cfg.get("news", {})
    if not n.get("enabled", False):
        return []
    from investigator import config
    from investigator.explanation_engine.explainer import explain_news_impact
    from investigator.historical_kb.knowledge_base import HistoricalKB
    from investigator.live_kb import merged_precedents
    from investigator.news_fetcher.relevance import is_relevant

    if not config.FINNHUB_API_KEY:
        print("[noticias] FINNHUB_API_KEY em falta — a saltar o scan de noticias.")
        return []
    horizon = int(n.get("horizon", 5))
    top_k = int(n.get("top_k", 3))
    min_sim = float(n.get("min_similarity", 0.45))
    half_life = float(n.get("recency_half_life_days", 365))
    max_prec_age = n.get("max_precedent_age_days")
    max_prec_age = int(max_prec_age) if max_prec_age is not None else None

    # Orçamento global de alertas por dia. Quando está definido, o score da triagem deixa de
    # ser porta e passa a ser critério de ORDENAÇÃO — ver a nota no ponto de decisão.
    orcamento = n.get("daily_budget")
    orcamento = int(orcamento) if orcamento is not None else None

    # Triagem aprendida (off por defeito): só ativa com min_materiality definido E modelo
    # presente. Sem modelo, avisa e segue com o comportamento de sempre.
    gate = n.get("min_materiality")
    bundle = None
    if gate is not None:
        from investigator.triage.infer import load_context_bundle

        bundle = load_context_bundle()
        if bundle is None:
            print("[triagem] models/triage_context_lr.joblib em falta — gate ignorado.")
        else:
            gate = float(gate)

    # KB + embedder decididos UMA vez (semântico MiniLM-ONNX com fail-open para a amostra;
    # em Actions o modelo vem da cache do workflow, senão desce ~23 MB na primeira corrida).
    # A KB VIVA (casos recentes maturados neste próprio runner) entra em primeiro na fusão:
    # "timeline matters" — a idade desempata a favor do recente, o cosseno decide o tema.
    from investigator.main import product_retrieval

    kb_path, embedder = product_retrieval(auto_download=True)
    kbs = []
    if _LIVE_KB.exists():
        try:
            kb_viva = HistoricalKB.load(_LIVE_KB)
            if len(kb_viva):
                kbs.append(kb_viva)
                print(f"[kb-viva] {len(kb_viva)} caso(s) recente(s) em uso.")
        except Exception as exc:  # noqa: BLE001
            print(f"[kb-viva] ilegível (ignorada): {type(exc).__name__}: {sem_segredos(exc)}")
    # Base reconstruída do último ano (2025-08 em diante), em formato compacto. É a que dá
    # volume real de casos comparáveis: 38 214 contra os ~2 000 da curada.
    #
    # ⚠️ TEM de ser o formato compacto, e o número que o justifica está medido: a mesma base
    # em JSONL custa **655 MB de RAM** e o contentor tem 512 MB. Em float32, com a matriz
    # mapeada do disco, são **25 MB** e carrega em 0,44 s em vez de 9. Carregá-la em JSONL
    # mataria o worker com falta de memória.
    if _BACKFILL_META.exists() and _BACKFILL_VEC.exists():
        try:
            kb_ano = HistoricalKB.load_compact(_BACKFILL_META, _BACKFILL_VEC)
            if len(kb_ano):
                kbs.append(kb_ano)
                print(f"[kb-ano] {len(kb_ano)} caso(s) do último ano em uso.")
        except Exception as exc:  # noqa: BLE001 — fail-open: sem ela o produto responde na mesma
            print(f"[kb-ano] indisponível (ignorada): {type(exc).__name__}: {sem_segredos(exc)}")
    kbs.append(HistoricalKB.load(kb_path))

    end = date.today().isoformat()
    start = (date.today() - timedelta(days=7)).isoformat()
    alerts: list[tuple[str, str]] = []
    hoje_iso = date.today().isoformat()

    def _gate(ticker: str, stage: str, detail: str = "") -> None:
        """Regista a etapa do funil onde este ticker parou (fail-open, nunca trava o scan)."""
        if gate_log is None:
            return
        try:
            from investigator.gate_log import GateRecord

            gate_log.append(GateRecord(date=hoje_iso, ticker=ticker, stage=stage, detail=detail))
        except Exception:  # noqa: BLE001
            pass

    # UMA busca de precos por empresa por varrimento, partilhada entre o registo das
    # candidatas e a triagem da escolhida. Duas buscas separadas esgotam o limite de ritmo
    # do yfinance e a serie volta truncada, o que apaga a pontuacao em silencio.
    precos_ciclo: dict = {}
    for ticker in n.get("tickers", []):
        try:
            items = _noticias_de_todas_as_fontes(ticker, start, end, n)
            # Filtro de relevância ANTES de escolher: mata as manchetes mal etiquetadas do
            # Finnhub (lei/escritórios, resumos "S&P500 movers"…) que sujavam o canal.
            relevantes = [i for i in items if is_relevant(i.headline, ticker)]
            if items and not relevantes:
                print(f"[noticias {ticker}] {len(items)} manchete(s), nenhuma relevante "
                      "(mal etiquetadas/boilerplate) — sem alerta.")
            if not relevantes:
                _gate(ticker, "none_relevant" if items else "no_news",
                      f"{len(items)} manchete(s) brutas")
                continue
            # KB viva: toda a manchete relevante é candidata a precedente futuro (captura
            # fail-open; matura dias depois, quando o impacto for observável).
            _capture_live_safe(relevantes, embedder)
            latest = max(relevantes, key=lambda it: it.date)  # a mais recente RELEVANTE
            max_age = int(n.get("max_age_days", 2))
            # R1: o registo passa a receber a população real de candidatas, e não só a que
            # sobrevive às portas. A `latest` é registada mais abaixo, na porta onde acabar.
            close_ticker = None
            if bundle is not None:
                try:
                    close_ticker = _hist_cached(ticker, precos_ciclo)["Close"]
                except Exception as exc:  # noqa: BLE001
                    print(f"[precos {ticker}] sem serie para triagem (ignorado): "
                          f"{type(exc).__name__}: {sem_segredos(exc)}")
            _registar_candidatas_safe(relevantes, latest, ticker, bundle, gate,
                                      max_age, date.today(), close=close_ticker)
            if not news_is_fresh(latest.date, date.today(), max_age):
                print(f"[noticias {ticker}] mais recente é de {latest.date} (>{max_age} dias) "
                      "— sem alerta (anti-repetição).")
                _gate(ticker, "stale", f"mais recente {latest.date} > {max_age}d")
                _log_decision_safe(latest.date, ticker, latest.headline, None, None,
                                   kept=False, stage="stale")
                continue
            precedents = merged_precedents(
                latest.headline, kbs, embedder, top_k=top_k, today=date.today(),
                half_life_days=half_life, max_age_days=max_prec_age,
            )
            # O movimento de hoje, para o alerta poder dizer o que a acção está a fazer. Sem
            # isto o utilizador lia sobre manchetes passadas e tinha de ir a outro lado buscar
            # a única coisa que lhe permitia julgar se aquilo importava. Fail-open: sem preço,
            # o alerta fica exactamente como era.
            movimento, nota_mov = _movimento_de_hoje(ticker)
            text = explain_news_impact(
                ticker, latest.headline, precedents, horizon=horizon,
                date=latest.date, today=date.today().isoformat(),
                move=movimento, move_note=nota_mov,
                source=latest.source, url=latest.url,
            )
            if not precedents_are_strong(precedents, min_sim):
                best = max((s for _, s in precedents), default=0.0)
                print(f"[noticias {ticker}] melhor precedente sim {best:.2f} < {min_sim:.2f} "
                      "— evidência fraca demais, sem alerta.")
                _gate(ticker, "weak_precedent", f"melhor sim {best:.2f} < {min_sim:.2f}")
                _log_decision_safe(latest.date, ticker, latest.headline, None, None,
                                   kept=False, stage="weak_precedent")
                continue
            if bundle is not None:
                from investigator.triage.infer import score_latest_with_snapshot

                scored_result = (
                    score_latest_with_snapshot(
                        bundle, close_ticker, latest.headline, ticker
                    ) if close_ticker is not None else None
                )
                scored = scored_result[0] if scored_result is not None else None
                feature_snapshot = scored_result[1] if scored_result is not None else None
                if scored is not None:
                    print(f"[triagem {ticker}] P(anormal)={scored[0]:.0%} "
                          f"(gate {gate:.0%})")
                # ⚠️ Com orçamento ligado, a triagem DEIXA DE VETAR e passa só a ordenar.
                # Razão medida (`evaluation_gate_selectivity.md`): dentro de uma empresa o
                # score quase não varia, logo um limiar sobre ele selecciona empresas e não
                # notícias — em 84% das decisões o resultado estava determinado pela empresa
                # antes de se ler a manchete, e cinco das doze não conseguiam alertar nunca.
                # O score continua a ser calculado, registado e mostrado: tem informação para
                # ORDENAR entre empresas, que é o uso que a medição sustenta.
                gated = apply_materiality(text, scored, gate)
                so_ordena = orcamento is not None
                _log_decision_safe(latest.date, ticker, latest.headline, scored, gate,
                                   kept=so_ordena or gated is not None,
                                   feature_snapshot=feature_snapshot,
                                   model_info=bundle.get("_model_info"),
                                   stage=("sobreviveu" if (so_ordena or gated is not None)
                                          else "triage_suppressed"))
                if gated is None and not so_ordena:
                    print(f"[triagem {ticker}] alerta de noticia suprimido pelo gate.")
                    p_str = f"P={scored[0]:.2f} < {gate:.2f}" if scored is not None else "sem P"
                    _gate(ticker, "triage_suppressed", p_str)
                    continue
                if gated is not None:
                    text = gated
            else:
                _log_decision_safe(latest.date, ticker, latest.headline,
                                   None, None, kept=True, stage="sobreviveu")
            alerts.append((ticker, text))
            # Canal lateral de instrumentação (mesmo padrão do `cache` dos scans de mercado):
            # guarda a HORA DE PUBLICAÇÃO da manchete que originou este alerta, indexada pela
            # mesma chave de dedup que o histórico usa. Permite medir publicação → entrega
            # sem alterar a forma dos tuplos (ticker, texto) que atravessam todo o runner.
            if event_times is not None and latest.published_at:
                event_times[news_key(ticker, text)] = latest.published_at
            # P(material) da triagem, para o tecto diário poder servir por importância. Só
            # existe quando o gate está ligado; sem ele o dicionário fica vazio e a ordem de
            # chegada mantém-se, que é o comportamento de sempre.
            if materiality is not None and bundle is not None and scored is not None:
                materiality[news_key(ticker, text)] = float(scored[0])
            # Manchete original, para a deteção de "mesma história noutras palavras". Tem de
            # ser a manchete e não o alerta: o alerta é quase todo template.
            if headlines is not None:
                headlines[news_key(ticker, text)] = latest.headline
            _gate(ticker, "alerted", latest.headline[:80])
        except Exception as exc:  # noqa: BLE001
            print(f"[saltar noticias {ticker}] {type(exc).__name__}: {sem_segredos(exc)}")
            _gate(ticker, "error", f"{type(exc).__name__}: {sem_segredos(exc)}"[:120])
    return alerts


def _capture_live_safe(items: list, embedder) -> None:
    """Captura manchetes relevantes para a KB viva (pendentes de maturação). Fail-open.

    Só captura com o embedder SEMÂNTICO (guarda R1: embeddings hashing 64-d misturados com
    a KB 384-d dariam vizinhos errados). O summary do Finnhub entra SÓ no embedding, nunca
    é persistido (governança §5.4).
    """
    try:
        if not getattr(embedder, "semantic", False):
            return
        from investigator.live_kb import (
            PendingNews,
            add_pending,
            embed_text,
            load_pending,
            save_pending,
        )

        existentes = load_pending(_LIVE_PENDING)
        chaves = {e.key for e in existentes}
        novos_items = [i for i in items if news_key(i.ticker, i.headline) not in chaves]
        if not novos_items:
            return
        textos = [embed_text(i.headline, getattr(i, "summary", "")) for i in novos_items]
        vetores = embedder.encode(textos)
        novos = [
            PendingNews(date=i.date, ticker=i.ticker, headline=i.headline,
                        key=news_key(i.ticker, i.headline),
                        embedding=[round(float(x), 5) for x in vec])
            for i, vec in zip(novos_items, vetores, strict=True)
        ]
        save_pending(add_pending(existentes, novos), _LIVE_PENDING)
        print(f"[kb-viva] +{len(novos)} pendente(s) capturado(s).")
    except Exception as exc:  # noqa: BLE001
        print(f"[kb-viva] captura falhou (ignorada): {type(exc).__name__}: {sem_segredos(exc)}")


def _mature_live_safe(today: date | None = None) -> None:
    """Matura pendentes cujo impacto já é observável e move-os para a KB viva. Fail-open."""
    try:
        from investigator.live_kb import append_records, load_pending, mature_ready, save_pending
        from investigator.market_data.prices import load_close_series

        today = today or date.today()
        pending = load_pending(_LIVE_PENDING)
        prontos = [e for e in pending
                   if (today - date.fromisoformat(e.date)).days >= 8]
        if not prontos:
            return
        tickers = sorted({e.ticker for e in prontos})
        start = (min(date.fromisoformat(e.date) for e in prontos)
                 - timedelta(days=5)).isoformat()
        closes = load_close_series(tickers, start, (today + timedelta(days=1)).isoformat())
        matured, still = mature_ready(pending, closes, today)
        if matured:
            append_records(matured, _LIVE_KB)
            save_pending(still, _LIVE_PENDING)
            print(f"[kb-viva] {len(matured)} caso(s) maturado(s) → live_kb.jsonl "
                  f"({len(still)} pendente(s)).")
    except Exception as exc:  # noqa: BLE001
        print(f"[kb-viva] maturação falhou (ignorada): {type(exc).__name__}: {sem_segredos(exc)}")


def is_us_market_session(now_utc) -> bool:
    """Puro: estamos dentro da sessão US (com folga)? Seg-sex, 13:00–21:30 UTC.

    Fora da sessão, a cotação `c` do Finnhub é o ÚLTIMO negócio (ex.: o fecho de sexta) —
    avaliar isso ao sábado re-alertaria o movimento de ontem como se fosse "em curso".
    A janela cobre verão e inverno (abertura 13:30/14:30, fecho 20:00/21:00 UTC).
    """
    if now_utc.weekday() >= 5:
        return False
    minutos = now_utc.hour * 60 + now_utc.minute
    return 13 * 60 <= minutos <= 21 * 60 + 30


def collect_intraday_results(cfg: dict, cache: dict | None = None) -> list[tuple[str, object]]:
    """Avalia o movimento DE HOJE em curso (cotação Finnhub) vs a norma diária, por ticker.

    Antes só corria no modo --watch (VM); desde 2026-07-13 corre TAMBÉM nas corridas
    agendadas (Actions, de 30 em 30 min) — é o caminho de mercado que NÃO depende do
    yfinance: a cotação vem do Finnhub (autenticado, fiável) e a norma vem do histórico
    diário, que NÃO precisa da barra de hoje (só de dias completos). Auto-protege-se:
    fora da sessão US, sem chave ou desligado → []. Devolve TODOS os tickers avaliados
    (não só anomalias) — o resumo diário também se serve daqui quando o fecho está cego.
    """
    from datetime import UTC, datetime

    m = cfg.get("market", {})
    intra = (m.get("intraday") or {})
    if not (m.get("enabled", False) and intra.get("enabled", False)):
        return []
    if not is_us_market_session(datetime.now(UTC)):
        return []  # fora da sessão, a cotação é estagnada — nada "em curso" a avaliar
    from investigator import config
    from investigator.anomaly_detector.detector import detect_intraday
    from investigator.market_data.prices import log_returns
    from investigator.news_fetcher.fetcher import fetch_finnhub_quote

    if not config.FINNHUB_API_KEY:
        return []
    cache = {} if cache is None else cache
    window = int(m.get("window", 20))
    threshold = float(intra.get("threshold", m.get("threshold", 3.0)))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            atual, fecho_anterior = fetch_finnhub_quote(ticker)
            running = atual / fecho_anterior - 1.0
            close = _hist_cached(ticker, cache)["Close"]
            # A norma usa só dias COMPLETOS: se a última barra é a de hoje (parcial,
            # durante a sessão), sai da série antes de calcular retornos.
            if close.index[-1].date() >= date.today():
                close = close.iloc[:-1]
            returns = log_returns(close)
            results.append(
                (ticker, detect_intraday(running, returns, window=window, threshold=threshold))
            )
        except Exception as exc:  # noqa: BLE001  (um ticker a falhar não pára a varredura)
            print(f"[intradiario {ticker}] {type(exc).__name__}: {sem_segredos(exc)}")
    return results


def build_intraday_alerts(results: list[tuple[str, object]]) -> list[tuple[str, str]]:
    """Puro: [(ticker, texto)] só das anomalias intradiárias. Dedup pelo `alerted_market`
    de sempre (1 alerta de mercado/ticker/dia — o fecho não repete o intradiário)."""
    from investigator.explanation_engine.explainer import explain_intraday

    return [(t, explain_intraday(t, r)) for t, r in results if r.is_anomaly]


def _attach_sector_safe(ticker: str, alert_text: str, moves: dict[str, float]) -> str:
    """Anexa a linha 'Sector check' a um alerta de mercado (fail-open: sem dados de pares
    ou com erro, o alerta segue intacto — a linha é contexto, nunca condição)."""
    try:
        from investigator.explanation_engine.explainer import sector_context_line

        line = sector_context_line(ticker, moves)
        return f"{alert_text}\n{line}" if line else alert_text
    except Exception as exc:  # noqa: BLE001
        print(
            f"[setor {ticker}] falhou (alerta segue sem linha): "
            f"{type(exc).__name__}: {sem_segredos(exc)}"
        )
        return alert_text


def _attach_decomposition_safe(ticker: str, alert_text: str, cache: dict,
                               out: dict | None = None) -> str:
    """Anexa a repartição mercado / setor / específico da empresa a um alerta de mercado.

    É a linha que responde à primeira pergunta de qualquer investidor perante um número
    vermelho — *"é a minha empresa ou é o mercado todo?"*. Ex. real (2026-07-28):
    `AMD -8.50% today = +0.61% market · -3.60% sector · -5.51% company-specific.`

    Reutiliza a cache de preços do ciclo, por isso o SPY e cada ETF de setor são buscados
    UMA vez por corrida, não uma vez por ticker.

    Fail-open total: sem índice, sem ETF, séries desalinhadas ou erro de rede, o alerta segue
    intacto. A decomposição é contexto — nunca condição para alertar.
    """
    try:
        import numpy as np
        import pandas as pd

        from investigator.correlation_engine.decomposition import decompose_move, describe
        from investigator.news_fetcher.relevance import MARKET_INDEX, sector_etf

        etf = sector_etf(ticker)
        cols = {ticker: _hist_cached(ticker, cache)["Close"],
                MARKET_INDEX: _hist_cached(MARKET_INDEX, cache)["Close"]}
        if etf:
            cols[etf] = _hist_cached(etf, cache)["Close"]

        frame = pd.DataFrame(cols)
        frame.index = pd.to_datetime(frame.index)
        if getattr(frame.index, "tz", None) is not None:
            frame.index = frame.index.tz_localize(None)
        frame = frame.dropna()
        rets = np.log(frame / frame.shift(1)).dropna()
        if len(rets) < 15:
            return alert_text

        d = decompose_move(
            rets[ticker].to_numpy(),
            rets[MARKET_INDEX].to_numpy(),
            rets[etf].to_numpy() if etf else None,
        )
        if out is not None:  # canal lateral: o narrador precisa do objeto, não do texto
            out[ticker] = d
        return f"{alert_text}\n{describe(d, ticker)}"
    except Exception as exc:  # noqa: BLE001
        print(f"[decomposicao {ticker}] falhou (alerta segue sem linha): "
              f"{type(exc).__name__}: {sem_segredos(exc)}")
        return alert_text


def _investigate_anomaly_safe(ticker: str, alert_text: str, observado_em: str = "") -> str:
    """Investigação cruzada: procura a notícia relevante mais recente (48h) que possa
    explicar a anomalia e anexa-a ao alerta; sem notícia, di-lo honestamente.

    Fail-open: sem FINNHUB_API_KEY ou com erro de rede, devolve o alerta original intacto.
    """
    try:
        from investigator import config
        from investigator.explanation_engine.explainer import attach_news_context
        from investigator.news_fetcher.fetcher import fetch_finnhub_company_news
        from investigator.news_fetcher.relevance import is_relevant

        if not config.FINNHUB_API_KEY:
            return alert_text
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=2)).isoformat()
        items = fetch_finnhub_company_news(ticker, start, end)
        relevantes = [i for i in items if is_relevant(i.headline, ticker)]
        # ⚠️ Guarda temporal (2026-08-10). Antes escolhia-se a manchete mais recente da janela
        # sem verificar se ela é ANTERIOR ao movimento que diz explicar. Num alerta
        # intradiário — "-1,6% até agora" — isso podia oferecer como "possible explanation"
        # uma notícia publicada DEPOIS da leitura, o que inverte a seta causal. A linha é
        # apresentada como hipótese e não como causa provada, mas oferecer o futuro como
        # explicação do passado é errado mesmo com ressalva.
        #
        # `published_at` é o instante exacto (ISO 8601 UTC) e existe desde 2026-07-29; quando
        # falta, cai-se para a data ao dia, que é o que havia antes. Notícias sem instante
        # e do próprio dia continuam elegíveis — não se pode provar que vieram depois.
        if observado_em:
            relevantes = [i for i in relevantes
                          if not i.published_at or i.published_at <= observado_em]
        if relevantes:
            recente = max(relevantes, key=lambda it: (it.published_at or "", it.date))
            return attach_news_context(alert_text, recente.headline,
                                       news_date=recente.date, today=end)
        return attach_news_context(alert_text, None)
    except Exception as exc:  # noqa: BLE001
        print(f"[investigar {ticker}] falhou (alerta segue sem contexto): "
              f"{type(exc).__name__}: {sem_segredos(exc)}")
        return alert_text


def _record_history_safe(alerts: list[tuple[str, str]], today: str,
                         path: str | Path = _HISTORY,
                         *,
                         event_times: dict[str, str] | None = None,
                         detected_at: str = "",
                         sent_at: str = "",
                         price_sources: dict[str, str] | None = None,
                         message_ids: dict[int, int] | None = None,
                         chat_id: str = "") -> None:
    """Regista os alertas REALMENTE enviados no histórico partilhado — a app lê este ficheiro
    em vez de recalcular, garantindo que mostra exatamente o que o Telegram recebeu.

    Os carimbos são opcionais e só são gravados quando existem: sem eles o comportamento é
    exatamente o de antes (entradas idênticas às antigas). `event_times` e `price_sources`
    vêm indexados pela chave de dedup / pelo ticker, preenchidos pelos scans.

    Fail-open (mesmo padrão de `_log_decision_safe`): um erro aqui nunca pode impedir o envio
    real ao Telegram nem derrubar o runner.
    """
    try:
        from investigator.alerts_history import (
            HistoryEntry,
            append_and_trim,
            classify_kind,
            load_jsonl,
            save_jsonl,
        )
        from investigator.explanation_engine.explainer import plain_text

        new = []
        for i, (ticker, text) in enumerate(alerts):
            kind = classify_kind(text)
            key = news_key(ticker, text) if kind == "news" else ""
            new.append(HistoryEntry(
                date=today, ticker=ticker, kind=kind, text=plain_text(text),
                key=key,
                event_at=(event_times or {}).get(key, ""),
                detected_at=detected_at,
                sent_at=sent_at,
                price_source=(price_sources or {}).get(ticker, ""),
                # ⚠️ O HTML EXATO, além da versão sem tags. O `plain_text` tira o negrito e
                # desfaz as entidades; reenviar isso numa edição perderia a formatação e, numa
                # manchete com «<» ou «&», produziria HTML que o Telegram rejeita. O `text`
                # continua a ser o que o painel lê — nada muda para ele.
                text_html=text,
                message_id=(message_ids or {}).get(i, 0),
                chat_id=chat_id if (message_ids or {}).get(i) else "",
            ))
        save_jsonl(append_and_trim(load_jsonl(path), new), path)
    except Exception as exc:  # noqa: BLE001
        print(f"[historico] registo falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def _market_evidence(ticker: str, res, decomp, today: str):
    """AnomalyResult (+ decomposição opcional) → AlertEvidence. Puro; None se faltar o básico."""
    from investigator.narrator.evidence import AlertEvidence, fmt_num, fmt_pct

    try:
        z_score = None if res.reported_z is None else fmt_num(res.reported_z)
        kw = dict(
            ticker=ticker, date=today, kind="market",
            move_pct=fmt_pct(res.last_return), z_score=z_score,
            threshold=fmt_num(res.threshold), window_days=int(res.window),
        )
        if decomp is not None:
            kw.update(
                market_pct=fmt_pct(decomp.market), sector_pct=fmt_pct(decomp.sector),
                company_pct=fmt_pct(decomp.idiosyncratic), driver=decomp.driver,
                decomposition_fallback=bool(decomp.fallback),
            )
        return AlertEvidence(**kw)
    except Exception:  # noqa: BLE001
        return None


def _narrate_safe(text: str, evidence, cfg: dict) -> str:
    """Antepõe ao alerta um parágrafo em linguagem simples, gerado pelo narrador ancorado.

    **Puramente ADITIVO, e essa é a decisão de desenho.** Se o narrador falhar, se a guarda
    de fidelidade rejeitar a resposta, ou se não houver chaves, o alerta segue EXATAMENTE
    como hoje — nunca se antepõe o texto-template, que só repetiria o que o corpo do alerta
    já diz. O narrador só pode acrescentar valor; nunca degradar o que já funciona.

    Fail-open total, como todo o resto do runner.
    """
    if evidence is None or not (cfg.get("narrator") or {}).get("enabled", False):
        return text
    try:
        from investigator.narrator.core import narrate

        r = narrate(evidence)
        if r.source == "template":  # sem LLM, ou guarda rejeitou → alerta inalterado
            if r.guarded:
                print(f"[narrador {evidence.ticker}] guarda rejeitou "
                      f"({'; '.join(r.violations[:2])[:80]}) — alerta segue sem parágrafo.")
            return text
        print(f"[narrador {evidence.ticker}] {r.source} em {r.latency_s:.2f}s")
        return f"{r.text}\n\n{text}"
    except Exception as exc:  # noqa: BLE001
        print(
            f"[narrador] falhou (alerta segue intacto): "
            f"{type(exc).__name__}: {sem_segredos(exc)}"
        )
        return text


def _write_snapshot_safe() -> None:
    """Reescreve o instantâneo pré-computado que o painel v4 lê.

    É o que torna a v4 possível em produção: a página deixa de fazer doze idas à rede antes da
    primeira pintura e passa a ler um ficheiro de ~4 KB. Medido: 4,92 s a construir contra
    0,011 s a ler.

    Corre no worker porque é aqui que o ciclo já paga o custo dos preços — construir o
    instantâneo no fim de um ciclo é quase de graça, e construí-lo no pedido do utilizador é
    exactamente o defeito que a v4 corrige.

    **Fail-open, e é obrigatório:** se isto rebentar, o ciclo de alertas continua. Um painel
    desactualizado é um inconveniente; um canal de alertas parado por causa do painel seria
    trocar o essencial pelo acessório. O ficheiro carrega o carimbo de tempo, e a v4 mostra a
    idade — portanto um instantâneo que pare de ser escrito **nota-se no ecrã** em vez de passar
    por actual.
    """
    try:
        from scripts.build_snapshot import DESTINO, construir

        snap = construir()
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        DESTINO.write_text(json.dumps(snap, indent=1), encoding="utf-8")
        print(f"[instantaneo] {len(snap['rows'])} tickers em {snap['build_seconds']:.1f}s")

        # E publica-o na branch de dados. No Heroku o web é OUTRO dyno, com outro disco: sem
        # este passo o ficheiro acima só existe aqui e o painel nunca o veria. Fail-open pela
        # mesma razão que o resto desta função.
        from investigator.history_publish import publish_blob

        msg = publish_blob(DESTINO, "dashboard_snapshot.json")
        if msg:
            print(msg)
    except Exception as exc:  # noqa: BLE001
        print(f"[instantaneo] falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def _reconcile_gates(records: list, suppressed: dict[str, tuple[str, str]]) -> None:
    """Puro: corrige o funil com o que foi suprimido DEPOIS da varredura.

    Sem isto, `stage="alerted"` significa "sobreviveu ao `scan_news`" e não "foi entregue", e o
    screener mostra **"Alert sent"** a um utilizador a quem não se enviou nada — na vista que
    existe precisamente para tornar o silêncio inspeccionável.

    Só reetiqueta registos que estejam em `alerted`: uma supressão pós-varredura não pode
    ressuscitar um ticker que já tinha morrido antes, e sobrescrever a etapa real apagaria a
    razão verdadeira pela qual ele saiu do funil.
    """
    if not suppressed:
        return
    for i, r in enumerate(records):
        if r.stage != "alerted":
            continue
        hit = suppressed.get(r.ticker)
        if hit:
            from dataclasses import replace

            records[i] = replace(r, stage=hit[0], detail=hit[1])


def _record_gates_safe(records: list, path: str | Path | None = None) -> None:
    """Persiste o funil de gates ao lado do histórico (mesma branch de dados, por isso é
    publicado pelos mesmos mecanismos). Fail-open: nunca pode travar o ciclo.

    Escreve SEMPRE que há registos — inclusive em dry-run e sem Telegram configurado: o
    funil descreve a DETEÇÃO, não a entrega, e é justamente nas corridas silenciosas
    (nenhum alerta enviado) que interessa saber o que foi filtrado e porquê."""
    if not records:
        return
    try:
        from investigator.gate_log import append_jsonl

        append_jsonl(records, path or _GATE_LOG)
    except Exception as exc:  # noqa: BLE001
        print(f"[funil] registo falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def _seed_from_branch_safe(path: str | Path, filename: str) -> None:
    """Semeia um ficheiro de dados a partir da branch, uma vez, no arranque.

    ⚠️ **Sem isto, publicar destruiria histórico.** O disco do dyno é efémero: a cada reinício o
    ficheiro local recomeça vazio, e publicá-lo escreveria por cima da cópia da branch com
    apenas os registos desde o último arranque. Semear primeiro e publicar depois preserva a
    série; é o mesmo raciocínio do `seed_state_from_shared_history`, aplicado ao ficheiro.

    Só semeia quando o local está **vazio ou ausente** — nunca sobrescreve trabalho local.
    """
    import os
    import urllib.request

    p = Path(path)
    try:
        if p.exists() and p.stat().st_size > 0:
            return
        repo = os.environ.get("INVESTIGATOR_HISTORY_REPO", "HS2000PT/DIMEIA")
        branch = os.environ.get("INVESTIGATOR_HISTORY_BRANCH", "alerts-history")
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/{filename}"
        with urllib.request.urlopen(url, timeout=15) as r:  # noqa: S310
            texto = r.read().decode("utf-8", "replace")
        if texto.strip():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texto, encoding="utf-8")
            print(f"[semear] {filename}: {len(texto.splitlines())} linhas da branch")
    except Exception as exc:  # noqa: BLE001
        print(f"[semear] {filename} indisponível (ignorado): "
              f"{type(exc).__name__}: {sem_segredos(exc)}")


def _publish_data_safe(path: str | Path, filename: str) -> None:
    """Publica um ficheiro de dados na branch. Fail-open, como tudo neste caminho.

    ⚠️ Existe porque o raciocínio que o instantâneo já tinha escrito — *"no Heroku o web é OUTRO
    dyno, com outro disco"* — nunca foi aplicado a estes dois ficheiros. O `gate_log` era escrito
    só localmente (apesar de o docstring afirmar que era "publicado pelos mesmos mecanismos") e o
    `predictions_log` idem. Resultado medido a 2026-08-15: o `alerts_history` estava actual
    (2026-08-14) e **os dois estavam parados em 2026-08-09** — seis dias. O screener servia uma
    semana atrasada, e o registo de decisões que alimenta a pós-validação **deixou de crescer**.
    """
    try:
        from investigator.history_publish import publish_blob

        msg = publish_blob(path, filename)
        if msg:
            print(msg)
    except Exception as exc:  # noqa: BLE001
        print(f"[publicar {filename}] indisponível (ignorado): "
              f"{type(exc).__name__}: {sem_segredos(exc)}")


_ULTIMA_PUB: dict[str, float] = {}


def _publish_lento_safe(path: str | Path, filename: str, minutos: int = 30) -> None:
    """Publica um ficheiro GRANDE, mas no máximo de `minutos` em `minutos`.

    ⚠️ Existe porque a base de casos viva **parou de crescer** e a razão é de escala, não de
    esquecimento. Medido a 2026-08-15: `live_kb.jsonl` estava congelado em 2026-07-27 e
    `live_pending.jsonl` tinha 1785 entradas de Julho ainda por maturar — 19 dias, quando a
    maturação precisa de 8. O sistema captava casos a cada minuto e nenhum chegava a ser
    convertido em precedente utilizável, ou seja, **o ciclo de aprendizagem estava parado**.

    A causa é a mesma dos outros ficheiros (disco efémero, o web é outro dyno) mas a correcção
    não pode ser a mesma: estes dois pesam **16,6 MB e 11,9 MB**, e publicá-los a cada ciclo de
    60 s seriam dezenas de GB por dia de tráfego. Daí o estrangulamento por tempo.

    O que se perde com isto fica dito: até `minutos` de capturas, se o contentor reiniciar
    nesse intervalo. É uma perda pequena e recuperável — a manchete volta a ser captada na
    varredura seguinte enquanto continuar dentro da janela de frescura.
    """
    import time

    agora = time.monotonic()
    ultima = _ULTIMA_PUB.get(filename)
    if ultima is not None and (agora - ultima) < minutos * 60:
        return
    _ULTIMA_PUB[filename] = agora
    _publish_data_safe(path, filename)


def _push_history_safe(path: str | Path = _HISTORY) -> None:
    """Publica o histórico na branch `alerts-history` a partir de uma máquina própria (VM).

    Só ativo com INVESTIGATOR_HISTORY_GIT=1 e com o ficheiro dentro de um checkout git da
    branch de dados (ver docs/design/vm_watch.md). No Actions este passo é feito pelo próprio
    workflow — aqui é o equivalente para o modo --watch. Fail-open total.
    """
    import os

    if os.environ.get("INVESTIGATOR_HISTORY_GIT") != "1":
        return
    import subprocess

    d = Path(path).resolve().parent
    try:
        def git(*a: str) -> None:
            subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, timeout=60)

        status = subprocess.run(["git", "status", "--porcelain"], cwd=d, check=True,
                                capture_output=True, text=True, timeout=30)
        if not status.stdout.strip():
            return
        git("add", Path(path).name)
        git("commit", "-m", "Alertas: atualização automática do histórico partilhado")
        git("pull", "--rebase")
        git("push")
        print("[historico] publicado na branch alerts-history.")
    except Exception as exc:  # noqa: BLE001
        print(f"[historico] push falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def _fetch_shared_history_safe(cfg: dict) -> list | None:
    """Histórico partilhado — a memória comum entre VM e Actions.

    ⚠️ Devolve `None` quando NÃO conseguiu ler, e `[]` quando leu e não havia nada. A distinção
    não é preciosismo: `[]` significa «hoje ainda não saiu nada» e autoriza gastar o orçamento;
    `None` significa «não sei o que já saiu» e não autoriza coisa nenhuma. Confundir os dois é
    exactamente o que fez sair vinte alertas num dia de orçamento cinco.
    """
    try:
        from investigator.alerts_history import fetch_remote

        url = (cfg.get("public", {}) or {}).get("history_url")
        if not url:
            return None
        return fetch_remote(str(url))
    except Exception:  # noqa: BLE001
        return None


def process_bot_commands(state: dict, bot_cfg: dict, *, dry_run: bool) -> None:
    """Fase B SEM servidor: processa em lote os comandos enviados ao bot desde a última corrida.

    Com o cron intradiário, quem escrever /watch TSLA recebe a resposta na corrida seguinte
    (≤30 min em horário de mercado). Não é instantâneo e dizemo-lo com honestidade — mas
    funciona sem nenhuma máquina do operador. (Para respostas imediatas: scripts/run_bot.py.)
    Fail-open: qualquer erro deixa o runner seguir; o offset fica no estado partilhado.
    """
    if not bot_cfg.get("enabled", False):
        return
    # ⚠️ O Telegram NÃO permite webhook e getUpdates ao mesmo tempo: com um webhook registado,
    # esta chamada devolve 409 em todos os ciclos. Quando o webhook está ligado é ele que trata
    # dos comandos (`investigator/telegram_bot/webhook.py`), e este caminho cala-se.
    from investigator import config as _cfg

    if _cfg.TELEGRAM_WEBHOOK_ENABLED:
        print("[bot] webhook ativo — comandos tratados em /telegram/webhook, polling saltado.")
        return
    if dry_run:
        print("[bot] dry-run — comandos pendentes não são processados nem respondidos.")
        return
    try:
        from investigator import config
        from investigator.telegram_bot import store
        from investigator.telegram_bot.commands import handle_command
        from investigator.telegram_bot.interactive import extract_command, poll_updates
        from investigator.telegram_bot.sender import send_message

        if not config.TELEGRAM_BOT_TOKEN:
            print("[bot] sem TELEGRAM_BOT_TOKEN — comandos saltados.")
            return
        updates = poll_updates(config.TELEGRAM_BOT_TOKEN, state.get("bot_offset"), timeout_s=1)
        if not updates:
            return
        conn = store.connect(Path(bot_cfg.get("db", store.DEFAULT_DB)))
        for upd in updates:
            state["bot_offset"] = int(upd.get("update_id", 0)) + 1
            par = extract_command(upd)
            if par is None:
                continue
            chat_id, text = par
            reply = handle_command(text, chat_id, conn)
            send_message(reply, chat_id=chat_id)
        print(f"[bot] {len(updates)} update(s) processado(s) em lote.")
    except Exception as exc:  # noqa: BLE001  (os comandos nunca podem partir o runner)
        print(
            f"[bot] processamento de comandos falhou (ignorado): "
            f"{type(exc).__name__}: {sem_segredos(exc)}"
        )


def _fanout_safe(alerts: list[tuple[str, str]], bot_cfg: dict, *, dry_run: bool) -> None:
    """Fase B (off por defeito): distribui cada alerta pelos subscritores do ticker.

    Fail-open total: sem `bot.enabled`, sem base de subscritores ou com qualquer erro, o
    runner comporta-se exatamente como sempre (só canal). Nunca levanta exceção.
    """
    if not bot_cfg.get("enabled", False):
        return
    try:
        from investigator.telegram_bot import store

        db = Path(bot_cfg.get("db", store.DEFAULT_DB))
        if not db.exists():
            print("[bot] sem base de subscritores (corre scripts/run_bot.py) — fan-out saltado.")
            return
        conn = store.connect(db)
        enviados = 0
        for ticker, text in alerts:
            for chat in store.subscribers_of(conn, ticker):
                if dry_run:
                    print(f"[bot dry-run] enviaria {ticker} a {chat}")
                    continue
                from investigator.telegram_bot.sender import send_message

                send_message(text, chat_id=chat)
                enviados += 1
        if not dry_run:
            print(f"[bot] fan-out: {enviados} envio(s) a subscritores.")
    except Exception as exc:  # noqa: BLE001  (o fan-out nunca pode partir o runner)
        print(f"[bot] fan-out falhou (ignorado): {type(exc).__name__}: {sem_segredos(exc)}")


def run_cycle(cfg: dict, *, dry_run: bool, watch: bool = False) -> int:
    """Um ciclo completo de varredura (comandos do bot → scans → filtros → envio → registo).

    Reutilizado pelo modo agendado (1 ciclo por invocação — Actions) e pelo modo --watch
    (loop contínuo na VM/PC). A deteção intradiária corre em AMBOS desde 2026-07-13
    (auto-protegida por sessão/chave/config); `watch` fica na assinatura por
    compatibilidade e para diferenciações futuras. Devolve o nº de mensagens da corrida.
    """
    _ = watch  # ver docstring
    from datetime import UTC, datetime

    bot_cfg = cfg.get("bot", {}) or {}
    state = load_state()
    process_bot_commands(state, bot_cfg, dry_run=dry_run)

    # Memória partilhada entre produtores (VM + Actions): o que QUALQUER um já enviou hoje
    # não se repete — sem isto, dois produtores duplicariam alertas no canal.
    partilhado = _fetch_shared_history_safe(cfg)
    seed_state_from_shared_history(state, partilhado or [], state["date"])
    # ⚠️ Memória do dia: ou o disco local já a tem, ou o histórico partilhado foi lido. Se
    # nenhuma das duas se verifica, este processo não sabe quantos alertas já saíram hoje — e um
    # orçamento gasto por quem não sabe o que já gastou não é um orçamento.
    state["memoria_do_dia"] = bool(state["news_count"]) or partilhado is not None
    if not state["memoria_do_dia"]:
        print("[orçamento] sem memória do dia (disco vazio e histórico partilhado ilegível) — "
              "nenhum alerta de notícia sai neste ciclo.")

    # Semear os ficheiros de série a partir da branch, se o disco local estiver vazio. No
    # contentor isso acontece a cada reinício, e publicar sem semear apagaria a série toda.
    # Não faz nada quando o ficheiro já existe — logo custa uma ida à rede por arranque.
    _seed_from_branch_safe(_GATE_LOG, "gate_log.jsonl")
    _seed_from_branch_safe(_PRED_LOG, "predictions_log.jsonl")
    # ⚠️ E estes dois são os que mais importam: sem semear, o contentor arranca sem base de
    # casos e sem pendentes, e o ciclo de aprendizagem recomeça do zero a cada reinício.
    _seed_from_branch_safe(_LIVE_KB, "live_kb.jsonl")
    _seed_from_branch_safe(_LIVE_PENDING, "live_pending.jsonl")

    # KB viva: maturar pendentes cujo impacto (+5d) já é observável — ANTES dos scans,
    # para os casos recém-maturados contarem já como precedentes nesta corrida.
    _mature_live_safe()

    # Proveniência das fontes de preço: limpar por ciclo para o registo descrever ESTE ciclo
    # (no modo --watch o processo é longo e o registo anterior contaminaria a medição).
    from investigator.market_data.prices import price_source_log, reset_price_source_log

    reset_price_source_log()

    cache: dict[str, object] = {}  # 1 busca de preços por ticker por ciclo (fecho+intradiário)
    market_results = collect_market_results(cfg, cache)
    tickers_anomalos = [t for t, r in market_results if r.is_anomaly]
    market_alerts = list(zip(tickers_anomalos, build_market_alerts(market_results),
                             strict=True))
    # Deteção intradiária (Actions E --watch desde 2026-07-13): o movimento EM CURSO via
    # cotação Finnhub — o caminho de mercado que não depende do yfinance. O dedup do
    # filter_new_alerts (1 alerta de mercado/ticker/dia) evita que o fecho repita o
    # intradiário do mesmo dia.
    intra_results = collect_intraday_results(cfg, cache)
    market_alerts.extend(build_intraday_alerts(intra_results))
    # Contexto setorial ("a NVIDIA mexe com o setor"): usa SÓ os movimentos já buscados
    # nesta varredura — fecho de hoje quando existe, senão o movimento em curso.
    moves = {t: r.last_return for t, r in market_results}
    for t, r in intra_results:
        moves.setdefault(t, r.last_return)
    market_alerts = [(t, _attach_sector_safe(t, text, moves)) for t, text in market_alerts]
    # Repartição mercado/setor/empresa — a linha que distingue "o mercado caiu" de "a TUA
    # empresa caiu". Usa a mesma cache do ciclo (SPY e ETFs buscados 1×).
    decomps: dict[str, object] = {}
    market_alerts = [(t, _attach_decomposition_safe(t, text, cache, decomps))
                     for t, text in market_alerts]
    # Investigação cruzada (anomalia → notícia): o comportamento do trader profissional —
    # vê o movimento, procura a causa. Fail-open: sem rede/chave, o alerta segue sem contexto.
    # `utc_stamp()` é o instante em que ESTE ciclo observou o movimento; é ele que define o
    # que conta como "anterior" na guarda temporal de `_investigate_anomaly_safe`.
    agora_iso = utc_stamp()
    market_alerts = [(t, _investigate_anomaly_safe(t, text, agora_iso))
                     for t, text in market_alerts]
    # Narrador ancorado: parágrafo em linguagem simples ANTES dos factos estruturados.
    # Aditivo — sem chaves, com o LLM em baixo ou com a guarda a rejeitar, o alerta segue
    # exatamente como hoje (ver `_narrate_safe`).
    if (cfg.get("narrator") or {}).get("enabled", False):
        anomalias = {t: r for t, r in market_results if r.is_anomaly}
        for t, r in intra_results:
            anomalias.setdefault(t, r)
        hoje = date.today().isoformat()
        market_alerts = [
            (t, _narrate_safe(text, _market_evidence(t, anomalias[t], decomps.get(t), hoje), cfg)
             if t in anomalias else text)
            for t, text in market_alerts
        ]
    max_per = int((cfg.get("news") or {}).get("max_per_ticker_per_day", 2))
    # Instrumentação de latência: o scan de notícias devolve, em canal lateral, a hora de
    # publicação de cada manchete alertada (ver `scan_news`). `detected_at` é carimbado
    # AQUI — fim da deteção, antes de qualquer envio.
    event_times: dict[str, str] = {}
    # Funil de gates: onde é que cada ticker parou nesta varredura. Sem isto não há resposta
    # para "a AAPL teve 135 manchetes relevantes e 0 alertas — qual gate a matou?", porque o
    # registo de decisões só é escrito depois dos gates de frescura e similaridade.
    gate_records: list = []
    # P(material) por manchete: o tecto diário serve por importância, não por ordem de chegada.
    materiality: dict[str, float] = {}
    # Manchete original de cada alerta, para apanhar a mesma história escrita por outro meio.
    headlines: dict[str, str] = {}
    # Piso escalonado do tecto diário (ver `filter_new_alerts`). Lista vazia/ausente = sem
    # escalonamento, comportamento de sempre.
    escada = [float(x) for x in ((cfg.get("news") or {}).get("materiality_ladder") or [])]
    # Supressões pós-varredura, para o funil poder ser reconciliado (ver `filter_new_alerts`).
    pos_scan: dict[str, tuple[str, str]] = {}
    # Orçamento global do dia (ver `filter_new_alerts`). None = comportamento de sempre.
    orcamento_dia = (cfg.get("news") or {}).get("daily_budget")
    alerts = filter_new_alerts(
        market_alerts, scan_news(cfg, event_times, gate_records, materiality, headlines),
        state, max_per, materiality, headlines, escada, pos_scan,
        daily_budget=int(orcamento_dia) if orcamento_dia is not None else None,
    )
    detected_at = utc_stamp()
    _reconcile_gates(gate_records, pos_scan)
    _record_gates_safe(gate_records)
    # Estes dois vivem em disco EFÉMERO no contentor e o web é outro dyno: sem publicar, o
    # screener serve o que existia no último arranque e a pós-validação deixa de crescer.
    # (Medido a 2026-08-15: parados havia seis dias enquanto o histórico estava actual.)
    _publish_data_safe(_GATE_LOG, "gate_log.jsonl")
    _publish_data_safe(_PRED_LOG, "predictions_log.jsonl")
    # A base de casos viva é grande (dezenas de MB) e por isso vai a um ritmo mais lento. Sem
    # isto, o que o sistema aprende morre no reinício do contentor e nada matura.
    _publish_lento_safe(_LIVE_KB, "live_kb.jsonl")
    _publish_lento_safe(_LIVE_PENDING, "live_pending.jsonl")
    _write_snapshot_safe()

    threshold = float((cfg.get("market") or {}).get("threshold", 3.0))
    hora_utc = datetime.now(UTC).hour
    # Nota de ABERTURA (o par matinal do resumo): como a watchlist abriu vs o fecho de ontem,
    # a partir da cotação intradiária. 1×/dia na janela de abertura (14–15 UTC).
    opening = maybe_opening_note(state, intra_results, hora_utc)
    # Resumo de FECHO: preferir os resultados de fecho; quando o fecho está cego (fontes
    # diárias sem a barra de hoje), os resultados intradiários servem — às 21h+ UTC a
    # sessão já fechou e a cotação Finnhub É o fecho do dia.
    summary = maybe_daily_summary(state, market_results or intra_results, threshold, hora_utc)
    # Anotação dos desfechos: corre DEPOIS do resumo e antes de o estado ser gravado, para
    # que a marca de "já corri hoje" persista como as outras.
    maybe_anotar_desfechos(state, hora_utc, dry_run=dry_run)

    if not dry_run:
        save_state(state)  # persiste marcas do dia + offset do bot (cache no Actions)
    else:
        print("[estado] dry-run — estado não gravado (não interfere com a corrida real).")

    mensagens = alerts + [("MARKET", m) for m in (opening, summary) if m]
    if not mensagens:
        print("Sem alertas novos nesta corrida (nenhuma anomalia nova acima do limiar).")
        return 0

    from investigator import config

    can_send = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID) and not dry_run
    from investigator.explanation_engine.explainer import plain_text

    falhas = 0
    # ⚠️ Pelo ÍNDICE, e não por `id()` do texto: duas mensagens com o mesmo texto são o mesmo
    # objeto em Python (as cadeias são internadas), e um dicionário indexado por `id()` daria a
    # ambas a chave da primeira. `mensagens` é `alerts` seguido das notas de mercado, portanto
    # os primeiros `len(alerts)` elementos são exatamente os alertas.
    n_alertas = len(alerts)
    # ⚠️ A IDENTIDADE DA MENSAGEM, guardada no único momento em que existe. O Telegram não
    # oferece maneira de reencontrar uma mensagem pelo conteúdo: se o `message_id` não for
    # apanhado aqui, a mensagem fica inalcançável para sempre — não há como lhe acrescentar
    # depois o desfecho observado a +1, +3 e +5 sessões. Os 522 alertas anteriores a
    # 2026-09-01 são exatamente esse caso.
    ids_por_indice: dict[int, int] = {}
    for i, (_ticker, text) in enumerate(mensagens):
        print("-" * 60)
        print(plain_text(text))
        if can_send:
            from investigator.telegram_bot.sender import send_message

            # O teclado de feedback vai só nos ALERTAS, e não na nota de abertura nem no resumo
            # de fecho. É uma escolha de amostra e não de conveniência: a pergunta que a tese
            # faz é sobre alertas — decisões que as portas deixaram passar — e um resumo diário
            # não é uma decisão dessas. Misturá-los daria uma taxa de utilidade que não
            # responde a pergunta nenhuma.
            teclado = None
            chave = news_key(_ticker, text) if i < n_alertas else ""
            if chave:
                try:
                    from investigator.telegram_bot.feedback import teclado as _teclado

                    teclado = _teclado(chave)
                except Exception as exc:  # noqa: BLE001
                    # Um defeito na construção do teclado não pode impedir a ENTREGA: o alerta
                    # sem botões continua a ser um alerta; um alerta não enviado não é nada.
                    print(f"[feedback] teclado indisponível (o alerta segue): {exc}")
            # Um envio falhado (rede/Telegram intermitente) não pode abortar o ciclo nem
            # impedir as mensagens seguintes: o modo agendado (Actions) sairia com código
            # de erro e as restantes ficariam por entregar. Falha-suave e continua.
            try:
                resposta = send_message(text, reply_markup=teclado)
                try:
                    from investigator.telegram_bot.sender import message_id_de

                    mid = message_id_de(resposta)
                    if mid:
                        ids_por_indice[i] = mid
                except Exception as exc:  # noqa: BLE001
                    # Perder o identificador custa a anotação futura desta mensagem, e nada
                    # mais. Nunca pode custar a entrega, que já aconteceu.
                    print(f"[historico] message_id não apanhado (o alerta seguiu): {exc}")
            except Exception as exc:  # noqa: BLE001
                falhas += 1
                # O envio leva o token do bot no URL: mascarar aqui não é opcional.
                print(f"[!] Falha ao enviar (o ciclo continua): {sem_segredos(exc)}")

    _fanout_safe(alerts, bot_cfg, dry_run=dry_run)  # fan-out só de alertas por ticker

    if can_send:
        from investigator import config as _cfg_tg

        _record_history_safe(
            mensagens, date.today().isoformat(),
            event_times=event_times, detected_at=detected_at, sent_at=utc_stamp(),
            price_sources=price_source_log(),
            message_ids=ids_por_indice,
            chat_id=str(_cfg_tg.TELEGRAM_CHAT_ID or ""),
        )
        _push_history_safe()  # VM: git CLI (INVESTIGATOR_HISTORY_GIT=1); fail-open
        # Contentor (Heroku): não há checkout git no slug, por isso o caminho acima não faz
        # nada. Este publica pela API do GitHub (INVESTIGATOR_HISTORY_API=1); também fail-open.
        try:
            from investigator.history_publish import publish_safe

            publish_safe(_HISTORY)
        except Exception as exc:  # noqa: BLE001
            print(
                f"[historico-api] indisponível (ignorado): "
                f"{type(exc).__name__}: {sem_segredos(exc)}"
            )
        entregues = len(mensagens) - falhas
        extra = f" ({falhas} falha[s] de envio)" if falhas else ""
        print(f"\n[{entregues}/{len(mensagens)} mensagem(ns) enviada(s) para o Telegram{extra}]")
    else:
        why = "modo --dry-run" if dry_run else "Telegram nao configurado (nada enviado)"
        print(f"\n[{len(mensagens)} mensagem(ns); {why}]")
    return len(mensagens)


def watch_loop(interval_s: int, *, dry_run: bool) -> None:
    """Modo vigia (VM/PC): ciclo contínuo a cada ~interval_s com jitter e paragem limpa.

    Latência de minutos em vez do cron best-effort do GitHub (~1-2h na prática). O estado
    local persiste no disco e o dedup partilhado impede duplicados com o cron de segurança.
    """
    import random
    import signal
    import time

    stop = {"flag": False}

    def _parar(_sig, _frame) -> None:
        stop["flag"] = True

    signal.signal(signal.SIGINT, _parar)
    signal.signal(signal.SIGTERM, _parar)
    print(f"[watch] vigia contínuo: 1 ciclo a cada ~{interval_s}s (SIGTERM/Ctrl+C para parar)")
    while not stop["flag"]:
        try:
            # reler config permite ajustar a quente; watch=True liga a deteção intradiária
            run_cycle(effective_config(), dry_run=dry_run, watch=True)
        except Exception as exc:  # noqa: BLE001  (um ciclo falhado nunca mata o vigia)
            print(f"[watch] ciclo falhou (continua): {type(exc).__name__}: {sem_segredos(exc)}")
        fim = time.monotonic() + interval_s + random.uniform(0, interval_s * 0.2)
        while not stop["flag"] and time.monotonic() < fim:
            time.sleep(1)
    print("[watch] terminado com graça.")


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(description="InvestiGator — runner de alertas")
    parser.add_argument("--dry-run", action="store_true", help="varre e imprime; nunca envia")
    parser.add_argument("--watch", action="store_true",
                        help="modo vigia: loop contínuo (VM/PC) em vez de 1 ciclo")
    parser.add_argument("--interval", type=int, default=300,
                        help="segundos entre ciclos no modo --watch (defeito: 300)")
    args = parser.parse_args()

    if args.watch:
        watch_loop(max(60, args.interval), dry_run=args.dry_run)
        return 0
    run_cycle(effective_config(), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
