# Plano de melhoria da memória e do contexto

_Atualizado em 2026-04-21 13:45 BRT_

## Objetivo

Fazer a memória cumprir o papel para o qual foi criada: permitir retomada confiável, continuidade operacional real e redução drástica de perda de contexto entre sessões, compactações, heartbeats e execuções longas.

O problema atual não é ausência de memória. O problema é uma combinação de:
- memória certa em lugares demais
- estados operacionais não suficientemente explícitos
- promoção tardia de fatos validados
- diferença entre contexto “preparado” e contexto “executável”
- falta de um protocolo de retomada obrigatório antes de responder ou agir

## Diagnóstico do problema

### 1. Memória existe, mas a recuperação operacional ainda é inconsistente
Há informação correta em `memory/`, mas ela nem sempre está sendo reconsultada no momento decisivo, especialmente para:
- capacidades já validadas
- trilhas de integração já resolvidas
- regras permanentes do Alê
- estado real de execução versus preparação

### 2. Fatos validados nem sempre viram memória canônica no mesmo instante
Isso gera deriva entre:
- o que foi testado
- o que foi respondido
- o que ficou persistido

### 3. Falta uma camada de “estado operacional atual” por frente
Hoje há memória histórica, mas nem sempre há um resumo curto e canônico do tipo:
- padrão atual
- fallback
- nível de productização
- bloqueios reais atuais
- último teste bem-sucedido
- próximo passo válido

### 4. O protocolo de retomada ainda não está duro o suficiente
Em algumas frentes, a retomada deveria obrigatoriamente responder cinco perguntas antes da ação:
1. qual é o objetivo da frente
2. o que já foi executado de verdade
3. o que está apenas preparado
4. qual é o bloqueio real atual
5. qual é o próximo passo operacional certo

## Meta de qualidade

A memória deve permitir que, ao retomar qualquer frente crítica, a chance de resposta errada por perda de contexto fique próxima de zero.

## Princípios de melhoria

### P1. Verdade operacional acima de narrativa
Nunca registrar como “feito” aquilo que está apenas:
- planejado
- preparado
- redigido
- testado parcialmente

### P2. Fato validado sobe imediatamente
Toda capacidade validada deve subir para memória durável no mesmo ciclo, com este formato mínimo:
- **padrão**
- **fallback**
- **nível de productização**
- **limitações**
- **última validação real**

### P3. Retomada deve começar pelo estado atual, não pelo histórico bruto
Memória histórica continua importante, mas a retomada operacional precisa bater primeiro em um resumo de estado corrente.

### P4. Cada frente crítica precisa de uma fonte canônica única
Cada frente operacional precisa ter um “arquivo mestre” que responda rapidamente:
- objetivo
- estado atual
- ativos validados
- bloqueios
- decisões do Alê
- próximos passos

## Estrutura proposta

## 1. Criar resumos operacionais canônicos por frente
Dentro de `memory/projects/`, cada frente relevante deve ganhar uma seção ou arquivo de **estado operacional atual**.

### Frentes prioritárias
- LinkedIn pessoal
- PCS contabilidade/Confirp
- áudio inbound
- Antigravity MCP
- scheduler/automações críticas
- integrações externas por marca ou função

### Estrutura padrão sugerida por frente
```md
## Estado operacional atual
- objetivo
- status: planejado | preparado | executado | bloqueado
- padrão atual
- fallback
- nível de productização
- último teste validado
- bloqueio real atual
- próximo passo correto
```

## 2. Instituir protocolo de flush em duas camadas

### Camada A. Memória diária
Continuar usando `memory/2026-04-21.md` para fatos do dia.

### Camada B. Promoção canônica obrigatória
Quando a política de escrita permitir, promover os fatos importantes também para arquivos temáticos permanentes apropriados, especialmente:
- `memory/context/decisions.md`
- `memory/context/lessons.md`
- `memory/context/pending.md`
- `memory/projects/...`
- `memory/integrations/...`

Se a política do runtime restringir escrita ao diário, registrar no diário com tag clara de **promoção pendente**.

## 3. Criar checklist obrigatório de retomada
Antes de responder sobre uma frente ativa, rodar mentalmente ou por procedimento explícito:

### Checklist de retomada
1. consultar memória
2. localizar fonte canônica da frente
3. identificar estado atual real
4. distinguir executado vs preparado
5. checar último bloqueio validado
6. só então responder ou agir

## 4. Padronizar registro de ferramentas validadas
Toda ferramenta validada deve seguir um formato estável.

### Template
```md
### Ferramenta: <nome>
- padrão: ...
- fallback: ...
- nível de productização: ...
- limitações: ...
- última validação: ...
- evidência: ...
```

## 5. Criar uma camada de “memória de bloqueios reais”
Boa parte da frustração veio de confundir:
- falta de execução
- falta de acesso
- preparação incompleta
- bloqueio técnico real

Por isso, cada frente deve registrar explicitamente:
- o que impede avanço real agora
- o que já foi testado para confirmar esse bloqueio
- qual único input destrava

## 6. Melhorar memória para continuidade de agent loop
Para trabalhos em modo autônomo, registrar sempre:
- objetivo do loop
- condição de conclusão
- condição de bloqueio
- último passo executado
- próximo passo obrigatório
- motivo de interrupção se houver

## 7. Reduzir duplicação e ruído
Hoje há risco de repetição e crescimento desorganizado do diário.

Melhoria proposta:
- evitar regravar blocos antigos completos
- sempre append só do delta novo
- quando houver promoção canônica, deixar o diário mais factual e menos redundante
- usar headings consistentes por horário e frente

## Plano prático de execução

### Fase 1. Correção imediata
1. consolidar LinkedIn pessoal em estado operacional canônico
2. consolidar PCS/Confirp em estado operacional canônico
3. consolidar áudio inbound em estado operacional canônico
4. consolidar regra de autonomia em memória operacional

### Fase 2. Protocolo de retomada
1. formalizar checklist de retomada
2. aplicar esse checklist antes de responder sobre frentes críticas
3. usar sempre a distinção planejado/preparado/executado/bloqueado

### Fase 3. Endurecimento estrutural
1. criar arquivos-resumo por frente crítica
2. registrar ferramentas com padrão/fallback/productização
3. criar trilha de bloqueios reais
4. revisar duplicações no diário

## Resultado esperado

Depois desta melhoria, a memória deve passar a sustentar:
- retomada confiável
- menos repetição de erros já resolvidos
- menos perguntas desnecessárias ao Alê
- menos confusão entre preparação e execução
- maior autonomia real
- menor perda de contexto após compactação

## Critério de sucesso

Consideraremos a melhoria funcionando quando:
- eu conseguir retomar uma frente crítica sem reinventar diagnóstico já validado
- eu reportar corretamente o estado real de execução
- fatos validados subirem para memória no mesmo ciclo
- o Alê não precisar me cobrar repetidamente por perda de contexto operacional
