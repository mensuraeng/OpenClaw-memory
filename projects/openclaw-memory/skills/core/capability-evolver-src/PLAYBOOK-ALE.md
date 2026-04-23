# Playbook operacional - Capability Evolver no ambiente do Alê

## Tese correta de uso
O Capability Evolver não deve decidir sozinho o rumo das skills críticas.
Ele deve funcionar como uma camada de:
- leitura de padrões de erro
- organização de hipóteses de melhoria
- geração de evolução auditável
- aceleração do refinamento das skills internas

## Onde usar

### 1. MENSURA
Aplicar em skills e rotinas ligadas a:
- leitura de cronogramas
- análise de desvios
- detecção de risco de prazo
- relatórios executivos de obra
- consolidação de padrões de erro por obra

### 2. MIA
Aplicar em skills e rotinas ligadas a:
- relatórios premium para cliente
- consistência de linguagem técnica e executiva
- estrutura de entregáveis de pré-construção
- organização de memória por cliente, obra e fase

### 3. PCS
Aplicar em skills e rotinas ligadas a:
- padronização operacional
- inteligência de recorrência de erros
- melhoria de relatórios, automações e fluxos internos

## Onde NÃO usar
- envio autônomo de comunicação externa
- decisões críticas de negócio
- alterações automáticas em fluxos sensíveis com email, calendário ou SharePoint
- loop contínuo sem revisão humana
- publicação para rede externa ou worker pool

## Pré-condição crítica
Antes de rodar, o ideal é que a árvore git do workspace esteja limpa ou com mudanças isoladas da skill alvo.

Se houver muitas mudanças soltas no workspace, o review do Evolver pode misturar diffs não relacionados e gerar leitura ruim.

Regra prática:
- não rodar com o workspace inteiro bagunçado
- preferir branch dedicada ou momento de revisão com escopo claro
- isolar a skill alvo antes da rodada sempre que possível

## Fluxo operacional recomendado

### Etapa 1 - acumular material útil
Rodar o Evolver só depois que existir um volume mínimo de sinais, por exemplo:
- 5 a 10 execuções de uma mesma skill
- 3 ou mais falhas parecidas
- outputs medianos repetidos
- retrabalho manual recorrente para corrigir mesma deficiência

### Etapa 2 - executar em modo seguro
Usar:
- `bash scripts/run_capability_evolver_safe.sh`

Isso força:
- estratégia harden
- sem self modify
- sem worker
- sem bridge
- sem auto issue
- rollback em stash

### Etapa 3 - revisar a saída
Perguntas de revisão obrigatórias:
1. O sinal detectado é real ou ruído?
2. A melhoria proposta é específica ou genérica?
3. O blast radius está pequeno e reversível?
4. Isso melhora a skill real ou só melhora o próprio Evolver?
5. Existe risco de afetar integração crítica?

### Etapa 4 - aplicar só o que presta
A lógica correta é:
- o Evolver sugere
- você ou eu decidimos
- a skill real é atualizada de forma cirúrgica
- a validação acontece na skill-alvo, não só no Evolver

### Etapa 5 - consolidar aprendizado
Quando uma melhoria se provar útil:
- incorporar na skill de origem
- registrar padrão recorrente em memória/projeto se fizer sentido
- evitar repetir correção manual no próximo ciclo

## Casos de uso práticos

### Caso A - control-tower-cronograma
Sinais que justificam rodar:
- análise de cronograma inconsistente
- respostas genéricas sobre risco
- perda de precisão em leitura de caminho crítico
- retrabalho frequente para reorganizar saída executiva

Resultado esperado:
- identificar falhas recorrentes na estrutura analítica
- propor ajustes de heurística, formato ou validação
- transformar isso em melhoria reutilizável

### Caso B - relatorio-preditivo-obras
Sinais que justificam rodar:
- relatórios repetidamente longos demais
- falta de priorização executiva
- alertas fracos ou pouco acionáveis
- baixa consistência entre obras diferentes

Resultado esperado:
- melhorar priorização, síntese e consistência
- padronizar alertas relevantes
- reduzir retrabalho manual no fechamento dos relatórios

### Caso C - novas skills da PCS
Sinais que justificam rodar:
- muita variação entre outputs
- repetição de falha por tipo de cliente ou tipo de obra
- dificuldade de manter padrão operacional entre execuções

Resultado esperado:
- consolidar critérios mais robustos
- reduzir improviso
- acelerar maturidade das skills internas

## Política de segurança
- Nunca habilitar `WORKER_ENABLED=1`
- Nunca preencher `A2A_HUB_URL` sem decisão explícita
- Nunca preencher `A2A_NODE_SECRET` para operação de rotina sem necessidade clara
- Nunca deixar `EVOLVE_ALLOW_SELF_MODIFY=true`
- Nunca tratar a saída como alteração já aprovada

## Frequência recomendada
- não contínua
- rodar sob demanda
- idealmente ao fim de um ciclo com erro recorrente ou após lote relevante de execuções

Sugestão prática:
- revisão semanal das skills críticas
- revisão extraordinária quando uma skill gerar erro repetido ou output abaixo do padrão

## Regra final
Se a melhoria não for pequena, auditável e claramente útil, não entra.
No teu ambiente, disciplina vale mais que autonomia performática.
