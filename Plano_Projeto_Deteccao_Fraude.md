# Plano de execução — Classificação de fraude e API de inferência

Guia para a equipe • Versão 1.0 • 6 de outubro de 2026

## 1. Missão e resultado esperado

Construam um serviço demonstrável que receba uma transação no formato do dataset, valide os campos, execute um classificador treinado e devolva um score e uma classificação. Comparem regressão logística e random forest, expliquem os resultados e entreguem uma API reproduzível e testada.

Considerem fraude a classe positiva, identificada por `Class = 1`. Um alerta é uma previsão do modelo, não uma comprovação de fraude. O objetivo desta versão é uma demonstração técnica com dados públicos, sem integração bancária.

O projeto estará concluído quando outra pessoa conseguir obter os dados conforme as instruções, reproduzir os experimentos, entender a escolha do modelo e do limiar, iniciar a API e verificar uma previsão.

## 2. Decisões iniciais e escopo

Adotem Python, pandas, scikit-learn, FastAPI, Pydantic, Uvicorn, pytest, joblib e Docker. Fixem versões compatíveis depois de validar a instalação. Usem Git para registrar alterações. Notebooks servem à exploração; preparação, treinamento, avaliação e inferência devem estar em módulos executáveis.

Incluam no escopo: análise dos dados; controle de qualidade; divisão dos conjuntos; baseline; dois modelos; tratamento do desbalanceamento; escolha do limiar; relatório; artefato versionado; API; testes; imagem Docker; documentação; demonstração de implantação e operação.

Deixem para uma evolução: interface visual, dashboard, banco de transações, processamento em lote, novos algoritmos, retreinamento automático e integração com pagamentos. Não são necessários para comprovar esta API.

Definam antes dos experimentos uma política de decisão. Proposta didática: maximizar recall desde que precision na validação seja pelo menos 80%. Esse número é uma meta de exercício, não um requisito bancário validado. Se nenhum candidato alcançar a meta, documentem a inviabilidade; não reduzam a exigência silenciosamente. Em uso real, substituam a meta por custos e capacidade de revisão definidos pelo responsável do negócio.

## 3. Papéis e modo de trabalho

| Responsável | Atribuição | Evidência para revisão |
|---|---|---|
| Líder técnico | Aprovar escopo, protocolo experimental, contratos e critérios de entrega | Decisões registradas e checklist de revisão |
| Dados e ML | Auditar dataset, implementar pipelines, treinar e comparar | Manifesto dos dados, experimentos e relatório |
| API | Implementar contrato, carregamento e inferência | Documentação OpenAPI e exemplos |
| Qualidade e entrega | Testes, integração contínua, empacotamento e operação | Checks automáticos e demonstração |

Se trabalhar sozinho, execute os quatro papéis em sequência. Para cada tarefa, registre objetivo, responsável, dependências, entrega e evidência de conclusão. Abram uma mudança pequena por tarefa e revisem antes de integrar. Nunca incluam credenciais no repositório.

## 4. Arquitetura e organização

Mantenham dois fluxos distintos:

1. **Preparação e treinamento:** dataset → auditoria → divisão → pipelines → experimentos → seleção → avaliação final → artefato.
2. **Inferência:** requisição → validação → pipeline salvo → score → comparação com limiar → resposta.

A API não treina o modelo em uma requisição. Carregue o artefato uma vez na inicialização e use a mesma transformação do treinamento.

| Diretório ou arquivo | Conteúdo esperado |
|---|---|
| `data/raw/` | Arquivo original, preservado e fora do Git |
| `data/processed/` | Partições ou índices reproduzíveis, fora do Git |
| `notebooks/` | Exploração e gráficos explicativos |
| `src/data/` | Leitura, auditoria e divisão |
| `src/ml/` | Pipelines, treinamento, avaliação e empacotamento |
| `src/api/` | Rotas, schemas, configuração e carregamento |
| `tests/` | Testes de dados, modelos e API |
| `configs/` | Semente, divisão, hiperparâmetros e política do limiar |
| `artifacts/` | Pipeline escolhido e metadados; versionados em armazenamento adequado |
| `reports/` | Métricas, gráficos, comparação e model card |
| `README.md` | Instruções para reproduzir e demonstrar |
| `Dockerfile` e configuração de CI | Execução consistente e verificações automáticas |

