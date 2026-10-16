import sys
from importlib.metadata import version
from pathlib import Path

import fastapi
import joblib
import numpy
import pandas
import pydantic
import pytest
import sklearn

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVOS_REQUISITOS = ("requirements.txt", "requirements-dev.txt")


def ler_versoes_fixadas():
    versoes = {}
    for nome_arquivo in ARQUIVOS_REQUISITOS:
        texto = (RAIZ_PROJETO / nome_arquivo).read_text(encoding="utf-8")
        for linha in texto.splitlines():
            linha = linha.strip()
            if not linha or linha.startswith(("#", "-")):
                continue
            assert "==" in linha, f"Versão não fixada em {nome_arquivo}: {linha}"
            pacote, versao = linha.split("==")
            versoes[pacote] = versao
    return versoes


def test_versao_python():
    assert sys.version_info[:2] == (3, 13)


def test_bibliotecas_principais_importam():
    for modulo in (pandas, numpy, sklearn, fastapi, pydantic, joblib):
        assert modulo.__version__


@pytest.mark.parametrize(("pacote", "versao_fixada"), ler_versoes_fixadas().items())
def test_versao_instalada_igual_a_fixada(pacote, versao_fixada):
    assert version(pacote) == versao_fixada
