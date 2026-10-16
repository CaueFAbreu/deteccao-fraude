# Definição do problema — API de detecção de fraude

**Versão:** 1.1 (inclui condições da demonstração e limitação sobre o número de fraudes)  
**Data:** 15/10/2026  
**Status:** especificação para implementação; metas ainda não medidas.  

## 1. Objetivo

Desenvolver uma API que receba uma transação no formato do dataset público Credit Card Fraud Detection, calcule um score de fraude e devolva uma classificação conforme um limiar previamente definido. A demonstração comparará regressão logística e random forest e disponibilizará o modelo selecionado por um protocolo reproduzível de avaliação.

## 2. Usuários da API

| Usuário ou consumidor | Uso previsto nesta versão |
|---|---|
| Desenvolvedor ou avaliador técnico | Enviar requisições, verificar respostas e reproduzir a demonstração. |
| Analista de dados | Consultar previsões para exemplos do dataset e analisar erros e métricas. |
| Sistema de revisão simulado | Consumir score e classificação para demonstrar encaminhamento de alertas. |

Esta versão é uma demonstração técnica com dados públicos. Não há integração com instituições financeiras, autorização de pagamentos ou atendimento a clientes reais. Uma interface gráfica não é requisito para consumir a API.

## 3. Entradas

O endpoint `POST /predict` receberá um objeto JSON com **uma transação e exatamente 30 campos**, identificados por nome:

| Campo | Quantidade | Tipo e regra | Interpretação |
|---|---:|---|---|
| `Time` | 1 | Número finito, maior ou igual a zero | Tempo na referência adotada pelo dataset; preservar a definição da versão utilizada. |
| `Amount` | 1 | Número finito, maior ou igual a zero | Valor da transação na unidade do dataset, sem conversão implícita. |
| `V1` a `V28` | 28 | Números finitos; valores negativos são permitidos | Características anonimizadas por PCA, na mesma representação do treinamento. |

Todos os campos são obrigatórios. Rejeitar campos ausentes, extras, `null`, strings, booleanos, NaN e infinito. Não preencher silenciosamente campos ausentes com zero. A ordem das chaves JSON não pode afetar a previsão: a API deve ordenar os atributos conforme os metadados do artefato.

**Não receber:** `Class`, limiar escolhido pelo cliente, versão arbitrária de modelo, nome, CPF, número de cartão ou outros campos fora do contrato. `Class` é o rótulo usado no treinamento e na avaliação e deve ser excluído das entradas do modelo e da API.

A API receberá os valores na escala do arquivo de origem. Transformações adicionais aprendidas pelo projeto, como normalização, serão aplicadas pelo pipeline salvo. O cliente não deve aplicá-las antes do envio.

## 4. Saída

Uma previsão bem-sucedida retornará HTTP 200 e os seguintes campos:

| Campo | Tipo | Significado e regra |
|---|---|---|
| `score` | Número entre 0 e 1 | Score associado à classe positiva, extraído da posição correspondente à classe 1 no estimador. Não representa uma probabilidade calibrada garantida. |
| `predicted_class` | Inteiro 0 ou 1 | Será 1 quando `score >= threshold`; caso contrário, será 0. |
| `threshold` | Número entre 0 e 1 | Limiar selecionado na validação e salvo com o modelo. |
| `model_version` | String não vazia | Identificador imutável do conjunto pipeline, esquema de atributos, limiar e metadados. |
| `request_id` | String no formato UUID | Identificador gerado pelo servidor para correlacionar resposta e registros daquela requisição. |

O serviço não retornará sucesso com score inventado quando houver falha. Entradas fora do contrato retornarão HTTP 422; modelo indisponível retornará HTTP 503 enquanto o processo estiver atendendo; erros internos inesperados retornarão HTTP 500, com mensagem genérica e `request_id`.

## 5. Significado das classes

| Valor | No dataset | Na previsão |
|---|---|---|
| `Class = 0` | Transação rotulada como legítima | Score abaixo do limiar: não gerar alerta. |
| `Class = 1` | Transação rotulada como fraude; classe positiva | Score igual ou superior ao limiar: gerar alerta de suspeita. |

**Um alerta significa** que o modelo encontrou características suficientes para ultrapassar o limiar configurado. Na demonstração, isso pode encaminhar o exemplo para revisão simulada.

