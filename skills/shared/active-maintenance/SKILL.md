# Active Maintenance — Flávia Edition

Skill para manutenção ativa do ambiente OpenClaw e higiene da memória operacional.

## Objetivo

Evitar degradação silenciosa do sistema, da estrutura de memória e do workspace.

## Escopo

### 1. Saúde operacional
Verificar periodicamente:
- uso de disco
- arquivos temporários acumulados
- sessões e artefatos soltos em lugares errados
- integridade básica da estrutura `memory/`
- presença de credenciais em texto onde não deveriam estar

### 2. Higiene da memória
Revisar:
- arquivos soltos no topo de `memory/`
- desalinhamentos com `MEMORY.md`
- duplicação óbvia entre `memory/context/`, `memory/projects/`, `memory/sessions/` e `memory/YYYY-MM-DD.md`

### 3. Limpeza segura
Pode:
- mover arquivos para pastas corretas
- registrar pendências estruturais em `memory/context/pending.md`
- registrar lições em `memory/context/lessons.md`

Não pode:
- apagar conteúdo importante sem confirmação
- remover configs em produção sem checar impacto
- "otimizar" memória destruindo contexto útil

## Checklist operacional

### Health check rápido
- `df -h`
- revisar diretórios de artefatos temporários relevantes
- checar arquivos grandes ou desnecessários no workspace

### Revisão da memória
- `MEMORY.md` continua compatível com a árvore real?
- existem arquivos soltos fora do padrão?
- existem segredos em texto fora do cofre?

### Saída esperada
Relatório curto com:
- o que está saudável
- o que está desalinhado
- o que foi corrigido
- o que depende de confirmação

## Regra de ouro

Manutenção ativa existe para preservar clareza e continuidade, não para criar automação ornamental.
