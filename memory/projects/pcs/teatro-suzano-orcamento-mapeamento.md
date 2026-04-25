# Teatro Suzano — Mapeamento do Módulo Orçamento (Sienge)

_Atualizado em 2026-04-25_

## Identificação

- **Obra:** TEATRO MUNICÍPIO DE SUZANO
- **buildingId:** 1354
- **API pública:** `https://api.sienge.com.br/pcsservices/public/api/v1`
- **Auth:** Basic Auth (username:password em base64) — sem OAuth

> ⚠️ A API legacy (`pcsservices.sienge.com.br/sienge/oauth/token`) está com OAuth falhando (400).
> O módulo de orçamento só existe na **API pública** (`api.sienge.com.br`).

## Endpoints mapeados

| Endpoint | Status | Observação |
|---|---|---|
| `GET /building-cost-estimations/{id}/sheets` | ✅ 200 | 1 planilha: "TEATRO MUNICÍPIO DE SUZANO" (UNLOCKED) |
| `GET /building-cost-estimations/{id}/sheets/{unitId}/items` | ✅ 200 | 5 itens — valores placeholder (R$0,00 / R$1,00) |
| `GET /building-cost-estimations/{id}/resources` | ✅ 200 | 5.227 insumos cadastrados |
| `GET /building-cost-estimations/{id}/cost-estimate-resources` | ✅ 200 | 0 registros — orçamento não lançado |

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

## Status da integração (2026-04-25)

✅ **Integração desbloqueada** — permissões `building-cost-estimations-v1` e `building-cost-estimation-cost-estimate-resources-v1` habilitadas no Sienge.

⚠️ **Orçamento não lançado** — a planilha existe no Sienge mas os itens têm valores placeholder (R$0,00). O orçamento real precisa ser inserido manualmente no Sienge antes de qualquer extração útil de dados.

## Código de integração

`/root/.openclaw/workspace/projects/openclaw-memory/projects/pcs-sienge-integration/src/pcs_sienge/endpoints/budget_estimations.py`