**Um alerta não significa** fraude comprovada, culpa de uma pessoa ou autorização para bloquear uma transação. Podem ocorrer falsos positivos: transações legítimas sinalizadas como fraude. A ausência de alerta também não comprova legitimidade; podem ocorrer falsos negativos: fraudes não detectadas.

## 6. Uso permitido e limitações

**Usos previstos:** experimentação reproduzível, comparação de classificadores e demonstração de integração com uma API usando dados públicos compatíveis com o contrato e seus termos de uso.

**Usos fora do escopo:** bloquear pagamentos reais, encerrar contas, acusar pessoas, determinar concessão de crédito ou tomar decisões financeiras automaticamente. O modelo não deve ser apresentado como um detector validado para operação bancária.

As limitações que devem acompanhar qualquer apresentação dos resultados são:

- `Time` mede segundos desde a primeira transação de um recorte de 48 horas; não há referência equivalente para transações novas, e padrões aprendidos a partir dele não devem ser presumidos válidos no futuro.
- O modelo depende da representação `V1`–`V28`. Não é possível presumir sua obtenção a partir de dados brutos de uma nova compra sem a transformação de origem apropriada.
- Resultados no dataset não garantem desempenho em outros períodos, instituições, populações ou distribuições de fraude.
- A divisão aleatória estratificada deste benchmark não comprova desempenho futuro. Essa afirmação exigiria avaliação temporal apropriada.
- A classe rara pode produzir estimativas instáveis. Reportar contagens de positivos, falsos positivos e falsos negativos junto às métricas.
- Após a remoção das duplicatas exatas, o dataset tem 283.726 transações e 473 fraudes (ver `docs/02_dados.md`). Com a divisão 60/20/20, validação e teste terão cerca de 95 fraudes cada. Assim, cada fraude equivale a aproximadamente 1 ponto percentual de recall, e poucos falsos positivos podem mover a precision em torno da meta de 0,80. Reportar intervalos de confiança e evitar conclusões fortes a partir de diferenças pequenas.
- O score não deve ser anunciado como probabilidade confiável sem avaliação de calibração.
- A equipe controla o pré-processamento que implementar, mas não pode garantir ausência de vazamento no processo original de anonimização do dataset.

## 7. Política de decisão

**Regra principal:** selecionar o par modelo–limiar que maximize o recall de fraude na validação, sujeito a **precision ≥ 0,80** no mesmo conjunto.

Precision é `TP / (TP + FP)` e recall é `TP / (TP + FN)`. TP são fraudes detectadas, FP são alertas em transações legítimas e FN são fraudes não detectadas. O limite de 80% é uma meta de referência definida antes dos experimentos; não é garantia de desempenho futuro nem requisito validado por uma instituição financeira.

Aplicar o seguinte procedimento:

1. Separar 60% dos dados para treino, 20% para validação e 20% para teste, com estratificação e semente fixa `42`. Tratar duplicatas antes da divisão ou mantê-las no mesmo conjunto. Registrar índices e contagens das classes.
2. Escolher os hiperparâmetros de cada família pela maior Average Precision (AP) média nos três folds internos do treino. Normalização e outros ajustes devem ocorrer apenas na parte de treino de cada fold.
3. Ajustar a melhor configuração de cada família no conjunto de treino completo e gerar scores na validação separada, preservando a proporção natural de classes.
4. Avaliar como limiares os valores distintos dos scores de validação e os extremos 0 e 1. Aplicar sempre `score >= threshold`. Descartar soluções sem alertas, pois sua precision é indefinida; não tratá-las como precision de 100%.
5. Para cada modelo, escolher o limiar elegível com maior recall. Em empate, preferir maior precision e, persistindo o empate, o maior limiar.
6. Comparar os dois candidatos elegíveis pelo recall de validação. Em empate, preferir maior AP na validação e depois regressão logística, pela simplicidade. Registrar todos os critérios e resultados.
7. Congelar pipeline, limiar e versão antes de consultar o teste. Usar o teste para relatar o resultado final, sem trocar o vencedor ou reajustar o limiar a partir dele.

Nesta versão, preservar o pipeline treinado que foi validado; não retreinar automaticamente com treino mais validação mantendo o limiar antigo.

**Se nenhum candidato atingir a meta:** registrar que nenhum modelo foi aprovado, publicar as curvas e métricas obtidas e manter a exigência de 80%. Não usar o teste para procurar uma solução nem reduzir a meta silenciosamente. A equipe poderá propor uma nova rodada com mudança documentada de orçamento ou política. Até haver artefato aprovado, a API pode ser demonstrada como serviço indisponível para inferência, retornando 503; não deve divulgar um candidato reprovado como modelo aprovado.