## 5. Etapas de execução

### Etapa 1 — Formalizem o problema

**Ordem:** escrevam uma página com objetivo, usuários da API, entradas, saída, significado de cada classe, uso permitido e limitações. Definam a política de decisão, o orçamento de experimentos e as condições da demonstração.

Definam requisitos funcionais: receber uma transação; validar; calcular score; aplicar limiar; devolver versão; disponibilizar documentação; informar disponibilidade.

Definam requisitos de qualidade: execução reproduzível; ausência de vazamento criado pelo projeto; consistência entre treinamento e API; erros previsíveis; artefatos rastreáveis; registros sem conteúdo completo das transações. Como meta inicial de desempenho, proponham p95 de até 200 ms para inferência unitária após aquecimento, com cinco clientes simultâneos durante 60 segundos. Registrem CPU, memória e local de medição; validem a meta por medição, sem prometer o resultado antecipadamente.

**Entregas:** escopo, requisitos e decisões.

**Concluído quando:** cada requisito possui uma forma de verificação e todos entendem o significado do alerta.

### Etapa 2 — Preparem o ambiente e o repositório

**Ordem:** criem ambiente virtual, organizem diretórios, fixem dependências e adicionem regras para ignorar dados, credenciais e arquivos locais. Registrem versão do Python e bibliotecas. Configurem formatação, análise estática e pytest na integração contínua.

Definam interfaces de execução para preparar dados, treinar, avaliar e iniciar a API. Documentem os comandos reais quando os módulos forem implementados; o plano não pressupõe scripts já existentes.

**Entregas:** estrutura inicial, dependências e CI.

**Concluído quando:** uma instalação limpa executa os checks iniciais seguindo o README.

### Etapa 3 — Obtenham e auditem os dados

**Ordem:** adotem inicialmente o Credit Card Fraud Detection do Kaggle. Confiram na versão baixada o esquema esperado: `Time`, `Amount`, `V1` a `V28` e o alvo `Class`. Registrem origem, data de obtenção, versão disponível, licença/termos, hash do arquivo, quantidade de linhas e frequência de cada classe. Verifiquem permissão antes de redistribuir o arquivo.

Inspecionem tipos, campos ausentes, valores não finitos, rótulos fora de 0/1, duplicatas e distribuições. Não descartem valores extremos somente por serem extremos: podem conter evidência de fraude. Registrem toda exclusão e seu efeito sobre a classe rara.

Criem um dicionário dos campos. As características `V1` a `V28` são uma representação anonimizada por PCA: não inventem significados de negócio nem tentem reconstruí-las a partir de nome, cartão ou estabelecimento. A API desta demonstração depende de entradas nessa representação. Uma futura integração real exigirá outro dataset ou uma transformação de origem disponível e reproduzível.

**Entregas:** manifesto dos dados, auditoria e dicionário.

**Concluído quando:** o esquema e a prevalência foram medidos, os problemas foram tratados e cada transformação tem justificativa.

### Etapa 4 — Definam o protocolo de avaliação

**Ordem:** usem, para o benchmark didático, divisão estratificada de 60% treino, 20% validação e 20% teste, com semente fixa. Gravem índices e contagem de positivos por conjunto. Antes da divisão, removam duplicatas exatas justificadamente ou mantenham cópias no mesmo conjunto; não permitam cópias da mesma observação em treino e teste.

Treino serve para aprender parâmetros. Façam busca limitada de hiperparâmetros com validação cruzada estratificada em três folds exclusivamente dentro do treino. Validação separada serve à escolha do limiar e à decisão entre candidatos. Reservem teste para avaliar a configuração congelada.

