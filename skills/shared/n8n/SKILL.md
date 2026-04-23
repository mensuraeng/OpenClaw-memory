---
name: n8n
description: Automação de workflows via n8n REST API (http://localhost:5678). Use para criar, executar, listar, ativar/desativar workflows n8n. Ativa em pedidos como "cria um workflow", "executa o flow X", "lista os workflows do n8n", "conecta n8n a [serviço]".
---

# n8n — Workflow Automation

Acesso completo à instância n8n local via REST API autenticada.

## Configuração

- **URL base:** `http://localhost:5678/api/v1/`
- **Auth:** HTTP Basic → usuário `n8n` / senha `mia_n8n_2026`
- **Header:** `Authorization: Basic $(echo -n 'n8n:mia_n8n_2026' | base64)`
- **Painel web:** http://localhost:5678 (mesma auth)

## Endpoints disponíveis

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | `/workflows` | Listar todos os workflows |
| GET | `/workflows/{id}` | Detalhes de um workflow |
| POST | `/workflows` | Criar novo workflow |
| PUT | `/workflows/{id}` | Atualizar workflow |
| DELETE | `/workflows/{id}` | Deletar workflow |
| POST | `/workflows/{id}/activate` | Ativar workflow |
| POST | `/workflows/{id}/deactivate` | Desativar workflow |
| POST | `/workflows/{id}/run` | Executar workflow manualmente |
| GET | `/executions` | Listar execuções |
| GET | `/executions/{id}` | Detalhes de execução |
| GET | `/credentials` | Listar credenciais registradas |

## Quando usar

- Criar automações entre serviços (webhooks, cron, HTTP triggers)
- Executar pipelines de dados
- Integrar Ghost → Postiz → notificações
- Disparar flows via agente (ex.: "toda segunda-feira, gera o relatório semanal")
- Listar/debugar workflows que falharam

## Exemplos

```bash
# Listar workflows
curl -s -u n8n:mia_n8n_2026 http://localhost:5678/api/v1/workflows | jq '.data[].name'

# Executar workflow por ID
curl -s -X POST -u n8n:mia_n8n_2026 \
  http://localhost:5678/api/v1/workflows/1/run \
  -H "Content-Type: application/json" -d '{}'

# Criar workflow mínimo
curl -s -X POST -u n8n:mia_n8n_2026 \
  http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{"name":"Meu Flow","nodes":[],"connections":{},"settings":{}}'
```

## Boas práticas

- Sempre verificar se o workflow está ativo antes de acionar por cron
- Para flows críticos, buscar execução recente e validar status
- Usar variáveis de ambiente do n8n para segredos (nunca hardcode)
- Após criar um workflow via API, abrir o painel para validar visualmente
- Execuções assíncronas: polling em `/executions/{id}` para checar resultado
