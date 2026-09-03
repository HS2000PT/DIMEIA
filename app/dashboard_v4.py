"""Painel v4 — a grelha que LÊ em vez de calcular.

Construído **ao lado** da v3, que continua a ser o que o `Procfile` serve. Nada aqui toca no
motor, nos congelados, nem na v3.

AS DECISÕES, TOMADAS PELA MEDIÇÃO E NÃO POR GOSTO
--------------------------------------------------
1. **Ler um instantâneo, não calcular.** A v3 faz doze idas à rede antes da primeira pintura.
   Medido no browser, tempo até os cartões existirem: **1.º pedido com caches vazias 6,0 s na v3
   contra 2,0 s na v4**; **morno, 1,2 s nas duas**.
   ⚠️ A segunda metade dessa frase importa tanto como a primeira: com a cache quente a v3 já era
   rápida, portanto dizer que a v4 "é mais rápida" sem qualificar seria falso. O ganho é a frio —
   depois de cada implantação e de cada reciclagem do dyno — e é **não depender da rede** no
   momento em que alguém olha.
2. **Ficar em Streamlit.** Consequência directa: trocar de framework sem pré-computar mantinha
   o defeito; pré-computar sem trocar remove-o quase todo. A migração teria de se justificar
   por controlo de interacção, nunca por "é lento".
3. **Estrutura fixa de resposta.** As três perguntas aparecem como secções nomeadas, na mesma
   ordem, **sempre** — incluindo quando a resposta é "nada aconteceu".
4. **Ligações reais.** `?t=NVDA` abre essa empresa; o botão do browser funciona; o link do
   alerta do Telegram pode apontar directamente para o detalhe.

Correr:  streamlit run app/dashboard_v4.py
"""

from __future__ import annotations

import pathlib
import sys

# A app é lançada por caminho, e nesse modo o Python põe no `sys.path` a pasta do SCRIPT, não a
# raiz. Sem esta guarda, `import app...` rebenta — defeito real da v3, e a causa não foi o
# código: foi ter sido verificada com `python -m`, que acrescenta o directório actual e esconde
# o problema. Testar o comando que o utilizador escreve, não um parecido.
_RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

import streamlit as st  # noqa: E402

from app import ui_tokens as T  # noqa: E402
from app.snapshot_io import carregar, resumo_do_dia, tira_distribuicao  # noqa: E402
from app.v4_views import (  # noqa: E402
    explicar_silencio,
    linhas_decomposicao,
    rotulo_atribuicao,
    rotulo_raridade,
)
from investigator.branding.logos import cached_logo  # noqa: E402
from investigator.news_fetcher.relevance import display_name  # noqa: E402

HISTORY_BRANCH = "alerts-history"

st.set_page_config(page_title="InvestiGator", page_icon="🐊", layout="wide")

LIMIAR = 1.5
GATE_LOG = _RAIZ / "data" / "gate_log.jsonl"