Mantenham validação e teste com a proporção natural de classes. Ajustem normalização, imputação e seleção de atributos apenas no treino de cada fold, por meio de pipelines. Não usem `Class` como entrada.

Para afirmar desempenho em transações futuras, planejem avaliação adicional por ordem de `Time`: passado para treino, período seguinte para validação e período posterior para teste. Não misturem observações futuras no treino e não estratifiquem embaralhando essa avaliação temporal. Relatem limitações se houver poucos positivos. O benchmark aleatório não comprova generalização temporal; a PCA fornecida também tem um processo de origem que vocês não controlam.

**Entregas:** protocolo e manifesto das partições.

**Concluído quando:** partições são reproduzíveis, sem sobreposição indevida e sem ajuste aprendido sobre validação ou teste.

### Etapa 5 — Implementem baseline e pipelines

**Ordem:** criem primeiro um baseline que sempre prevê a classe legítima. Mostrem que alta acurácia pode coexistir com recall de fraude igual a zero. Tratem precision indefinida quando não houver alertas explicitamente.

Implementem dois candidatos:

- **Regressão logística:** pipeline com normalização e classificador. Avaliem regularização `C`, ponderação de classes e convergência.
- **Random forest:** pipeline com seleção consistente dos campos e classificador. Avaliem número de árvores, profundidade, mínimo de amostras por folha e ponderação de classes.

Comecem comparando ponderação de classes desligada e ligada. Limitem a busca, por exemplo, a até 12 configurações por família e três folds. Registrem o mesmo orçamento para os dois modelos. Fixem a semente quando aplicável.

Não tornem SMOTE obrigatório. Se adicionarem reamostragem como experimento, executem-na somente no treino de cada fold, em pipeline compatível; nunca antes da divisão nem na validação ou no teste.

**Entregas:** baseline, pipelines e histórico dos experimentos.

**Concluído quando:** os dois modelos foram avaliados nas mesmas partições e cada execução registra configuração, dados, duração e resultados.

### Etapa 6 — Comparem resultados e escolham o limiar

**Ordem:** adotem Average Precision (AP) como métrica principal para comparar o ranking dos scores na validação cruzada. Reportem também curva precision-recall. AP e área trapezoidal sob a curva PR não são a mesma implementação: nomeiem exatamente o cálculo utilizado.

| Medida | Pergunta respondida |
|---|---|
| Precision da fraude | Entre os alertas, quantos eram fraudes? |
| Recall da fraude | Entre as fraudes, quantas foram detectadas? |
| F1 | Como precision e recall se equilibram? |
| F2 | Qual o equilíbrio com maior peso para recall? |
| AP | Como o modelo ordena positivos ao variar o limiar? |
| ROC-AUC | Como o score separa as classes? Use como complemento. |
| Matriz de confusão | Quantos TP, FP, FN e TN ocorreram? |
| Taxa de alertas | Qual parcela das transações precisaria de revisão? |
| Acurácia | Qual o acerto global? Não use isoladamente para seleção. |
| Latência e tamanho | Quanto custa servir cada candidato? |

Na validação separada, testem limiares e apliquem a política definida na etapa 1. O valor 0,5 pode ser uma referência, mas não precisa ser a decisão final. Em empate, usem AP e depois simplicidade/latência como critérios registrados previamente.

Tratem o resultado como score do modelo. Se quiserem apresentá-lo como probabilidade confiável, avaliem calibração e curva de confiabilidade; ajustem calibradores com folds ou conjunto específico dentro do treino, sem usar o teste. Ponderação de classes não garante probabilidades calibradas.

**Entregas:** tabela comparativa, curvas, modelo escolhido, limiar e justificativa.

**Concluído quando:** a escolha cumpre a política ou sua inviabilidade está registrada, sem seleção pelo teste.

### Etapa 7 — Congelem, avaliem e empacotem

**Ordem:** preservem nesta primeira versão o pipeline treinado que foi validado. Não retreinem em treino mais validação mantendo automaticamente o mesmo limiar: a distribuição dos scores pode mudar. Uma evolução pode usar protocolo próprio de refit, calibração e limiar.

