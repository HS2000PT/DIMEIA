"""Testes do CAMINHO VIVO — a API que o produto implantado serve.

⚠️ **Porque é que este ficheiro existe.** Até aqui a suíte tinha **zero** testes a tocar em `api/`
ou `web/` — os 359 + 352 linhas que estão de facto no ar — enquanto o Streamlit **retirado** tinha
67. A cobertura estava toda no que já não se serve.

**Todos offline.** O `api.services` vai à rede buscar o instantâneo e o histórico; aqui é
substituído por dados sintéticos, para o teste medir o código e não a ligação. Um teste que depende
da Internet mede a Internet.

A regra que estes testes protegem, e que é a mais fácil de partir sem dar por isso:
**nenhum número é calculado na API.** Se um dia alguém recalcular aqui, o produto e a avaliação
podem divergir em silêncio — é a classe de defeito que este projecto já pagou três vezes.
"""

from __future__ import annotations

import pathlib

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api import main as api_main  # noqa: E402
from api import services as S  # noqa: E402

SNAP = {
    "as_of": "2026-08-14T17:00:00+00:00",
    "age_label": "1 min ago",
    "age_s": 60.0,
    "fresh": True,
    "remote": False,
    "rows": [
        {"ticker": "NVDA", "move": -0.0235, "z": -0.99, "flagged": False,
         "rarity": {"count": 72, "n": 249, "move": -0.0235, "same_direction": 35},
         "decomp": {"market": -0.001, "sector": -0.004, "company": -0.018, "driver": "company"},
         "vol_ratio": 1.2, "closes": [["2026-08-13", 100.0], ["2026-08-14", 97.65]],
         "events": [], "intraday": []},
        {"ticker": "XOM", "move": 0.0447, "z": 2.65, "flagged": True,
         "rarity": {"count": 2, "n": 249, "move": 0.0447, "same_direction": 2},
         "decomp": {"market": 0.0002, "sector": 0.0337, "company": 0.0108, "driver": "sector"},
         "vol_ratio": 2.4, "closes": [["2026-08-14", 110.0]], "events": [], "intraday": []},
    ],
}


@pytest.fixture(autouse=True)
def _sem_rede(monkeypatch):
    monkeypatch.setattr(S, "snapshot", lambda: SNAP)
    monkeypatch.setattr(S, "alerts", lambda: [
        {"date": "2026-08-14", "ticker": "NVDA", "kind": "news", "text": "News alert for NVDA"},
    ])
    monkeypatch.setattr(S, "news_days", lambda t, limit=400: [])
    monkeypatch.setattr(S, "screener", lambda: [
        {"ticker": "XOM", "stage": "weak_precedent", "detail": "sim 0.31 < 0.45"},
    ])
    monkeypatch.setattr(S, "market_state", lambda: {"open": False, "label": "closed"})
    monkeypatch.setattr(S, "watchlist", lambda: ["NVDA", "XOM"])


@pytest.fixture
def client():
    return TestClient(api_main.app)


