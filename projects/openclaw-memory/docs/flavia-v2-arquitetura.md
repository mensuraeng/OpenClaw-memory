# Flávia v2 — Arquitetura Adaptada

_Atualizado em 2026-04-13_

## Objetivo

Transformar o workspace da Flávia em um sistema operacional de contexto e execução.
A referência de "second brain" entra como arquitetura de organização, não como ideologia de autoevolução.

Princípio central:
- menos hype
- menos automação ornamental
- mais contexto auditável
- mais separação de responsabilidades
- mais escalabilidade para subagentes e frentes da operação

## O que manter

A base atual já está correta e deve continuar existindo:

- `AGENTS.md` → como operar
- `MEMORY.md` → painel executivo de continuidade
- `SOUL.md` → persona operacional
- `IDENTITY.md` → identidade e escopo
- `USER.md` → perfil executivo do Alê
- `memory/` → memória institucional
- `scripts/` → automações operacionais
- `skills/` → capacidades especializadas

## O que evoluir

Hoje o workspace já tem memória e identidade, mas ainda mistura muito:
- contexto institucional
- execução por área
- projetos
- materiais de apoio
- automações

A evolução proposta é separar isso em camadas mais claras.

## Estrutura alvo

```text
workspace/
├── AGENTS.md
├── MEMORY.md
├── SOUL.md
├── USER.md
├── IDENTITY.md
├── TOOLS.md
├── docs/
│   ├── flavia-v2-arquitetura.md
│   ├── operating-model/
│   └── references/
├── memory/
│   ├── context/
│   ├── projects/
│   ├── integrations/
│   ├── content/
│   ├── sessions/
│   └── YYYY-MM-DD.md
├── areas/
│   ├── mensura/
│   ├── mia/
│   ├── pcs/
│   ├── comercial/
│   ├── financeiro/
│   ├── operacao/
│   └── marketing/
├── projects/
├── scripts/
├── skills/
└── referencias/
```

## Papel de cada camada

### 1. Root files
Arquivos de identidade, operação e continuidade.
São pequenos, estáveis e sempre legíveis no boot.

### 2. `memory/`
Memória institucional compartilhada.
Não guarda execução operacional detalhada por área quando isso merecer estrutura própria.

### 3. `areas/`
Camada operacional por frente.
Serve para organizar contexto vivo por domínio de trabalho.

Exemplos:
- `areas/mensura/` → materiais operacionais da frente MENSURA
- `areas/mia/` → operação e contexto da MIA
- `areas/pcs/` → narrativa, comercial e operação PCS
- `areas/comercial/` → propostas, ICP, pipeline, posicionamento
- `areas/financeiro/` → rotinas e controles financeiros
- `areas/operacao/` → rotinas transversais, cadências, checklists
- `areas/marketing/` → conteúdo, presença, ativos de marca

### 4. `projects/`
Projetos com começo, meio e fim.
Se algo é temporário e tem entregável claro, deve viver aqui.

### 5. `docs/`
Documentação estruturante.
Playbooks, modelos operacionais, referências de arquitetura e decisões mais amplas.

## Regras de uso

### Vai para `memory/context/`
- decisão permanente
- lição recorrente
- pendência executiva
- contexto institucional estável

### Vai para `memory/projects/`
- projeto ainda leve, sem necessidade de pasta própria
- histórico resumido de projeto

### Vai para `areas/`
- operação contínua por frente
- material que tende a crescer por domínio
- arquivos usados por uma função específica com frequência

### Vai para `projects/`
- iniciativa delimitada
- entrega clara
- início e fim definidos

### Vai para `docs/`
- playbook
- padrão operacional
- documentação de arquitetura
- referência que não é memória nem projeto

## O que NÃO adotar da skill original

- autoevolução automática
- mutação de comportamento
- goal alignment em tudo
- dashboards ornamentais como centro do sistema
- importação de cápsulas de terceiros

Motivo:
- reduz auditabilidade
- aumenta deriva comportamental
- adiciona complexidade sem ganho proporcional
- piora confiança operacional

## Adoção recomendada

### Fase 1 — arquitetura e organização
- definir estrutura-alvo
- criar pastas-base
- adicionar README curto em cada camada importante

### Fase 2 — migração leve
- mover ou espelhar conteúdos que hoje estão difusos
- sem quebrar caminhos já usados
- priorizar organização, não perfeccionismo

### Fase 3 — especialização por frente
- preparar áreas para subagentes e fluxos específicos
- ex.: Mensura, PCS, Financeiro, Comercial

## Recomendação prática

A Flávia não precisa de um "second brain" paralelo.
Ela precisa de um workspace mais disciplinado, modular e escalável.

A melhor adaptação é:
- aproveitar a lógica de separação por camadas
- manter identidade e memória como núcleo
- criar camada operacional por área
- evitar qualquer mecanismo que auto-altere comportamento sem controle
