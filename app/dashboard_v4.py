"""Painel v4 — a grelha que LÊ em vez de calcular.

Construído **ao lado** da v3, que continua a ser o que o `Procfile` serve. Nada aqui toca no
motor, nos congelados, nem na v3.

AS TRÊS DECISÕES QUE O ESTUDO DE MERCADO E A MEDIÇÃO TOMARAM POR MIM
--------------------------------------------------------------------
1. **Ler um instantâneo, não calcular.** A v3 faz doze idas à rede antes da primeira pintura.
   Medido: construir a frio 4,92 s · calcular com cache quente 0,870 s · **ler 0,011 s**. É a
   correcção de arquitectura, e é ela — não o CSS, não o framework — que responde a "laggy".
2. **Ficar em Streamlit.** Consequência directa da medição acima: trocar de framework sem
   pré-computar mantinha o defeito; pré-computar sem trocar remove-o quase todo. A migração
   teria de se justificar por controlo de interacção, não por velocidade.
3. **Estrutura fixa de resposta.** As três perguntas do trabalho aparecem como três secções
   **nomeadas, na mesma ordem, em todos os cartões** — incluindo quando a resposta é "nada
   aconteceu". Uma pergunta que só aparece às vezes ensina o leitor a não a procurar.

Correr:  streamlit run app/dashboard_v4.py
"""

from __future__ import annotations

import pathlib
import sys

# A app é lançada por caminho (`streamlit run app/dashboard_v4.py`), e nesse modo o Python põe no
# `sys.path` a pasta do SCRIPT, não a raiz. Sem esta guarda, `import app...` rebenta — foi um
# defeito real da v3, e a causa não foi o código: foi ter sido verificada com `python -m`, que
# acrescenta o directório actual e esconde o problema.
_RAIZ = pathlib.Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

import streamlit as st  # noqa: E402

from app import ui_tokens as T  # noqa: E402
from app.snapshot_io import carregar, resumo_do_dia, tira_distribuicao  # noqa: E402
from investigator.branding.logos import cached_logo  # noqa: E402
from investigator.news_fetcher.relevance import display_name  # noqa: E402

st.set_page_config(page_title="InvestiGator", page_icon="🐊", layout="wide")

LIMIAR = 1.5


def _css() -> str:
    return f"""<style>
 :root {{
   --bg:{T.BG}; --panel:{T.PANEL}; --line:{T.LINE};
   --fg:{T.FG}; --dim:{T.FG_DIM}; --mute:{T.FG_MUTE};
   --up:{T.UP}; --down:{T.DOWN}; --flag:{T.FLAG};
   --strip-on:{T.FLAG}; --strip-off:#242C38;
 }}
 .stApp {{ background:var(--bg); }}
 .block-container {{ padding:0.9rem 1.1rem 2rem; max-width:1920px; }}
 #MainMenu, footer, header {{ visibility:hidden; }}

 .top {{ display:flex; align-items:baseline; gap:14px; flex-wrap:wrap;
         border-bottom:1px solid var(--line); padding-bottom:9px; margin-bottom:12px; }}
 .brand {{ font-weight:700; letter-spacing:.16em; font-size:13px; color:var(--fg); }}
 .age {{ font-family:ui-monospace,monospace; font-size:11.5px; color:var(--mute); }}
 .age.stale {{ color:var(--flag); }}

 /* C1: a resposta ao dia ANTES de qualquer cartão */
 .day {{ font-size:19px; color:var(--fg); font-weight:600; margin:2px 0 16px;
         line-height:1.35; max-width:78ch; }}

 .grid {{ display:grid; gap:12px; grid-template-columns:repeat(4,minmax(0,1fr)); }}
 @media (max-width:1500px) {{ .grid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} }}
 @media (max-width:1080px) {{ .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
 @media (max-width:700px)  {{ .grid {{ grid-template-columns:1fr; }} }}

 .card {{ background:var(--panel); border:1px solid var(--line); border-radius:13px;
          padding:13px 14px 12px; display:flex; flex-direction:column; gap:9px; }}
 .card.flagged {{ border-color:color-mix(in srgb,var(--flag) 55%,var(--line)); }}
 .head {{ display:flex; align-items:baseline; gap:8px; }}
 .name {{ font-weight:650; font-size:14.5px; color:var(--fg); }}
 .logo {{ width:19px; height:19px; border-radius:4px; object-fit:contain;
          background:#fff; padding:1px; flex:0 0 auto; }}
 .tick {{ font-family:ui-monospace,monospace; font-size:10.5px; color:var(--mute);
          letter-spacing:.06em; }}
 .move {{ margin-left:auto; font-family:ui-monospace,monospace; font-size:15px;
          font-variant-numeric:tabular-nums; font-weight:650; }}

 /* C2: as três perguntas, nomeadas, sempre na mesma ordem */
 .slot {{ border-top:1px solid var(--line); padding-top:8px; }}
 .q {{ font-size:9.5px; letter-spacing:.1em; text-transform:uppercase; color:var(--mute);
       margin-bottom:3px; }}
 .a {{ font-size:13px; color:var(--dim); line-height:1.42; }}
 .a b {{ color:var(--fg); font-weight:620; }}
 .strip {{ display:block; margin-top:6px; border-radius:2px; }}
 .none {{ color:var(--mute); font-style:italic; }}
</style>"""