def test_health_responde_e_declara_a_frescura(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["as_of"] == SNAP["as_of"]


def test_overview_serve_tudo_num_pedido(client):
    """O critério de desempenho da v5 é 'a primeira pintura num só pedido'. Se alguém partir o
    overview em duas rotas, o critério vai-se e ninguém dá por isso."""
    d = client.get("/api/overview").json()
    for chave in ("rows", "market", "watchlist", "as_of", "window", "threshold"):
        assert chave in d, f"falta {chave} — a primeira pintura deixaria de caber num pedido"
    assert len(d["rows"]) == 2


def test_overview_decora_com_veredicto_e_nome(client):
    """O veredicto é calculado em Python (29 testes) e não em JavaScript, de propósito: reescrevê-lo
    no cliente criava uma segunda verdade que ninguém testaria."""
    linhas = {r["ticker"]: r for r in client.get("/api/overview").json()["rows"]}
    assert linhas["XOM"]["verdict"], "sem veredicto — a página abriria com números e sem frase"
    assert linhas["XOM"]["name"] and linhas["XOM"]["name"] != "XOM"


def test_asset_desconhecido_devolve_404_e_nao_500(client):
    r = client.get("/api/asset/ZZZZ")
    assert r.status_code == 404
    assert "watchlist" in r.json()["error"]


def test_asset_devolve_a_serie_sem_recalcular_nada(client):
    d = client.get("/api/asset/NVDA").json()
    assert d["ticker"] == "NVDA"
    # Os valores têm de ser os do instantâneo, byte a byte: a API serve, não calcula.
    assert d["move"] == SNAP["rows"][0]["move"]
    assert d["z"] == SNAP["rows"][0]["z"]
    assert d["decomp"] == SNAP["rows"][0]["decomp"]


def test_screener_expoe_a_etapa_e_a_margem(client):
    """A vista existe para tornar o silêncio inspeccionável; sem a margem, dizia 'não' sem dizer
    por quanto."""
    linhas = client.get("/api/screener").json()["rows"]
    assert linhas and linhas[0]["stage"] == "weak_precedent"
    assert "0.45" in linhas[0]["detail"]


def test_a_api_nao_serve_nada_que_a_pagina_nao_use(client):
    """A regra inversa da anterior, e é a que mantém a superfície pequena.

    Sete rotas foram retiradas a uma semana da entrega — geração com modelo de linguagem,
    pacote de evidência, probabilidade da triagem, precedentes, logótipos e números da
    avaliação — porque **nenhuma delas era usada pela página**. Uma rota pública que ninguém
    consome é risco sem retorno: mais código para manter, mais para correr mal e mais para
    explicar. Duas delas eram POST sem limite de ritmo contra a quota de um fornecedor
    externo, e uma servia um número que o critério H2 proíbe em vistas de produto.

    Este teste existe para que voltar a expor uma rota seja uma **decisão**, e não um resto.
    """
    import re

    html = _PAGINA.read_text(encoding="utf-8")
    # A documentação do contrato fica, e é a única excepção: não é superfície de produto,
    # não corre lógica nenhuma, e numa defesa é a resposta a "o que é que isto serve?".
    DOCS = {"/api/docs", "/api/openapi.json"}
    servidas = {r.path for r in api_main.app.routes
                if getattr(r, "path", "").startswith("/api/")} - DOCS
    usadas = {m.group(1) for m in re.finditer(r'json\("(/api/[a-z]+)', html)}
    # `/api/asset/{ticker}` é montada com template literal, logo não aparece no varrimento
    usadas.add("/api/asset/{ticker}")

    assert servidas == usadas, f"rotas servidas e não usadas: {sorted(servidas - usadas)}"


def test_spa_serve_o_index_em_rotas_profundas(client):
    """`?t=NVDA` e o botão 'voltar' do browser só funcionam se qualquer caminho cair no index."""
    r = client.get("/qualquer/caminho/inexistente")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "")


def test_alertas_servem_os_MAIS_RECENTES_e_nao_os_primeiros(client, monkeypatch):
    """⚠️ Regressão apanhada a preparar a gravação da defesa, a 2026-08-17.

    O histórico está por ordem cronológica e cresce. Servir `[:200]` significava que, assim que
    o ficheiro passasse esse tamanho, a página deixava de ver alertas novos e servia em silêncio
    uma janela cada vez mais antiga. Com o canal em 391 alertas, a página mostrava como mais
    recente um alerta de 31 de julho.
    """
    historico = [{"date": f"2026-01-{d:02d}", "ticker": "NVDA", "kind": "news", "text": f"n{d}"}
                 for d in range(1, 29)]
    monkeypatch.setattr(S, "alerts", lambda: historico)

    linhas = client.get("/api/alerts").json()["rows"]

    assert linhas[-1]["date"] == "2026-01-28", "o mais recente do histórico tem de estar presente"


