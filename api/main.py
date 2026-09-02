"""API do InvestiGator — o processo web deixa de renderizar e passa a servir dados.

## O que mudou, e porquê é uma decisão de arquitectura e não de moda

O Streamlit **re-executa o script inteiro a cada interacção**, do lado do servidor. Trocar de
intervalo no gráfico, paginar uma tabela ou expandir um painel custa uma ida ao servidor e uma
repintura da página. O estudo de percursos mediu o efeito e escreveu a conclusão sem rodeios:
*"No CSS fixes this; a client-side interaction layer does."*

Aqui o servidor responde a pedidos e o cliente guarda o estado. Trocar de intervalo passa a
ser um recorte de um vector que já está no browser: sem rede, sem repintura, sem salto.

## A regra que mantém isto honesto

Nenhum número é calculado neste ficheiro. Todos os caminhos chamam `investigator/…` — os
mesmos motores que a avaliação da tese usa e que o worker corre de 60 em 60 segundos. Se a API
recalculasse fosse o que fosse, o produto e a avaliação podiam divergir sem ninguém dar por
isso, que é a classe de defeito que este projecto já pagou em três sítios diferentes.

## Fail-open em toda a superfície

Cada rota devolve o que conseguir e diz o que falta. Uma API que devolve 500 porque o GitHub
está lento transforma uma indisponibilidade parcial numa página branca — e uma página branca é
indistinguível de um produto avariado.
"""

from __future__ import annotations

import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api import services as S

RAIZ = pathlib.Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"

