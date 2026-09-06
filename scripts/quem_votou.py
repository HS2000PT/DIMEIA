"""O autor está entre os votantes da Secção 5.6.5? Responde sem escrever o identificador.

⚠️ **PORQUE EXISTE.** A Secção 5.6.5 reporta 41 de 42 votos efetivos como «útil», com uma só
pessoa a representar 67% deles. Um arguente que faça a subtração pergunta, e com razão, quem são
as três pessoas e se o autor é uma delas. O registo **não sabe responder**: o que guarda é um
resumo BLAKE2b com sal, e o identificador do Telegram nunca é armazenado
(`investigator/telegram_bot/feedback.py::resumir_votante`). Mas quem tem o sal e o seu próprio
identificador reconstrói o resumo, e a pergunta fica respondida em segundos.

⚠️ **O IDENTIFICADOR É PEDIDO POR ENTRADA INTERATIVA E NÃO É ESCRITO EM LADO NENHUM.** Um
identificador colado num ficheiro versionado, ou passado por argumento e deixado no histórico da
linha de comandos, seria exactamente o dado pessoal que o resto do sistema evita guardar. O que
este procedimento imprime é apenas quantos votos o resumo tem, e nunca o resumo nem o sal.

⚠️ **A CONTAGEM É A MESMA DA SECÇÃO 5.6.5, e não uma segunda contagem parecida.** O filtro que
exclui votos sem alerta correspondente é **importado** do `analyse_feedback.py`, e não
reimplementado: duas contagens que se pretendem iguais e vivem em sítios diferentes acabam
sempre por divergir, e esta dissertação já pagou esse defeito noutro sítio.

    python scripts/quem_votou.py
"""

from __future__ import annotations

import pathlib
import runpy
import subprocess
import sys
import tempfile
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parents[1]
FICHEIROS = ("feedback.jsonl", "alerts_history.jsonl")


def _da_branch() -> tuple[dict[str, list[str]], str] | None:
    """Os dois registos da branch de dados, e como foram obtidos."""
    try:
        from investigator.history_publish import fetch_jsonl

        lidos = {n: fetch_jsonl(n) for n in FICHEIROS}
        if all(v is not None for v in lidos.values()):
            return lidos, "API autenticada"  # type: ignore[return-value]
    except Exception:  # noqa: BLE001 — qualquer falha cai no git, que é o caminho de reserva
        pass
    try:
        subprocess.run(
            ["git", "fetch", "--quiet", "origin",
             "+refs/heads/alerts-history:refs/remotes/origin/alerts-history"],
            cwd=REPO, capture_output=True, timeout=120, check=False)
        lidos = {}
        for n in FICHEIROS:
            r = subprocess.run(["git", "show", f"origin/alerts-history:{n}"],
                               cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=120)
            if r.returncode != 0:
                return None
            lidos[n] = r.stdout.splitlines()
        return lidos, "git origin/alerts-history"
    except Exception:  # noqa: BLE001
        pass
    return None


def _do_disco() -> tuple[dict[str, list[str]], str] | None:
    lidos = {}
    for n in FICHEIROS:
        f = REPO / "data" / n
        if not f.exists():
            return None
        lidos[n] = f.read_text(encoding="utf-8", errors="replace").splitlines()
    return lidos, "ficheiros LOCAIS"


def main() -> int:
    from investigator import config
    from investigator import feedback_log as FL
    from investigator.telegram_bot.feedback import resumir_votante

    if not config.FEEDBACK_SALT:
        print("ERRO: FEEDBACK_SALT não está configurado neste ambiente.")
        print("      Sem o sal o resumo não é reconstruível, e a pergunta fica sem resposta.")
        print("      O sal está no .env e nas variáveis de configuração do alojamento.")
        return 2

    lido = _da_branch()
    if lido is None:
        lido = _do_disco()
        if lido is None:
            print("ERRO: não consegui ler a branch de dados nem os ficheiros locais.")
            return 2
        print("⚠️  A branch não respondeu. Os ficheiros locais só têm os votos que passaram por")
        print("    esta máquina, e podem não ser a amostra que a Secção 5.6.5 reporta.\n")
    linhas, origem = lido

    # O MESMO filtro da Secção 5.6.5, importado e não reescrito.
    af = runpy.run_path(str(REPO / "scripts" / "analyse_feedback.py"), run_name="nao_main")
    with tempfile.TemporaryDirectory() as td:
        alertas = pathlib.Path(td) / "alerts_history.jsonl"
        alertas.write_text("\n".join(linhas["alerts_history.jsonl"]), encoding="utf-8")
        chaves = af["chaves_do_historico"](alertas)

    registos = FL.parse_jsonl_lines(linhas["feedback.jsonl"])
    registos, excluidos = af["_filtrar_por_historico"](registos, chaves)
    efetivos = FL.votos_efetivos(registos)
    if not efetivos:
        print(f"Origem: {origem}. Nenhum voto efetivo no registo; nada a comparar.")
        return 0

    por_pessoa = Counter(v for v, _ in efetivos)
    total = len(efetivos)
    dominante, n_dominante = por_pessoa.most_common(1)[0]
    print(f"Origem: {origem} · {total} votos efetivos de {len(por_pessoa)} pessoas"
          f"{f' · {excluidos} excluídos por não corresponderem a alerta' if excluidos else ''}.")
    print(f"Votante dominante: {n_dominante} de {total} ({n_dominante / total:.0%}).\n")

    try:
        bruto = input("Identificador de utilizador do Telegram (não fica guardado): ").strip()
    except EOFError:
        print("\nERRO: é preciso um terminal interativo. O identificador não se passa por"
              " argumento de propósito.")
        return 2
    if not bruto:
        print("Nada introduzido; nada a verificar.")
        return 0

    resumo = resumir_votante(bruto, config.FEEDBACK_SALT)
    del bruto  # não fica em memória mais tempo do que o necessário
    meus = por_pessoa.get(resumo, 0)

    print()
    if meus == 0:
        print("ok  Esse identificador NÃO figura no registo. O autor não votou.")
        print("    Resposta a dar: «Verifiquei-o contra o registo, e nenhum dos resumos é o meu.»")
        return 0

    print(f"!!  Esse identificador figura no registo, com {meus} de {total} votos efetivos "
          f"({meus / total:.0%}).")
    if resumo == dominante:
        print("!!  É o VOTANTE DOMINANTE.")
        print("    A Secção 5.6.5 tem de o declarar antes da entrega. A proporção sem o votante")
        print("    dominante já não é reportada, por ficar abaixo do mínimo pré-registado, mas os")
        print("    98% incluem o autor e não podem ser lidos como retorno de terceiros.")
    else:
        print(f"    NÃO é o votante dominante, que tem {n_dominante} de {total}.")
        print("    A Secção 5.6.5 deve mesmo assim declarar a participação do autor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
