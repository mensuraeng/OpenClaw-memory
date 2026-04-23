# HEARTBEAT — Mensura, MIA Engenharia & PCS Engenharia
## Versão 2.1 | Ritmo Operacional Inteligente

## FILOSOFIA
> Não monitorar tudo. Monitorar o que mata e o que multiplica.
> Silêncio inteligente > relatório inútil.
> 2nd-brain é a memória operacional oficial.

## CICLOS DIÁRIOS (Seg-Sex)

### PULSO MATINAL — 07:45
Objetivo: preparar Alexandre para atacar o dia com contexto total.

Checar:
- emails críticos recebidos desde o último check
- agenda completa do dia + preparação necessária
- agenda de amanhã
- alertas de projeto com marco hoje ou amanhã
- clima/condições que afetem obras em andamento
- contexto ativo em `/root/2nd-brain/02-context/`

Formato esperado:

BOM DIA, ALEXANDRE.

DECISÕES PENDENTES (X): → [Prioridade] Descrição — Deadline

AGENDA HOJE: → HH:MM — Evento — Local — O que precisa

RADAR DE PROJETOS: → [Projeto] Marco X vence em Y dias — Status: OK/ATENÇÃO/CRÍTICO

CLIMA OBRAS: → [Cidade/Região] — Previsão — Impacto: SIM/NÃO

### CHECK TÁTICO — 12:00
Objetivo: correção de rota do meio-dia.

Checar:
- emails novos que exigem ação hoje
- reuniões da tarde e eventuais mudanças
- mudança de status de projeto desde 07:45

Regra de saída:
- só reportar se houver mudança ou ação necessária
- sem mudança → `✓ MEIO-DIA LIMPO`

### FECHAMENTO TÁTICO — 17:00
Objetivo: fechar o dia operacional e preparar o amanhã.

Checar:
- emails sem resposta hoje
- compromissos de amanhã com preparação necessária
- marcos concluídos ou atrasados
- delegações sem retorno há mais de 48h

Formato esperado:

FECHAMENTO DO DIA.

PENDÊNCIAS ABERTAS (X): → [Item] — Sugestão de ação — Urgência

AMANHÃ EXIGE PREPARAÇÃO: → [Evento] — O que providenciar

DELEGAÇÕES SEM RETORNO: → [Pessoa] — [Assunto] — Último contato: DD/MM

### REVISÃO NOTURNA — 20:30
Opcional, só se solicitado.

Checar:
- pipeline comercial sem retorno há mais de 3 dias
- fluxo de caixa dos próximos 7 dias
- oportunidades detectadas
- 1 insight ou provocação estratégica

## CICLO SEMANAL

### SEGUNDA — 07:30

BRIEFING SEMANAL

SEMANA PASSADA: → Marcos atingidos / perdidos → Propostas enviadas / respondidas → Decisões tomadas / adiadas

ESTA SEMANA: → 3 prioridades críticas → Deadlines contratuais → Reuniões-chave

RADAR ESTRATÉGICO: → Tendências do setor → Oportunidades identificadas → Riscos emergentes

### SEXTA — 17:00

RETROSPECTIVA SEMANAL

SCORE DA SEMANA: X/10 → O que avançou → O que travou e por quê → Decisão mais importante da semana → Decisão que está sendo evitada

## GATILHOS DE ALERTA IMEDIATO

- email de cliente com urgente, prazo, problema ou rescisão → alerta imediato
- reunião em menos de 90 min sem preparação feita → lembrete com contexto
- pagamento/recebimento acima de R$10k vencendo em 48h → alerta financeiro
- projeto sem movimentação há mais de 2 dias úteis → alerta amarelo
- projeto sem movimentação há mais de 4 dias úteis → alerta vermelho
- assunto jurídico/contratual novo → alerta imediato

## HORÁRIO SILENCIOSO

- 23:00 — 08:00: zero notificações
- sábado e domingo: só urgência real
- exceções:
  - falha operacional relevante
  - risco de perda de acesso
  - email urgente de cliente Tier 1
  - assunto jurídico/contratual crítico

## QUANDO CALAR

- nenhuma mudança desde o último ciclo → não reportar
- tarefas de organização interna → executar sem reportar
- informação sem necessidade de decisão → acumular para o próximo ciclo
- nunca enviar status vazio como "sem novidades", "tudo certo" ou repetição de estado

## CHECKS ADICIONAIS RECOMENDADOS

### MANUTENÇÃO DE MEMÓRIA — 22:00

Objetivo: manter contexto útil, limpo e recuperável.

Executar:
- revisar `/root/2nd-brain/02-context/pending.md`
- limpar itens resolvidos
- consolidar nota diária em `/root/2nd-brain/06-agents/flavia/memory/`
- promover decisões para `/root/2nd-brain/02-context/decisions.md`
- promover lições para `/root/2nd-brain/02-context/lessons.md`
- atualizar a memória específica do agente se mudar estado, risco, prioridade ou localização de contexto

Regra de saída:
- silêncio por padrão
- alertar só se houver pendência crítica esquecida, inconsistência relevante ou acúmulo que comprometa operação

### HEALTH CHECK OPERACIONAL — 06:00

Objetivo: detectar quebra silenciosa antes do início do dia.

Executar:
- `openclaw doctor --non-interactive`
- testar `memory_search()`
- checar gateway e canais ativos
- detectar falhas de auth, plugin, config ou restart pendente

Regra de saída:
- silêncio se tudo estiver funcional
- alerta imediato se houver falha real de operação

## REGRA DE MODELO

- usar sempre **GPT 4o Mini** nos crons desta rotina

## EVOLUÇÃO

Este documento é vivo. A cada 30 dias:
- remover o que gera ruído
- adicionar o que estiver faltando
- recalibrar gatilhos inúteis
- simplificar ciclos ignorados
