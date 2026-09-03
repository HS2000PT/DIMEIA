"""Registo dos votos dos leitores sobre os alertas.

**Porque é um ficheiro e não uma tabela.** O sistema corre na Heroku, onde o disco é efémero e
o `web` e o `worker` são dynos distintos com discos distintos. O projeto já resolveu este
problema duas vezes — para o `gate_log` e para o `predictions_log` — publicando o ficheiro numa
branch de dados que ambos leem. Este segue o mesmo caminho, pelo mesmo motivo, e é por isso
JSONL e não SQLite: um ficheiro de linhas é publicável, versionado, e legível por qualquer
análise sem abrir uma ligação.

**Porque é acrescento e nunca alteração.** Cada voto é uma linha nova, mesmo quando a pessoa
muda de opinião. A contagem resolve-se na leitura, onde o último voto de cada par
(votante, alerta) ganha. Assim o ficheiro é ao mesmo tempo o estado e o seu histórico: dá para
perguntar quantas pessoas mudaram de ideias depois de ler a análise completa, que é uma
pergunta que a versão mutável não permitiria fazer.

Puro: só constrói, lê e resume registos. Quem os persiste e publica é `api/main.py`.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from pathlib import Path

UTIL = "u"
INUTIL = "n"
RETIRAR = "d"


@dataclass(frozen=True)
class FeedbackRecord:
    """Um voto. `votante` é sempre o resumo criptográfico, nunca o identificador do Telegram.

    `chave_alerta` é a chave curta que o botão transportou, e é a que liga o voto ao alerta no
    histórico partilhado. `message_id` e `chat_id` guardam-se porque são o que permite editar o
    teclado da mensagem para lhe pôr a contagem — e porque, se a chave alguma vez colidir, são
    eles que desfazem o empate.
    """

    chave_alerta: str
    votante: str
    acao: str  # "u" | "n" | "d" (retirada dos votos anteriores da pessoa)
    at: str  # ISO 8601 UTC
    chat_id: str = ""
    message_id: int = 0
    ticker: str = ""


_CAMPOS = frozenset(f.name for f in fields(FeedbackRecord))


def agora() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_jsonl_lines(linhas: list[str]) -> list[FeedbackRecord]:
    """Interpreta linhas JSONL, ignorando as que não se leem.

    Uma linha corrompida — escrita truncada por um dyno reiniciado a meio — não pode fazer
    perder as boas. É o mesmo critério do `alerts_history`.
    """
    saida: list[FeedbackRecord] = []
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        try:
            carga = json.loads(linha)
        except (ValueError, TypeError):
            continue
        if not isinstance(carga, dict) or carga.get("acao") not in (UTIL, INUTIL, RETIRAR):
            continue
        try:
            saida.append(FeedbackRecord(**{k: v for k, v in carga.items() if k in _CAMPOS}))
        except TypeError:
            continue
    return saida


def load_jsonl(caminho: str | Path) -> list[FeedbackRecord]:
    """Lê o registo. Ficheiro inexistente é lista vazia, e não um erro: antes do primeiro voto
    é exatamente esse o estado do mundo."""
    p = Path(caminho)
    if not p.exists():
        return []
    return parse_jsonl_lines(p.read_text(encoding="utf-8").splitlines())


def append_jsonl(registo: FeedbackRecord, caminho: str | Path,
                 max_entries: int = 50000) -> None:
    """Acrescenta um voto ao ficheiro, criando-o se preciso, e apara o mais antigo."""
    p = Path(caminho)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(registo), ensure_ascii=False) + "\n")
    linhas = p.read_text(encoding="utf-8").splitlines()
    if len(linhas) > max_entries:
        p.write_text("\n".join(linhas[-max_entries:]) + "\n", encoding="utf-8")


def _cronologicos(registos: list[FeedbackRecord]) -> list[FeedbackRecord]:
    """Ordena por instante, preservando a ordem de chegada em empates.

    Uma recuperação pode voltar a acrescentar hoje uma linha antiga. Usar apenas a posição no
    ficheiro faria esse voto antigo substituir um voto posterior da mesma pessoa.
    """
    numerados = enumerate(registos)
    return [r for _, r in sorted(numerados, key=lambda par: (par[1].at or "", par[0]))]


def votos_efetivos(registos: list[FeedbackRecord]) -> dict[tuple[str, str], FeedbackRecord]:
    """Último voto por pessoa e alerta, respeitando retiradas de participação.

    Uma linha ``d`` é uma marca de retirada: elimina da análise todos os votos anteriores da
    pessoa. Mantém-se no registo acrescentável para a retirada sobreviver às junções entre
    produtores. Se a pessoa voltar a votar depois, esse novo gesto constitui nova participação.
    """
    efetivos: dict[tuple[str, str], FeedbackRecord] = {}
    for r in _cronologicos(registos):
        if r.acao == RETIRAR:
            efetivos = {par: voto for par, voto in efetivos.items() if par[0] != r.votante}
            continue
        efetivos[(r.votante, r.chave_alerta)] = r
    return efetivos


def contagem(registos: list[FeedbackRecord], chave_alerta: str) -> tuple[int, int]:
    """(úteis, inúteis) para um alerta, já com um voto por pessoa."""
    uteis = inuteis = 0
    for (_votante, chave), r in votos_efetivos(registos).items():
        if chave != chave_alerta:
            continue
        if r.acao == UTIL:
            uteis += 1
        else:
            inuteis += 1
    return uteis, inuteis


def resumo(registos: list[FeedbackRecord]) -> dict[str, int]:
    """Os números que a tese vai reportar. Sem interpretação, só contagem.

    `pessoas` é o que impede a leitura mais fácil e mais errada — a de tomar o número de votos
    por número de pessoas. Com uma amostra desta dimensão, um leitor entusiasta que vote em
    trinta alertas seria, sem este campo, indistinguível de trinta leitores.
    """
    efetivos = votos_efetivos(registos)
    c = Counter(r.acao for r in efetivos.values())
    ultimas_acoes: dict[tuple[str, str], str] = {}
    mudancas = repeticoes = retiradas = 0
    votos_brutos = 0
    for r in _cronologicos(registos):
        if r.acao == RETIRAR:
            retiradas += 1
            ultimas_acoes = {
                par: acao for par, acao in ultimas_acoes.items() if par[0] != r.votante
            }
            continue
        votos_brutos += 1
        par = (r.votante, r.chave_alerta)
        if par in ultimas_acoes:
            if ultimas_acoes[par] == r.acao:
                repeticoes += 1
            else:
                mudancas += 1
        ultimas_acoes[par] = r.acao
    return {
        "votos_brutos": votos_brutos,
        "votos_efetivos": len(efetivos),
        "uteis": c.get(UTIL, 0),
        "inuteis": c.get(INUTIL, 0),
        "pessoas": len({v for v, _ in efetivos}),
        "alertas_votados": len({a for _, a in efetivos}),
        "mudancas_de_voto": mudancas,
        "repeticoes_iguais": repeticoes,
        "retiradas": retiradas,
    }
