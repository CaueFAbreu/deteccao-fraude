import hashlib
from pathlib import Path

import pandas as pd

COLUNAS_FEATURES = ["Time", *(f"V{i}" for i in range(1, 29)), "Amount"]
COLUNA_ALVO = "Class"


def calcular_sha256(caminho):
    hash_arquivo = hashlib.sha256()
    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1 << 20), b""):
            hash_arquivo.update(bloco)
    return hash_arquivo.hexdigest()


def remover_duplicatas(df):
    return df.drop_duplicates(keep="first")


def carregar_dados(caminho, sha256_esperado):
    sha256 = calcular_sha256(caminho)
    if sha256 != sha256_esperado:
        raise ValueError(f"SHA-256 de {caminho} difere do manifesto: {sha256}")

    df = pd.read_csv(caminho)
    colunas_esperadas = [*COLUNAS_FEATURES, COLUNA_ALVO]
    if list(df.columns) != colunas_esperadas:
        raise ValueError(f"Colunas inesperadas em {caminho}: {list(df.columns)}")

    return remover_duplicatas(df)