# ─────────────────────────────────────────────────────────────────────── estilo
def _css() -> str:
    return f"""<style>
 :root {{
   --bg:{T.BG}; --panel:{T.PANEL}; --line:{T.LINE};
   --fg:{T.FG}; --dim:{T.FG_DIM}; --mute:{T.FG_MUTE};
   --up:{T.UP}; --down:{T.DOWN}; --flag:{T.FLAG}; --info:{T.NEWS};
   --strip-on:{T.FLAG}; --strip-off:#242C38;
 }}
 .stApp {{ background:var(--bg); }}
 .block-container {{ padding:0.85rem 1.1rem 2.4rem; max-width:1920px; }}
 #MainMenu, footer, header {{ visibility:hidden; }}
 a {{ text-decoration:none; }}

 .top {{ display:flex; align-items:center; gap:13px; flex-wrap:wrap;
         border-bottom:1px solid var(--line); padding-bottom:9px; margin-bottom:13px; }}
 .brand {{ font-weight:700; letter-spacing:.15em; font-size:13px; color:var(--fg); }}
 .brand .g {{ color:{T.UP}; }}
 .age {{ font-family:ui-monospace,monospace; font-size:11.5px; color:var(--mute); }}
 .age.stale {{ color:var(--flag); }}
 .nav {{ margin-left:auto; display:flex; gap:16px; }}
 .nav a {{ font-size:12px; color:var(--mute); border-bottom:1px solid transparent; }}
 .nav a:hover {{ color:var(--fg); border-bottom-color:var(--fg); }}

 .day {{ font-size:19px; color:var(--fg); font-weight:600; margin:2px 0 16px;
         line-height:1.35; max-width:82ch; }}

 /* A promessa. Aparece UMA vez por página, no fim — critério H1: dizê-la em cada cartão
    fazia a v2 ler como defensiva, e não a dizer de todo (o que a v4 fazia até aqui) é pior,
    porque é a única posição ética que este trabalho assume em voz alta. */
 .foot {{ margin-top:26px; padding-top:11px; border-top:1px solid var(--line);
          font-size:11.5px; color:var(--mute); max-width:82ch; line-height:1.5; }}

 .grid {{ display:grid; gap:12px; grid-template-columns:repeat(4,minmax(0,1fr)); }}
 @media (max-width:1500px) {{ .grid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} }}
 @media (max-width:1080px) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
 @media (max-width:700px)  {{ .grid {{ grid-template-columns:1fr; }} }}

 .card {{ background:var(--panel); border:1px solid var(--line); border-radius:13px;
          padding:13px 14px 12px; display:flex; flex-direction:column; gap:9px;
          transition:border-color .15s, transform .15s; }}
 a.card:hover {{ border-color:var(--fg); transform:translateY(-2px); }}
 .card.flagged {{ border-color:color-mix(in srgb,var(--flag) 55%,var(--line)); }}
 .head {{ display:flex; align-items:center; gap:8px; }}
 .name {{ font-weight:650; font-size:14.5px; color:var(--fg); }}
 .logo {{ width:19px; height:19px; border-radius:4px; object-fit:contain;
          background:#fff; padding:1px; flex:0 0 auto; }}
 .tick {{ font-family:ui-monospace,monospace; font-size:10.5px; color:var(--mute);
          letter-spacing:.06em; }}
 .move {{ margin-left:auto; font-family:ui-monospace,monospace; font-size:15px;
          font-variant-numeric:tabular-nums; font-weight:650; }}

 .slot {{ border-top:1px solid var(--line); padding-top:8px; }}
 .q {{ font-size:9.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--mute);
       margin-bottom:3px; }}
 .a {{ font-size:13px; color:var(--dim); line-height:1.42; }}
 .a b {{ color:var(--fg); font-weight:620; }}
 .strip {{ display:block; margin-top:6px; border-radius:2px; }}
 .none {{ color:var(--mute); font-style:italic; }}

 /* ---- detalhe ---- */
 .back {{ font-size:12px; color:var(--mute); }}
 .dhead {{ display:flex; align-items:center; gap:12px; margin:6px 0 4px; }}
 .dname {{ font-size:26px; font-weight:700; color:var(--fg); }}
 .dmove {{ font-family:ui-monospace,monospace; font-size:26px; font-weight:700;
           font-variant-numeric:tabular-nums; }}
 .dlogo {{ width:34px; height:34px; border-radius:7px; background:#fff; padding:2px;
           object-fit:contain; }}
 .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:13px;
           padding:15px 17px; margin-bottom:12px; }}
 .ptitle {{ font-size:10px; letter-spacing:.11em; text-transform:uppercase;
            color:var(--mute); margin-bottom:9px; }}
 .bar {{ display:flex; align-items:center; gap:10px; margin:7px 0;
         font-family:ui-monospace,monospace; font-size:12.5px; }}
 .bar .lab {{ width:150px; color:var(--dim); font-family:inherit; }}
 .bar .val {{ width:74px; text-align:right; font-variant-numeric:tabular-nums;
              color:var(--fg); }}
 .bar .track {{ flex:1; height:9px; background:#1A2029; border-radius:5px; position:relative; }}
 .bar .fill {{ position:absolute; top:0; height:9px; border-radius:5px; }}
 .bar.driver .lab {{ color:var(--fg); font-weight:650; }}

 /* ---- triagem / screener ---- */
 .row {{ display:flex; align-items:baseline; gap:12px; padding:9px 0;
         border-bottom:1px solid var(--line); }}
 .row:last-child {{ border-bottom:none; }}
 .row .t {{ font-family:ui-monospace,monospace; font-size:12px; color:var(--fg); width:64px; }}
 .row .ti {{ font-size:13px; color:var(--fg); font-weight:600; width:190px; }}
 .row .ex {{ font-size:12.5px; color:var(--dim); flex:1; }}
 .pill {{ font-size:9.5px; letter-spacing:.08em; text-transform:uppercase; padding:2px 7px;
          border-radius:5px; border:1px solid var(--line); color:var(--mute); }}
 .pill.sent {{ color:var(--up); border-color:color-mix(in srgb,{T.UP} 45%,var(--line)); }}

 /* ---- método ---- */
 .mrow {{ display:flex; align-items:baseline; gap:12px; padding:7px 0;
          border-bottom:1px solid var(--line); }}
 .mrow:last-child {{ border-bottom:none; }}
 .mrow .ml {{ font-size:12.5px; color:var(--dim); flex:1; }}
 .mrow .mv {{ font-family:ui-monospace,monospace; font-size:13.5px; font-weight:650;
              color:var(--fg); font-variant-numeric:tabular-nums; width:66px;
              text-align:right; }}
 .mrow .ms {{ font-family:ui-monospace,monospace; font-size:10.5px; color:var(--mute);
              width:270px; }}
 .msub {{ font-size:12.5px; color:var(--dim); line-height:1.5; max-width:80ch;
          margin:-2px 0 10px; }}
</style>"""


