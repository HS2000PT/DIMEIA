"""A série de fechos da QI1 está fixada, versionada, e é ela que as avaliações leem.

⚠️ POR QUE E QUE ESTE FICHEIRO EXISTE. Ate 2026-09-10 o `evaluate_anomaly.py` e o
`evaluate_anomaly_ext.py` iam ao yfinance ao vivo, sem cache e sem serie fixada, e o segundo
tinha por baixo uma cadeia de cinco fontes de recurso. Eram as duas unicas avaliacoes do
trabalho a depender da rede no momento da leitura, e produzem numeros que a dissertacao cita:
a amplitude da taxa de disparo, o F1 do z-score, e o do Isolation Forest.

E A DERIVA NAO ERA HIPOTETICA. O proprio `evaluation_anomaly_ext.md` declarava que o Isolation
Forest diferia ~0,002 do congelado «porque o yfinance reajusta os fechos historicos a cada
dividendo novo», e apresentava isso como deriva documentada e irredutivel.

⚠️ E A CAUSA DECLARADA ESTAVA ERRADA, o que e a parte que interessa. Medido: **duas buscas da
mesma janela a MINUTOS de distancia devolvem fechos diferentes** -- 6e-05 na AAPL, 4e-05 na
NVDA, e zero na TSLA. E precisao de float32, nao acumulacao de dividendos. Basta para virar uma
decisao no limiar de um detetor que sinaliza uma fracao fixa dos pontos, e foi o que fez o F1 do
Isolation Forest andar 0,271 -> 0,270 -> 0,269 em tres corridas do mesmo dia.
"""

from __future__ import annotations

import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PASTA = RAIZ / "data" / "samples" / "precos_qi1"
INICIO, FIM = "2023-06-01", "2026-06-01"
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]


def test_a_serie_existe_e_esta_completa():
    """Quinze séries. Uma em falta faria a avaliação correr sobre catorze empresas.

    E publicaria uma amplitude entre catorze que no ecrã se lê exactamente como a de quinze --
    a classe «não encontrar nada e aprovar tudo têm o mesmo aspeto».
    """
    assert PASTA.is_dir(), f"{PASTA} não existe; correr scripts/fixar_precos_qi1.py"
    csvs = sorted(p.name for p in PASTA.glob("*.csv"))
    assert len(csvs) == len(TICKERS), f"esperava {len(TICKERS)} séries, encontrei {len(csvs)}"


def test_as_somas_de_controlo_batem():
    """O manifesto guarda um sha256 por série; se um ficheiro mudar, isto parte.

    É o que separa uma série fixada de uma pasta com ficheiros lá dentro.
    """
    from investigator.market_data import price_cache
    problemas = price_cache.verificar(PASTA)
    assert not problemas, "somas de controlo que não batem:\n" + "\n".join(problemas)


def test_a_serie_e_versionada_e_nao_gitignored():
    """⚠️ O ponto todo. `data/**` está gitignored e `data/prices/` tem ZERO ficheiros
    versionados: fixar lá tornava a corrida determinística **só nesta máquina**, o que não é
    reprodutibilidade. Esta pasta passa pela excepção de `data/samples/**`.
    """
    import subprocess
    exemplo = PASTA / f"AAPL_{INICIO}_{FIM}.csv"
    assert exemplo.exists()
    r = subprocess.run(["git", "check-ignore", "-v", str(exemplo.relative_to(RAIZ))],
                       cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    # `check-ignore` sai a 0 quando QUALQUER regra casa, incluindo uma negacao `!`. O que
    # decide e' a regra: se comeca por `!`, o ficheiro esta' DES-ignorado.
    if r.returncode == 0:
        regra = r.stdout.split("\t")[0].split(":")[-1].strip()
        assert regra.startswith("!"), (
            f"a série está ignorada pela regra {regra!r}; não seria versionada"
        )


def test_os_dois_scripts_leem_a_serie_por_defeito():
    """Nenhum dos dois pode voltar a ir à rede sem que alguém o peça explicitamente."""
    for nome in ("evaluate_anomaly.py", "evaluate_anomaly_ext.py"):
        fonte = (RAIZ / "scripts" / nome).read_text(encoding="utf-8")
        assert "data/samples/precos_qi1" in fonte, f"{nome} não conhece a série fixada"
        assert "--rede" in fonte, f"{nome} não tem a opção explícita de ir à rede"
        assert "retornos_log" in fonte, f"{nome} não usa o leitor determinístico"


def test_o_leitor_falha_alto_quando_falta_uma_serie(tmp_path):
    """Uma pasta vazia tem de levantar, não devolver um dicionário com menos empresas.

    Era assim que uma avaliação sobre catorze passava por uma sobre quinze.
    """
    from investigator.market_data import price_cache
    with pytest.raises(FileNotFoundError):
        price_cache.retornos_log(tmp_path, TICKERS, INICIO, FIM)


def test_o_leitor_nomeia_as_series_em_falta(tmp_path):
    """A mensagem tem de dizer QUAIS faltam e quantas: um erro que não nomeia não orienta."""
    from investigator.market_data import price_cache
    (tmp_path / "manifesto.json").write_text('{"series": {}}', encoding="utf-8")
    with pytest.raises(FileNotFoundError) as e:
        price_cache.retornos_log(tmp_path, ["AAPL", "MSFT"], INICIO, FIM)
    assert "AAPL" in str(e.value) and "MSFT" in str(e.value)


def test_retornos_log_devolve_um_retorno_menos_do_que_fechos():
    """Um retorno logarítmico por par de fechos consecutivos, e nenhum inventado."""
    from investigator.market_data import price_cache
    rets = price_cache.retornos_log(PASTA, ["AAPL"], INICIO, FIM)
    serie = price_cache.carregar(PASTA, "AAPL", INICIO, FIM)
    assert len(rets["AAPL"]) == len(serie) - 1


def test_o_artefacto_declara_a_proveniencia_dos_precos():
    """Uma corrida fixada e uma corrida à rede não podem produzir documentos indistinguíveis.

    Sem esta linha, só um dos dois é reprodutível e o leitor não sabe qual tem à frente.
    """
    md = (RAIZ / "docs" / "evaluation" / "evaluation_anomaly.md").read_text(encoding="utf-8")
    assert "série fixada" in md, "o artefacto não diz de onde vieram os preços"


def test_os_dois_artefactos_concordam_no_isolation_forest():
    """⚠️ ERA ESTE O DESENCONTRO QUE A RESSALVA DESCREVIA, e fechou.

    O `evaluation_anomaly.md` publicava 0,159/0,271 e o `evaluation_anomaly_ext.md`
    0,158/0,269 para a MESMA comparação, com o segundo a explicar a diferença pela deriva do
    yfinance. Com a série fixada os dois publicam a mesma linha. Se voltarem a divergir, alguém
    correu um deles com `--rede`.
    """
    import re
    ev = RAIZ / "docs" / "evaluation"
    linhas = {}
    for nome in ("evaluation_anomaly.md", "evaluation_anomaly_ext.md"):
        t = (ev / nome).read_text(encoding="utf-8")
        m = re.search(r"\|\s*Isolation Forest\s*\|([^\n]*)", t)
        assert m, f"não encontrei a linha do Isolation Forest em {nome}"
        linhas[nome] = [c.strip() for c in m.group(1).split("|") if c.strip()][:3]
    a, b = linhas["evaluation_anomaly.md"], linhas["evaluation_anomaly_ext.md"]
    assert a == b, f"os dois artefactos divergem no Isolation Forest: {a} contra {b}"
