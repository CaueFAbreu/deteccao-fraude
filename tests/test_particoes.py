import json

import numpy as np
import pandas as pd
import pytest

from src.data.dados import COLUNA_ALVO, carregar_dados
from src.data.particoes import (
    NOMES_PARTICOES,
    RAIZ_PROJETO,
    calcular_sha256_indices,
    carregar_protocolo,
    gerar_particoes,
    resumir,
)

FRACOES = {"treino": 0.6, "validacao": 0.2, "teste": 0.2}
TOTAL_LINHAS = 1000
TOTAL_FRAUDES = 50


@pytest.fixture
def y():
    rotulos = np.zeros(TOTAL_LINHAS, dtype=int)
    rotulos[:TOTAL_FRAUDES] = 1
    np.random.default_rng(0).shuffle(rotulos)
    # Índice não contíguo, como o que sobra após a remoção de duplicatas.
    return pd.Series(rotulos, index=np.arange(0, 2 * TOTAL_LINHAS, 2), name=COLUNA_ALVO)


@pytest.fixture
def particoes(y):
    return gerar_particoes(y, semente=42, fracoes=FRACOES, n_folds=3)


def test_protocolo_do_projeto_segue_especificacao():
    protocolo = carregar_protocolo()
    assert protocolo["semente"] == 42
    assert protocolo["fracoes"] == FRACOES
    assert protocolo["n_folds"] == 3


def test_protocolo_rejeita_fracoes_que_nao_somam_um(tmp_path):
    caminho = tmp_path / "protocolo.json"
    caminho.write_text(json.dumps({"fracoes": {"treino": 0.6, "validacao": 0.2, "teste": 0.1}}))
    with pytest.raises(ValueError, match="somar 1"):
        carregar_protocolo(caminho)


def test_particoes_cobrem_todas_as_linhas_sem_sobreposicao(particoes, y):
    assert particoes.index.is_unique
    assert particoes.index.equals(y.index)
    assert set(particoes["particao"]) == set(NOMES_PARTICOES)


def test_tamanhos_seguem_fracoes(particoes):
    contagens = particoes["particao"].value_counts()
    for nome, fracao in FRACOES.items():
        assert contagens[nome] == round(fracao * TOTAL_LINHAS)


def test_estratificacao_preserva_proporcao_de_fraudes(particoes, y):
    for nome, fracao in FRACOES.items():
        fraudes = y[particoes["particao"] == nome].sum()
        assert abs(fraudes - fracao * TOTAL_FRAUDES) <= 1


def test_divisao_reproduzivel_com_mesma_semente(particoes, y):
    pd.testing.assert_frame_equal(particoes, gerar_particoes(y, 42, FRACOES, 3))


def test_semente_diferente_produz_outra_divisao(particoes, y):
    outra = gerar_particoes(y, 7, FRACOES, 3)
    assert not particoes["particao"].equals(outra["particao"])


def test_folds_existem_apenas_no_treino(particoes):
    no_treino = particoes["particao"] == "treino"
    assert particoes.loc[no_treino, "fold"].notna().all()
    assert particoes.loc[~no_treino, "fold"].isna().all()
    assert set(particoes.loc[no_treino, "fold"]) == {0, 1, 2}


def test_folds_sao_estratificados(particoes, y):
    treino = particoes[particoes["particao"] == "treino"]
    fraudes_treino = y[treino.index].sum()
    for _, grupo in treino.groupby("fold"):
        assert abs(len(grupo) - len(treino) / 3) <= 1
        assert abs(y[grupo.index].sum() - fraudes_treino / 3) <= 1


def test_sha256_indices_independe_da_ordem():
    assert calcular_sha256_indices([3, 1, 2]) == calcular_sha256_indices([1, 2, 3])


def test_resumo_soma_as_particoes(particoes, y):
    resumo = resumir(particoes, y)
    assert resumo["linhas"] == TOTAL_LINHAS
    assert resumo["fraudes"] == TOTAL_FRAUDES
    assert sum(p["linhas"] for p in resumo["particoes"].values()) == TOTAL_LINHAS
    linhas_treino = resumo["particoes"]["treino"]["linhas"]
    assert sum(f["linhas"] for f in resumo["folds"].values()) == linhas_treino


PROTOCOLO = carregar_protocolo()
ARQUIVO_DADOS = RAIZ_PROJETO / PROTOCOLO["dados"]["arquivo"]
ARQUIVO_RESUMO = RAIZ_PROJETO / PROTOCOLO["saidas"]["resumo"]


@pytest.mark.skipif(
    not (ARQUIVO_DADOS.exists() and ARQUIVO_RESUMO.exists()),
    reason="Requer o dataset local e o resumo das partições",
)
def test_particoes_reais_coincidem_com_resumo_registrado():
    df = carregar_dados(ARQUIVO_DADOS, PROTOCOLO["dados"]["sha256"])
    assert not df.duplicated().any()

    y_real = df[COLUNA_ALVO]
    particoes = gerar_particoes(
        y_real, PROTOCOLO["semente"], PROTOCOLO["fracoes"], PROTOCOLO["n_folds"]
    )
    registrado = json.loads(ARQUIVO_RESUMO.read_text(encoding="utf-8"))
    obtido = resumir(particoes, y_real)
    for chave in ("linhas", "fraudes", "particoes", "folds"):
        assert obtido[chave] == registrado[chave]