def _marca() -> str:
    return '<span class="brand">INVESTI<span class="g">G</span>ATOR</span>'


@st.cache_data(show_spinner=False)
def _logo(ticker: str, grande: bool = False) -> str:
    """Logótipo embebido como `data:` URI: o navegador não faz pedidos a terceiros, o que
    mantém P2 (zero rede no render) e é coerente com a posição de privacidade."""
    try:
        uri = cached_logo(ticker)
        cls = "dlogo" if grande else "logo"
        return f'<img class="{cls}" src="{uri}" alt="">' if uri else ""
    except Exception:  # noqa: BLE001
        return ""


def _cor(v: float) -> str:
    return "var(--up)" if v > 0 else "var(--down)" if v < 0 else "var(--mute)"


def _seta(v: float) -> str:
    return T.ICON_UP if v > 0 else T.ICON_DOWN if v < 0 else T.ICON_FLAT


def _flagged(r: dict) -> bool:
    if "flagged" in r:
        return bool(r["flagged"])
    return abs(float(r.get("z") or 0.0)) >= LIMIAR


def _score(r: dict) -> float:
    if _flagged(r) and r.get("z") is None:
        return float("inf")
    return abs(float(r.get("z") or 0.0))


# ──────────────────────────────────────────────────────────────────────── grelha
def _cartao(r: dict) -> str:
    t = r["ticker"]
    move = float(r.get("move") or 0.0)
    flagged = _flagged(r)
    rar = r.get("rarity") or {}
    c, n = rar.get("count"), rar.get("n")

    return f"""<a class="card{' flagged' if flagged else ''}" href="?t={t}" target="_self">
 <div class="head">{_logo(t)}<span class="name">{display_name(t)}</span>
  <span class="tick">{t}</span>
  <span class="move" style="color:{_cor(move)}">{_seta(move)} {move * 100:+.2f}%</span></div>
 <div class="slot"><div class="q">Unusual for this stock?</div>
  <div class="a">{rotulo_raridade(c, n)}</div>{tira_distribuicao(c, n)}</div>
 <div class="slot"><div class="q">Company or market?</div>
  <div class="a">{rotulo_atribuicao(r.get('decomp'), move)}</div></div>
 <div class="slot"><div class="q">Happened before?</div>
  <div class="a">Open to see similar past cases and <b>what followed, measured</b>.</div></div>
</a>"""


