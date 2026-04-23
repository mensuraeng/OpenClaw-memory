# GitHub como Segundo Cérebro Operacional

_Proposta operacional inicial — 2026-04-14_

## Objetivo

Transformar o GitHub na memória institucional de longo prazo da operação, usando o OpenClaw como camada automática de captura, triagem e consolidação.

A lógica é simples:

- durante o dia, o trabalho gera contexto bruto
- esse contexto entra em um inbox operacional
- à noite, o OpenClaw consolida esse material
- o que importa vira memória durável versionada

## Princípio

Não construir uma infraestrutura nova se o GitHub já entrega a base necessária.

O GitHub já resolve:
- versionamento
- rastreabilidade
- colaboração
- histórico auditável
- acesso compartilhado

O OpenClaw entra como sistema nervoso da operação:
- captura contexto em execução
- organiza memória de curto prazo
- consolida à noite
- reduz redundância
- preserva contexto útil

## Analogia operacional

- Inbox = memória de curto prazo
- Consolidação noturna do OpenClaw = sono
- GitHub = memória de longo prazo

Sem consolidação, o sistema acumula ruído.
Com consolidação, o time acorda no dia seguinte com contexto coletivo utilizável.

## Arquitetura recomendada

### 1. Camada de captura diária
Tudo que nasce durante o dia entra primeiro no inbox.

Entradas típicas:
- notas brutas de execução
- saídas importantes de agentes
- decisões ainda não consolidadas
- pendências abertas
- logs úteis de operação
- resumos de interações relevantes
- referências novas ainda não classificadas

Estrutura sugerida:

```text
memory/
  inbox/
    2026-04-14/
      main.md
      mensura.md
      mia.md
      pcs.md
      finance.md
      raw-events.jsonl
```

### 2. Camada de consolidação noturna
No fim do dia, o OpenClaw percorre o inbox e promove só o que merece persistência institucional.

Destinos típicos:
- `memory/context/decisions.md`
- `memory/context/lessons.md`
- `memory/context/pending.md`
- `memory/projects/*.md`
- `memory/integrations/*.md`
- `memory/people/*.md` ou `memory/context/people.md`
- nota diária consolidada

### 3. Camada de memória institucional
É a parte que os agentes devem carregar como base estável.

Critérios:
- pouco ruído
- alto valor de reuso
- linguagem limpa
- sem duplicação desnecessária
- fácil de localizar

## Regras operacionais

### Regra 1 — Inbox não é memória final
Inbox serve para velocidade e captura. Não serve para consulta institucional permanente.

### Regra 2 — Consolidação precisa de critério
Só promover:
- decisão estável
- preferência recorrente
- lição reaproveitável
- pendência real
- contexto de projeto que seguirá valendo

### Regra 3 — O que não merece memória longa deve morrer
Não carregar ruído para a memória institucional.

### Regra 4 — Toda consolidação precisa deixar trilha
A consolidação noturna deve gerar:
- resumo do que foi promovido
- origem dos itens consolidados
- timestamp da rodada

### Regra 5 — GitHub é a fonte compartilhada
A memória institucional deve viver versionada no repositório, e não espalhada em silos locais.

## Fluxo diário proposto

### Durante o dia
1. agentes trabalham normalmente
2. contexto relevante vai para `memory/inbox/YYYY-MM-DD/`
3. sem exigir disciplina manual do time para classificar tudo na hora

### À noite
1. cron de consolidação roda
2. lê inbox do dia
3. deduplica
4. conecta itens relacionados
5. promove o que importa
6. registra resumo da consolidação
7. opcionalmente arquiva ou compacta o inbox bruto

### Na manhã seguinte
1. agentes leem memória institucional consolidada
2. começam já com contexto coletivo
3. sem briefing manual

## MVP recomendado

### Fase 1 — Estruturar o repositório como segundo cérebro
Criar:
- `memory/inbox/`
- `memory/consolidation/`
- convenção por agente/domínio
- checklist de promoção

### Fase 2 — Implantar consolidação noturna
Criar um job diário para:
- ler inbox do dia
- extrair decisões, lições, pendências e fatos duráveis
- gravar nos destinos corretos
- gerar log da consolidação

### Fase 3 — Aumentar captura automática
Passar a registrar automaticamente no inbox:
- eventos de agentes
- saídas relevantes
- mudanças estruturais
- decisões explícitas do Alê

### Fase 4 — Melhorar recuperação
Adicionar vínculos entre:
- decisão ↔ projeto
- lição ↔ tipo de operação
- pendência ↔ responsável
- integração ↔ contexto afetado

## Estrutura sugerida de apoio

```text
docs/
  github-segundo-cerebro-operacional.md

memory/
  inbox/
  consolidation/
  context/
  projects/
  integrations/
  content/
  sessions/
```

## Próximos passos objetivos

1. criar a estrutura `memory/inbox/`
2. definir o formato mínimo dos arquivos de captura
3. criar o job noturno de consolidação
4. decidir quais eventos entram automaticamente no inbox
5. testar por 3 dias
6. ajustar ruído, promoção e descarte

## Critério de sucesso

O sistema estará funcionando quando:
- o time trabalhar sem ritual manual de documentação
- o contexto útil continuar aparecendo no dia seguinte
- a memória institucional ficar mais limpa com o tempo, não mais inchada
- decisões e lições deixarem de depender da cabeça do Alê
