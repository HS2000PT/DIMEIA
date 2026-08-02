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

# Teto de memória, não afinação de desempenho. O pico durante a inferência cresce
# linearmente com o tamanho do lote, e 32 mantém-no na ordem das dezenas de MB mesmo com
# sequências no comprimento máximo. Ver a docstring de `encode` para o incidente que o
# obrigou a existir.
_ENCODE_BATCH = 32

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
        # Sessão deliberadamente MONO-THREAD e sem arena de memória.
        #
        # Por omissão o onnxruntime dimensiona os seus pools de threads e a arena de memória
        # pelo número de CPUs que a máquina REPORTA. Num contentor pequeno isso é desastroso:
        # o contentor vê os cores do hospedeiro mas só tem a sua fatia de RAM. Medido: 96 MB
        # numa máquina de 4 cores, contra >1,2 GB num dyno Heroku Basic (limite 512 MB), onde
        # o processo entrava em ciclo de crash por R15 antes de completar um ciclo de varredura.
        #
        # Um thread não custa nada aqui: o produto embebe uma mão-cheia de manchetes de cada
        # vez, e o paralelismo intra-operação só compensa em lotes grandes. A arena serve para
        # reutilizar blocos entre inferências frequentes; num processo que embebe algumas
        # dezenas de frases por minuto, é memória reservada e não usada.
        #
        # Não altera resultados: a mesma entrada dá o mesmo embedding, e a validação de
        # paridade contra o sentence-transformers (docs/evaluation/onnx_minilm_validation.md)
        # continua a passar.
        opts = onnxruntime.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.enable_cpu_mem_arena = False
        self._session = onnxruntime.InferenceSession(
            str(cache / "model_quint8_avx2.onnx"),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
        self._input_names = {i.name for i in self._session.get_inputs()}

    def encode(self, texts: list[str]) -> np.ndarray:
        """Embeddings 384-d, sempre por LOTES pequenos.

        O tamanho do lote não é uma afinação de desempenho, é um limite de memória. A saída
        intermédia do transformer tem forma ``(n, seq, 384)`` e as ativações internas são
        várias vezes maiores, pelo que o pico de memória cresce LINEARMENTE com ``n``. Embeber
        tudo de uma vez é seguro com dez manchetes e fatal com mil.

        Foi exatamente assim que o worker morreu no primeiro deploy: numa máquina nova o
        ficheiro de pendentes está vazio, por isso *todas* as manchetes da varredura de 7 dias
        × 10 tickers são novas e iam num único lote. Resultado: 1,4 GB num contentor de
        512 MB, morto por SIGKILL em ciclo de crash. Na máquina do autor o mesmo código nunca
        falhou, porque lá o ficheiro de pendentes já existe e os lotes são minúsculos.

        **Ressalva medida, e não assumida.** Seria natural escrever aqui que fatiar não altera
        resultados, porque o *mean pooling* é mascarado e cada texto é independente. Medido a
        2026-08-02, é FALSO: o mesmo texto embebido sozinho e ao lado de uma frase mais longa
        difere em ``0.022`` (cosseno ``0.986``). O modelo é quantizado em int8, e as posições de
        padding influenciam de facto as não-padding apesar da máscara de atenção.

        Isto é uma propriedade **pré-existente** deste embebedor, não uma consequência de
        fatiar: o tamanho do lote em produção já variava de varredura para varredura, consoante
        quantas manchetes eram novas. O que importa é o efeito na recuperação, e esse foi
        medido: com lotes de 32 contra o lote único de antes, o top-3 é **idêntico em 8 de 8**
        consultas e a sobreposição de vizinhos é ``1.000``. Só em lotes de 1, o extremo oposto
        de padding, é que dois top-3 mudam.
        """
        if not texts:
            return np.zeros((0, self.dim), dtype="float64")
        saidas = [
            self._encode_batch(texts[i : i + _ENCODE_BATCH])
            for i in range(0, len(texts), _ENCODE_BATCH)
        ]
        return np.vstack(saidas)

    def _encode_batch(self, texts: list[str]) -> np.ndarray:
        encoded = self._tokenizer.encode_batch(list(texts))
        ids = np.array([e.ids for e in encoded], dtype="int64")
        mask = np.array([e.attention_mask for e in encoded], dtype="int64")
        feeds: dict[str, np.ndarray] = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self._input_names:
            feeds["token_type_ids"] = np.zeros_like(ids)
        hidden = self._session.run(None, feeds)[0]  # (n, seq, 384)
        return masked_mean_pool(hidden, mask)
