import sys

import fastapi
import joblib
import numpy
import pandas
import pydantic
import sklearn


def test_versao_python():
    assert sys.version_info[:2] == (3, 13)


def test_bibliotecas_principais():
    for modulo in (pandas, numpy, sklearn, fastapi, pydantic, joblib):
        assert modulo.__version__

    assert sklearn.__version__ == "1.9.1"