@st.cache_data(show_spinner=False)
def _logo(ticker: str) -> str:
    """Logótipo embebido como `data:` URI — o navegador não faz pedidos a terceiros, o que é
    coerente com a posição de privacidade e mantém o critério P2 (zero rede no render)."""
    try:
        uri = cached_logo(ticker)
        return f'<img class="logo" src="{uri}" alt="">' if uri else ""
    except Exception:  # noqa: BLE001
        return ""


def _cartao(r: dict) -> str:
    t = r["ticker"]
    move = float(r.get("move") or 0.0)
    z = float(r.get("z") or 0.0)
    flagged = abs(z) >= LIMIAR
    cor = "var(--up)" if move > 0 else "var(--down)" if move < 0 else "var(--mute)"
    seta = T.ICON_UP if move > 0 else T.ICON_DOWN if move < 0 else T.ICON_FLAT

    # ── 1. É invulgar? ─────────────────────────────────────────────────────────
    rar = r.get("rarity") or {}
    c, n = rar.get("count"), rar.get("n")
    if n:
        if c == 0:
            r1 = f"<b>No other day</b> in the last {n} trading days moved this much."
        else:
            r1 = f"<b>{c} of the last {n}</b> trading days moved this much or more."
    else:
        r1 = '<span class="none">Not enough history to say.</span>'
    strip = tira_distribuicao(c, n)

    # ── 2. Empresa ou mercado? ─────────────────────────────────────────────────
    d = r.get("decomp")
    if d:
        nomes = {"market": "the market as a whole", "sector": "its sector",
                 "company": "the company itself"}
        r2 = f"Mostly <b>{nomes.get(d.get('driver'), d.get('driver'))}</b>."
        oposto = [k for k in ("market", "sector", "company")
                  if d.get(k) is not None and d[k] * move < 0]
        if oposto:
            r2 += f" {nomes.get(oposto[0], oposto[0]).capitalize()} pulled the other way."
    else:
        r2 = '<span class="none">Attribution unavailable for this name today.</span>'

    # ── 3. Já aconteceu antes? ─────────────────────────────────────────────────
    # Honesto: a contagem exige o modelo semântico, e carregá-lo na página de entrada mede-se em
    # +7,5 s (emenda V6′). Fica a UM clique, mas o SÍTIO da resposta é sempre este.
    r3 = 'Open to see similar past cases and <b>what followed, measured</b>.'

    return f"""<div class="card{' flagged' if flagged else ''}">
 <div class="head">{_logo(t)}<span class="name">{display_name(t)}</span>
  <span class="tick">{t}</span>
  <span class="move" style="color:{cor}">{seta} {move * 100:+.2f}%</span></div>
 <div class="slot"><div class="q">Unusual for this stock?</div>
  <div class="a">{r1}</div>{strip}</div>
 <div class="slot"><div class="q">Company or market?</div><div class="a">{r2}</div></div>
 <div class="slot"><div class="q">Happened before?</div><div class="a">{r3}</div></div>
</div>"""


def main() -> None:
    st.markdown(_css(), unsafe_allow_html=True)
    snap = carregar()

    if snap is None:
        st.markdown('<div class="top"><span class="brand">INVESTIGATOR</span></div>',
                    unsafe_allow_html=True)
        # Falha ABERTA e em voz alta: nunca um ecrã vazio que pareça um dia calmo.
        st.warning(
            "No precomputed snapshot available. The worker writes it every cycle; "
            "run `python scripts/build_snapshot.py` to create one locally.",
            icon="⚠️",
        )
        return

    classe = "age" if snap.fresco else "age stale"
    st.markdown(
        f'<div class="top"><span class="brand">INVESTIGATOR</span>'
        f'<span class="{classe}">snapshot · {snap.idade_legivel}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="day">{resumo_do_dia(snap.linhas, LIMIAR)}</div>',
                unsafe_allow_html=True)

    ordenadas = sorted(snap.linhas, key=lambda r: -abs(float(r.get("z") or 0.0)))
    st.markdown(f'<div class="grid">{"".join(_cartao(r) for r in ordenadas)}</div>',
                unsafe_allow_html=True)


main()
