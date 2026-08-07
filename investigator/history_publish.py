"""Publicar o histórico partilhado na branch de dados pela **API do GitHub**.

*Porque é que isto teve de existir.* Já havia um publicador, mas usa o `git` da linha de
comandos e exige que o ficheiro esteja dentro de um checkout da branch de dados. Isso funciona
numa VM; num contentor Heroku não, porque o *slug* implantado **não tem diretório `.git`**. O
mecanismo antigo não daria erro visível: é fail-open, por isso limitava-se a não fazer nada, e
o painel ficava para sempre sem ver os alertas novos.

*O que este módulo faz.* Lê o ficheiro atual na branch, junta-lhe as entradas locais que ainda
lá não estão, e volta a escrevê-lo. Nada de `git`, nada de checkout: só HTTP com um token.

*Porquê juntar em vez de substituir.* Podem existir dois produtores ao mesmo tempo (o vigia no
Heroku e o cron do GitHub Actions). Substituir faria o último a escrever apagar o trabalho do
outro. A junção é por **chave de entrada**, a mesma que já serve a deduplicação entre
produtores, e a escrita leva o `sha` que veio na leitura: se alguém escreveu entretanto, o
GitHub devolve 409 e nós desistimos desta ronda em vez de sobrepor.

*Fail-open, sempre.* Qualquer falha aqui é registada e ignorada. Publicar o histórico é um
apoio ao painel; nunca pode impedir o envio de um alerta.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path

from investigator.alerts_history import (
    _OMIT_WHEN_EMPTY,
    HistoryEntry,
    load_jsonl,
    parse_jsonl_lines,
)

_API = "https://api.github.com"
DEFAULT_REPO = "HS2000PT/DIMEIA"
DEFAULT_BRANCH = "alerts-history"
DEFAULT_FILE = "alerts_history.jsonl"


def _enabled() -> bool:
    return os.environ.get("INVESTIGATOR_HISTORY_API") == "1"


def _token() -> str:
    return (os.environ.get("GITHUB_TOKEN") or "").strip()


def _request(url: str, token: str, method: str = "GET", payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "investigator-history-publisher")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _entry_key(e: HistoryEntry) -> str:
    """Chave de identidade de uma entrada, para a junção não duplicar.

    Usa a `key` quando existe (é a de deduplicação entre produtores). As entradas antigas não
    a têm, e para essas o par (data, texto) identifica de forma suficientemente segura.
    """
    return e.key or f"{e.date}|{e.text}"


def publish(path: str | Path, repo: str = "", branch: str = "",
            filename: str = "") -> str:
    """Junta o histórico local ao remoto e publica. Devolve uma linha de estado legível.

    Nunca levanta: qualquer erro vira texto de diagnóstico, porque o chamador está no meio do
    ciclo de alertas.
    """
    if not _enabled():
        return ""
    token = _token()
    if not token:
        return "[historico-api] INVESTIGATOR_HISTORY_API=1 mas falta o GITHUB_TOKEN."

    repo = repo or os.environ.get("INVESTIGATOR_HISTORY_REPO", DEFAULT_REPO)
    branch = branch or os.environ.get("INVESTIGATOR_HISTORY_BRANCH", DEFAULT_BRANCH)
    filename = filename or os.environ.get("INVESTIGATOR_HISTORY_FILE", DEFAULT_FILE)
    url = f"{_API}/repos/{repo}/contents/{filename}?ref={branch}"

    try:
        locais = load_jsonl(path)
    except Exception as exc:  # noqa: BLE001
        return f"[historico-api] não li o ficheiro local (ignorado): {type(exc).__name__}: {exc}"
    if not locais:
        return ""

    try:
        meta = _request(url, token)
        sha = meta.get("sha", "")
        bruto = base64.b64decode(meta.get("content", "")).decode("utf-8", "replace")
        remotos = parse_jsonl_lines(bruto.splitlines())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            sha, remotos = "", []  # primeira publicação
        else:
            return f"[historico-api] leitura falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[historico-api] leitura falhou (ignorado): {type(exc).__name__}"

    vistos = {_entry_key(e) for e in remotos}
    novos = [e for e in locais if _entry_key(e) not in vistos]
    if not novos:
        return ""

    # Serialização IDÊNTICA à de `save_jsonl`, e de propósito: é este ficheiro que a app lê e
    # que o `parse_jsonl_lines` interpreta. Reescrevê-lo noutro formato (por exemplo com os
    # campos vazios que a versão original omite) partiria a leitura sem dar erro aqui.
    juntos = remotos + novos
    corpo = "\n".join(
        json.dumps({k: v for k, v in asdict(e).items() if v or k not in _OMIT_WHEN_EMPTY},
                   ensure_ascii=False)
        for e in juntos
    ) + "\n"
    payload = {
        "message": f"Alertas: +{len(novos)} entrada(s) do vigia",
        "content": base64.b64encode(corpo.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    try:
        _request(f"{_API}/repos/{repo}/contents/{filename}", token, "PUT", payload)
        return f"[historico-api] publicadas {len(novos)} entrada(s) em {branch}."
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            return "[historico-api] conflito (outro produtor escreveu); tenta na próxima ronda."
        return f"[historico-api] escrita falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[historico-api] escrita falhou (ignorado): {type(exc).__name__}"


def publish_blob(path: str | Path, filename: str, repo: str = "", branch: str = "") -> str:
    """Publica um ficheiro inteiro na branch de dados, **substituindo** o que lá está.

    *Porque é que isto é diferente do `publish`.* O histórico é acumulativo e por isso junta-se
    por chave: perder uma entrada seria perder um alerta que aconteceu mesmo. Um instantâneo é o
    **estado agora** — a versão nova torna a antiga obsoleta por definição, e juntá-las não
    significaria nada. Logo: substituir.

    *Porque é que isto teve de existir.* O instantâneo do painel v4 é escrito pelo worker e lido
    pelo web. Na máquina do aluno é o mesmo disco e funciona; no Heroku são **dois dynos com
    sistemas de ficheiros separados e efémeros**, portanto o web nunca veria o ficheiro do
    worker e a v4 mostraria "sem instantâneo" para sempre. A branch de dados é o único sítio que
    os dois já sabem partilhar.

    *Sem `sha` prévio não há escrita possível* — o GitHub exige-o para substituir. Um 409 aqui é
    outro produtor a escrever ao mesmo tempo, e a resposta certa é desistir desta ronda: o
    próximo ciclo é daqui a 60 s e traz dados mais recentes de qualquer maneira.

    Nunca levanta. Devolve uma linha de estado legível (vazia quando desligado).
    """
    if not _enabled():
        return ""
    token = _token()
    if not token:
        return "[instantaneo-api] INVESTIGATOR_HISTORY_API=1 mas falta o GITHUB_TOKEN."

    repo = repo or os.environ.get("INVESTIGATOR_HISTORY_REPO", DEFAULT_REPO)
    branch = branch or os.environ.get("INVESTIGATOR_HISTORY_BRANCH", DEFAULT_BRANCH)

    try:
        corpo = Path(path).read_bytes()
    except Exception as exc:  # noqa: BLE001
        return f"[instantaneo-api] não li o ficheiro local (ignorado): {type(exc).__name__}"

    sha = ""
    try:
        meta = _request(f"{_API}/repos/{repo}/contents/{filename}?ref={branch}", token)
        sha = meta.get("sha", "")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:  # 404 = primeira publicação, e é normal
            return f"[instantaneo-api] leitura falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[instantaneo-api] leitura falhou (ignorado): {type(exc).__name__}"

    payload = {
        "message": "Painel: instantaneo do ciclo",
        "content": base64.b64encode(corpo).decode("ascii"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    try:
        _request(f"{_API}/repos/{repo}/contents/{filename}", token, "PUT", payload)
        return f"[instantaneo-api] publicado {filename} em {branch}."
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            return "[instantaneo-api] conflito (outro produtor); tenta na próxima ronda."
        return f"[instantaneo-api] escrita falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[instantaneo-api] escrita falhou (ignorado): {type(exc).__name__}"


def publish_safe(path: str | Path) -> None:
    """Como `publish`, mas imprime o estado e engole tudo. É o que o runner chama."""
    try:
        msg = publish(path)
    except Exception as exc:  # noqa: BLE001
        msg = f"[historico-api] falhou (ignorado): {type(exc).__name__}: {exc}"
    if msg:
        print(msg)
