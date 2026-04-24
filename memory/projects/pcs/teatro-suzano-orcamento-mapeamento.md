# Teatro Suzano — Mapeamento do Módulo Orçamento (Sienge)

_Atualizado em 2026-04-24_

## Identificação

- **Obra:** TEATRO MUNICÍPIO DE SUZANO
- **buildingId:** 1354
- **API pública:** `https://api.sienge.com.br/pcsservices/public/api/v1`
- **Auth:** Basic Auth (username:password em base64) — sem OAuth

> ⚠️ A API legacy (`pcsservices.sienge.com.br/sienge/oauth/token`) está com OAuth falhando (400).
> O módulo de orçamento só existe na **API pública** (`api.sienge.com.br`).

## Endpoints mapeados

| Endpoint | Status | Recurso necessário |
|---|---|---|
| `GET /building-cost-estimations/{id}/sheets` | ❌ 403 | `building-cost-estimations-v1` |
| `GET /building-cost-estimations/{id}/sheets/{unitId}/items` | ❌ 403 | `building-cost-estimations-v1` |
| `GET /building-cost-estimations/{id}/resources` | ✅ OK | (já liberado) |
| `GET /building-cost-estimations/{id}/cost-estimate-resources` | ❌ 403 | `building-cost-estimation-cost-estimate-resources-v1` |

### O que cada endpoint retorna

- **`/sheets`** → lista de planilhas por unidade construtiva (estrutura do orçamento)
- **`/sheets/{unitId}/items`** → itens do orçamento: serviços, composições, quantidades e valores — **é aqui que está o orçamento detalhado**
- **`/resources`** → cadastro de insumos (materiais, mão de obra, equipamentos) — **5.227 insumos cadastrados**
- **`/cost-estimate-resources`** → insumos orçados com valores unitários por composição

## Dados disponíveis hoje (/resources)

Total de insumos cadastrados: **5.227**
- MATERIAL: ~96%
- LABOR: ~3%
- EQUIPMENT: ~1%

## Para destravar o orçamento completo

Acessar Sienge → **Gerenciamento de API** → usuário `pcsservices-project` → habilitar:
1. `building-cost-estimations-v1` → libera `/sheets` e `/sheets/{id}/items` (valores reais do orçamento)
2. `building-cost-estimation-cost-estimate-resources-v1` → libera insumos orçados com preços

## Código de integração

`/root/.openclaw/workspace/projects/openclaw-memory/projects/pcs-sienge-integration/src/pcs_sienge/endpoints/budget_estimations.py`
