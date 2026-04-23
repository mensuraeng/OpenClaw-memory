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
- integridade básica da estrutura do `2nd-brain` e dos diretórios locais do workspace
- presença de credenciais em texto onde não deveriam estar

### 2. Higiene da memória
Revisar:
- arquivos soltos fora da estrutura oficial do `2nd-brain`
- desalinhamentos entre ponte local e fonte de verdade
- duplicação óbvia entre `2nd-brain`, memória legada do workspace e artefatos locais

### 3. Limpeza segura
Pode:
- mover arquivos para pastas corretas
- registrar pendências estruturais em `/root/2nd-brain/02-context/pending.md`
- registrar lições em `/root/2nd-brain/02-context/lessons.md`

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
- a ponte local (`MEMORY.md`) continua compatível com o `2nd-brain`?
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
