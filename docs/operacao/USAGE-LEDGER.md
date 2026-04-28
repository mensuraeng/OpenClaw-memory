# Usage Ledger — Custo e Uso Operacional

_Atualizado em 2026-04-28_

## Objetivo

Medir custo e utilidade das automações para evitar uma operação agentic cara, opaca e sem retorno.

## O que registrar

Cada operação relevante deve poder registrar:
- agente;
- tarefa;
- ferramenta/API;
- tokens/créditos quando disponíveis;
- custo estimado;
- entidade afetada;
- output gerado;
- sucesso/falha;
- evidência.

## Arquivo padrão

`runtime/usage-ledger/usage-ledger.jsonl`

Um JSON por linha.

## Schema mínimo

```json
{
  "ts": "2026-04-28T00:00:00Z",
  "agent": "main",
  "domain": "growth|finance|obra|infra|trade|authority",
  "operation": "",
  "tool": "",
  "entity": "",
  "input_units": null,
  "output_units": null,
  "credits": null,
  "estimated_cost_usd": null,
  "status": "ok|fail|skipped",
  "evidence": "",
  "notes": ""
}
```

## Princípios

- Não precisa ser perfeito no início.
- Melhor custo estimado do que custo invisível.
- Operação recorrente sem valor deve ser cortada.
- Toda API paga ou consumo alto de LLM deve entrar no ledger.

## Uso futuro

- custo por lead;
- custo por relatório;
- custo por integração;
- custo por subagente;
- custo por loop fechado.
