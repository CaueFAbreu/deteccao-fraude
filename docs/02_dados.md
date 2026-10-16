# Dados — Credit Card Fraud Detection

## 1. Manifesto

| Campo | Valor |
|---|---|
| Fonte | https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud |
| Publicação | Machine Learning Group — Université Libre de Bruxelles (ULB) |
| Citação principal | Andrea Dal Pozzolo, Olivier Caelen, Reid A. Johnson e Gianluca Bontempi. *Calibrating Probability with Undersampling for Unbalanced Classification*. IEEE Symposium on Computational Intelligence and Data Mining (CIDM), 2015. Demais trabalhos indicados na página do dataset. |
| Versão | Version 3 |
| Licença | Database Contents License (DbCL) v1.0 — https://opendatacommons.org/licenses/dbcl/1-0/ |
| Data de obtenção | 16/10/2026 |
| Arquivo | `data/raw/creditcard.csv` |
| Tamanho | 150.828.752 bytes |
| SHA-256 | `76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89` |

### Licença e distribuição

A DbCL v1.0 permite usar, copiar e redistribuir o conteúdo do banco de dados. Ainda assim, o arquivo não é versionado neste repositório: ele excede o limite de 100 MB por arquivo do GitHub, e a reprodução deve partir da fonte oficial com verificação do SHA-256 acima.

### Contexto declarado pela fonte

Segundo a descrição do dataset, as informações abaixo não foram medidas por este projeto:

- Transações realizadas com cartões de crédito de titulares europeus em setembro de 2013, ao longo de dois dias.
- `V1` a `V28` são componentes resultantes de PCA; os atributos originais não são divulgados por confidencialidade.
- `Time` é o número de segundos decorridos entre cada transação e a primeira transação do dataset.
- `Amount` é o valor da transação.
- `Class` vale 1 para fraude e 0 para os demais casos.

## 2. Obtenção

1. Acessar a página da fonte com uma conta Kaggle e baixar o arquivo da versão indicada no manifesto.
2. Extrair `creditcard.csv` em `data/raw/`.
3. Conferir a integridade:

```powershell
Get-FileHash data/raw/creditcard.csv -Algorithm SHA256
```

```bash
sha256sum data/raw/creditcard.csv
```

O hash deve coincidir com o do manifesto. Se divergir, o arquivo não corresponde ao utilizado neste projeto e os resultados publicados não se aplicam a ele.

## 3. Auditoria

Resultados medidos sobre o arquivo do manifesto por `notebooks/01_auditoria.ipynb`.

| Verificação | Resultado |
|---|---|
| Dimensões | 284.807 linhas e 31 colunas |
| Esquema | Colunas `Time`, `V1`–`V28`, `Amount`, `Class`, nessa ordem; nenhuma ausente ou extra |
| Tipos | 30 colunas `float64`; `Class` em `int64` |
| Valores ausentes | 0 |
| Valores infinitos | 0 |
| Rótulos | Apenas 0 e 1 |
| Classes | 284.315 legítimas e 492 fraudes (prevalência de 0,1727%) |
| Duplicatas exatas | 1.854 linhas envolvidas; 1.081 cópias excedentes, das quais 19 são fraudes |
| Features idênticas com rótulos divergentes | 0 grupos |
| `V1`–`V28` e `Amount` repetidos com `Time` diferente | 8.063 linhas, nenhuma fraude |
| `Time` | 0 a 172.792 s (0 a 48 h), valores inteiros |
| `Amount` | Mínimo 0; mediana 22,00; média 88,35; máximo 25.691,16; nenhum valor negativo |
| `Amount = 0` | 1.825 transações, 27 fraudes |
| Mediana de `Amount` por classe | Legítimas 22,00; fraudes 9,25 |

### Após a remoção das duplicatas exatas

| Medida | Valor |
|---|---|
| Linhas | 283.726 |
| Fraudes | 473 (prevalência de 0,1667%) |
| `Amount = 0` | 1.808 transações, 25 fraudes (taxa de fraude de 1,38%) |
| Mediana de `Amount` | Legítimas 22,00; fraudes 9,82 |

