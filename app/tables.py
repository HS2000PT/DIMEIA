"""Filtrar, ordenar e paginar as tabelas do painel. Puro: sem Streamlit, sem rede.

**Porque é que isto não vive dentro de `dashboard.py`.** Pela mesma razão que as frases
foram para `verdict.py`: uma tabela que só se verifica abrindo um browser não se verifica.
Um filtro tem casos de fronteira a sério — o registo sem impacto medido, a página que
deixou de existir quando o filtro encolheu a lista, o "0,00%" que não é subida nem descida
— e cada um deles é uma linha errada no ecrã de alguém. Aqui são testes de milissegundos.

**A decisão de desenho que estas funções tornam possível:** a tabela mostra o que o
gráfico mostra. Não é uma segunda consulta aos dados com a sua própria noção de janela —
é a mesma lista, filtrada. Duas consultas paralelas divergem, e quando divergem ninguém dá
por isso, porque cada uma parece certa sozinha.
"""

from __future__ import annotations

import bisect
from math import ceil

# As opções de ordenação, na ordem em que aparecem no selector. Chaves aqui e não strings
# soltas nas chamadas: um erro de escrita passa a `KeyError` em vez de ordenação silenciosa
# pela opção errada.
ORDERS = ("Newest first", "Oldest first", "Largest move first")

DIRECTIONS = ("Any", "Up", "Down")

# Degraus do filtro de magnitude. Texto → fracção; "any" é 0,0 e deixa passar tudo,
# inclusive os registos sem impacto medido.
MAGNITUDES: dict[str, float] = {"any": 0.0, "≥1%": 0.01, "≥2%": 0.02, "≥5%": 0.05}


def _num(row: dict, key: str) -> float | None:
    """O valor numérico de uma coluna, ou `None` quando não é comparável.

    Um impacto pode faltar por duas razões diferentes e igualmente reais: a notícia é
    recente demais para o horizonte ter fechado, ou a série de preços tinha um buraco.
    As duas chegam aqui como `None` e nenhuma pode ser tratada como zero — zero é uma
    medição, ausência não é.
    """
    v = row.get(key)
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f  # NaN é ausência disfarçada de número


def filter_events(
    rows: list[dict],
    query: str = "",
    direction: str = "Any",
    min_abs: float = 0.0,
    key: str = "d1",
    text_key: str = "headline",
) -> list[dict]:
    """As linhas que sobrevivem aos filtros, na ordem em que entraram.

    **Os registos sem impacto medido passam quando não se filtra por impacto e caem quando
    se filtra.** É a única resposta honesta: se alguém pede "só quedas de 2% ou mais", uma
    linha cujo impacto ainda não fechou não é uma queda de 2% ou mais — mas também não é o
    contrário, e por isso não se mostra como se fosse.
    """
    q = query.strip().lower()
    saida = []
    for r in rows:
        if q and q not in str(r.get(text_key) or "").lower():
            continue
        if direction != "Any" or min_abs > 0:
            v = _num(r, key)
            if v is None:
                continue
            if direction == "Up" and v <= 0:
                continue
            if direction == "Down" and v >= 0:
                continue
            if abs(v) < min_abs:
                continue
        saida.append(r)
    return saida


def sort_events(rows: list[dict], order: str = ORDERS[0], key: str = "d1") -> list[dict]:
    """Ordena sem nunca deixar cair uma linha.

    Os registos sem valor vão para o **fim** em "Largest move first", nunca para o início:
    ordenar por magnitude e ver ausências no topo lê-se como se elas fossem as maiores.
    """
    if order == "Oldest first":
        return sorted(rows, key=lambda r: str(r.get("date") or ""))
    if order == "Largest move first":
        return sorted(rows, key=lambda r: (_num(r, key) is None,
                                           -abs(_num(r, key) or 0.0),
                                           str(r.get("date") or "")))
    return sorted(rows, key=lambda r: str(r.get("date") or ""), reverse=True)


def paginate(rows: list[dict], page: int, per_page: int = 8
             ) -> tuple[list[dict], int, int]:
    """`(linhas da página, página efectiva, total de páginas)`.

    **A página é corrigida para dentro dos limites, e é isso que interessa aqui.** O erro
    clássico desta função é escrever um filtro estando na página 5, o filtro deixar duas
    linhas, e a tabela ficar vazia — com dados, com filtros que combinam, e sem nenhuma
    mensagem. O utilizador conclui que não há nada. Devolver a página corrigida (em vez de
    só a fatia) é o que permite a quem desenha mostrar "3 de 3" e não "5 de 3".

    Uma lista vazia tem **uma** página, não zero: "Page 1 of 0" não quer dizer nada.
    """
    per_page = max(1, int(per_page))
    n_pages = max(1, ceil(len(rows) / per_page))
    efectiva = min(max(1, int(page)), n_pages)
    inicio = (efectiva - 1) * per_page
    return rows[inicio:inicio + per_page], efectiva, n_pages


def anchor(sessions: list[str], day: str) -> str | None:
    """A sessão em que uma data se desenha: a **primeira em ou depois** dela.

    Uma notícia de sábado não tem barra onde pousar. Antes não se desenhava de todo, e o
    resultado era o gráfico a mostrar 13 marcas enquanto a tabela listava 18 dias — a mesma
    janela a dar dois números diferentes, sem nada a explicar a diferença.

    A regra não é uma invenção para tapar esse buraco: é exactamente a que o sistema usa
    para alinhar eventos quando mede o impacto (`live_kb.mature_entry`, e a KB histórica
    antes dela). A marca aparece na sessão contra a qual os +1d/+5d daquela linha foram
    medidos, que é o sítio honesto.

    `None` quando a data cai fora do que está no ecrã — incluindo **antes** da primeira
    sessão. Esse caso importa mais do que parece: sem ele, um ano inteiro de notícias
    anteriores à janela ancorava todo na primeira barra e empilhava centenas de marcas
    num único ponto.

    É `bisect_left` e não `bisect_right`: com uma data que é exactamente uma sessão, a
    resposta tem de ser essa sessão, não a seguinte. `bisect_right` desviava **todas** as
    marcas um dia para a frente, e um desvio de um dia num gráfico de preços é invisível a
    olho e completamente errado.
    """
    if not sessions or day < sessions[0] or day > sessions[-1]:
        return None
    return sessions[bisect.bisect_left(sessions, day)]


def within(rows: list[dict], desde: str | None, ate: str | None) -> list[dict]:
    """As linhas dentro da janela de datas mostrada no gráfico (ISO, inclusive).

    Recebe as datas em vez de as calcular: quem sabe que janela está desenhada é o gráfico,
    e voltar a deduzi-la aqui a partir do rótulo do intervalo seria a segunda consulta
    paralela que este módulo existe para não haver. Se o gráfico mudar de regra, a tabela
    acompanha sem que ninguém se lembre de a actualizar.
    """
    if not desde and not ate:
        return list(rows)
    saida = []
    for r in rows:
        d = str(r.get("date") or "")
        if not d:
            continue
        if desde and d < desde:
            continue
        if ate and d > ate:
            continue
        saida.append(r)
    return saida
