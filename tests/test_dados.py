import pandas as pd
import pytest

from src.data.dados import (
    COLUNA_ALVO,
    COLUNAS_FEATURES,
    calcular_sha256,
    carregar_dados,
    remover_duplicatas,
)


def criar_transacoes(linhas):
    return pd.DataFrame(
        [[*valores, classe] for valores, classe in linhas],
        columns=[*COLUNAS_FEATURES, COLUNA_ALVO],
    )


@pytest.fixture
def transacoes():
    zeros = [0.0] * len(COLUNAS_FEATURES)
    uns = [1.0] * len(COLUNAS_FEATURES)
    return criar_transacoes([(zeros, 0), (uns, 1), (zeros, 0), (uns, 0)])


def test_remover_duplicatas_mantem_primeira_ocorrencia_e_indice_original(transacoes):
    resultado = remover_duplicatas(transacoes)
    assert list(resultado.index) == [0, 1, 3]


def test_mesmas_features_com_classe_diferente_nao_sao_duplicatas(transacoes):
    resultado = remover_duplicatas(transacoes)
    assert resultado.loc[[1, 3], COLUNA_ALVO].tolist() == [1, 0]


def test_carregar_dados_confere_hash_e_remove_duplicatas(tmp_path, transacoes):
    caminho = tmp_path / "transacoes.csv"
    transacoes.to_csv(caminho, index=False)
    resultado = carregar_dados(caminho, calcular_sha256(caminho))
    assert list(resultado.index) == [0, 1, 3]


def test_carregar_dados_rejeita_hash_diferente(tmp_path, transacoes):
    caminho = tmp_path / "transacoes.csv"
    transacoes.to_csv(caminho, index=False)
    with pytest.raises(ValueError, match="SHA-256"):
        carregar_dados(caminho, "0" * 64)


def test_carregar_dados_rejeita_colunas_inesperadas(tmp_path, transacoes):
    caminho = tmp_path / "transacoes.csv"
    transacoes.drop(columns="Amount").to_csv(caminho, index=False)
    with pytest.raises(ValueError, match="Colunas"):
        carregar_dados(caminho, calcular_sha256(caminho))
