# Detecção de Fraude em Cartão de Crédito

[![CI](https://github.com/CaueFAbreu/deteccao-fraude/actions/workflows/ci.yml/badge.svg)](https://github.com/CaueFAbreu/deteccao-fraude/actions/workflows/ci.yml)

Serviço de classificação de transações com cartão de crédito. Compara regressão logística e random forest sob um protocolo de avaliação reproduzível e disponibiliza o modelo selecionado por uma API REST que devolve um score de fraude e uma classificação baseada em limiar.

> **Status:** em desenvolvimento. Os resultados dos modelos serão publicados em `reports/` à medida que forem medidos.

## Escopo

- **Entrada:** uma transação no formato do dataset [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (`Time`, `Amount`, `V1`–`V28`).
- **Saída:** score de fraude, classe prevista, limiar aplicado, versão do modelo e identificador da requisição.
- **Classe positiva:** fraude (`Class = 1`). Um alerta é uma previsão do modelo, não uma comprovação de fraude.
- **Uso:** demonstração técnica com dados públicos, executada localmente. Não se destina a decisões financeiras reais.

Especificação completa: [docs/01_problema.md](docs/01_problema.md).

## Stack

Python 3.13 · pandas · scikit-learn · FastAPI · Pydantic · Uvicorn · pytest · Ruff · GitHub Actions

## Instalação

Pré-requisitos: Python 3.13 e Git.

```bash
git clone https://github.com/CaueFAbreu/deteccao-fraude.git
cd deteccao-fraude
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements-dev.txt
```

`requirements.txt` contém apenas as dependências de execução; `requirements-dev.txt` acrescenta as de teste, lint e exploração.

## Verificações

Os mesmos comandos executados pela integração contínua:

```bash
ruff check .
ruff format --check .
pytest
```

## Dados

O dataset não é distribuído neste repositório. Fonte: [Credit Card Fraud Detection (Kaggle)](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud). As instruções de obtenção e verificação de integridade serão documentadas junto com a auditoria dos dados.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/data/` | Leitura, auditoria e divisão dos dados |
| `src/ml/` | Pipelines, treinamento, avaliação e empacotamento |
| `src/api/` | Rotas, schemas, configuração e carregamento do modelo |
| `tests/` | Testes de ambiente, dados, modelos e API |
| `configs/` | Semente, divisão, hiperparâmetros e política de limiar |
| `notebooks/` | Análise exploratória |
| `reports/` | Métricas, gráficos, comparação e model card |
| `docs/` | Especificação do problema e decisões do projeto |
| `data/` | Dados brutos e processados (fora do Git) |
| `artifacts/` | Pipeline treinado e metadados (fora do Git) |

## Roadmap

- [x] Especificação do problema e política de decisão
- [x] Ambiente, dependências fixadas e integração contínua
- [ ] Auditoria dos dados
- [ ] Protocolo de avaliação e partições
- [ ] Baseline e pipelines dos modelos
- [ ] Comparação de modelos e escolha do limiar
- [ ] Avaliação final e empacotamento do artefato
- [ ] API de inferência
- [ ] Testes de integração e desempenho
- [ ] Imagem Docker e demonstração local
- [ ] Model card e documentação final
