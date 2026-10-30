import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split

from src.data.dados import COLUNA_ALVO, carregar_dados

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_PROTOCOLO = RAIZ_PROJETO / "configs" / "protocolo.json"
NOMES_PARTICOES = ("treino", "validacao", "teste")


def carregar_protocolo(caminho=CAMINHO_PROTOCOLO):
    protocolo = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if not math.isclose(sum(protocolo["fracoes"].values()), 1.0):
        raise ValueError("As frações das partições devem somar 1")
    return protocolo


def dividir(y, semente, fracoes):
    fracao_avaliacao = fracoes["validacao"] + fracoes["teste"]
    indices_treino, indices_avaliacao = train_test_split(
        y.index, test_size=fracao_avaliacao, stratify=y, random_state=semente
    )
    indices_validacao, indices_teste = train_test_split(
        indices_avaliacao,
        test_size=fracoes["teste"] / fracao_avaliacao,
        stratify=y.loc[indices_avaliacao],
        random_state=semente,
    )
    return {
        "treino": np.sort(indices_treino),
        "validacao": np.sort(indices_validacao),
        "teste": np.sort(indices_teste),
    }


def atribuir_folds(y_treino, semente, n_folds):
    divisor = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=semente)
    folds = pd.Series(0, index=y_treino.index, dtype="int8")
    for numero, (_, posicoes) in enumerate(divisor.split(y_treino.index, y_treino)):
        folds.iloc[posicoes] = numero
    return folds


def gerar_particoes(y, semente, fracoes, n_folds):
    indices = dividir(y, semente, fracoes)
    particoes = pd.concat(
        pd.DataFrame({"particao": nome}, index=indices[nome]) for nome in NOMES_PARTICOES
    ).sort_index()
    folds = atribuir_folds(y.loc[indices["treino"]], semente, n_folds)
    particoes["fold"] = folds.reindex(particoes.index).astype("Int8")
    return particoes.rename_axis("indice")


def calcular_sha256_indices(indices):
    texto = "\n".join(str(indice) for indice in sorted(indices))
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def contar(indices, y):
    fraudes = int(y.loc[indices].sum())
    return {
        "linhas": len(indices),
        "fraudes": fraudes,
        "taxa_fraude": round(fraudes / len(indices), 6),
        "sha256_indices": calcular_sha256_indices(indices),
    }


def resumir(particoes, y):
    resumo_particoes = {
        nome: contar(particoes.index[particoes["particao"] == nome], y) for nome in NOMES_PARTICOES
    }
    treino = particoes[particoes["particao"] == "treino"]
    resumo_folds = {str(fold): contar(grupo.index, y) for fold, grupo in treino.groupby("fold")}
    return {
        "linhas": len(particoes),
        "fraudes": int(y.loc[particoes.index].sum()),
        "particoes": resumo_particoes,
        "folds": resumo_folds,
    }


def main():
    protocolo = carregar_protocolo()
    df = carregar_dados(RAIZ_PROJETO / protocolo["dados"]["arquivo"], protocolo["dados"]["sha256"])
    y = df[COLUNA_ALVO]
    particoes = gerar_particoes(y, protocolo["semente"], protocolo["fracoes"], protocolo["n_folds"])

    caminho_particoes = RAIZ_PROJETO / protocolo["saidas"]["particoes"]
    caminho_particoes.parent.mkdir(parents=True, exist_ok=True)
    particoes.to_csv(caminho_particoes)

    resumo = {
        "sha256_dados": protocolo["dados"]["sha256"],
        "semente": protocolo["semente"],
        "fracoes": protocolo["fracoes"],
        "n_folds": protocolo["n_folds"],
        **resumir(particoes, y),
    }
    texto_resumo = json.dumps(resumo, indent=2, ensure_ascii=False) + "\n"
    (RAIZ_PROJETO / protocolo["saidas"]["resumo"]).write_text(texto_resumo, encoding="utf-8")
    print(texto_resumo)


if __name__ == "__main__":
    main()