Se a precision no teste ficar abaixo de 80%, reportar a falha de generalização da meta, sem retocar o limiar. Esse resultado limita a conclusão do experimento, mesmo que a implementação esteja correta.

## 8. Orçamento de experimentos

| Componente | Orçamento inicial |
|---|---|
| Regressão logística | Até 12 configurações distintas de hiperparâmetros. |
| Random forest | Até 12 configurações distintas de hiperparâmetros. |
| Validação cruzada | 3 folds estratificados por configuração, exclusivamente dentro dos 60% de treino. |
| Total da busca | Até 24 configurações e 72 ajustes: 2 famílias × 12 configurações × 3 folds. |
| Ajustes dos candidatos finais | Até 2 ajustes adicionais no treino completo, um por família. |
| Baseline | Um baseline que sempre prevê a classe 0, sem busca de hiperparâmetros. |

Congelar as configurações antes da busca. Incluir ponderação de classes ligada e desligada dentro do limite de 12, sem ampliar o orçamento implicitamente. Usar os mesmos folds para as duas famílias e registrar sementes, parâmetros, duração, falhas e métricas por execução.

A varredura de limiares utiliza scores já calculados e não envolve novos treinamentos. Calibração, SMOTE, novos algoritmos ou novas rodadas não fazem parte deste orçamento inicial; sua inclusão exige revisão registrada do protocolo. O baseline é referência e não concorre como detector aprovado quando não emite alertas.

## 9. Condições da demonstração

**Ambiente:** a demonstração será **apenas local**, na máquina do desenvolvedor, com a API em contêiner Docker acessível somente por `localhost` (porta publicada em `127.0.0.1`). Não haverá exposição na internet nem em rede compartilhada.

**Fora do escopo desta versão:** HTTPS, autenticação, limites de requisição e de tamanho e CORS. Se a API vier a ser exposta, esses controles passam a ser obrigatórios: HTTPS, chave de acesso mantida em configuração externa, limites de requisição e tamanho, e testes com credencial válida, inválida e ausente. Qualquer mudança de exposição exige revisar este documento antes.

**Dados:** cada pessoa obtém o dataset pela fonte oficial, seguindo o README. O arquivo não será redistribuído no repositório.

**Roteiro da demonstração:**

| Item | O que mostrar | Evidência |
|---|---|---|
| D01 | Baseline com acurácia alta e recall de fraude igual a zero | Execução registrada do baseline |
| D02 | Comparação entre regressão logística e random forest | Tabela e curvas PR do relatório |
| D03 | Efeito de mudar o limiar sobre precision, recall e taxa de alertas | Varredura de limiares na validação |
| D04 | Requisição válida retornando 200 com score, classe, limiar, versão e `request_id` | Chamada a `POST /predict` |
| D05 | Requisição inválida retornando 422 sem executar o modelo | Chamada com campo ausente ou extra |
| D06 | Consistência entre inferência offline e API | Resultado do teste RQ03 |
| D07 | Versão servida e prontidão | `GET /health`, `GET /ready` e `model_version` |
| D08 | Rollback para o artefato anterior | Reiniciar o contêiner apontando para a versão anterior e conferir `/ready` e `model_version` |

Toda métrica apresentada deve apontar para uma execução registrada. Registrar também sistema operacional, CPU, memória, versão do Docker e do Python da máquina usada (ver RQ04).

## 10. Requisitos funcionais

Todos os critérios abaixo são verificações a implementar; nenhum é apresentado como já executado.