# ══ A PÁGINA (v6) ═══════════════════════════════════════════════════════════════════
# A v6 é um ficheiro só, sem build, e por isso não há módulo para importar. O que se pode
# testar sem um browser é o CONTRATO entre a página e a API, e as regras que ela aplica ao
# texto do alerta. Foi um defeito destes que fez a hiperligação da fonte sair como texto cru.

_PAGINA = pathlib.Path(__file__).resolve().parents[1] / "web" / "index.html"


def test_a_pagina_so_usa_rotas_que_a_api_serve():
    """Uma rota escrita à mão na página e inexistente na API é um ecrã vazio em produção.

    Nada avisa: o `fetch` falha, o `catch` mostra a mensagem de indisponibilidade, e parece um
    problema de rede.
    """
    import re

    html = _PAGINA.read_text(encoding="utf-8")
    pedidas = {m.group(1) for m in re.finditer(r'json\("(/api/[a-z]+)', html)}
    servidas = {r.path for r in api_main.app.routes
                if getattr(r, "path", "").startswith("/api/")}

    assert pedidas, "a página tem de pedir alguma coisa"
    assert pedidas <= servidas, f"a página pede rotas que a API não serve: {pedidas - servidas}"


def test_a_pagina_nao_mostra_a_probabilidade_da_triagem():
    """O critério H2 proíbe um número sobre o futuro em qualquer vista de produto.

    A v5 servia-o em três sítios. A v6 não pode voltar a fazê-lo por distração.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert "/api/triage" not in html
    assert "/api/report" not in html and "/api/ask" not in html


def test_a_hiperligacao_da_fonte_sobrevive_ao_escape():
    """⚠️ Regressão medida no browser a 2026-08-20: ZERO ligações reais em 25 alertas.

    O texto do alerta é escapado antes de ser inserido, e o escape converte as aspas em
    `&quot;`. O padrão que reconstruía a ligação procurava aspas literais, portanto nunca
    casava, e o `<a href="...">` saía impresso no ecrã. A página tem de aceitar as duas formas.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    padrao = next(li for li in html.splitlines() if "&lt;a href=" in li)

    assert "&quot;" in padrao, "sem isto o escape das aspas parte a ligação, e ninguém dá por isso"
    assert "function comLigacoes" in html, \
        "a v7 apagou a reconstrução da ligação; o leitor volta a ver a etiqueta impressa"
    assert "soRotulo" in html, \
        "o resumo do feed tem de ficar só com a etiqueta: um <a> dentro de um <button> é inválido"


def test_a_pagina_recusa_um_href_que_nao_seja_http():
    """O URL vem de uma API externa, portanto não é de confiança.

    Um `javascript:` no href seria execução de código a partir de dados de terceiros, na única
    parte da página que insere HTML vindo de fora.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert "const seguro" in html and "https?" in html
    # Verificado no browser a 2026-09-01 com quatro entradas hostis: `javascript:`, `data:`,
    # um href relativo e um `HTTPS://` legítimo. Os três primeiros perdem a ligação e ficam só
    # com a etiqueta; o quarto passa, com o `&` reescapado.
    assert 'rel="noopener noreferrer nofollow"' in html, \
        "uma ligação para fora sem rel= entrega a página de origem ao destino"


# ══ A PÁGINA (v6.1, revisão de produto F6) ══════════════════════════════════════════
# As três regras abaixo já foram quebradas uma vez cada, e nenhuma delas dá erro: a página
# continua a compilar, a carregar e a parecer bem. Só se nota a olhar para o ecrã e a saber o
# que devia lá estar — que é exactamente o tipo de defeito que um teste deve apanhar por nós.


def test_a_pagina_usa_o_veredicto_que_o_servidor_calcula():
    """`app/verdict.py` tem 29 testes e resolve o caso das duas réguas que discordam.

    A v6 pedia `/api/overview`, recebia o campo `verdict` de cada linha e **não o mostrava**:
    uma camada testada, servida e ignorada. Reescrever a frase em JavaScript seria pior ainda,
    porque criava uma segunda verdade que ninguém verificava.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert ".verdict" in html, "a página tem de mostrar o veredicto do servidor, não inventar um"


