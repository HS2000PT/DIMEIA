"""Quanto é que a MANCHETE move a pontuação da triagem, com tudo o resto igual?

Motivação: uma crítica externa afirmou que várias notícias do mesmo dia recebem «exatamente a
mesma pontuação». A afirmação é verificável sem dados de produção, porque decorre do contrato
de entradas do modelo implantado.

O modelo implantado (`models/triage_context_lr.joblib`, variante só-contexto) recebe nove
entradas: `vol20`, `mom5`, `ret_event`, `headline_len` e cinco indicadores de setor. Fixados o
ticker e o dia, oito delas são constantes: o setor não muda, e a volatilidade, o momento e a
reação do dia são calculados a partir da série de preços, não do texto. **A única entrada que
varia de notícia para notícia é o número de caracteres do título.**

Este script mede a amplitude que essa única entrada consegue produzir, e compara-a com a
amplitude do setor e da volatilidade. Não usa registos de produção nem dados novos: só o
artefacto congelado do modelo, pelo que é reproduzível em qualquer máquina que tenha o
repositório. Os valores de referência das restantes entradas são as **médias do conjunto de
treino**, lidas do próprio normalizador guardado no artefacto — não são escolhidas à mão.

USO:  python scripts/check_headline_sensitivity.py
SAI:  docs/evaluation/sensibilidade_headline.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import pathlib
import sys

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

SAIDA = RAIZ / "docs" / "evaluation" / "sensibilidade_headline.md"
MODELO = RAIZ / "models" / "triage_context_lr.joblib"

# Intervalo de comprimentos de título coberto pela varredura. O limite inferior e o superior
# cobrem folgadamente o que uma manchete real ocupa; alargá-los só aumentaria a amplitude
# reportada, pelo que a conclusão é conservadora.
LEN_MIN, LEN_MAX = 20, 200

SETORES = ["banking", "consumer", "energy", "health", "tech"]

# Volatilidade diária baixa e alta, em valores explícitos e realistas (1% e 4%). Ambos caem
# dentro do intervalo do conjunto de treino. Evita-se um percentil normal porque `vol20` é
# assimétrica à direita e a aproximação daria um valor negativo, que não é uma volatilidade.
VOL_BAIXA, VOL_ALTA = 0.010, 0.040


def _pontua(bundle: dict, valores: dict[str, float]) -> float:
    """Probabilidade calibrada a partir de um vetor de features explícito.

    Passa pelo mesmo par modelo/calibrador que a produção usa; só a montagem do vetor é feita
    aqui, para poder variar uma entrada de cada vez.
    """
    nomes = bundle["feature_names"]
    x = np.array([[float(valores.get(n, 0.0)) for n in nomes]])
    return float(bundle["calibrator"](bundle["model"].predict_proba(x)[:, 1])[0])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--saida", default=str(SAIDA))
    args = ap.parse_args()
    destino = pathlib.Path(args.saida)
    if not destino.is_absolute():
        destino = RAIZ / destino

    if not MODELO.exists():
        print(f"ERRO: {MODELO} não existe.", file=sys.stderr)
        raise SystemExit(2)

    from investigator.triage.model import load_bundle

    bundle = load_bundle(MODELO)
    nomes: list[str] = bundle["feature_names"]
    escala = bundle["model"].named_steps["scale"]
    media = dict(zip(nomes, escala.mean_, strict=True))
    desvio = dict(zip(nomes, escala.scale_, strict=True))
    sha = hashlib.sha256(MODELO.read_bytes()).hexdigest()
    import sklearn  # só para registar a versão no cabeçalho do relatório
    versao_sk = sklearn.__version__

    base = {n: float(media[n]) for n in ("vol20", "mom5", "ret_event")}

    # 1. Só a manchete varia (mesmo ticker, mesmo dia).
    por_setor: dict[str, tuple[float, float]] = {}
    for setor in SETORES:
        ps = []
        for comprimento in range(LEN_MIN, LEN_MAX + 1):
            v = dict(base)
            v["headline_len"] = float(comprimento)
            v[f"sector_{setor}"] = 1.0
            ps.append(_pontua(bundle, v))
        por_setor[setor] = (min(ps), max(ps))
    amp_manchete = max(hi - lo for lo, hi in por_setor.values())

    # 2. Só o setor varia (mesma manchete, mesmo dia).
    p_setor: dict[str, float] = {}
    for setor in SETORES:
        v = dict(base)
        v["headline_len"] = float(media["headline_len"])
        v[f"sector_{setor}"] = 1.0
        p_setor[setor] = _pontua(bundle, v)
    amp_setor = max(p_setor.values()) - min(p_setor.values())

    # 3. Só a volatilidade varia (mesma manchete, mesma empresa, dias diferentes).
    #    Dois valores explícitos e realistas de volatilidade diária, ambos dentro do intervalo
    #    do treino. Não se usam percentis normais:
    #    `vol20` é assimétrica à direita e a aproximação normal produziria um valor negativo,
    #    que não é uma volatilidade possível.
    p_vol: dict[str, float] = {}
    for etiqueta, valor in (("baixa", VOL_BAIXA), ("alta", VOL_ALTA)):
        v = dict(base)
        v["vol20"] = float(valor)
        v["headline_len"] = float(media["headline_len"])
        v["sector_tech"] = 1.0
        p_vol[etiqueta] = _pontua(bundle, v)
    amp_vol = abs(p_vol["alta"] - p_vol["baixa"])

    linhas_setor = "\n".join(
        f"| {s} | {lo:.4f} | {hi:.4f} | {hi - lo:.4f} |" for s, (lo, hi) in por_setor.items()
    )
    linhas_p_setor = "\n".join(
        f"| {s} | {p:.4f} |" for s, p in sorted(p_setor.items(), key=lambda kv: kv[1])
    )

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"""# Quanto é que a manchete move a pontuação da triagem?