### Observações

- `Amount` tem distribuição fortemente assimétrica à direita: a média é cerca de quatro vezes a mediana.
- A densidade de transações legítimas cai acentuadamente em dois intervalos (aproximadamente 0–8 h e 24–32 h), compatíveis com períodos noturnos; as fraudes não acompanham essa queda na mesma intensidade.
- A taxa de fraude entre transações com `Amount = 0` (1,38%) é cerca de oito vezes a prevalência geral (0,1667%).

## 4. Decisões

| ID | Decisão | Justificativa | Efeito |
|---|---|---|---|
| D1 | Remover duplicatas exatas, mantendo a primeira ocorrência, antes da divisão dos conjuntos | Cópias idênticas distribuídas entre treino e avaliação permitiriam que o modelo fosse avaliado sobre exemplos já vistos, inflando as métricas | −1.081 linhas e −19 fraudes; restam 283.726 linhas e 473 fraudes |
| D2 | Manter transações com `Amount = 0` | Valor válido pelo contrato da API; concentram taxa de fraude superior à geral; podem corresponder a operações de verificação de cartão (hipótese não confirmada pela fonte) | Nenhuma linha removida |
| D3 | Manter valores extremos de `Amount` e `V1`–`V28` | Extremos podem conter evidência de fraude; não há indício de erro de registro | Nenhuma linha removida |
| D4 | Não aplicar imputação | Não há valores ausentes nem infinitos | Nenhuma transformação |
| D5 | Manter linhas que repetem `V1`–`V28` e `Amount` com `Time` diferente | Representam transações distintas no tempo, não cópias do mesmo registro | Nenhuma linha removida; risco registrado nas limitações |

## 5. Dicionário de dados

Intervalos observados após a remoção das duplicatas exatas.

| Campo | Tipo | Unidade | Intervalo observado | Significado |
|---|---|---|---|---|
| `Time` | Número, ≥ 0 | Segundos | 0 a 172.792 | Tempo decorrido desde a primeira transação do arquivo. Não representa data nem hora do dia. |
| `V1`–`V28` | Número real | Sem unidade | −113,74 a 120,59 (conjunto dos 28 campos) | Componentes de PCA fornecidos pela fonte. Não possuem significado de negócio divulgado e não devem ser interpretados nem reconstruídos. |
| `Amount` | Número, ≥ 0 | Moeda não informada pela fonte | 0 a 25.691,16 | Valor da transação, sem normalização pela fonte. |
| `Class` | Inteiro, 0 ou 1 | — | 0 ou 1 | Rótulo: 1 para fraude (classe positiva), 0 para legítima. Usado apenas como alvo; nunca como entrada. |

## 6. Limitações

- **`Time` é relativo ao arquivo.** Mede segundos desde a primeira transação de um recorte de 48 horas, não um instante absoluto. Para uma transação nova não há referência equivalente, e valores acima de 172.792 s ficam fora do intervalo observado no treinamento. Padrões que o modelo aprenda a partir de `Time` não devem ser presumidos válidos para transações futuras.
- **Janela curta.** Dois dias de setembro de 2013 não cobrem sazonalidade, mudanças no comportamento de fraude nem outras populações de clientes.
- **Representação fixa.** O modelo depende de `V1`–`V28`, cuja transformação de origem não está disponível; não é possível gerá-los para transações fora do dataset.
- **Repetições com `Time` diferente.** As 8.063 linhas que repetem `V1`–`V28` e `Amount` podem ficar em conjuntos diferentes numa divisão aleatória, favorecendo a avaliação. Como nenhuma delas é fraude, o efeito esperado concentra-se na classe legítima.
- **Poucos positivos.** Com 473 fraudes após a deduplicação, validação e teste terão cerca de 95 fraudes cada na divisão 60/20/20; pequenas variações de contagem alteram precision e recall de forma perceptível.