def test_a_pagina_mostra_a_reparticao_do_movimento():
    """*Foi a empresa, ou foi o mercado?* é uma das três perguntas fundadoras do trabalho.

    A v6 tinha-a deixado cair: a API servia `decomp` em cada linha e o cliente deitava-a fora.
    Um produto que responde a duas das três perguntas não é o produto que a dissertação
    descreve.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert "decomp" in html
    for parte in ("market", "sector", "company"):
        assert parte in html, f"falta a parcela {parte} na repartição"


def test_a_pagina_nao_corta_o_canal_em_silencio():
    """Mostrar as primeiras N mensagens sem dizer quantas ficaram de fora é um corte silencioso.

    A página é um espelho do canal: se não couber tudo, tem de dizer quanto não coube e ter
    onde carregar. É a mesma regra que os relatórios de avaliação seguem quando limitam
    cobertura.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert "older message" in html, "o resto do canal tem de estar alcançável e contado"
    assert "S.feedLimite" in html, \
        "a v7 cortou o feed num `slice` fixo; sem limite em estado não há como carregar mais"
    assert "not shown — load" in html, \
        "contar o que ficou de fora sem dar onde carregar continua a ser um corte"


def test_uma_rota_de_api_inexistente_falha_como_api_e_nao_como_pagina(client):
    """⚠️ Medido em produção a 2026-08-20, logo a seguir a retirar sete rotas.

    O apanha-tudo do SPA servia `index.html` para **qualquer** caminho, incluindo os que
    começam por `/api/`. Resultado: `GET /api/report` respondia **200 com HTML**. Quem
    estivesse a chamar a rota recebia uma página web onde esperava JSON, o que se lê como
    "a rota existe e devolveu lixo" em vez de "a rota não existe".
    """
    r = client.get("/api/rota-que-nao-existe")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
    # e o SPA continua a apanhar tudo o resto, que é o que faz o botão "voltar" funcionar
    assert client.get("/qualquer/coisa").status_code == 200