def _grelha(snap) -> None:
    st.markdown(f'<div class="day">{resumo_do_dia(snap.linhas, LIMIAR)}</div>',
                unsafe_allow_html=True)
    ordenadas = sorted(snap.linhas, key=lambda r: -_score(r))
    st.markdown(f'<div class="grid">{"".join(_cartao(r) for r in ordenadas)}</div>',
                unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────── detalhe
def _barra_decomp(rotulo: str, valor: float, motor: bool, maior: float) -> str:
    largura = 0 if maior == 0 else abs(valor) / maior * 50
    lado = "left:50%" if valor >= 0 else f"right:{50}%"
    return (f'<div class="bar{" driver" if motor else ""}">'
            f'<span class="lab">{rotulo}</span>'
            f'<span class="val" style="color:{_cor(valor)}">{valor * 100:+.2f}%</span>'
            f'<span class="track"><span class="fill" style="{lado};width:{largura:.1f}%;'
            f'background:{_cor(valor)}"></span></span></div>')


def _raw(caminho: str) -> str:
    import os

    repo = os.getenv("INVESTIGATOR_HISTORY_REPO", "HS2000PT/DIMEIA")
    return f"https://raw.githubusercontent.com/{repo}/{HISTORY_BRANCH}/{caminho}"


@st.cache_data(ttl=120, show_spinner=False)
def _alertas() -> list:
    """Os alertas que o canal REALMENTE recebeu.

    É a única fonte: a app não recalcula texto nenhum. Se o canal e o painel discordassem, um
    dos dois estaria a mentir — e como o painel é o que o júri vê, seria o painel.

    É a única chamada de rede de toda a v4, e vive no detalhe (um clique), nunca na grelha,
    portanto não toca no critério P2.
    """
    try:
        from investigator.alerts_history import fetch_remote

        return fetch_remote(_raw("alerts_history.jsonl")) or []
    except Exception:  # noqa: BLE001
        return []


def _grafico(linha: dict, meses: int = 6):
    """Preço com os dias que o detector teria assinalado.

    Os marcadores NÃO são decorativos: vêm do `detect_all`, a mesma regra sem lookahead do
    `detect_latest`, aplicada a cada dia do ano. É a RQ1 desenhada sobre o passado.
    """
    import plotly.graph_objects as go

    fechos = linha.get("closes") or []
    if len(fechos) < 5:
        return None
    corte = max(0, len(fechos) - meses * 21)
    datas = [d for d, _ in fechos[corte:]]
    valores = [v for _, v in fechos[corte:]]
    dentro = set(datas)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datas, y=valores, mode="lines", name="Close",
        line={"color": T.FG_DIM, "width": 1.8},
        hovertemplate="%{x|%d %b %Y}<br><b>$%{y:.2f}</b><extra></extra>",
    ))

    por_data = dict(fechos)
    eventos = []
    for evento in linha.get("events") or []:
        d, z = evento[:2]
        direcao = evento[2] if len(evento) > 2 else (-1 if z is not None and z < 0 else 1)
        eventos.append((d, z, direcao))
    for sinal, cor, marca, rotulo in ((1, T.UP, "triangle-up", "flagged up"),
                                      (-1, T.DOWN, "triangle-down", "flagged down")):
        pts = [(d, z) for d, z, direcao in eventos
               if d in dentro and (direcao > 0) == (sinal > 0)]
        if not pts:
            continue
        fig.add_trace(go.Scatter(
            x=[d for d, _ in pts], y=[por_data[d] for d, _ in pts],
            mode="markers", name=rotulo,
            marker={"symbol": marca, "size": 11, "color": cor,
                    "line": {"width": 1, "color": T.BG}},
            customdata=[f"z {z:+.2f}" if z is not None else "flat baseline; z undefined"
                        for _, z in pts],
            hovertemplate=("%{x|%d %b %Y}<br>$%{y:.2f}"
                           "<br><b>flagged</b> · %{customdata}<extra></extra>"),
        ))

    fig.update_layout(
        height=310, margin={"l": 8, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": T.FG_MUTE, "size": 11},
        hovermode="x unified", showlegend=False,
        xaxis={"showgrid": False, "showspikes": True, "spikemode": "across",
               "spikethickness": 1, "spikecolor": T.LINE, "linecolor": T.LINE},
        yaxis={"gridcolor": T.LINE, "zeroline": False, "tickprefix": "$"},
    )
    return fig


def _detalhe(snap, ticker: str) -> None:
    linha = next((r for r in snap.linhas if r["ticker"] == ticker), None)
    st.markdown('<a class="back" href="?" target="_self">← all companies</a>',
                unsafe_allow_html=True)
    if linha is None:
        st.warning(f"{ticker} is not in the watchlist snapshot.", icon="⚠️")
        return

    move = float(linha.get("move") or 0.0)
    st.markdown(
        f'<div class="dhead">{_logo(ticker, True)}'
        f'<span class="dname">{display_name(ticker)}</span>'
        f'<span class="tick">{ticker}</span>'
        f'<span class="dmove" style="color:{_cor(move)}">{_seta(move)} '
        f'{move * 100:+.2f}%</span></div>',
        unsafe_allow_html=True,
    )

    fig = _grafico(linha)
    if fig is not None:
        st.markdown('<div class="panel" style="padding-bottom:4px">'
                    '<div class="ptitle">Price, and the days the detector would have '
                    'flagged</div></div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False})
        st.markdown(
            '<div class="a" style="margin:-6px 0 14px;color:var(--mute);font-size:12px">'
            'The markers are the same rule the system runs live, replayed over the past year — '
            'not annotations added by hand. Hover for the z-score on that day.</div>',
            unsafe_allow_html=True)

    rar = linha.get("rarity") or {}
    c, n = rar.get("count"), rar.get("n")
    st.markdown(
        f'<div class="panel"><div class="ptitle">Unusual for this stock?</div>'
        f'<div class="a">{rotulo_raridade(c, n)}</div>{tira_distribuicao(c, n, largura=420)}'
        f'<div class="a" style="margin-top:9px;color:var(--mute);font-size:12px">'
        f'Counted, not modelled. Turning the z-score into a probability would assume normal '
        f'returns; they have fat tails, so it would be wrong on exactly the days that matter.'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    d = linha.get("decomp")
    linhas_d = linhas_decomposicao(d, move)
    if linhas_d:
        maior = max(abs(v) for _, v, _ in linhas_d) or 1.0
        barras = "".join(_barra_decomp(rot, v, motor, maior) for rot, v, motor in linhas_d)
        st.markdown(
            f'<div class="panel"><div class="ptitle">Company or market?</div>'
            f'<div class="a" style="margin-bottom:10px">{rotulo_atribuicao(d, move)}</div>'
            f'{barras}'
            f'<div class="a" style="margin-top:10px;color:var(--mute);font-size:12px">'
            f'The three parts sum to the observed move by construction, so the line cannot lie. '
            f'Betas are estimated only on days before this one.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="panel"><div class="ptitle">Company or market?</div>'
            '<div class="a none">Attribution unavailable for this name today.</div></div>',
            unsafe_allow_html=True,
        )

    # ⚠️ Honestidade: dizer "no comparable past cases" seria afirmar que se PROCUROU e nao se
    # encontrou. Nao se procurou -- a recuperacao corre no modelo semantico, que esta fora desta
    # pagina de proposito (+7,5 s de carga a frio, medidos). Um ecra que confunde "nao ha" com
    # "nao vimos" e exactamente o tipo de silencio que este trabalho recusa.
    st.markdown(
        '<div class="panel"><div class="ptitle">Happened before?</div>'
        '<div class="a">Not checked on this page. Retrieval runs on the semantic model, which '
        'is deliberately not loaded here: measured, it adds about seven seconds to cold load.'
        '</div>'
        '<div class="a" style="margin-top:9px;color:var(--mute);font-size:12px">'
        'Where the answer does live: every news alert the Telegram channel received carries its '
        'own retrieved precedents and their measured outcome at +1, +3 and +5 days, always with '
        'the reminder that similar in topic is not similar in direction.</div></div>',
        unsafe_allow_html=True,
    )

    # Os alertas EXACTOS que o canal recebeu. A app não recalcula texto nenhum: se o canal e o
    # painel discordassem, um dos dois estaria a mentir, e seria o painel.
    meus = [a for a in _alertas() if getattr(a, "ticker", "") == ticker]
    if meus:
        itens = []
        for a in sorted(meus, key=lambda x: getattr(x, "date", ""), reverse=True)[:6]:
            # `split()` sem argumento colapsa QUALQUER espaço em branco, incluindo as quebras
            # de linha do alerta — que é o que se quer numa linha de tabela.
            texto = " ".join((getattr(a, "text", "") or "").split())
            itens.append(
                f'<div class="row"><span class="t">{getattr(a, "date", "")}</span>'
                f'<span class="ex">{texto[:260]}{"…" if len(texto) > 260 else ""}</span></div>')
        st.markdown(
            f'<div class="panel"><div class="ptitle">Alerts the channel received '
            f'({len(meus)} for this company)</div>{"".join(itens)}'
            f'<div class="a" style="margin-top:10px;color:var(--mute);font-size:12px">'
            f'Read from the shared history, word for word. Nothing here is recomputed — if the '
            f'channel and this page disagreed, this page would be the one lying.</div></div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="panel"><div class="ptitle">Alerts the channel received</div>'
            '<div class="a none">None for this company yet.</div></div>',
            unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────── screener
@st.cache_data(ttl=120, show_spinner=False)
def _gates() -> list[dict]:
    """Onde cada ticker parou hoje. Fail-open: sem registo, a vista di-lo.

    ⚠️ O campo do `GateRecord` chama-se **`stage`**, não `gate`. A primeira versão disto lia
    `r.gate`, e o resultado foi instrutivo: o `AttributeError` era engolido pelo `except` largo,
    a função devolvia lista vazia, e o ecrã dizia "sem registo" — indistinguível de um dia em
    que o runner ainda não tinha corrido. **Um fail-open largo demais transforma um erro de
    programação num estado plausível**, que é a pior maneira de esconder um defeito.

    Por isso o `except` passou a distinguir os dois casos: falta de ficheiro é normal e
    silenciosa; um erro a interpretar o que lá está aparece no log do servidor.
    """
    from investigator.gate_log import load_jsonl

    try:
        registos = load_jsonl(GATE_LOG)
    except OSError:
        return []
    ultimos: dict[str, dict] = {}
    for r in registos:
        try:
            ultimos[r.ticker] = {"ticker": r.ticker, "gate": r.stage,
                                 "detail": getattr(r, "detail", "") or ""}
        except AttributeError as exc:  # esquema mudou: dizer, não engolir
            print(f"[v4] registo de gates com esquema inesperado: {exc}")
    return list(ultimos.values())


def _screener(snap) -> None:
    st.markdown('<a class="back" href="?" target="_self">← all companies</a>',
                unsafe_allow_html=True)
    st.markdown('<div class="day">Why each company was quiet today</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="a" style="margin:-8px 0 14px;color:var(--mute);max-width:80ch">'
        'Every name the scan looked at, and the gate that stopped it — with the margin it '
        'missed by. Silence is a decision this system makes, so it should be inspectable.'
        '</div>',
        unsafe_allow_html=True,
    )
    registos = _gates()
    if not registos:
        st.info(
            "No gate log on this machine yet. The alert runner writes it on every scan "
            "(`data/gate_log.jsonl`).",
            icon="ℹ️",
        )
        return
    linhas = []
    for g in sorted(registos, key=lambda x: x["ticker"]):
        titulo, texto = explicar_silencio(g["gate"], g["detail"])
        pill = ' <span class="pill sent">sent</span>' if g["gate"] == "alerted" else ""
        linhas.append(f'<div class="row"><span class="t">{g["ticker"]}</span>'
                      f'<span class="ti">{titulo}{pill}</span>'
                      f'<span class="ex">{texto}</span></div>')
    st.markdown(f'<div class="panel">{"".join(linhas)}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────── main
@st.cache_data(ttl=45, show_spinner=False)
def _bloco_metodo(titulo: str, intro: str, numeros, veredicto: str = "") -> str:
    partes = []
    for n in numeros:
        nota = ""
        if n.note:
            nota = ('<br><span style="color:var(--mute);font-size:11.5px">'
                    f'{n.note}</span>')
        partes.append(f'<div class="mrow"><span class="ml">{n.label}{nota}</span>'
                      f'<span class="mv">{n.value}</span>'
                      f'<span class="ms">{n.source}</span></div>')
    linhas = "".join(partes)
    fim = (f'<div class="msub" style="margin:11px 0 0">{veredicto}</div>') if veredicto else ""
    return (f'<div class="panel"><div class="ptitle">{titulo}</div>'
            f'<div class="msub">{intro}</div>{linhas}{fim}</div>')


def _metodo() -> None:
    """A avaliação congelada, alcançável por um link (critério V7).

    Vive fora da grelha de propósito: quem abre o painel quer saber o que aconteceu às suas
    empresas; quem quer saber se pode confiar no método faz outra pergunta e merece uma página.

    Os números vêm de `app.method`, onde cada um guarda a **cadeia exacta** com que aparece no
    `.md` que o produziu — e `tests/test_method.py` abre esses ficheiros e exige-a lá. Se uma
    avaliação for recorrida, a suite parte em vez de a página continuar a afirmar um número que
    os documentos já não sustentam.
    """
    from app.method import ANOMALY, RETRIEVAL, TRIAGE, TRIAGE_BUDGET, TRIAGE_VERDICT

    st.markdown('<a class="back" href="?" target="_self">← all companies</a>',
                unsafe_allow_html=True)
    st.markdown('<div class="day">How this works, and how well</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="msub">Every number on the other pages is produced by the procedure below. '
        'These results are from the dissertation and are reported as they fell, including where '
        'the method lost. The right-hand column is the file each value comes from.</div>',
        unsafe_allow_html=True)

    st.markdown(_bloco_metodo(
        "Is the day unusual for this stock?",
        "A move is judged against the same company&rsquo;s own previous twenty days, not against a "
        "fixed percentage. The test is whether the rule fires at a comparable rate across "
        "companies of very different volatility. Lower spread is better.",
        ANOMALY), unsafe_allow_html=True)

    st.markdown(_bloco_metodo(
        "Are the retrieved precedents genuinely analogous?",
        "Share of the top five retrieved past headlines that come from the query&rsquo;s sector, "
        "with the company&rsquo;s own news excluded so the score cannot be won trivially. Higher "
        "is better.",
        RETRIEVAL), unsafe_allow_html=True)

    st.markdown(_bloco_metodo(
        "Does a trained model rank news better than simple volatility?",
        "Area under the precision&ndash;recall curve on a held-out period, from a model trained "
        "on 79,753 news&ndash;market examples.",
        TRIAGE + TRIAGE_BUDGET, TRIAGE_VERDICT), unsafe_allow_html=True)


def _instantaneo():
    """O instantâneo, com cache curta.

    Sem cache, cada interacção (abrir um detalhe, trocar de vista) voltaria a puxar o ficheiro
    pela rede em produção, e a v4 existe precisamente para não pagar rede no caminho de leitura.
    45 s fica abaixo do ciclo de 60 s do worker, portanto a cache nunca é o que faz um
    instantâneo parecer mais velho do que é.
    """
    return carregar()


def main() -> None:
    st.markdown(_css(), unsafe_allow_html=True)
    snap = _instantaneo()

    q = st.query_params
    ticker = (q.get("t") or "").upper()
    vista = q.get("view") or ""

    if snap is None:
        st.markdown(f'<div class="top">{_marca()}</div>', unsafe_allow_html=True)
        # Falha ABERTA e em voz alta: nunca um ecrã vazio que se confunda com um dia calmo.
        st.warning(
            "No precomputed snapshot available — neither on disk nor on the data branch. "
            "The worker writes and publishes one every cycle; run "
            "`python scripts/build_snapshot.py` to create one locally.",
            icon="⚠️",
        )
        return

    st.markdown(
        f'<div class="top">{_marca()}'
        f'<span class="{"age" if snap.fresco else "age stale"}">snapshot · '
        f'{snap.idade_legivel}</span>'
        f'<span class="nav"><a href="?" target="_self">Companies</a>'
        f'<a href="?view=quiet" target="_self">Why quiet?</a>'
        f'<a href="?view=method" target="_self">Method</a></span></div>',
        unsafe_allow_html=True,
    )

    if vista == "quiet":
        _screener(snap)
    elif vista == "method":
        _metodo()
    elif ticker:
        _detalhe(snap, ticker)
    else:
        _grelha(snap)

    # Uma vez por página, depois do conteúdo. Não se repete por cartão (H1) e não desaparece
    # (que era o defeito): é o que distingue este produto dos que resumem sem se comprometer.
    st.markdown(
        '<div class="foot">Markets move. We investigate. '
        'InvestiGator explains what already happened and shows the evidence behind it. '
        'It does not forecast prices and is not investment advice.</div>',
        unsafe_allow_html=True,
    )


main()
