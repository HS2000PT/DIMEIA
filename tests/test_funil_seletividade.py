"""Testes do funil de seletividade.

O que estes testes guardam é o defeito concreto de 2026-07-13, e não o script em
abstracto: um instantâneo publicou três empresas com exatamente catorze alertas cada e
sete a zero, e catorze era o TECTO da política (duas por empresa por dia, sete dias) e não
uma medição. Nenhum verificador o assinalou. O teste central abaixo planta essa forma
exacta e exige que o relatório a assinale.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "evaluate_funil_seletividade.py"
SAIDA = REPO / "docs" / "evaluation" / "evaluation_funil_seletividade.md"


def _escrever(d: Path, registo: list[dict], hist: list[dict]) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / "predictions_log.jsonl").write_text(
        "\n".join(json.dumps(x) for x in registo) + "\n", encoding="utf-8")
    (d / "alerts_history.jsonl").write_text(
        "\n".join(json.dumps(x) for x in hist) + "\n", encoding="utf-8")


def _correr(d: Path, de: str, ate: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--local", str(d), "--de", de, "--ate", ate],
        capture_output=True, text=True, encoding="utf-8", cwd=str(REPO))


def _registo(dia: str, ticker: str, n: int) -> list[dict]:
    return [{"news_date": dia, "ticker": ticker, "headline": f"{ticker} título {i}",
             "stage": "not_latest"} for i in range(n)]


def test_forma_de_julho_e_assinalada_como_tecto(tmp_path, monkeypatch):
    """Três empresas com o MESMO número e as restantes a zero tem de ser assinalado.

    É a forma exacta do instantâneo de 2026-07-13. Sem este aviso, o leitor lê uma
    igualdade produzida por um limite como se fosse um resultado sobre a matéria-prima.
    """
    guardado = SAIDA.read_text(encoding="utf-8") if SAIDA.exists() else None
    try:
        reg, hist = [], []
        for dia in ("2026-07-14", "2026-07-15"):
            for t in ("AMD", "META", "TSLA", "AAPL", "MSFT", "NVDA"):
                reg += _registo(dia, t, 20)
            for t in ("AMD", "META", "TSLA"):
                hist += [{"date": dia, "ticker": t, "kind": "news"} for _ in range(2)]
        _escrever(tmp_path, reg, hist)

        r = _correr(tmp_path, "2026-07-14", "2026-07-15")
        assert r.returncode == 0, r.stderr
        txt = SAIDA.read_text(encoding="utf-8")

        assert "Todas as empresas com alerta têm exatamente o mesmo número" in txt
        assert "limite por empresa" in txt
    finally:
        if guardado is not None:
            SAIDA.write_text(guardado, encoding="utf-8")


def test_distribuicao_desigual_nao_dispara_o_aviso(tmp_path):
    """Controlo no sentido oposto: um aviso que dispare sempre não é um aviso."""
    guardado = SAIDA.read_text(encoding="utf-8") if SAIDA.exists() else None
    try:
        reg, hist = [], []
        for t in ("AMD", "META", "TSLA", "AAPL"):
            reg += _registo("2026-09-01", t, 30)
        for t, n in (("AMD", 3), ("META", 2), ("TSLA", 1)):
            hist += [{"date": "2026-09-01", "ticker": t, "kind": "news"} for _ in range(n)]
        _escrever(tmp_path, reg, hist)

        r = _correr(tmp_path, "2026-09-01", "2026-09-01")
        assert r.returncode == 0, r.stderr
        txt = SAIDA.read_text(encoding="utf-8")

        assert "Todas as empresas com alerta têm exatamente o mesmo número" not in txt
        assert "não é uniforme" in txt
    finally:
        if guardado is not None:
            SAIDA.write_text(guardado, encoding="utf-8")


def test_recusa_janela_sem_registo(tmp_path):
    """Uma janela sem registo é um funil que não se mediu, não um funil vazio."""
    _escrever(tmp_path, _registo("2026-09-01", "AMD", 5), [])
    r = _correr(tmp_path, "2026-01-01", "2026-01-02")
    assert r.returncode == 2
    assert "RECUSA" in r.stdout


def test_conta_titulos_distintos_e_nao_avaliacoes(tmp_path):
    """O sistema reavalia os mesmos títulos a cada ciclo: contar linhas infla o funil."""
    guardado = SAIDA.read_text(encoding="utf-8") if SAIDA.exists() else None
    try:
        um = {"news_date": "2026-09-01", "ticker": "AMD",
              "headline": "o mesmo título", "stage": "not_latest"}
        _escrever(tmp_path, [dict(um) for _ in range(50)],
                  [{"date": "2026-09-01", "ticker": "AMD", "kind": "news"}])
        r = _correr(tmp_path, "2026-09-01", "2026-09-01")
        assert r.returncode == 0, r.stderr
        txt = SAIDA.read_text(encoding="utf-8")
        assert "**Total** | **1** |" in txt, "50 avaliações do mesmo título são 1 título"
        assert "50 linhas para 1 títulos distintos" in txt
    finally:
        if guardado is not None:
            SAIDA.write_text(guardado, encoding="utf-8")