Congelem pipeline, lista e ordem de campos, limiar e versões. Avaliem todos os candidatos previamente definidos no teste para relatório, mas mantenham o vencedor já escolhido. Não alterem hiperparâmetros depois de observar o teste; uma nova rodada deve ser identificada como tal e exige nova evidência independente para conclusões finais.

Reportem métricas, números absolutos da matriz e número de fraudes no teste. Acrescentem intervalos de confiança por bootstrap, explicitando pressupostos de independência e limitações para dependência temporal. Evitem concluir superioridade definitiva com diferenças pequenas e poucos positivos.

Salvem pipeline e metadados: identificador da versão, features, classe positiva, limiar, hash do dataset, semente, configuração, dependências, commit, métricas e data. Carreguem apenas artefatos confiáveis: formatos como joblib podem executar código ao desserializar.

**Entregas:** artefato, metadados, relatório final e model card.

**Concluído quando:** carregar o pipeline reproduz scores e decisões do objeto original dentro da tolerância definida.

### Etapa 8 — Construam a API

**Ordem:** definam o contrato antes de implementar rotas. Usem objeto JSON com campos nomeados `Time`, `Amount`, `V1` a `V28`; excluam `Class`. Todos devem ser numéricos finitos e obrigatórios. Para este dataset, validem `Time` e `Amount` não negativos; aceitem componentes V negativos. Rejeitem campos extras e tipos incorretos, incluindo strings e booleanos quando se exige número.

Façam a aplicação construir explicitamente a ordem das features pelos metadados. Não dependam da ordem das chaves JSON. Apliquem normalização pelo pipeline salvo, sem recalcular nem duplicar transformação.

| Rota | Contrato |
|---|---|
| `POST /predict` | Recebe uma transação; devolve score de fraude, `predicted_class`, `threshold`, `model_version` e `request_id` |
| `GET /health` | Informa que o processo responde |
| `GET /ready` | Confirma artefato carregado e compatível; 503 se indisponível |
| `GET /docs` | Documenta entradas, saídas e exemplos |

Use `score >= threshold` para a decisão e confirme que o score corresponde à classe 1, consultando as classes do estimador. Não aceite o limiar enviado pelo cliente. Devolva 200 para previsão válida, 422 para contrato inválido e 503 para indisponibilidade; erros internos devem ter resposta genérica e identificação para diagnóstico. Não substitua falha do modelo por previsão legítima.

**Entregas:** API, contrato OpenAPI e amostras de requisição/resposta.

**Concluído quando:** uma transação válida gera resposta coerente e entradas inválidas são recusadas sem chamar inferência.

### Etapa 9 — Verifiquem o sistema

**Ordem:** testem os comportamentos que podem invalidar o resultado:

1. Esquema incorreto, rótulos inválidos e vazamento entre partições.
2. Mesmo exemplo produz score e classe iguais offline e via API.
3. JSON com chaves reordenadas produz o mesmo resultado.
4. Campos ausentes/extras, NaN/infinito, tipos incorretos e `Amount` negativo são recusados.
5. Classe positiva e regra do limiar são aplicadas corretamente, inclusive na igualdade.
6. Artefato ausente, incompatível ou corrompido impede readiness.
7. Resposta contém versão e identificador; erros não expõem detalhes internos.
8. Medição de latência segue o cenário definido e registra erros e recursos.

Não criem teste exigindo que toda fraude do dataset seja classificada corretamente: modelos cometem erros. Testem consistência da implementação e avaliem qualidade estatística no relatório. Usem pequena amostra permitida ou dados sintéticos para CI; treinar o dataset inteiro a cada commit é desnecessário.

**Entregas:** suíte de testes, checks de CI e relatório de desempenho.

**Concluído quando:** os testes passam em ambiente limpo e eventuais metas não atingidas têm ação registrada.

### Etapa 10 — Empacotem e demonstrem a implantação

**Ordem:** construam imagem Docker com dependências fixadas e processo sem privilégios. Carreguem o artefato aprovado com checksum e versão. Configurem checks de saúde/readiness e executem teste de fumaça após a implantação.

