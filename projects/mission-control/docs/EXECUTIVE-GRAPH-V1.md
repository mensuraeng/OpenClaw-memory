# Mission Control Executive Graph v1

_Atualizado em 2026-04-29_

## Objetivo

Conectar, em modo interno e read-only, os principais elementos da operação:

```text
projeto → tarefa → agente → documento → memória → evidência → decisão
```

A v1 não substitui GitHub nem `/root/2nd-brain`. O Mission Control é cockpit de observabilidade e navegação executiva.

## Rotas implantadas

### `/projects`

Tela executiva de projetos com:

- projetos detectados em `/root/2nd-brain/04-projects` e `workspace/projects`;
- domínio/empresa;
- owner/agente sugerido;
- prioridade;
- risco;
- status;
- próximo passo;
- tarefas vinculadas;
- documentos vinculados;
- evidências de runtime vinculadas;
- decisões vinculadas.

### `/docs`

Biblioteca executiva de documentos com:

- fonte: `2nd-brain` ou `workspace`;
- categoria;
- empresa/domínio;
- projeto vinculado quando inferível;
- status;
- sensibilidade;
- tamanho;
- data de modificação;
- caminho interno.

A tela não lê/exibe o conteúdo completo dos documentos sensíveis; v1 mostra metadados e caminhos.

## API interna

### `GET /api/executive-graph`

Retorna grafo agregado de projetos, tarefas, documentos, evidências e decisões.

### `GET /api/executive-graph?mode=documents`

Retorna biblioteca documental agregada.

### `GET /api/executive-graph?q=<termo>`

Filtra projetos por termo.

## Fontes de dados

- `/root/2nd-brain/04-projects/`
- `/root/2nd-brain/02-context/decisions.md`
- `runtime/tasks/task-executions.jsonl`
- `runtime/`
- `workspace/docs/`
- `workspace/projects/*/docs/`
- `workspace/projects/*/README.md`

## Guardrails

- read-only: não cria, edita, envia ou apaga arquivos;
- não altera autenticação, gateway, cron ou configurações sensíveis;
- não envia mensagens externas;
- não vira fonte de verdade acima de GitHub/2nd-brain;
- não expõe segredos/certificados/tokens; exibe apenas metadados de arquivo e caminhos internos.

## Limites conhecidos

- vínculos são heurísticos por nome/domínio/caminho; ainda não há sidecar obrigatório por documento;
- `/docs` v1 classifica por regras simples de caminho/conteúdo;
- `/projects` v1 não permite alterar status ou próximos passos;
- evidências dependem de nomes de arquivos/pastas em `runtime/`.

## Backlog

1. Adicionar sidecars `.meta.yaml` para documentos gerados por agentes.
2. Criar detalhe `/projects/[id]` com linha do tempo completa.
3. Ligar `/tasks` com campo formal `projectId`.
4. Adicionar alerta de projeto parado.
5. Evoluir classificação documental para metadados explícitos.
6. Adicionar reverse prompts read-only por projeto.