def test_a_legenda_descreve_as_marcas_que_o_grafico_desenha_mesmo():
    """Uma legenda que não bate com o desenho é pior do que legenda nenhuma: ensina errado.

    ⚠️ **O defeito que este teste fixa.** O gráfico marcava um alerta enviado com uma seta para
    baixo (``shape:"arrowDown"``) e a legenda mostrava um quadrado; marcava um dia assinalado com
    um círculo **verde ou vermelho** conforme a direção do movimento, e a legenda mostrava um
    círculo cinzento, sem dizer em lado nenhum que a cor queria dizer alguma coisa. Das duas
    marcas que o gráfico usa, nenhuma aparecia na legenda com a forma certa.

    É a mesma classe de defeito que a legenda do funil tinha (``0 sent`` com alertas na lista ao
    lado): duas representações do mesmo facto a discordar no mesmo ecrã. Nenhum registo a mostra,
    e nenhum teste a apanhava, porque cada metade estava internamente correcta.

    O teste é estrutural de propósito: não sabe desenhar, sabe exigir que para cada forma que o
    gráfico usa exista uma classe de legenda declarada, e que a cor seja explicada quando carrega
    sentido.

    Reescrito para a v7 a 2026-09-01. O gráfico mudou de marcas — deixou de usar um círculo
    para o dia assinalado e passou a usar a seta, para cima ou para baixo conforme o fecho —,
    portanto as afirmações antigas deixaram de descrever o desenho. A regra é a mesma e não se
    negociou: para cada forma que o gráfico usa existe o mesmo símbolo na legenda, e a cor é
    explicada porque carrega sentido.

    Mudou também uma coisa que este teste não vigiava e passou a vigiar: as etiquetas `z` foram
    retiradas dos marcadores. Com quinze dias assinalados em seis meses sobrepunham-se umas às
    outras e à linha de preço — medido no browser, não suposto. A data e o z de cada dia estão
    nas fichas por baixo do gráfico, que além de legíveis são navegáveis por teclado.

    Reescrito outra vez a 2026-09-02, quando o gráfico ganhou camadas. Agora usa TRÊS formas —
    o círculo para o alerta que saiu, as duas setas para o dia assinalado que não gerou alerta,
    e o quadrado para a notícia que o sistema viu e não usou — e a distinção entre a primeira e
    as segundas é a tese inteira: assinalar não é enviar.

    E ganhou uma regra que não existia: **a legenda descreve o que está DESENHADO, não o que
    está ligado.** No 1D a caixa dos alertas pode estar ligada e não haver marca nenhuma no
    ecrã, porque o alerta saiu de madrugada e a janela intradiária começa na abertura. Uma
    legenda ligada ao interruptor voltaria a descrever uma marca ausente.
    """
    html = _PAGINA.read_text(encoding="utf-8")

    # as três formas que o gráfico usa, cada uma com o seu símbolo na legenda
    assert 'shape: dir > 0 ? "arrowUp" : "arrowDown"' in html, \
        "mudou a marca do dia assinalado; rever a legenda do gráfico"
    assert 'shape:"circle"' in html, "o alerta enviado deixou de ter marca própria"
    assert 'shape:"square"' in html, "a notícia sem alerta deixou de ter marca própria"

    # os símbolos da legenda são triângulos CSS, com a mesma orientação das setas do gráfico
    assert "border-bottom:8px solid var(--sobe)" in html, "falta a seta para cima na legenda"
    assert "border-top:8px solid var(--desce)" in html, "falta a seta para baixo na legenda"
    assert ".legenda .quad" in html, "o quadrado da notícia não tem símbolo na legenda"

    # ⚠️ a legenda lê o que foi desenhado, e não as camadas ligadas
    assert "S.desenhado" in html, \
        "a legenda voltou a olhar para os interruptores em vez do que está no ecrã"
    assert "const d = S.desenhado" in html, "a legenda deixou de ler o desenhado"

    # a cor da seta é a direcção do movimento, e isso tem de estar escrito
    assert "the colour is the direction" in html, \
        "a cor da seta carrega sentido e a legenda não o explica"
    # e o z, que é a unidade do eixo invisível, tem de ser dito onde as setas aparecem
    assert "standard deviations" in html, \
        "a legenda do gráfico mostra z sem dizer o que z é"
    # ⚠️ as etiquetas dos marcadores ficaram de fora de propósito; ver o docstring
    assert "text:`z ${z}`" not in html, \
        "voltaram as etiquetas aos marcadores; sobrepõem-se, medido a 2026-09-01"
    assert 'shape:"circle", text:"alert"' not in html, \
        "voltaram as etiquetas aos alertas; sobrepõem-se, medido a 2026-09-02"