Para exposição pública, configurem HTTPS, autenticação por chave ou mecanismo equivalente, segredo em configuração externa e limites de requisição/tamanho. Validem credencial válida, inválida e ausente. Restrinjam CORS somente se houver cliente de navegador que precise dele. Não salvem o corpo inteiro das requisições em logs.

Registrem request_id, versão, status, latência e falhas. Monitorem disponibilidade, p95 e taxa de erros. Monitorem distribuição de scores, entradas e alertas; só calculem precision/recall de produção quando rótulos confiáveis estiverem disponíveis. Definam quem investiga degradação e como retornar à versão anterior.

**Entregas:** imagem, instruções de implantação, configuração de observabilidade e procedimento de rollback.

**Concluído quando:** o ambiente de demonstração atende uma requisição autenticada, rejeita acesso indevido quando exposto e permite restaurar o artefato anterior.

### Etapa 11 — Documentem e façam a entrega

**Ordem:** escrevam README com instalação, obtenção dos dados, reprodução dos experimentos, inicialização da API, teste, exemplos e troubleshooting. Incluam relatório comparativo e model card com origem, limitações, população observada, critérios de seleção, métricas, usos previstos e usos não validados.

Demonstrem: baseline; comparação entre modelos; efeito de mudar limiar; uma requisição válida; uma inválida; consistência offline/API; versão servida e rollback. Toda métrica apresentada deve apontar para execução registrada. Nunca preencham resultados esperados como se fossem medidos.

**Entregas:** repositório utilizável, documentação e demonstração.

**Concluído quando:** outra pessoa reproduz o fluxo sem instruções verbais adicionais.

## 6. Sequência sugerida de trabalho

| Bloco | Etapas | Marco de entrega |
|---|---|---|
| 1 | 1–3 | Problema definido, ambiente e dados auditados |
| 2 | 4–5 | Partições e experimentos reproduzíveis |
| 3 | 6–7 | Comparação, limiar e artefato aprovado |
| 4 | 8–9 | API integrada e testada |
| 5 | 10–11 | Demonstração implantada e documentação completa |

Use blocos de aproximadamente uma semana como referência inicial, ajustando à experiência e disponibilidade. Não avance só porque o prazo terminou: passe ao próximo marco quando os critérios forem atendidos. O bloco 4 depende do contrato e artefato; o desenho do contrato pode começar antes, mas a integração deve usar o pipeline real.

## 7. Checklist de aceite final

- [ ] Dados identificados, termos conferidos e hash registrado.
- [ ] Partições e transformações reproduzíveis, sem vazamento introduzido pelo projeto.
- [ ] Baseline, regressão logística e random forest comparados com o mesmo protocolo.
- [ ] Precision, recall, F1/F2, AP, curva PR e matriz de confusão documentados.
- [ ] Modelo e limiar escolhidos sem consulta ao teste.
- [ ] Teste final reportado com contagens e limitações.
- [ ] Pipeline e metadados versionados e verificados após carregamento.
- [ ] API valida dados e coincide com inferência offline.
- [ ] CI, testes de integração e medição de desempenho executados.
- [ ] Implantação demonstrada, logs adequados e rollback documentado.
- [ ] README e model card permitem reprodução independente.

## 8. Referências técnicas

- Dataset proposto: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud — conferir metadados e termos da versão obtida; não foi baixado neste planejamento.
- Pipelines e prevenção de vazamento: https://scikit-learn.org/stable/common_pitfalls.html
- Definição de Average Precision: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
- Escolha do limiar: https://scikit-learn.org/stable/modules/classification_threshold.html
- Contratos de entrada FastAPI: https://fastapi.tiangolo.com/tutorial/body/
- Testes de API: https://fastapi.tiangolo.com/tutorial/testing/

As metas, divisão dos conjuntos, orçamento de busca e sequência de trabalho são decisões propostas para este projeto. Métricas e desempenho serão medidos durante a implementação.
