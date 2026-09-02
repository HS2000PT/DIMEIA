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


# ══ FICHEIROS ACUMULATIVOS ═════════════════════════════════════════════════════════════════
# ⚠️ **O defeito que estas duas funções corrigem, medido em produção a 2026-09-02.**
#
# O registo de votos usava o `publish_blob`, que **substitui**. O `publish_blob` foi escrito
# para o instantâneo do painel, onde substituir é a operação certa porque a versão nova torna a
# antiga obsoleta. Um registo de votos é o contrário: é acumulativo, como o histórico de
# alertas, e o próprio `publish` já dizia porquê — «perder uma entrada seria perder um alerta
# que aconteceu mesmo».
#
# O que acontecia na prática, em três passos, nenhum deles visível:
#   1. um deploy reinicia o dyno e o `data/feedback.jsonl` local desaparece (disco efémero);
#   2. chega o primeiro voto novo e é escrito sozinho no ficheiro local;
#   3. a publicação substitui o ficheiro da branch — que tinha tudo — por essa única linha.
# Resultado observado: os seis votos recolhidos antes do deploy das 19:10 desapareceram.
#
# Havia um segundo defeito, da mesma família e igualmente silencioso: o `/api/feedback` lia o
# ficheiro **local do dyno web**, e quem escreve os votos é o **dyno worker**. São dois sistemas
# de ficheiros separados, portanto o painel mostrava zero votos mesmo com votos a chegar. É
# exactamente a razão pela qual o instantâneo do painel passou pela branch de dados; faltava
# aplicar a mesma conclusão aqui.


def fetch_jsonl(filename: str, repo: str = "", branch: str = "") -> list[str] | None:
    """Lê as linhas de um JSONL da branch de dados. `None` quando não deu para ler.

    `None` e `[]` querem dizer coisas diferentes, e a diferença importa: `[]` é «li, e está
    vazio», e autoriza escrever; `None` é «não consegui ler», e nesse caso escrever seria
    substituir às cegas. Quem chama tem de distinguir.
    """
    if not _enabled():
        return None
    token = _token()
    if not token:
        return None
    repo = repo or os.environ.get("INVESTIGATOR_HISTORY_REPO", DEFAULT_REPO)
    branch = branch or os.environ.get("INVESTIGATOR_HISTORY_BRANCH", DEFAULT_BRANCH)
    try:
        meta = _request(f"{_API}/repos/{repo}/contents/{filename}?ref={branch}", token)
        bruto = base64.b64decode(meta.get("content", "")).decode("utf-8")
        return [ln for ln in bruto.splitlines() if ln.strip()]
    except urllib.error.HTTPError as exc:
        return [] if exc.code == 404 else None      # 404 = ainda não existe, e isso é legítimo
    except Exception:  # noqa: BLE001
        return None


def publish_jsonl_merge(path: str | Path, filename: str,
                        repo: str = "", branch: str = "") -> str:
    """Publica um JSONL acumulativo **juntando** as linhas locais às remotas.

    A junção é por linha inteira. Cada voto traz o instante em que foi dado, portanto duas
    linhas iguais são o mesmo voto e uma delas é ruído de reenvio; qualquer diferença real
    (outro votante, outra chave, outro instante) dá uma linha diferente e sobrevive.

    A ordem é preservada: primeiro o que já lá estava, depois o que é novo. Um registo
    append-only lido de trás para a frente continua a dar o voto mais recente de cada pessoa,
    que é o que a `votos_efetivos` assume.

    Nunca levanta, e nunca escreve às cegas: se a leitura falhar, desiste desta ronda. O
    ficheiro local fica na mesma, e a ronda seguinte volta a tentar.
    """
    if not _enabled():
        return ""
    token = _token()
    if not token:
        return "[votos-api] INVESTIGATOR_HISTORY_API=1 mas falta o GITHUB_TOKEN."

    repo = repo or os.environ.get("INVESTIGATOR_HISTORY_REPO", DEFAULT_REPO)
    branch = branch or os.environ.get("INVESTIGATOR_HISTORY_BRANCH", DEFAULT_BRANCH)

    try:
        locais = [ln for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]
    except FileNotFoundError:
        locais = []
    except Exception as exc:  # noqa: BLE001
        return f"[votos-api] não li o ficheiro local (ignorado): {type(exc).__name__}"

    sha = ""
    remotas: list[str] = []
    try:
        meta = _request(f"{_API}/repos/{repo}/contents/{filename}?ref={branch}", token)
        sha = meta.get("sha", "")
        remotas = [ln for ln in base64.b64decode(meta.get("content", ""))
                   .decode("utf-8").splitlines() if ln.strip()]
    except urllib.error.HTTPError as exc:
        if exc.code != 404:      # 404 = primeira publicação; qualquer outro erro é desistir
            return f"[votos-api] leitura falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[votos-api] leitura falhou (ignorado): {type(exc).__name__}"

    vistas = set(remotas)
    novas: list[str] = []
    for ln in locais:
        if ln not in vistas:
            vistas.add(ln)
            novas.append(ln)
    if not novas:
        return f"[votos-api] {filename} já tinha tudo ({len(remotas)} linhas)."

    corpo = ("\n".join(remotas + novas) + "\n").encode("utf-8")
    payload = {"message": f"Votos: +{len(novas)}",
               "content": base64.b64encode(corpo).decode("ascii"), "branch": branch}
    if sha:
        payload["sha"] = sha
    try:
        _request(f"{_API}/repos/{repo}/contents/{filename}", token, "PUT", payload)
        return f"[votos-api] {filename}: +{len(novas)}, total {len(remotas) + len(novas)}."
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            return "[votos-api] conflito (outro produtor); tenta na próxima ronda."
        return f"[votos-api] escrita falhou (ignorado): HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return f"[votos-api] escrita falhou (ignorado): {type(exc).__name__}"
