# NotebookLM Sync

Sincronização local do NotebookLM para memória operacional/pessoal do OpenClaw.

## Objetivo

- verificar notebooks e fontes do NotebookLM
- identificar mudanças recentes
- registrar um resumo mínimo e útil em memória
- não copiar segredos nem conteúdo bruto desnecessário

## Estado atual

- ambiente Python preparado em `/root/.openclaw/venvs/notebooklm`
- autenticação do NotebookLM ainda precisa existir no storage esperado pelo CLI

## Comandos úteis

```bash
/root/.openclaw/venvs/notebooklm/bin/notebooklm status
/root/.openclaw/venvs/notebooklm/bin/notebooklm list
python3 /root/.openclaw/workspace/tools/notebooklm-sync/sync_notebooklm.py --dry-run
```

## Política de memória

- salvar apenas resumos e índices
- não salvar chaves, tokens ou segredos
- priorizar mudanças úteis para contexto futuro
- se não houver login válido, registrar falha curta e encerrar com código não-zero