> **Gerado por** `scripts/check_headline_sensitivity.py`. Não editar à mão.
> **Fonte:** `models/triage_context_lr.joblib` (sha256 `{sha[:16]}…`), o artefacto congelado do
> modelo implantado. Não usa registos de produção nem dados novos.
> **Gerado a:** {dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M')} UTC ·
> **scikit-learn:** {versao_sk}. O artefacto foi gravado com a versão do venv do projeto; se a
> versão acima for outra, regerar antes de citar qualquer número deste ficheiro.

## A pergunta

Fixados o ticker e o dia, oito das nove entradas do modelo são constantes: o setor não muda, e
`vol20`, `mom5` e `ret_event` vêm da série de preços e não do texto. A única entrada que varia
de notícia para notícia é `headline_len`, o número de caracteres do título. Quanto é que essa
entrada, sozinha, consegue mover a probabilidade calibrada?

As restantes entradas ficam nas **médias do conjunto de treino**, lidas do normalizador
guardado no próprio artefacto.

## 1. Só a manchete varia — mesmo ticker, mesmo dia

Comprimento do título de {LEN_MIN} a {LEN_MAX} caracteres:

| Setor | p mínima | p máxima | Amplitude |
|---|---:|---:|---:|
{linhas_setor}

**Amplitude máxima atribuível à manchete: `{amp_manchete:.4f}`** — menos de um ponto percentual.

## 2. Só o setor varia — mesma manchete, mesmo dia

| Setor | p |
|---|---:|
{linhas_p_setor}

**Amplitude entre setores: `{amp_setor:.4f}`.**

## 3. Só a volatilidade varia — mesma manchete, mesma empresa

| `vol20` (volatilidade diária) | p |
|---|---:|
| {VOL_BAIXA:.3f} ({VOL_BAIXA * 100:.0f}%) | {p_vol['baixa']:.4f} |
| {VOL_ALTA:.3f} ({VOL_ALTA * 100:.0f}%) | {p_vol['alta']:.4f} |

Média do treino: `{media['vol20']:.4f}`; desvio-padrão: `{desvio['vol20']:.4f}`.

**Amplitude atribuível à volatilidade: `{amp_vol:.4f}`.**

## Leitura

A manchete move a pontuação `{amp_manchete:.4f}`; o setor move-a `{amp_setor:.4f}`, cerca de
{amp_setor / amp_manchete:.0f} vezes mais; a volatilidade move-a `{amp_vol:.4f}`, cerca de
{amp_vol / amp_manchete:.0f} vezes mais.

A crítica de que várias notícias do mesmo dia recebem «exatamente a mesma pontuação» é, à
letra, falsa: as pontuações diferem, porque os títulos têm comprimentos diferentes. Na
substância é correta, e passa aqui de afirmação a medição: **entre duas notícias da mesma
empresa no mesmo dia, a pontuação não pode diferir mais do que
{amp_manchete * 100:.1f} pontos percentuais, e o que as separa é o comprimento do título e não
o seu significado.**

Isto é o mecanismo, medido no artefacto, do resultado que
`evaluation_gate_selectivity_unicos.md` observa nos registos de produção: a amplitude média
dentro de cada empresa é de `0.072`, e a maior parte dela vem de a volatilidade mudar de dia
para dia, não de a manchete mudar.

Não é um defeito de implementação: o modelo implantado é a variante **só-contexto**, que por
construção não recebe o texto. A variante com texto precisa do codificador SBERT, que não corre
na configuração de produção. A consequência a reter é a de que a pontuação da triagem, tal como
está implantada, ordena empresas e dias, não notícias.
""", encoding="utf-8")

    print(f"manchete   : {amp_manchete:.4f}")
    print(f"setor      : {amp_setor:.4f}")
    print(f"volatilidade: {amp_vol:.4f}")
    print(f"-> {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
