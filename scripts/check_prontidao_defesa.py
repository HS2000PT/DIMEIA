"""Este portátil está pronto para o dia da defesa? Verificação local, sem rede.

Corre em segundos e responde a uma pergunta só: **se a sala não tiver internet e nada puder
ser instalado, o que é que ainda funciona?** Verifica o interpretador e os pacotes, os
artefactos dos modelos, os dados que a demonstração lê, a configuração, as credenciais (só a
presença de cada chave — nunca o valor) e os documentos que vão ser mostrados.

Não descarrega nada, não envia nada, não escreve em `models/` nem altera números da tese.
A única escrita possível é o relatório, e só com `--escrever`.

Severidades:
  CRÍTICO — sem isto alguma coisa da defesa não corre.
  AVISO   — convém, mas há alternativa no dia.

USO:  python scripts/check_prontidao_defesa.py
      python scripts/check_prontidao_defesa.py --escrever docs/design/prontidao_defesa.md
SAI:  código 0 se nenhum CRÍTICO falhar; 1 caso contrário.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import os
import pathlib
import shutil
import sys
import warnings

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

# (módulo, severidade). A stack leve é o que a demonstração e a API precisam; a pesada só é
# necessária para reproduzir avaliações, que não se fazem no dia.
PACOTES = [
    ("numpy", "CRÍTICO"), ("pandas", "CRÍTICO"), ("sklearn", "CRÍTICO"),
    ("joblib", "CRÍTICO"), ("yaml", "CRÍTICO"), ("onnxruntime", "CRÍTICO"),
    ("tokenizers", "CRÍTICO"), ("requests", "CRÍTICO"),
    ("fastapi", "AVISO"), ("uvicorn", "AVISO"), ("yfinance", "AVISO"),
    ("plotly", "AVISO"), ("streamlit", "AVISO"), ("matplotlib", "AVISO"),
    ("pytest", "AVISO"), ("ruff", "AVISO"),
    ("torch", "AVISO"), ("sentence_transformers", "AVISO"),
]

# Chaves de `.env`. Só se verifica a PRESENÇA do nome com valor não vazio; nenhum valor é
# lido para memória, impresso ou escrito no relatório.
CHAVES = [
    ("TELEGRAM_BOT_TOKEN", "AVISO"), ("TELEGRAM_CHAT_ID", "AVISO"),
    ("FINNHUB_API_KEY", "AVISO"), ("ALPHAVANTAGE_API_KEY", "AVISO"),
    ("TIINGO_API_KEY", "AVISO"), ("POLYGON_API_KEY", "AVISO"),
]

DOCUMENTOS = [
    ("tese-v2/main.pdf", "CRÍTICO"),
    ("slides/guia_estudo/main.pdf", "AVISO"),
    ("docs/defence/guiao_de_defesa.md", "AVISO"),
    ("docs/defence/DEFENSE_QA.md", "AVISO"),
    ("archive/streamlit-app/quiz/index.html", "AVISO"),
]

DADOS = [
    ("data/samples/kb_sample.jsonl", "CRÍTICO", "demo do Capítulo 3 (+6,46%)"),
    ("data/samples/kb_fnspid_light.jsonl", "CRÍTICO", "recuperação semântica do produto"),
    ("data/samples/backfill_kb_meta.jsonl", "AVISO", "base de casos do último ano"),
    ("data/samples/backfill_kb_vec.npy", "AVISO", "vetores da base de casos"),
    ("data/samples/dashboard_snapshot.json", "AVISO", "painel sem rede"),
    ("data/_demo_cache/gate_log.jsonl", "CRÍTICO", "demo de defesa offline"),
    ("data/_demo_cache/predictions_log.jsonl", "CRÍTICO", "demo de defesa offline"),
    ("data/_demo_cache/alerts_history.jsonl", "CRÍTICO", "demo de defesa offline"),
]


class Registo:
    def __init__(self) -> None:
        self.linhas: list[tuple[str, str, str, str]] = []

    def add(self, seccao: str, item: str, estado: str, detalhe: str = "") -> None:
        self.linhas.append((seccao, item, estado, detalhe))

    @property
    def criticos(self) -> list[tuple[str, str, str, str]]:
        return [x for x in self.linhas if x[2] == "FALHA"]

    @property
    def avisos(self) -> list[tuple[str, str, str, str]]:
        return [x for x in self.linhas if x[2] == "aviso"]


def _estado(ok: bool, severidade: str) -> str:
    if ok:
        return "ok"
    return "FALHA" if severidade == "CRÍTICO" else "aviso"


def _versao(mod: str) -> str:
    try:
        m = importlib.import_module(mod)
    except Exception as exc:  # noqa: BLE001
        return f"__erro__:{type(exc).__name__}"
    return str(getattr(m, "__version__", "?"))


def ambiente(r: Registo) -> None:
    v = sys.version_info
    r.add("Ambiente", "Python ≥ 3.12", _estado(v >= (3, 12), "CRÍTICO"),
          f"{v.major}.{v.minor}.{v.micro}")
    dentro = (pathlib.Path(sys.prefix).resolve() == (RAIZ / ".venv").resolve())
    r.add("Ambiente", "a correr no .venv do projeto", _estado(dentro, "AVISO"), sys.prefix)
    for mod, sev in PACOTES:
        ver = _versao(mod)
        r.add("Ambiente", mod, _estado(not ver.startswith("__erro__"), sev),
              "em falta" if ver.startswith("__erro__") else ver)
    try:
        importlib.import_module("investigator")
        r.add("Ambiente", "pacote investigator importável", "ok", "")
    except Exception as exc:  # noqa: BLE001
        r.add("Ambiente", "pacote investigator importável", "FALHA", type(exc).__name__)
    r.add("Ambiente", "latexmk no PATH", _estado(shutil.which("latexmk") is not None, "AVISO"),
          "só necessário para recompilar a tese")


def modelos(r: Registo) -> None:
    bundle_path = RAIZ / "models" / "triage_context_lr.joblib"
    if not bundle_path.exists():
        r.add("Modelos", "triage_context_lr.joblib", "FALHA", "ficheiro em falta")
    else:
        try:
            with warnings.catch_warnings(record=True) as avisos:
                warnings.simplefilter("always")
                from investigator.triage.model import load_bundle
                bundle = load_bundle(bundle_path)
            incompat = [str(a.message)[:80] for a in avisos
                        if "InconsistentVersion" in type(a.message).__name__]
            r.add("Modelos", "modelo de triagem carrega", "ok",
                  f"{len(bundle['feature_names'])} entradas")
            if incompat:
                r.add("Modelos", "versão de scikit-learn", "aviso",
                      "artefacto gravado com outra versão — regenerar números antes de citar")
        except Exception as exc:  # noqa: BLE001
            r.add("Modelos", "modelo de triagem carrega", "FALHA",
                  f"{type(exc).__name__}: {exc}"[:90])
            bundle = None
        # Guarda R1: o contrato de features tem de bater com o código atual. Um bundle
        # desatualizado só se manifesta no momento em que alguém pontua uma notícia.
        if bundle is not None:
            try:
                import pandas as pd

                from investigator.triage.features import context_block
                df = pd.DataFrame([{"vol20": 0.0, "mom5": 0.0, "ret_event": 0.0,
                                    "headline_len": 0.0, "sector": "tech"}])
                _, nomes = context_block(df)
                r.add("Modelos", "contrato de features bate com o código",
                      _estado(nomes == bundle["feature_names"], "CRÍTICO"),
                      "" if nomes == bundle["feature_names"] else "bundle desatualizado")
            except Exception as exc:  # noqa: BLE001
                r.add("Modelos", "contrato de features bate com o código", "FALHA",
                      f"{type(exc).__name__}: {exc}"[:90])

    try:
        from investigator.historical_kb.onnx_embedder import _CACHE_DIR, _FILES
    except Exception as exc:  # noqa: BLE001
        r.add("Modelos", "codificador ONNX", "FALHA", type(exc).__name__)
        return
    for nome, (_url, digest) in _FILES.items():
        f = _CACHE_DIR / nome
        if not f.exists():
            r.add("Modelos", nome, "FALHA", "em falta — precisa de rede para descarregar")
            continue
        h = hashlib.sha256()
        with f.open("rb") as fh:
            for bloco in iter(lambda: fh.read(1 << 20), b""):
                h.update(bloco)
        igual = h.hexdigest() == digest
        r.add("Modelos", nome, _estado(igual, "CRÍTICO"),
              f"{f.stat().st_size / 1e6:.1f} MB" if igual else "SHA256 não bate")

    # O teste que interessa: o codificador arranca e produz um vetor, sem rede. É isto que
    # decide se a recuperação semântica funciona numa sala sem wi-fi.
    try:
        from investigator.historical_kb.onnx_embedder import OnnxMiniLMEmbedder
        vec = OnnxMiniLMEmbedder(auto_download=False).encode(["teste de arranque"])
        ok = getattr(vec, "shape", (0, 0))[1] == 384
        r.add("Modelos", "codificador ONNX embebe sem rede", _estado(ok, "CRÍTICO"),
              f"vetor de {vec.shape[1]} dimensões" if ok else "dimensão inesperada")
    except Exception as exc:  # noqa: BLE001
        r.add("Modelos", "codificador ONNX embebe sem rede", "FALHA",
              f"{type(exc).__name__}: {exc}"[:90])


def dados(r: Registo) -> None:
    for rel, sev, para_que in DADOS:
        f = RAIZ / rel
        r.add("Dados", rel, _estado(f.exists(), sev),
              f"{f.stat().st_size / 1e6:.1f} MB · {para_que}" if f.exists()
              else f"em falta — {para_que}")


def configuracao(r: Registo) -> None:
    cfg = RAIZ / "config" / "alerts.yaml"
    if not cfg.exists():
        r.add("Configuração", "config/alerts.yaml", "FALHA", "em falta")
    else:
        try:
            import yaml
            conf = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            tickers = (conf.get("news") or {}).get("tickers") or []
            r.add("Configuração", "config/alerts.yaml", "ok", f"{len(tickers)} empresas")
        except Exception as exc:  # noqa: BLE001
            r.add("Configuração", "config/alerts.yaml", "FALHA", type(exc).__name__)

    env = RAIZ / ".env"
    if not env.exists():
        r.add("Credenciais", ".env", "aviso", "em falta — a demo offline não precisa dele")
        return
    presentes: set[str] = set()
    for linha in env.read_text(encoding="utf-8", errors="replace").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        nome, _, valor = linha.partition("=")
        if valor.strip().strip("'\""):
            presentes.add(nome.strip())
    r.add("Credenciais", ".env", "ok", f"{len(presentes)} chaves com valor")
    for chave, sev in CHAVES:
        r.add("Credenciais", chave, _estado(chave in presentes, sev),
              "definida" if chave in presentes else "por definir")


def documentos(r: Registo) -> None:
    for rel, sev in DOCUMENTOS:
        f = RAIZ / rel
        r.add("Documentos", rel, _estado(f.exists(), sev),
              f"{f.stat().st_size / 1e6:.1f} MB" if f.exists() else "em falta")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--escrever", default=None, help="também escrever o relatório neste caminho")
    args = ap.parse_args()

    os.environ.setdefault("HF_HUB_OFFLINE", "1")  # nada de rede durante a verificação
    r = Registo()
    ambiente(r)
    modelos(r)
    dados(r)
    configuracao(r)
    documentos(r)

    largura = max(len(x[1]) for x in r.linhas) + 2
    seccao_atual = ""
    for seccao, item, estado, detalhe in r.linhas:
        if seccao != seccao_atual:
            print(f"\n── {seccao} " + "─" * max(0, 60 - len(seccao)))
            seccao_atual = seccao
        marca = {"ok": "  ok  ", "aviso": " aviso", "FALHA": " FALHA"}[estado]
        print(f"[{marca}] {item:<{largura}} {detalhe}")

    print()
    if r.criticos:
        print(f"{len(r.criticos)} verificação(ões) CRÍTICA(S) falhou/falharam:")
        for _s, item, _e, detalhe in r.criticos:
            print(f"  - {item}: {detalhe}")
    else:
        print("Nenhuma verificação crítica falhou.")
    if r.avisos:
        print(f"{len(r.avisos)} aviso(s).")

    if args.escrever:
        destino = pathlib.Path(args.escrever)
        if not destino.is_absolute():
            destino = RAIZ / destino
        destino.parent.mkdir(parents=True, exist_ok=True)
        linhas = "\n".join(f"| {s} | `{i}` | {e} | {d} |" for s, i, e, d in r.linhas)
        destino.write_text(
            "# Prontidão para a defesa\n\n"
            "> Gerado por `scripts/check_prontidao_defesa.py`. Não editar à mão.\n\n"
            "| Secção | Item | Estado | Detalhe |\n|---|---|---|---|\n" + linhas + "\n",
            encoding="utf-8")
        print(f"-> {destino}")

    return 1 if r.criticos else 0


if __name__ == "__main__":
    raise SystemExit(main())
