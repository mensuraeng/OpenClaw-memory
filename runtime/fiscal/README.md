# Runtime Fiscal — read-only

Estrutura local para evidências fiscais geradas pela frente `projects/fiscal-emission-lab`.

## Guardrails

- Não contém certificado digital.
- Não contém token/API key.
- Não executa consulta SEFAZ, transmissão, emissão, cancelamento, inutilização ou envio externo.
- `outbox-notificacoes/` é apenas fila local de mensagens sugeridas; nada é enviado automaticamente.

## Estrutura

```text
runtime/fiscal/
  notas-recebidas/<empresa>/<YYYY-MM>/   # XML/JSON/PDF baixados ou importados
  ledger/                                # índices JSONL locais
  outbox-notificacoes/                   # mensagens sugeridas para revisão humana
```

## Status v0

A estrutura está preparada para parser local de XML NF-e de amostra/fixture sintética. Integração com DFe.NET/DistribuicaoDFe exige certificado e ambiente controlado, portanto permanece planejada, não executada.
