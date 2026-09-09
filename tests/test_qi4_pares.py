"""QI4 — os pares de treino, e as três maneiras de os construir mal.

A QI4 pergunta se um codificador de frases pode ser ajustado para que a proximidade signifique
**materialidade comparável**: duas manchetes ficam perto quando o movimento que se lhes seguiu
teve grandeza parecida. Nunca direção — essa é a restrição fundadora da tese, e a §5.3.5 já
mediu que a direção quase não se aprende do texto.

Três maneiras de estragar isto antes de começar, e um teste para cada:

1. **Fuga pelo bloco.** Um par com um membro no treino e outro no teste treina o codificador
   sobre o que ele vai ser avaliado. É a fuga clássica, e é silenciosa.
2. **Fuga pela normalização.** O alvo é a distância entre percentis da grandeza. Se o mapa de
   percentis for ajustado sobre *todos* os dados, a distribuição do teste entra no treino sem
   que nenhum par cruze fronteira nenhuma. É a fuga que passa despercebida.
3. **Braços que não diferem.** Se o braço de magnitude e o de direção produzirem o mesmo alvo,
   a comparação que **é** o resultado da QI4 não mede coisa nenhuma. Tem de estar provado que
   um ignora o sinal e o outro não.

Ver `docs/design/reproducao_corpus_2026-09-09.md` e a Fase C do `TASKS.md`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from investigator.qi4 import pares as P


def quadro(n: int = 60, split: str = "train", semente: int = 0) -> pd.DataFrame:
    """Quadro sintético: n linhas, tickers alternados, retornos com sinais variados."""
    rng = np.random.default_rng(semente)
    tickers = np.array(["AAA", "BBB", "CCC"])[np.arange(n) % 3]
    ret = rng.normal(0, 0.03, n)
    return pd.DataFrame({
        "headline": [f"manchete {i}" for i in range(n)],
        "ticker": tickers,
        "abn_h3": ret,
        "split": split,
    })


# ── o mapa de percentis ───────────────────────────────────────────────────────

def test_o_percentil_e_a_fracao_de_valores_nao_superiores():
    """Verificação à mão. Sobre [0, 1, 2, 3], o percentil de 2 é 3/4."""
    m = P.mapa_percentil(np.array([0.0, 1.0, 2.0, 3.0]))
    assert m(np.array([2.0]))[0] == pytest.approx(0.75)
    assert m(np.array([0.0]))[0] == pytest.approx(0.25)
    assert m(np.array([3.0]))[0] == pytest.approx(1.00)


def test_o_percentil_e_monotono_e_fica_em_zero_um():
    m = P.mapa_percentil(np.array([0.0, 1.0, 2.0, 3.0]))
    v = m(np.array([-5.0, 0.5, 1.5, 9.0]))
    assert np.all((v >= 0) & (v <= 1))
    assert np.all(np.diff(v) >= 0)


def test_valores_fora_do_apoio_saturam_em_vez_de_extrapolar():
    m = P.mapa_percentil(np.array([0.0, 1.0, 2.0, 3.0]))
    assert m(np.array([-100.0]))[0] == pytest.approx(0.0)
    assert m(np.array([100.0]))[0] == pytest.approx(1.0)


# ── o alvo ────────────────────────────────────────────────────────────────────

def test_grandezas_iguais_dao_alvo_um():
    assert P.alvo_similaridade(np.array([0.4]), np.array([0.4]))[0] == pytest.approx(1.0)


def test_extremos_opostos_dao_alvo_zero():
    assert P.alvo_similaridade(np.array([0.0]), np.array([1.0]))[0] == pytest.approx(0.0)


def test_o_alvo_e_simetrico():
    a, b = np.array([0.2, 0.9]), np.array([0.7, 0.1])
    assert np.allclose(P.alvo_similaridade(a, b), P.alvo_similaridade(b, a))


# ── os dois braços TÊM de diferir ─────────────────────────────────────────────

def test_a_magnitude_deita_o_sinal_fora_e_a_direcao_guarda_o():
    r = np.array([0.05, -0.05, 0.01, -0.01])
    assert np.allclose(P.valores_do_braco(r, "magnitude"), [0.05, 0.05, 0.01, 0.01])
    assert np.allclose(P.valores_do_braco(r, "direcao"), r)


def test_mais_x_e_menos_x_sao_identicos_na_magnitude_e_opostos_na_direcao():
    """⚠️ A propriedade que faz a QI4 ser uma comparação e não uma tautologia. Feita à mão.

    Distribuição simétrica: ±1%, ±2%, ±3%, ±4%, ±5%, dez valores ao todo.

    Na MAGNITUDE, `|+5%| = |−5%| = 5%`, que é o máximo: o percentil de ambos é `10/10 = 1`, e
    o alvo é `1 − 0 = 1`. Dois movimentos de igual grandeza e sinais opostos são o par mais
    parecido que existe — é exactamente o que «materialidade comparável» quer dizer.

    Na DIREÇÃO, os valores ordenados são `[−5%, −4%, −3%, −2%, −1%, +1%, …, +5%]`. O percentil
    de `+5%` é `10/10 = 1` e o de `−5%` é `1/10 = 0,1`; o alvo é `1 − 0,9 = 0,1`. O mesmo par
    passa a ser dos mais distantes.

    Um alvo de 1,0 contra um de 0,1 sobre o mesmo par: é isto que separa os dois braços, e não
    a inversão global do sinal — essa apenas inverte a ordem e deixa as diferenças de percentil
    na mesma.
    """
    xs = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    r = np.concatenate([xs, -xs])

    vm = P.valores_do_braco(r, "magnitude")
    mm = P.mapa_percentil(vm)
    alvo_mag = P.alvo_similaridade(mm(np.array([0.05])), mm(np.array([0.05])))[0]
    assert alvo_mag == pytest.approx(1.0)

    vd = P.valores_do_braco(r, "direcao")
    md = P.mapa_percentil(vd)
    assert md(np.array([0.05]))[0] == pytest.approx(1.0)
    assert md(np.array([-0.05]))[0] == pytest.approx(0.1)
    alvo_dir = P.alvo_similaridade(md(np.array([0.05])), md(np.array([-0.05])))[0]
    assert alvo_dir == pytest.approx(0.1)


def test_os_dois_bracos_produzem_alvos_diferentes_no_mesmo_quadro():
    """Fecho ao nível do construtor: mesmos pares, alvos que têm de divergir.

    Usa `estratificado=False` de propósito. Com estratificação a escolha dos pares **depende
    dos valores**, logo os dois braços deixam de seleccionar os mesmos pares — o que é o
    comportamento correcto, e não um defeito. Para comparar alvos sobre pares idênticos é
    preciso a amostragem que ignora os valores.
    """
    df = quadro()
    a = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=200,
                          seed=7, estratificado=False)
    b = P.construir_pares(df, coluna_retorno="abn_h3", arma="direcao", n_pares=200,
                          seed=7, estratificado=False)
    assert (a["texto_a"] == b["texto_a"]).all(), "os pares deviam ser os mesmos"
    assert not np.allclose(a["alvo"].to_numpy(), b["alvo"].to_numpy())


# ── fuga pelo bloco ───────────────────────────────────────────────────────────

def test_nenhum_par_cruza_a_fronteira_dos_blocos():
    df = pd.concat([quadro(60, "train", 1), quadro(60, "test", 2),
                    quadro(20, "embargo", 3)], ignore_index=True)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=300, seed=11, blocos=("train",))
    assert set(p["split"]) == {"train"}


def test_o_embargo_nunca_entra():
    df = pd.concat([quadro(40, "train", 1), quadro(40, "embargo", 2)], ignore_index=True)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=200, seed=11, blocos=("train", "val", "test"))
    assert "embargo" not in set(p["split"])


def test_os_pares_sao_entre_empresas_diferentes():
    """A avaliação proíbe recuperar da própria empresa; o treino não pode ensinar o contrário."""
    df = quadro(90)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=300, seed=3)
    assert (p["ticker_a"] != p["ticker_b"]).all()


def test_nenhuma_manchete_e_emparelhada_consigo_propria():
    df = quadro(90)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=300, seed=3)
    assert (p["texto_a"] != p["texto_b"]).all()


def test_a_mesma_semente_da_os_mesmos_pares():
    df = quadro(90)
    a = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=150, seed=42)
    b = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=150, seed=42)
    pd.testing.assert_frame_equal(a, b)


def test_sementes_diferentes_dao_pares_diferentes():
    df = quadro(90)
    a = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=150, seed=42)
    b = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=150, seed=43)
    assert not a[["texto_a", "texto_b"]].equals(b[["texto_a", "texto_b"]])


# ── a fuga que passa despercebida: pela normalização ──────────────────────────

def test_o_mapa_de_percentis_e_ajustado_so_no_treino():
    """⚠️ O teste mais importante deste ficheiro.

    O alvo é a distância entre percentis. Se o mapa for ajustado sobre todos os blocos, a
    distribuição do teste entra no treino **sem que nenhum par cruze fronteira nenhuma** — e
    nenhum dos testes acima o apanharia.

    A prova: constrói-se o mapa com o treino, guardam-se os alvos; a seguir mete-se no bloco
    de teste um punhado de valores absurdos, que mudariam qualquer percentil calculado sobre
    o conjunto todo; os alvos do treino **não podem mexer**.
    """
    treino = quadro(60, "train", 1)
    teste = quadro(60, "test", 2)
    df = pd.concat([treino, teste], ignore_index=True)
    antes = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                              n_pares=200, seed=5, blocos=("train",))

    teste_extremo = teste.assign(abn_h3=teste["abn_h3"] * 1000.0)
    df2 = pd.concat([treino, teste_extremo], ignore_index=True)
    depois = P.construir_pares(df2, coluna_retorno="abn_h3", arma="magnitude",
                               n_pares=200, seed=5, blocos=("train",))

    assert np.allclose(antes["alvo"].to_numpy(), depois["alvo"].to_numpy()), (
        "a distribuição do bloco de teste mudou os alvos do treino — o mapa de percentis "
        "está a ser ajustado sobre dados que o treino não pode ver")


def test_o_mapa_do_treino_e_reutilizado_nos_outros_blocos():
    """Avaliar noutro bloco usa o mapa do treino, não um mapa novo."""
    treino = quadro(60, "train", 1)
    val = quadro(60, "val", 2)
    df = pd.concat([treino, val], ignore_index=True)
    mapa = P.mapa_percentil(np.abs(treino["abn_h3"].to_numpy()))
    a = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=100, seed=9, blocos=("val",), mapa=mapa)
    b = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=100, seed=9, blocos=("val",))
    # sem `mapa`, ajusta-se ao próprio bloco -> alvos diferentes. É a diferença que interessa.
    assert not np.allclose(a["alvo"].to_numpy(), b["alvo"].to_numpy())


def test_o_alvo_fica_sempre_em_zero_um():
    df = quadro(90)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=300, seed=3)
    v = p["alvo"].to_numpy()
    assert np.all((v >= 0.0) & (v <= 1.0))


def test_pede_pares_a_mais_do_que_o_bloco_permite():
    """Um bloco pequeno não pode devolver silenciosamente menos pares do que os pedidos."""
    df = quadro(6)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude", n_pares=50, seed=1)
    assert len(p) == 50, "o construtor devolveu menos pares do que os pedidos, sem avisar"


def test_recusa_um_braco_desconhecido():
    df = quadro(30)
    with pytest.raises(ValueError, match="arma"):
        P.construir_pares(df, coluna_retorno="abn_h3", arma="tendencia", n_pares=10, seed=1)


# ── o colapso, e a amostragem que o evita ─────────────────────────────────────

def test_a_amostragem_ao_acaso_concentra_o_alvo_no_meio():
    """O defeito, documentado como teste: é isto que faz o codificador colapsar.

    Sorteando dois índices ao acaso, a diferença de percentis é triangular — média 1/3, quase
    nada nos extremos — e o alvo `1 − |Δ|` fica agarrado a 0,67. O modelo minimiza a perda a
    prever a média para tudo, que é o mesmo que mapear todas as manchetes para o mesmo sítio.
    Foi o que aconteceu no primeiro treino: o cosseno entre manchetes diferentes passou de
    0,22 para 0,99.
    """
    df = quadro(300, semente=4)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=3000, seed=1, estratificado=False)
    assert p["alvo"].mean() == pytest.approx(2 / 3, abs=0.05)
    assert p["alvo"].std() < 0.26
    nos_extremos = float(((p["alvo"] < 0.15) | (p["alvo"] > 0.95)).mean())
    assert nos_extremos < 0.15, f"só {nos_extremos:.1%} de pares informativos"


def test_a_amostragem_estratificada_cobre_o_intervalo_todo():
    """A correcção: sorteia-se a distância pretendida e só depois se procura o par.

    A comparação é contra a amostragem ao acaso, sobre o mesmo quadro e o mesmo número de
    pares. Um limiar absoluto seria má ideia: com `|Δ|` uniforme a fracção de pares extremos
    tem valor teórico exacto, e um teste posto em cima dele falha por ruído sem que nada esteja
    errado.
    """
    df = quadro(300, semente=4)
    acaso = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                              n_pares=3000, seed=1, estratificado=False)
    estrat = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                               n_pares=3000, seed=1, estratificado=True)

    assert estrat["alvo"].mean() == pytest.approx(0.5, abs=0.08)
    assert estrat["alvo"].std() > acaso["alvo"].std()

    # O que distingue as duas amostragens é a cauda dos pares MUITO DIFERENTES. Sob a
    # triangular, P(alvo < 0,15) = (1 − 0,85)² ≈ 2%; sob a uniforme é 15%. Os pares muito
    # PARECIDOS abundam nas duas, e por isso não servem de indicador.
    def dissemelhantes(p):
        return float((p["alvo"] < 0.15).mean())

    assert dissemelhantes(acaso) < 0.05, "a triangular não devia produzir estes pares"
    assert dissemelhantes(estrat) > 4 * dissemelhantes(acaso), (
        f"estratificada {dissemelhantes(estrat):.1%} contra "
        f"acaso {dissemelhantes(acaso):.1%}")


def test_a_estratificada_mantem_as_garantias_todas():
    df = pd.concat([quadro(200, "train", 1), quadro(200, "test", 2)], ignore_index=True)
    p = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=800, seed=3, blocos=("train",), estratificado=True)
    assert set(p["split"]) == {"train"}
    assert (p["ticker_a"] != p["ticker_b"]).all()
    assert (p["texto_a"] != p["texto_b"]).all()
    v = p["alvo"].to_numpy()
    assert np.all((v >= 0.0) & (v <= 1.0))


def test_a_estratificada_e_determinista():
    df = quadro(200)
    a = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=400, seed=9, estratificado=True)
    b = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                          n_pares=400, seed=9, estratificado=True)
    pd.testing.assert_frame_equal(a, b)


def test_a_estratificada_e_o_comportamento_por_omissao():
    """Quem não escolher, recebe a que não colapsa."""
    df = quadro(200)
    padrao = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                               n_pares=400, seed=9)
    estrat = P.construir_pares(df, coluna_retorno="abn_h3", arma="magnitude",
                               n_pares=400, seed=9, estratificado=True)
    pd.testing.assert_frame_equal(padrao, estrat)
