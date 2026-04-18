# NotebookLM Sync, operação na realidade da Flávia

_Data: 2026-04-18_

## Objetivo
Consultar diariamente todos os notebooks existentes no NotebookLM e gerar um rascunho auditável de atualização de memória no workspace.

## O que foi implantado

### Ambiente isolado
- virtualenv: `/root/.openclaw/workspace/.venvs/notebooklm`
- pacote instalado: `notebooklm-py==0.3.4`

### Script operacional
- `/root/.openclaw/workspace/scripts/notebooklm_daily_sync.py`

### Saída esperada
- `memory/notebooklm-sync/YYYY-MM-DD/index.json`
- `memory/notebooklm-sync/YYYY-MM-DD/<slug-do-notebook>.md`

## O que o script faz
1. lista todos os notebooks existentes
2. entra em cada notebook
3. pede uma atualização executiva de memória em português
4. captura também o summary do NotebookLM
5. grava um arquivo por notebook
6. gera um índice consolidado da rodada

## O que ele não faz ainda
- promoção automática para `decisions.md`, `pending.md` e `lessons.md`
- deduplicação semântica
- resolução de conflito entre notebooks
- autenticação automática já pronta

## Estado real agora
A automação está **parcialmente implantada**, mas **bloqueada por autenticação**.

Erro atual validado:
- `Not logged in`
- storage esperado: `/root/.notebooklm/storage_state.json`

## Comando para autenticar
```bash
/root/.openclaw/workspace/.venvs/notebooklm/bin/python -m notebooklm login
```

## Depois da autenticação
Teste manual:
```bash
/root/.openclaw/workspace/.venvs/notebooklm/bin/python /root/.openclaw/workspace/scripts/notebooklm_daily_sync.py
```

## Automação recomendada
Depois do login, criar cron diária silenciosa por exemplo às 06:40 BRT, antes do pulso matinal.

Payload sugerido:
- rodar `scripts/notebooklm_daily_sync.py`
- silêncio por padrão
- alertar só em caso de falha de auth ou erro real

## Leitura estratégica
NotebookLM aqui deve funcionar como:
- camada de consulta
- fonte auxiliar de atualização
- acelerador de síntese

Não deve virar:
- memória principal
- fonte canônica de decisão
- depósito bruto de contexto
