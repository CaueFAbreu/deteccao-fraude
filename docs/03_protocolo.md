# Protocolo de avaliação e partições

## 1. Procedimento

Parâmetros em `configs/protocolo.json`.

1. Conferir o SHA-256 de `data/raw/creditcard.csv` contra o manifesto (`docs/02_dados.md`) e validar as colunas.
2. Remover duplicatas exatas, mantendo a primeira ocorrência (decisão D1).
3. Dividir em treino (60%), validação (20%) e teste (20%) em duas etapas estratificadas por `Class`, com semente `42`: primeiro treino contra o restante (40%), depois o restante em metades iguais.
4. Atribuir a cada linha de treino um de três folds com `StratifiedKFold(shuffle=True, random_state=42)`, aplicado aos índices de treino em ordem crescente.
5. Gravar a atribuição de cada linha e o resumo com contagens e hashes.

A divisão usa apenas o rótulo; nenhuma feature participa e nenhuma transformação é ajustada nesta etapa. Validação e teste mantêm a proporção natural de classes e não são reamostrados.

## 2. Papéis dos conjuntos

| Conjunto | Uso |
|---|---|
| Treino | Busca de hiperparâmetros nos três folds internos e ajuste final de cada família. |
| Validação | Escolha do limiar e decisão entre candidatos. |
| Teste | Avaliação única da configuração congelada. |

As duas famílias usam os mesmos folds, lidos do arquivo de partições.

## 3. Saídas

| Arquivo | Conteúdo | Versionado |
|---|---|---|
| `data/processed/particoes.csv` | Colunas `indice`, `particao` e `fold` (vazio fora do treino) | Não |
| `reports/particoes.json` | Contagens, taxa de fraude e SHA-256 dos índices por partição e por fold | Sim |

`indice` é a posição da linha no CSV original, contada a partir de 0 na primeira linha de dados. O SHA-256 dos índices é calculado sobre os índices em ordem crescente, um por linha, em UTF-8.

## 4. Resultado

| Partição | Linhas | Fraudes | Taxa de fraude |
|---|---:|---:|---:|
| Treino | 170.235 | 284 | 0,1668% |
| Validação | 56.745 | 94 | 0,1657% |
| Teste | 56.746 | 95 | 0,1674% |
| **Total** | **283.726** | **473** | **0,1667%** |

| Fold (treino) | Linhas | Fraudes |
|---|---:|---:|
| 0 | 56.745 | 94 |
| 1 | 56.745 | 95 |
| 2 | 56.745 | 95 |

Os hashes dos índices estão em `reports/particoes.json`.

## 5. Reprodução

```powershell
python -m src.data.particoes
pytest tests/test_particoes.py
```

Com o dataset presente, o teste `test_particoes_reais_coincidem_com_resumo_registrado` regenera as partições e compara contagens e hashes com `reports/particoes.json`. Sem o dataset, como na integração contínua, o teste é ignorado.

## 6. Limitações

- A divisão aleatória estratificada não avalia desempenho em transações futuras. Essa afirmação exigiria uma avaliação adicional ordenada por `Time`, fora do escopo desta versão.
- As linhas que repetem `V1`–`V28` e `Amount` com `Time` diferente (D5) podem ficar em partições diferentes, o que pode favorecer a avaliação da classe legítima.
- Com cerca de 95 fraudes em validação e teste, cada fraude corresponde a aproximadamente 1 ponto percentual de recall.
