# Piloto - Capability Evolver aplicado à skill relatorio-preditivo-obras

## Situação atual
A skill `relatorio-preditivo-obras` não foi localizada materialmente no workspace com esse nome até agora.

Então este piloto foi montado de forma operacional para dois cenários:
- a skill já existe com outro nome e será conectada depois
- a skill ainda será formalizada no workspace

## Objetivo do piloto
Validar se o Capability Evolver consegue melhorar, de forma auditável e útil, a qualidade da rotina de relatório preditivo de obras sem gerar ruído, regressão ou complexidade desnecessária.

## Hipótese do piloto
Se alimentarmos o Evolver com um volume mínimo de execuções reais e critérios claros de revisão, ele deve conseguir:
- detectar padrões de saída fraca
- sugerir ajustes pequenos e reutilizáveis
- reduzir retrabalho manual
- elevar consistência executiva do relatório

## O que é sucesso neste piloto
O piloto é considerado bem-sucedido se, em até 2 ciclos de revisão:
1. reduzir retrabalho manual no fechamento do relatório
2. melhorar priorização executiva dos alertas
3. aumentar consistência entre relatórios de obras diferentes
4. gerar pelo menos 1 melhoria reaproveitável na skill real

## O que é fracasso
O piloto fracassa se acontecer qualquer um destes casos:
- a saída do Evolver for genérica demais
- o review misturar ruído do workspace com sinal útil demais vezes
- a melhoria sugerida mexer em escopo excessivo
- a proposta melhorar o Evolver, mas não melhorar a skill real
- o custo cognitivo da revisão for maior que o ganho operacional

## Skill alvo - definição operacional
A skill alvo, qualquer que seja o nome final, precisa executar algo próximo disso:
- receber dados de obra, avanço, pendências, desvios ou cronograma
- transformar isso em relatório executivo preditivo
- destacar risco, tendência, prioridade e ação recomendada

## Saída esperada da skill alvo
O relatório ideal deve conter:
1. leitura executiva curta
2. principais desvios ou riscos
3. impactos prováveis de prazo/custo/governança
4. prioridades objetivas
5. ações recomendadas
6. tom técnico, direto e defensável

## Sinais que justificam rodar o Evolver
Rodar somente quando houver pelo menos 1 destes conjuntos:

### Conjunto A - repetição de retrabalho
- 3 ou mais relatórios exigiram reescrita manual parecida
- correções repetidas em ordem, síntese ou priorização

### Conjunto B - baixa qualidade recorrente
- alertas genéricos
- excesso de texto e pouca decisão
- falha em distinguir ruído de risco real
- inconsistência entre obras semelhantes

### Conjunto C - falha de padrão executivo
- conclusão sem acionabilidade
- linguagem pouco defensável em ambiente executivo
- priorização ruim das urgências

## Insumos mínimos para o piloto
Antes de rodar o Evolver, separar:

### 1. Lote mínimo de amostras
- 5 a 10 relatórios gerados
- idealmente de mais de uma obra
- incluir casos bons e ruins

### 2. Registro de correções manuais
Para cada relatório, registrar rapidamente:
- o que precisou ser corrigido
- por que precisou ser corrigido
- qual padrão se repetiu

### 3. Critério de avaliação
Avaliar cada relatório em 1 a 5 nos critérios:
- clareza executiva
- priorização
- capacidade preditiva
- acionabilidade
- consistência estrutural

## Procedimento do piloto

### Etapa 1 - baseline
Criar uma linha de base com 5 relatórios reais.

Para cada um, registrar:
- nota dos 5 critérios
- quantidade de retrabalho manual
- tipo de erro dominante

### Etapa 2 - consolidação de sinais
Consolidar os padrões mais recorrentes, por exemplo:
- abre com contexto demais
- alerta fraco
- não diferencia causa e efeito
- recomendação vaga
- linguagem extensa para pouca decisão

### Etapa 3 - rodada segura do Evolver
Executar:
- `bash scripts/run_capability_evolver_safe.sh`

Observação:
- só rodar com escopo claro
- evitar workspace excessivamente sujo
- revisar apenas sinais ligados à skill de relatório

### Etapa 4 - revisão das propostas
Perguntas obrigatórias:
1. a proposta ataca um erro recorrente real?
2. a melhoria é pequena e reversível?
3. a proposta melhora a skill alvo ou só reorganiza metaprocesso?
4. o ganho esperado é mensurável?
5. há risco de contaminar outras rotinas?

### Etapa 5 - aplicação controlada
Se uma melhoria for aprovada:
- aplicar manualmente na skill alvo
- validar com novo lote pequeno de relatórios
- comparar antes vs depois

## Métricas do piloto

### Métricas principais
- tempo de retrabalho manual por relatório
- nota média de clareza executiva
- nota média de acionabilidade
- quantidade de correções repetidas

### Meta mínima de ganho
- reduzir retrabalho em pelo menos 25%
- elevar em pelo menos 1 ponto médio a clareza/priorização em escala 1-5

## Template de avaliação por relatório

### Identificação
- obra:
- data:
- origem dos dados:
- versão da skill:

### Nota 1 a 5
- clareza executiva:
- priorização:
- capacidade preditiva:
- acionabilidade:
- consistência:

### Falhas observadas
- 
- 
- 

### Correções manuais feitas
- 
- 
- 

### Ganho esperado se corrigir isso na raiz
- 

## Regras de aprovação de melhoria
A melhoria só entra se atender todos:
- problema recorrente comprovado
- escopo pequeno
- reversível
- benefício operacional claro
- validação possível em lote curto

## Regras de rejeição
Rejeitar se:
- for abstrata demais
- vier com linguagem bonita e ação fraca
- mexer demais no processo para ganho marginal
- depender de autonomia externa ou loop contínuo
- não estiver claramente ligada à qualidade do relatório

## Resultado esperado do piloto
Ao fim do piloto, precisamos sair com uma destas conclusões:

### cenário 1 - aprovado
O Evolver ajudou de forma prática e vale manter como camada auxiliar de refinamento.

### cenário 2 - uso restrito
O Evolver ajuda pouco e deve ficar só para casos específicos de erro recorrente.

### cenário 3 - reprovado
O custo de revisão supera o ganho e a melhoria deve continuar feita por curadoria manual direta.

## Próximo passo após este documento
1. localizar ou formalizar a skill real `relatorio-preditivo-obras`
2. separar 5 relatórios reais com revisão manual
3. preencher o baseline
4. rodar 1 ciclo seguro
5. decidir se escala ou corta