app = FastAPI(
    title="InvestiGator API",
    description="Market intelligence: measured statistics, learned models, grounded generation.",
    version="5.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


# ── Dados ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict:
    snap = S.snapshot()
    return {"ok": True, "snapshot": bool(snap), "as_of": snap.get("as_of", ""),
            "age_s": snap.get("age_s"), "fresh": snap.get("fresh")}


def _decorate(rows: list[dict], market_open: bool) -> list[dict]:
    """Junta a cada linha o veredicto e o nome legível.

    ⚠️ **Calculado aqui e não no cliente, de propósito.** `app/verdict.py` tem 29 testes e
    resolve casos que não são óbvios: as duas réguas que discordam (a MSFT com +4,82% e z
    +1,11, "calma" pela norma recente e no top 2% do ano), a linha do motor que se cala
    quando o motor é a própria empresa, e um varrimento sobre 112 combinações contra 16
    palavras que impõe a proibição de prever.
    Reescrever isso em JavaScript criava uma segunda verdade que ninguém testaria, e as duas
    divergiriam na primeira alteração.
    """
    try:
        from app.verdict import verdict
        from investigator.anomaly_detector.frequency import Exceedance
        from investigator.news_fetcher.relevance import display_name
    except Exception:  # noqa: BLE001
        return rows

    out = []
    for r in rows:
        r = dict(r)
        name = display_name(r.get("ticker", ""))
        rar = r.get("rarity")
        exc = None
        if rar and rar.get("n") is not None and rar.get("move") is not None:
            # Sem `try` à volta da construção, e é deliberado. A primeira versão embrulhava
            # isto num `except` largo; `Exceedance` exige quatro campos, a construção com dois
            # levantava `TypeError`, o `except` transformava-o em `exc = None`, e o veredicto
            # caía no ramo "an ordinary day".
            #
            # O resultado medido: a AAPL a **-2,11%**, o 35.º maior movimento de 249 dias
            # (top 14%), descrita como "um dia normal". É EXACTAMENTE o defeito de honestidade
            # que a sessão 48 corrigiu na v3 — e voltou por uma porta diferente, escondido por
            # um `except` que tornava um erro de programação indistinguível de dados em falta.
            exc = Exceedance(move=float(rar["move"]), n=int(rar["n"]),
                             count=int(rar["count"]),
                             same_direction=int(rar.get("same_direction", 0)))
        r["name"] = name
        r["verdict"] = verdict(name, exc, r.get("decomp"), bool(r.get("flagged")),
                               market_open=market_open)
        out.append(r)
    return out


@app.get("/api/overview")
def overview() -> dict:
    """Tudo o que a primeira pintura precisa, num pedido. Sem rede por ticker."""
    snap = S.snapshot()
    mkt = S.market_state()
    rows = _decorate(snap.get("rows", []), bool(mkt.get("open")))
    alerts = S.alerts()
    today_alerts = [a for a in alerts if a.get("date", "")[:10] == (
        snap.get("as_of", "")[:10] or "___")]
    return {
        "as_of": snap.get("as_of", ""),
        "age_label": snap.get("age_label", ""),
        "age_s": snap.get("age_s"),
        "fresh": snap.get("fresh", False),
        "source": "snapshot(remote)" if snap.get("remote") else "snapshot(local)",
        "market": mkt,
        "watchlist": S.watchlist(),
        "rows": rows,
        "alerts_total": len(alerts),
        "alerts_today": len(today_alerts),
        "window": 20,
        "threshold": 1.5,
    }


@app.get("/api/asset/{ticker}")
def asset(ticker: str) -> dict:
    """O que é barato de um activo. O caro (precedentes, triagem) tem rota própria."""
    t = ticker.upper()
    snap = S.snapshot()
    row = next((r for r in snap.get("rows", []) if r.get("ticker") == t), None)
    if row is None:
        return JSONResponse({"error": f"{t} is not in the watchlist"}, status_code=404)

    news = S.news_days(t, limit=400)
    alerts = [a for a in S.alerts() if a.get("ticker") == t][:40]
    try:
        from investigator.news_fetcher.relevance import display_name, sector_etf
        name, sector = display_name(t), sector_etf(t)
    except Exception:  # noqa: BLE001
        name, sector = t, None
    return {
        "ticker": t, "name": name, "sector_etf": sector,
        "as_of": snap.get("as_of", ""),
        "move": row.get("move"), "z": row.get("z"), "flagged": row.get("flagged"),
        "rarity": row.get("rarity"), "decomp": row.get("decomp"),
        "vol_ratio": row.get("vol_ratio"),
        "closes": row.get("closes", []),
        "events": row.get("events", []),
        "news": news,
        "alerts": alerts,
    }


# ── O que esta API deliberadamente NÃO serve ──────────────────────────────────
#
# Sete rotas foram **retiradas** a 2026-08-20, uma semana antes da entrega, e a razão é a
# mesma para todas: **nenhuma delas era usada pela página**, e uma superfície pública que
# ninguém consome é risco sem retorno — mais código para manter, mais para correr mal, e
# mais para explicar numa defesa.
#
#   /api/report, /api/ask   geração com modelo de linguagem. Eram POST **públicos e sem
#                           limite de ritmo** que gastavam a quota de um fornecedor externo
#                           a pedido de qualquer pessoa. E a dissertação curta não descreve
#                           camada generativa nenhuma: posiciona-se, no §2.7, precisamente
#                           contra o resumo gerado, por ser uma afirmação sem evidência
#                           anexada. Manter no ar o que o documento não reivindica é dívida.
#   /api/evidence           existia para tornar verificável a ancoragem do texto gerado.
#                           Sem texto gerado, não há o que ancorar.
#   /api/triage             servia a probabilidade da triagem, que o critério H2 proíbe em
#                           qualquer vista de produto. Estava fora da página e continuava
#                           acessível a quem soubesse o caminho.
#   /api/precedents         a recuperação semântica carrega o modelo e a base de casos:
#                           ~7 s a frio e centenas de MB num contentor de 512 MB, para uma
#                           rota que ninguém chamava. Os precedentes chegam ao utilizador
#                           dentro do texto do alerta, que é onde a dissertação os mostra.
#   /api/logos, /api/method  simplesmente sem consumidor.
#
# ⚠️ **O código NÃO foi apagado.** `investigator/intelligence/`, `app/method.py` e o motor
# de recuperação continuam no repositório, testados: são história do trabalho e as duas
# teses longas descrevem-nos. O que saiu foi a **exposição pública**, que é outra coisa.
# Voltar a expor qualquer uma é acrescentar oito linhas.


@app.get("/api/screener")
def screener() -> dict:
    """Porque é que o sistema ficou calado sobre cada nome. Com a margem que faltou."""
    return {"rows": S.screener()}


@app.get("/api/alerts")
def alerts() -> dict:
    # ⚠️ Os ÚLTIMOS 200, não os primeiros. O histórico está por ordem cronológica e cresce; com
    # `[:200]` a página deixava de ver alertas novos assim que o ficheiro passasse esse tamanho,
    # e servia em silêncio uma janela cada vez mais antiga. Apanhado a 2026-08-17, com o canal
    # em 391 alertas: a página mostrava como mais recente um alerta de 31 de julho.
    return {"rows": S.alerts()[-200:]}


# ── Telegram: webhook (votos do leitor + comandos do bot) ─────────────────────────────────

_VOTOS = RAIZ / "data" / "feedback.jsonl"


def _ctx_webhook():
    """Monta o contexto do webhook com as saídas reais. Importa tarde, como o resto do módulo.

    A publicação na branch de dados é o que torna os votos duráveis: o disco do dyno é efémero
    e reinicia pelo menos uma vez por dia. É o mesmo mecanismo que o `gate_log` já usa.
    """
    from investigator import config
    from investigator.telegram_bot import sender, store, webhook

    def publicar(caminho):
        # ⚠️ `publish_jsonl_merge` e não `publish_blob`. O `publish_blob` substitui, e substituir
        # um registo acumulativo a partir de um disco efémero apaga tudo o que foi recolhido
        # antes do último reinício. Aconteceu a 2026-09-01. O porquê está escrito no módulo.
        from investigator.history_publish import publish_jsonl_merge

        print(publish_jsonl_merge(caminho, "feedback.jsonl"))

    return webhook.Contexto(
        sal=config.FEEDBACK_SALT,
        caminho_votos=_VOTOS,
        enviar=sender.send_message,
        responder_callback=sender.answer_callback_query,
        editar_teclado=sender.edit_message_reply_markup,
        publicar=publicar,
        ligacao_db=lambda: store.connect(),
    )


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request) -> JSONResponse:
    """Recebe updates do Telegram.

    ⚠️ **Devolve 200 em quase todos os casos, de propósito.** Um estatuto de erro faz o
    Telegram reenviar o mesmo update, com recuo crescente, durante muito tempo. Um voto que
    não conseguimos gravar é um voto perdido; um 500 devolvido em ciclo é o bot inteiro
    parado. A única resposta que não é 200 é a do segredo errado, que tem de ser 403 porque
    aí queremos mesmo que a outra ponta desista.

    O segredo em falta fecha a rota. Um webhook público sem verificação aceita votos de quem
    descobrir o endereço, e a amostra da tese deixaria de significar o que diz significar.
    """
    from investigator import config
    from investigator.telegram_bot import webhook

    if not webhook.segredo_confere(
        request.headers.get("x-telegram-bot-api-secret-token"),
        config.TELEGRAM_WEBHOOK_SECRET or "",
    ):
        return JSONResponse({"ok": False, "error": "forbidden"}, status_code=403)
    try:
        update = await request.json()
    except Exception:  # noqa: BLE001
        return JSONResponse({"ok": True, "ignored": "corpo ilegível"})
    linha = webhook.processar(update, _ctx_webhook())
    print(linha)
    return JSONResponse({"ok": True})


