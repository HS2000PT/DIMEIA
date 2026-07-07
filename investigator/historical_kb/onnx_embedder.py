"""Embedder semântico LEVE para produção: MiniLM exportado em ONNX (sem torch).

Problema real: a app pública e o runner correm na stack leve (sem torch/SBERT), por isso
até aqui a KB de produção usava o HashingEmbedder (sobreposição de palavras) — mais fraco
que o SBERT avaliado na tese, e a app dizia-o com honestidade. Este módulo fecha esse fosso:
o MESMO modelo da tese (`all-MiniLM-L6-v2`), exportado em ONNX quantizado (~23 MB), corre
em `onnxruntime` (CPU, sem torch) e reproduz o pipeline do sentence-transformers:
tokenização → transformer → mean pooling com máscara de atenção → normalização L2.

O modelo NÃO é versionado (regra do repo: modelos grandes fora do git). É descarregado
sob demanda do Hugging Face com SHA256 pinado (integridade verificada) para `models/onnx/`.
Sem rede e sem cache local, o construtor falha com instruções claras — quem consome
(`investigator.main.product_retrieval`) faz fail-open para a KB-amostra word-overlap.

Como explico ao júri (3 frases): "A tese avaliou o SBERT MiniLM; a app pública usa
exatamente esse modelo, convertido para um formato leve (ONNX) que dispensa a stack pesada.
Validei numericamente que os embeddings coincidem com os do SBERT original. Assim o que o
utilizador vê na nuvem é o método avaliado, não uma aproximação lexical."
"""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import numpy as np

_HF_BASE = "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main"
_CACHE_DIR = Path(__file__).resolve().parents[2] / "models" / "onnx"
_MAX_SEQ_LENGTH = 256  # sentence_bert_config.json do all-MiniLM-L6-v2

# Ficheiros pinados (integridade verificada após download; falha em caso de mismatch).
_FILES: dict[str, tuple[str, str]] = {
    "model_quint8_avx2.onnx": (
        f"{_HF_BASE}/onnx/model_quint8_avx2.onnx",
        "b941bf19f1f1283680f449fa6a7336bb5600bdcd5f84d10ddc5cd72218a0fd21",
    ),
    "tokenizer.json": (
        f"{_HF_BASE}/tokenizer.json",
        "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037",
    ),
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_model(cache_dir: Path | None = None, auto_download: bool = False) -> Path:
    """Garante o modelo+tokenizer na cache local; devolve a pasta.

    `auto_download=False` (defeito): nunca toca na rede — se faltar algo, FileNotFoundError
    com instruções (os testes ficam determinísticos/offline). Com `auto_download=True`
    descarrega o que faltar (~23 MB) e verifica o SHA256 pinado antes de aceitar.
    """
    cache = Path(cache_dir) if cache_dir else _CACHE_DIR
    for name, (url, digest) in _FILES.items():
        dest = cache / name
        if dest.exists():
            continue
        if not auto_download:
            raise FileNotFoundError(
                f"Modelo ONNX em falta: {dest}. Descarregar com "
                "`python -c \"from investigator.historical_kb.onnx_embedder import "
                "ensure_model; ensure_model(auto_download=True)\"` (~23 MB, uma vez)."
            )
        cache.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)  # noqa: S310 — URL fixo (HF), hash verificado
        got = _sha256(tmp)
        if got != digest:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(
                f"SHA256 inesperado para {name}: {got} (esperado {digest}) — download rejeitado."
            )
        tmp.replace(dest)
    return cache


def masked_mean_pool(hidden: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
    """Mean pooling com máscara + normalização L2 — igual ao sentence-transformers.

    hidden: (n, seq, dim); attention_mask: (n, seq) com 1 nos tokens reais. Puro numpy,
    testável offline (tests/test_onnx_embedder.py cobre a matemática sem o modelo).
    """
    mask = attention_mask[..., None].astype("float64")
    summed = (hidden.astype("float64") * mask).sum(axis=1)
    counts = np.clip(mask.sum(axis=1), 1e-9, None)
    pooled = summed / counts
    norms = np.linalg.norm(pooled, axis=1, keepdims=True)
    return pooled / np.clip(norms, 1e-12, None)


class OnnxMiniLMEmbedder:
    """`all-MiniLM-L6-v2` em ONNX (quantizado, CPU) — implementa a interface `Embedder`.

    Embeddings 384-d normalizados (L2), no MESMO espaço semântico do SbertEmbedder
    (validação numérica em docs/evaluation/onnx_minilm_validation.md).
    """

    dim = 384
    semantic = True  # a UI usa isto para descrever o motor com honestidade

    def __init__(self, cache_dir: Path | None = None, auto_download: bool = False):
        import onnxruntime  # import tardio: a stack core/testes não depende disto
        from tokenizers import Tokenizer

        cache = ensure_model(cache_dir, auto_download=auto_download)
        self._tokenizer = Tokenizer.from_file(str(cache / "tokenizer.json"))
        self._tokenizer.enable_truncation(max_length=_MAX_SEQ_LENGTH)
        pad_id = self._tokenizer.token_to_id("[PAD]") or 0
        self._tokenizer.enable_padding(pad_id=pad_id, pad_token="[PAD]")
        self._session = onnxruntime.InferenceSession(
            str(cache / "model_quint8_avx2.onnx"), providers=["CPUExecutionProvider"]
        )
        self._input_names = {i.name for i in self._session.get_inputs()}

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype="float64")
        encoded = self._tokenizer.encode_batch(list(texts))
        ids = np.array([e.ids for e in encoded], dtype="int64")
        mask = np.array([e.attention_mask for e in encoded], dtype="int64")
        feeds: dict[str, np.ndarray] = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self._input_names:
            feeds["token_type_ids"] = np.zeros_like(ids)
        hidden = self._session.run(None, feeds)[0]  # (n, seq, 384)
        return masked_mean_pool(hidden, mask)
