# Mapeamento RDO Sienge → OpenClaw

## Status de Permissões (testado em 2026-04-19)

| Endpoint | Status HTTP | Situação |
|---|---|---|
| GET /construction-daily-report | 403 Permission Denied | EXISTE — solicitar liberação |
| GET /construction-daily-report/{buildingId}/{id} | 403 | EXISTE — solicitar liberação |
| POST /construction-daily-report | 403 | EXISTE — solicitar liberação |
| GET /construction-daily-report/event-type | 403 | EXISTE — solicitar liberação |
| GET /construction-daily-report/types | 403 | EXISTE — solicitar liberação |
| POST /construction-daily-report/{id}/{id}/tasks | 403 | EXISTE — solicitar liberação |
| POST /construction-daily-report/{id}/{id}/events | 403 | EXISTE — solicitar liberação |
| POST /construction-daily-report/{id}/{id}/crews | 403 | EXISTE — solicitar liberação |
| POST /construction-daily-report/{id}/{id}/equipments | 403 | EXISTE — solicitar liberação |
| GET /cost-centers | 200 OK | ATIVO (22 obras encontradas) |
| GET /obras | 200 OK (com params) | ATIVO (2 obras acessíveis) |

**Ação necessária:** Habilitar recurso  para o usuário de API
 no Admin Sienge > Usuários de API > Recursos autorizados.

---

## Estrutura Completa do RDO (GET /construction-daily-report/{buildingId}/{id})



---

## Mapeamento Campo-a-Campo: Sienge → OpenClaw

### Cabeçalho do RDO

| Campo Sienge | Tipo | OpenClaw → Destino |
|---|---|---|
|  | int | →  no contexto da obra |
| Sun Apr 19 21:04:17 -03 2026 | string (yyyy-MM-dd) | →  no Last Planner / PPC |
|  | string | →  (precisa lookup de usuário) |
|  | string | → Contexto de dia útil / feriado |
|  | float | →  → Banco de Restrições |
|  | string | →  → Relatório Preditivo |
|  | Fine/Light rain/Heavy rain/Unworkable | →  → IAO/PPC |

### Tarefas Planejadas → Last Planner

| Campo Sienge | OpenClaw → Destino |
|---|---|
|  | → ID da atividade no Last Planner (vincular com cronograma) |
|  | → Pacote de trabalho (WBS level) |
|  | →  (medição real) |
|  | → Unidade de medição |
|  | → Fornecedor responsável pela tarefa |
|  | → Local de execução |

### Tarefas Avulsas → Banco de Tarefas Não Planejadas

| Campo Sienge | OpenClaw → Destino |
|---|---|
|  | →  → sinal de imprevistos |
|  | → Quantidade executada fora do plano |
|  | → Unidade |

### Equipes → PPC / IAO

| Campo Sienge | OpenClaw → Destino |
|---|---|
|  | → Insumo MO (precisa lookup em /building-cost-estimations) |
|  | → Categoria de MO (Pedreiro, Servente, etc.) |
|  | →  → cálculo de produtividade |
|  | DIRECT_LABOR/INDIRECT_LABOR/THIRD_PARTY → Tipo de MO |
|  | type/resource → origem do dado |

### Equipamentos → Controle de Frentes

| Campo Sienge | OpenClaw → Destino |
|---|---|
|  | → Tipo de equipamento |
|  | → Quantidade em uso |
|  | IN_USE/IDLE/OUT_OF_ORDER →  |

### Ocorrências → Banco de Restrições

| Campo Sienge | OpenClaw → Destino |
|---|---|
|  | →  no Banco de Restrições |
|  | → Categoria da restrição (precisa lookup em /event-type) |
|  | → Tipo legível da restrição |

---

## Gaps Identificados

### O que o RDO tem que o OpenClaw AINDA NÃO CONSOME

1. **Índice pluviométrico** (): dado valioso para correlacionar dias improdutivos
   com chuva. O OpenClaw não tem campo para isso no Banco de Restrições.

2. **Turno x condição climática por turno** (): a granularidade por
   turno existe no Sienge, mas o OpenClaw trabalha com dia inteiro.

3. **Tarefas avulsas** (): sinal direto de trabalho não planejado — fundamental
   para PPC mas não existe campo específico no OpenClaw atual.

4. **Status de equipamento** (IN_USE/IDLE/OUT_OF_ORDER): o IDLE e OUT_OF_ORDER são restrições
   de equipamento, mas o OpenClaw não tem esse mapeamento automático.

5. **Assignment de MO** (DIRECT_LABOR/INDIRECT_LABOR/THIRD_PARTY): distinção importante para
   custo mas o OpenClaw só registra presença, não tipo de vínculo.

6. **Anexos/fotos** (): evidências fotográficas que não têm destino no OpenClaw.

7. **Responsável como string** (): precisa de lookup para obter nome completo
   — endpoint  não está liberado ainda.

### Dependências para Integração Completa

| Endpoint Necessário | Por quê | Status |
|---|---|---|
| GET /construction-daily-report | Principal — RDO | 403 — liberar |
| GET /construction-daily-report/types | Categorias de ocorrência | 403 — liberar |
| GET /building-cost-estimations/{id}/resources | Lookup insumos MO/Equip | Não testado |
| GET /employees ou /users | Resolver responsibleId para nome | Não liberado |
| GET /construction-daily-report/{id}/{id} (nested tasks) | Detalhe de tarefas | 403 — liberar |

---

## Fluxo de Integração Proposto



---

## Bloqueio Atual: Como Liberar a Permissão

1. Acessar Sienge como administrador
2. Menu: Configurações → Usuários de API → pcsservices-project
3. Módulo: Diário de Obra → habilitar 
4. Salvar

Após liberação, validar com:
{ "message": "Permission denied" }
Esperado: HTTP 200 com JSON 

---

## Bug Identificado no Projeto Existente

Os endpoints  e  usam prefixo  no path:

 retorna 200 sem o prefixo. Corrigir antes de integrar.