def test_a_promessa_da_pagina_aparece_uma_vez_e_nao_duas():
    """Critério H1: a promessa é a identidade da página, e aparece **uma** vez.

    ⚠️ Aparecia duas. A página inteira já é a promessa (as secções chamam-se ``What was sent`` e
    ``Why it stayed quiet``) e o cabeçalho repetia-a em palavras por baixo do nome. O ficheiro da
    própria marca, ``app/assets/logo-lockup.svg``, já tinha a decisão escrita: *"SEM assinatura,
    de propósito ... para capas há a variante -tagline"*. A página contradizia-o.

    Fica no ``<title>``, que é a identidade do separador do browser e não uma segunda afirmação
    no ecrã.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    corpo = html.split("<body>", 1)[1]
    visivel = corpo.replace("<!--", "\x00").split("\x00")
    visivel = "".join(p.split("-->", 1)[-1] if "-->" in p else p for p in visivel)

    # ⚠️ Mudou na v7, por decisão do autor a 2026-09-01: «corrigir o tab title, ficar apenas
    # InvestiGator». O separador passa a ter só o nome. A regra de fundo não mudou — a promessa
    # aparece uma vez —, mudou o sítio: deixa de estar escrita em palavras e passa a estar
    # cumprida pela página. É por isso que este teste deixou de exigir a frase e passou a exigir
    # as duas metades dela.
    assert "<title>InvestiGator</title>" in html, \
        "o separador voltou a ter mais do que o nome"
    assert visivel.count("what was sent, and what was not") == 0, \
        "a assinatura voltou ao corpo da página: H1 diz que a promessa aparece uma vez"

    # metade um: o que foi enviado, com o texto exacto
    assert "<h2>What was sent</h2>" in html, \
        "sem o espelho do canal a página deixa de cumprir metade da promessa"
    assert "The exact text that reached the phone" in html, \
        "o espelho tem de mostrar o texto tal como saiu, e dizê-lo"
    # metade dois: o que não foi enviado, e porquê — na v7 é o modal por empresa
    assert "why it is where it is" in html, \
        "a segunda metade da promessa (o silêncio explicado) desapareceu da página"
    assert "Silence is a decision this system makes" in html, \
        "o silêncio voltou a ser ausência de informação em vez de uma decisão registada"


def test_o_estado_da_bolsa_nao_esta_em_dois_sitios():
    """Uma representação por facto. Aprendido três vezes nesta página, ao custo de três defeitos.

    O estado do mercado subiu do rodapé para a barra, onde se vê sem rolar. Deixá-lo também no
    rodapé criaria dois sítios a dizer o mesmo, que é como nasceram o ``0 sent`` com alertas na
    lista ao lado e a legenda do funil a discordar da contagem.
    """
    html = _PAGINA.read_text(encoding="utf-8")
    assert 'id="mercado"' in html, "o estado da bolsa saiu da barra"
    assert "NASDAQ" in html and "NYSE" in html, \
        "a barra tem de dizer de QUE bolsas fala; 'closed' sozinho não diz de onde"
    js = html.split("rodape\").textContent", 1)
    assert len(js) == 2, "mudou a forma de escrever o rodapé; rever este teste"
    assert "m.label" not in js[1][:200], \
        "o estado do mercado voltou ao rodapé, e está agora em dois sítios"


def test_os_logotipos_sao_servidos_por_nos_e_nunca_por_terceiros():
    """Um <img> para um domínio de terceiros conta-lhe quem visita a página e o que está a ver.

    Isso contradiz a posição de privacidade do trabalho, que é a razão pela qual estes ficheiros
    estão versionados em vez de puxados de um CDN. O teste fixa as duas metades: a origem é
    relativa, e cada empresa da watchlist tem mesmo o seu ficheiro.
    """
    import re

    html = _PAGINA.read_text(encoding="utf-8")
    externos = re.findall(r'<img[^>]+src="(https?://[^"]+)"', html)
    assert not externos, f"a página carrega imagens de terceiros: {externos}"
    assert "/assets/logos/" in html, "a barra deixou de mostrar os logótipos"
    # ⚠️ A v7 acrescentou uma segunda origem de terceiros, e esta não é uma imagem: a folha de
    # estilo do Google Fonts. Cai na mesma regra — conta a um terceiro quem abriu a página — e
    # por isso as letras passaram a ser servidas por nós, de `web/assets/fonts/`.
    # Receita reproduzível em `scripts/preparar_fontes.sh`.
    assert "fonts.googleapis.com/css" not in html, \
        "as letras voltaram ao Google Fonts: o visitante volta a ser contado a um terceiro"
    assert "/assets/fonts/IBMPlexSans-Regular.woff2" in html, \
        "as letras deixaram de ser servidas por nós"

    pasta = _PAGINA.parent / "assets" / "logos"
    tem = {f.stem for f in pasta.glob("*.png")}
    faltam = {"AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL",
              "META", "JPM", "AMD", "NFLX", "XOM", "JNJ"} - tem
    assert not faltam, f"sem logótipo para {sorted(faltam)}; o botão fica sem imagem"
