---
name: kestra
description: Orquestração de dados e ETL via Kestra (http://localhost:8080). Use para executar flows, monitorar execuções, criar namespaces, agendar pipelines. Ativa em pedidos como "roda o flow do Kestra", "agenda pipeline", "verifica execução kestra".
---

# Kestra — Data Orchestration

Acesso à instância Kestra local para orquestração de pipelines, ETL e workflows de dados.

## Configuração

- **URL base:** `http://localhost:8080/api/v1/`
- **Auth:** nenhuma por padrão (instância local)
- **Painel web:** http://localhost:8080

## Endpoints REST disponíveis

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | `/flows` | Listar todos os flows |
| GET | `/flows/{namespace}/{id}` | Detalhes de um flow |
| POST | `/flows` | Criar/atualizar flow (YAML body) |
| DELETE | `/flows/{namespace}/{id}` | Deletar flow |
| POST | `/executions/{namespace}/{id}` | Executar flow |
| GET | `/executions` | Listar execuções |
| GET | `/executions/{id}` | Status de execução específica |
| GET | `/executions/{id}/logs` | Logs de execução |
| POST | `/executions/{id}/kill` | Cancelar execução |
| GET | `/namespaces` | Listar namespaces |

## Quando usar

- Rodar pipelines de ingestão de dados (ex.: importar CSV → PostgreSQL)
- Orquestrar jobs com dependências entre etapas
- Agendar tarefas recorrentes com CRON
- Monitorar status de pipelines de dados
- ETL entre bases: mia_finance ↔ outros sistemas

## Exemplos

```bash
# Listar flows do namespace padrão
curl -s http://localhost:8080/api/v1/flows | jq '.[].id'

# Executar flow
curl -s -X POST \
  "http://localhost:8080/api/v1/executions/io.kestra/my-flow" \
  -H "Content-Type: application/json" -d '{}'

# Verificar status da execução
curl -s http://localhost:8080/api/v1/executions/EXEC_ID | jq '.state.current'

# Criar flow via YAML
curl -s -X POST http://localhost:8080/api/v1/flows \
  -H "Content-Type: application/x-yaml" \
  -d 'id: teste\nnamespace: default\ntasks:\n  - id: hello\n    type: io.kestra.core.tasks.log.Log\n    message: Ola Kestra'
```

## Boas práticas

- Usar namespaces para organizar flows por domínio (finance, mkt, ops)
- Flows com falha: checar logs via `/executions/{id}/logs`
- Para pipelines de dados críticos, adicionar `retry` no YAML do flow
- Integrar com n8n para triggers externos → Kestra para execução pesada