| ID | Requisito | Como verificar e critério de aceite |
|---|---|---|
| RF01 | Receber uma transação em `POST /predict`. | Enviar JSON válido com os 30 campos e modelo aprovado disponível; esperar HTTP 200 e uma única previsão. |
| RF02 | Validar o contrato antes da inferência. | Testar campo ausente, extra, `Class`, `null`, string, booleano, valor não finito e `Time`/`Amount` negativos; todos devem produzir 422 sem executar o modelo. Componentes V negativos devem ser aceitos. |
| RF03 | Carregar o pipeline aprovado na inicialização. | Registrar o carregamento e enviar várias requisições; confirmar que não há treinamento ou recarga do modelo em cada previsão. |
| RF04 | Calcular o score correspondente à classe 1. | Comparar com a coluna da classe 1 do estimador em exemplos fixos; verificar score finito no intervalo de 0 a 1. |
| RF05 | Aplicar o limiar salvo no artefato. | Com scores controlados abaixo, iguais e acima do limiar, esperar respectivamente classes 0, 1 e 1. Recusar limiar enviado pelo cliente. |
| RF06 | Retornar todos os campos definidos na seção 4. | Validar o schema da resposta, UUID válido e versão/limiar iguais aos metadados carregados. |
| RF07 | Disponibilizar saúde e prontidão. | `GET /health` retorna 200 quando o processo responde; `GET /ready` retorna 200 somente com artefato compatível carregado e 503 quando indisponível. |
| RF08 | Disponibilizar documentação em `GET /docs`. | Abrir a documentação e conferir endpoint, campos obrigatórios, saídas e respostas de erro contra o contrato real. |
| RF09 | Informar falhas sem produzir previsão fictícia. | Simular modelo indisponível e erro interno; esperar 503 ou 500, respectivamente, mensagem genérica e `request_id`, sem score/classificação de sucesso. |
| RF10 | Comparar e documentar os modelos fora da API. | Conferir baseline, regressão logística e random forest no relatório, com AP, precision, recall, F1/F2, curva PR, matriz de confusão, limiar e identificação da execução. Não aceitar apenas acurácia. |

## 11. Requisitos de qualidade

| ID | Requisito | Como verificar e critério de aceite |
|---|---|---|
| RQ01 | Reprodutibilidade. | Registrar hash dos dados, partições, semente, configurações, commit e versões. Reexecutar no mesmo ambiente fixado: índices e configurações devem coincidir; scores devem ter diferença absoluta ≤ `1e-8` e classes devem ser idênticas. Investigar divergências antes do aceite. |
| RQ02 | Não introduzir vazamento de dados. | Revisar código e testar isolamento dos índices e duplicatas entre partições; confirmar que `Class` não integra as features, que transformações são ajustadas somente no treino de cada fold e que validação/teste não são reamostrados. Registrar que o teste foi consultado após o congelamento. |
| RQ03 | Consistência entre treinamento e API. | Usar o mesmo pipeline salvo em uma amostra fixa com pelo menos 100 transações cobrindo as duas classes reais. Comparar inferência offline e API: diferença absoluta de score ≤ `1e-8`, classes idênticas e mesmo limiar/versão. Reordenar as chaves JSON e repetir. |
| RQ04 | Latência p95 de até 200 ms. | Após 100 requisições de aquecimento, executar 5 clientes simultâneos durante 60 segundos, uma transação por requisição, em ambiente local documentado. Medir do envio HTTP ao recebimento completo da resposta, incluindo validação e inferência. Exigir p95 ≤ 200 ms nas respostas válidas e zero erros para a carga válida. Registrar total de requisições, CPU, RAM, versões, workers, tamanho do artefato e configuração da máquina. |
| RQ05 | Rastreabilidade. | Conferir metadados com versão, hash do artefato/dataset, esquema, limiar, dependências e execução. Verificar correspondência entre `request_id` da resposta e log com status, duração e versão. |
| RQ06 | Falhas previsíveis. | Simular artefato ausente, corrompido e incompatível; o serviço não pode ficar pronto nem prever com fallback silencioso. Se não iniciar, registrar falha de inicialização; se atender HTTP, `/ready` e `/predict` devem retornar 503. |
| RQ07 | Minimização dos registros. | Inspecionar logs de sucesso e erro: não devem conter corpo completo da transação, credenciais ou traceback devolvido ao cliente. Manter metadados técnicos suficientes para diagnóstico. |
| RQ08 | Manutenção verificável. | Em ambiente limpo, instalar dependências fixadas e executar os testes de contrato, pipeline e integração pelo procedimento documentado. A integração contínua deve concluir sem falhas. |

O p95 é o percentil 95 dos tempos observados: aproximadamente 95% das requisições medidas devem terminar nesse tempo ou antes. A meta desta versão se aplica ao cenário local acima; não implica a mesma latência pela internet ou em qualquer hardware. Se a medição falhar, registrar o resultado e a ação corretiva; não declarar o requisito cumprido nem alterar a meta sem revisão do documento.

**Condição de encerramento desta especificação:** cada requisito possui identificação e critério de verificação. A conclusão da implementação dependerá das evidências produzidas pelos testes e experimentos; este documento, sozinho, não comprova aprovação do modelo ou da API.
