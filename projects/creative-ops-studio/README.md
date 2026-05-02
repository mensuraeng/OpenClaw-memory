# Creative Ops Studio

MVP interno para transformar a análise da repo `Anil-matcha/Open-Generative-AI` em operação prática de conteúdo/asset para MENSURA, MIA e PCS.

## Tese

A repo analisada é útil como referência de **hub multimodal + catálogo de modelos + workflow/agents**, mas não deve ser usada como publicação automática nem como voz institucional direta.

Este projeto cria uma camada segura:

```text
brief → marca → canal/formato → use case → modelo recomendado → prompt → aprovação humana
```

## Status

- Versão: `0.1.0`
- Efeito externo: nenhum
- Publicação automática: bloqueada
- Saída gerada: JSON de rascunho operacional

## Arquivos principais

- `config/brands.json` — guardrails de MENSURA, MIA e PCS
- `config/model_router.json` — roteador de casos de uso para famílias/modelos inspirados na repo
- `scripts/brief_to_asset_plan.py` — CLI que transforma brief em pacote de geração
- `runtime/` — saídas geradas localmente

## Uso

```bash
python3 scripts/brief_to_asset_plan.py \
  --brand MENSURA \
  --channel LinkedIn \
  --asset-type image \
  --format "post 1:1" \
  --brief "obra não atrasa por falta de esforço, atrasa por falta de sistema"
```

## Regras permanentes

1. Todo asset gerado é rascunho.
2. Publicação externa exige aprovação humana.
3. Não usar rostos/vozes de pessoas reais sem autorização.
4. Não simular cliente, órgão público, documento oficial ou aprovação contratual.
5. Não transformar estética boa em claim técnico sem evidência.

## Próximas evoluções

1. Conectar com geradores reais via API segura, sem expor chave no frontend.
2. Criar biblioteca de prompts aprovados por marca.
3. Adicionar scoring de risco por asset.
4. Integrar calendário editorial e status: `draft`, `review`, `approved`, `published`.
5. Salvar variações e decisões para reaproveitamento em campanhas.
