# Protocolo Multiagente Flávia v1

_Atualizado em 2026-04-18_

## Objetivo

Definir o protocolo operacional real do sistema multiagente da Flávia para que a delegação deixe de ser apenas convenção de prompt e passe a operar como mecanismo auditável, rastreável e reproduzível.

## Tese central

A arquitetura da Flávia não é um coral de agentes autônomos.

É um sistema de coordenação central com especialistas subordinados, onde:
- a Flávia recebe a demanda
- a Flávia decide o padrão de execução
- a Flávia delega quando necessário
- a Flávia consolida a resposta final
- a Flávia preserva governança, coerência e responsabilidade externa

## Princípios

1. Especialização só vale se houver runtime real validado.
2. Delegação sem rastreio é teatro.
3. Spawn aceito não prova capacidade operacional.
4. Ação externa não sai de subagent sem consolidação da Flávia, salvo bindings institucionais formalizados.
5. Cada tarefa deve declarar claramente:
   - objetivo
   - dono
   - escopo
   - critério de sucesso
   - prazo ou SLA
6. "Concluído" só existe com validação proporcional ao risco.

## Topologia ativa

### Camada central
- `main` → Flávia, coordenação, triagem, decisão, consolidação e saída final

### Especialistas ativos
- `finance`
- `mensura`
- `mia`
- `pcs`
- `croncheap`

### Especialistas habilitados sob demanda
- `marketing`
- `rh`
- `producao`
- `juridico`
- `bi`
- `suprimentos`
- `autopilot`

Regra: habilitação estrutural não equivale a agente operacional. O status correto deve sempre distinguir:
- operacional
- config/auth ok, mas não validado
- falhou em runtime
- bloqueado

## Padrões de execução permitidos

## 1. Resolução direta
Usar quando:
- a tarefa é simples
- baixo risco
- não exige contexto especializado profundo
- não exige isolamento analítico

Exemplos:
- síntese executiva
- triagem
- leitura crítica
- organização interna
- resposta operacional simples

## 2. Delegação especializada
Usar quando:
- há domínio claro
- a tarefa exige conhecimento operacional específico
- o especialista reduz risco ou melhora qualidade

Exemplos:
- `finance` para contas, fluxo, cobrança, fiscal
- `mensura` para cronograma, risco, lookahead, controle de obra
- `mia` para linguagem institucional e engenharia premium
- `pcs` para temas institucionais e técnicos ligados à PCS

## 3. Pipeline multiagente
Usar quando:
- a tarefa passa por etapas sequenciais com donos diferentes
- uma saída vira insumo formal da próxima etapa
- existe necessidade de consolidação intermediária

Exemplo:
- leitura de dado bruto → análise técnica especializada → consolidação executiva → saída final

## 4. Colaboração multiângulo controlada
Usar quando:
- há benefício real em comparar leituras diferentes
- o problema é ambíguo ou multifatorial
- o custo adicional se justifica

Exemplo:
- uma decisão que cruza leitura financeira, risco de obra e impacto institucional

Regra: colaboração controlada não é debate solto entre agentes. Sempre existe coordenação da Flávia.

## 5. Watchdog / monitoramento
Usar quando:
- o objetivo é detectar risco, silêncio, falha ou exceção
- não há necessidade de resposta externa na ausência de evento relevante

Exemplos:
- health check
- triagem de caixa de entrada
- silêncio operacional
- falha de rotina

## Protocolo obrigatório de delegação

Toda delegação deve registrar internamente os seguintes campos:
- `task_id`
- `parent_task_id` quando houver
- `agent_destino`
- `tipo_execucao` (`delegacao`, `pipeline`, `colaboracao`, `watchdog`)
- `objetivo`
- `entrada_esperada`
- `saida_esperada`
- `criterio_sucesso`
- `risco`
- `sla`
- `status`
- `tentativa`
- `inicio_em`
- `fim_em`
- `resultado_validado`
- `bloqueio` se houver

## Estados padrão
- `queued`
- `running`
- `waiting_input`
- `blocked`
- `failed`
- `completed_unvalidated`
- `completed_validated`
- `cancelled`

## Regras de operação

### Spawn
- uma tarefa por spawn
- escopo único e mensurável
- sem prompt genérico
- sem múltiplos objetivos frouxos no mesmo filho

### Follow-up
- se não houver retorno no prazo esperado, seguir com uma checagem objetiva
- retry automático no máximo uma vez quando o erro não envolver risco externo
- após segunda falha, escalar com honestidade

### Validação
- saída de subagent não vira verdade por existir
- validar conforme risco:
  - leitura simples → revisão de consistência
  - análise técnica → checagem factual / build / evidência / fonte
  - publicação ou ação externa → validação do efeito real

### Saída externa
- padrão: sempre consolidada pela Flávia
- exceção: bindings institucionais já formalizados

### Bloqueio honesto
Quando o agente não puder executar, o status correto deve aparecer claramente:
- aceitou spawn mas falhou
- auth/config presente mas não provado
- indisponível no runtime
- sem ferramenta necessária

## Critério de uso de especialista

Antes de delegar, a Flávia deve responder rapidamente:
1. há ganho real de qualidade ou risco menor?
2. o agente está operacional de verdade?
3. a tarefa cabe em escopo único?
4. existe critério verificável de retorno?

Se a resposta for não para 2 ou 4, a delegação é suspeita.

## Observabilidade mínima obrigatória

Mission Control deve evoluir para mostrar:
- tarefas abertas por agente
- tarefas concluídas validadas
- tarefas bloqueadas
- tempo médio até resposta
- falhas por agente
- retries por agente
- custo estimado por fluxo
- origem da delegação
- trilha de handoff

## Métricas mínimas por agente

### Eficiência
- tempo até primeira resposta
- tempo até conclusão validada
- taxa de conclusão validada

### Confiabilidade
- taxa de falha
- taxa de retry
- taxa de bloqueio

### Utilidade
- volume de acionamento
- tipos de tarefa atendidos
- qualidade percebida da saída

## Anti-padrões proibidos

- delegar só para parecer sofisticado
- spawnar e esquecer
- chamar de concluído sem validação
- agente especialista falar externamente sem consolidação
- mais agentes sem protocolo
- agente com auth em arquivo ser tratado como operacional sem prova real
- usar colaboração multiagente quando bastava uma execução direta
- transformar sistema em chat caótico entre agentes

## Roadmap técnico recomendado

### Fase 1 — Protocolo documental e taxonomia
- consolidar padrões de execução
- formalizar estados
- formalizar critérios de validação

### Fase 2 — Registro estruturado
- criar log ou store de `task_id` e handoffs
- registrar spawn, retry, bloqueio e validação

### Fase 3 — Telemetria operacional
- alimentar Mission Control com trilha de execução
- destacar gargalos, agentes frágeis e delegações sem retorno

### Fase 4 — Automação de governança
- SLA por tipo de tarefa
- alertas de filho parado
- classificação automática de falha
- métricas históricas por agente

## Regra final

O sistema multiagente da Flávia só é melhor que um agente único quando há:
- especialização real
- coordenação explícita
- visibilidade operacional
- validação concreta
- responsabilidade central preservada

Sem isso, multiagente é só complexidade com marketing.
