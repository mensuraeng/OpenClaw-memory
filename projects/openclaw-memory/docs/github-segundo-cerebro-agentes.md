# GitHub como Segundo Cérebro dos Agentes

_Arquitetura operacional para memória distribuída + consolidação compartilhada — 2026-04-14_

## Objetivo

Transformar o conjunto de agentes em um sistema com:
- memória curta local por agente
- consolidação noturna automática
- memória institucional compartilhada no GitHub

A meta é simples:
**cada agente trabalha com contexto local durante o dia e contribui para uma memória coletiva consolidada à noite.**

## Princípio operacional

Durante o dia, cada agente precisa de velocidade.
À noite, o sistema precisa de estrutura.

Por isso, a arquitetura separa três camadas:

### 1. Memória curta por agente
Uso operacional rápido, sujeita a ruído, incompletude e redundância.

### 2. Consolidação por agente
Triagem do que merece subir, do que deve ser descartado e do que precisa ser conectado a outros agentes ou domínios.

### 3. Memória institucional compartilhada
Conhecimento estável, versionado no GitHub, acessível a todo o sistema.

## Analogia

- inbox do agente = memória de curto prazo
- consolidação noturna = sono
- GitHub = memória de longo prazo do time

## Arquitetura recomendada

```text
memory/
  inbox/
    2026-04-14/
      main/
        notes.md
        events.jsonl
      mensura/
        notes.md
        events.jsonl
      mia/
        notes.md
        events.jsonl
      pcs/
        notes.md
        events.jsonl
      finance/
        notes.md
        events.jsonl

  consolidation/
    2026-04-14/
      main-summary.md
      mensura-summary.md
      mia-summary.md
      pcs-summary.md
      finance-summary.md
      cross-agent-summary.md

  context/
    decisions.md
    lessons.md
    pending.md
    people.md

  projects/
  integrations/
  sessions/
  content/
```

## Regra por camada

### Camada 1 — Inbox por agente
Cada agente registra material bruto do dia.

Entradas típicas:
- decisões ainda não consolidadas
- descobertas operacionais
- pendências abertas
- fatos relevantes de execução
- saídas úteis de ferramentas
- contexto novo de projeto
- sinais de risco

Regras:
- aceitar imperfeição
- priorizar velocidade
- não exigir organização final no momento da captura
- manter origem clara quando possível

### Camada 2 — Consolidação por agente
No fechamento, cada agente ou um consolidador central analisa o inbox do dia.

Perguntas obrigatórias:
- isso é decisão permanente?
- isso é lição reutilizável?
- isso é pendência real?
- isso pertence a um projeto específico?
- isso interessa a mais de um agente?
- isso é ruído e deve morrer?

Saídas esperadas:
- resumo do dia por agente
- itens promovidos
- itens descartados
- conflitos ou duplicações identificadas
- itens que precisam subir para a camada transversal

### Camada 3 — Memória institucional compartilhada
Recebe apenas o que tem valor durável.

Inclui:
- decisões estáveis
- lições reutilizáveis
- pendências reais
- contexto de projeto de continuidade
- mapa de pessoas e relações
- contexto de integrações

Não inclui:
- conversa bruta sem valor futuro
- log irrelevante
- tentativa descartada sem aprendizado
- duplicação de informação já consolidada

## Regras de promoção

### Promover para `memory/context/decisions.md`
Quando houver:
- decisão explícita do Alê
- padrão operacional validado
- regra permanente de execução

### Promover para `memory/context/lessons.md`
Quando houver:
- erro com valor de prevenção futura
- padrão técnico reaproveitável
- insight operacional recorrente

### Promover para `memory/context/pending.md`
Quando houver:
- pendência aberta real
- item aguardando input
- ação futura combinada

### Promover para `memory/projects/*.md`
Quando houver:
- contexto durável de um projeto específico
- mudança de estado relevante
- decisão contextual que continua valendo

### Promover para camada transversal
Quando houver:
- impacto em mais de um agente
- regra comum
- integração compartilhada
- contexto institucional

## Governança entre agentes

### Cada agente pensa localmente
O inbox é local.
O trabalho do dia nasce no contexto do agente que executou.

### A memória longa é coletiva
O que vira padrão, decisão, lição ou contexto institucional sobe para a base compartilhada.

### Duplicação deve ser reduzida na consolidação
Se `mensura` e `mia` registrarem o mesmo fato sob ângulos diferentes, a consolidação deve:
- manter um registro principal
- criar vínculo cruzado se necessário
- evitar duplicação textual desnecessária

### Conflito entre agentes deve ser explicitado
Se houver conflito de interpretação, a consolidação deve registrar:
- qual é o conflito
- o que está confirmado
- o que depende de decisão do Alê

## Fluxo diário sugerido

### Durante o dia
1. cada agente executa normalmente
2. fatos úteis vão para `memory/inbox/YYYY-MM-DD/<agent>/`
3. sem ritual manual pesado

### No fechamento noturno
1. o consolidator lê os inboxes dos agentes
2. separa por tipo
3. deduplica
4. conecta itens relacionados
5. promove para memória compartilhada
6. gera resumo consolidado da rodada

### Na manhã seguinte
1. agentes leem a memória institucional atualizada
2. partem do conhecimento coletivo mais recente
3. sem briefing manual

## Estratégia de implantação

### Fase 1 — Estrutura mínima
Criar:
- `memory/inbox/YYYY-MM-DD/<agent>/`
- `memory/consolidation/YYYY-MM-DD/`
- convenção de captura por agente

### Fase 2 — Consolidação noturna
Criar um job que:
- percorra todos os agentes
- leia o inbox do dia
- extraia decisões, lições, pendências e fatos duráveis
- escreva na memória institucional
- produza um resumo da rodada

### Fase 3 — Cross-agent memory
Adicionar uma camada para identificar automaticamente:
- itens repetidos
- temas relacionados
- impacto multiagente
- dependências cruzadas

### Fase 4 — Melhoria contínua
Ajustar:
- o que entra no inbox
- o que sobe
- o que morre
- o que gera ruído demais

## Critério de sucesso

O sistema estará maduro quando:
- cada agente puder trabalhar sem documentar manualmente tudo
- o contexto importante sobreviver ao fim do dia
- o conhecimento útil aparecer consolidado para todos no dia seguinte
- o GitHub virar de fato a memória institucional do time
- briefing manual deixar de ser necessidade recorrente

## Próximos passos imediatos

1. criar a estrutura física de inbox por agente
2. definir formato mínimo de captura (`notes.md` + `events.jsonl`)
3. criar o consolidator noturno
4. ligar esse consolidator a um cron noturno
5. testar por 3 dias com `main`, `mensura`, `mia`, `pcs` e `finance`
6. ajustar antes de expandir para os demais agentes