_VOTOS_CACHE: dict = {"at": 0.0, "linhas": None}
_VOTOS_TTL = 45.0          # abaixo dos 30 s de sondagem do painel seria bater no GitHub por visita


def _registos_votos():
    """Os votos como o painel os tem de ver: o disco deste dyno **mais** a branch de dados.

    ⚠️ Quem escreve os votos é o dyno **worker**; quem serve esta rota é o dyno **web**. São
    dois sistemas de ficheiros separados e efémeros, portanto ler só o ficheiro local devolvia
    zero votos com votos a entrar — foi o que o painel mostrou a 2026-09-02. A branch de dados é
    o único sítio que os dois dynos já sabem partilhar, e é a mesma conclusão a que o
    instantâneo do painel tinha chegado antes.

    Nada é escrito no disco a partir daqui: o web lê, o worker escreve. A junção é em memória e
    por linha inteira, e fica em cache uns segundos para não bater no GitHub uma vez por visita.
    """
    import time

    from investigator import feedback_log as FL
    from investigator.history_publish import fetch_jsonl

    try:
        locais = [ln for ln in _VOTOS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except Exception:  # noqa: BLE001
        locais = []

    agora = time.monotonic()
    if _VOTOS_CACHE["linhas"] is None or agora - _VOTOS_CACHE["at"] > _VOTOS_TTL:
        remotas = fetch_jsonl("feedback.jsonl")
        # `None` é «não consegui ler», e nesse caso o que já estava em cache vale mais do que
        # nada; só um `[]` verdadeiro autoriza dizer que a branch está vazia.
        if remotas is not None:
            _VOTOS_CACHE["linhas"] = remotas
            _VOTOS_CACHE["at"] = agora

    vistas: set[str] = set()
    juntas: list[str] = []
    for ln in (_VOTOS_CACHE["linhas"] or []) + locais:
        if ln not in vistas:
            vistas.add(ln)
            juntas.append(ln)
    return FL.parse_jsonl_lines(juntas)


@app.get("/api/feedback")
def feedback() -> dict:
    """Votos dos leitores, em agregado. Sem identificadores, por construção.

    A rota tinha sido retirada quando a página ainda não a consumia — o
    `test_a_api_nao_serve_nada_que_a_pagina_nao_use` apanhou-a, e com razão. Volta agora porque a
    v7 do painel mostra as contagens em cada alerta e no indicador do dia.

    Devolve as contagens por chave de alerta e nada mais: o resumo do estudo vive no relatório de
    avaliação, e um painel de produto não é o sítio para reportar proporções sobre uma amostra
    que ainda não atingiu o mínimo pré-registado.
    """
    registos = _registos_votos()
    from investigator import feedback_log as FL

    return {"por_alerta": {c: list(FL.contagem(registos, c))
                           for c in {r.chave_alerta for r in registos}}}


# ── Estáticos ─────────────────────────────────────────────────────────────────

if WEB.exists():
    app.mount("/assets", StaticFiles(directory=str(WEB / "assets")), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB / "index.html")

    @app.get("/{path:path}")
    def spa(path: str):
        """Qualquer caminho serve o SPA — o cliente resolve a rota.

        Ficheiros reais servem-se; o resto cai no `index.html` para que `?t=NVDA` e as URLs
        profundas funcionem com o botão "voltar" do browser, que é o que faz um produto web
        parecer um produto web.
        """
        # ⚠️ Menos `/api/`, que tem de falhar como API e não como página. Sem esta linha, um
        # pedido a uma rota retirada devolvia **200 com HTML**, e quem estivesse a chamá-la
        # recebia uma página web onde esperava JSON — que se lê como "a rota existe e
        # devolveu lixo", em vez de "a rota não existe". Um 404 explícito é a resposta
        # honesta e é a que diz o que aconteceu.
        if path.startswith("api/"):
            return JSONResponse({"error": f"no such route: /{path}"}, status_code=404)
        f = WEB / path
        if f.is_file():
            return FileResponse(f)
        return FileResponse(WEB / "index.html")
