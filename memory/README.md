# workspace/memory — Inbox Operacional

Esta pasta é a **camada quente** da memória do agente.

## Arquitetura de duas camadas

| Camada | Caminho | Papel |
|---|---|---|
| **Inbox operacional** | `/root/.openclaw/workspace/memory/` | Escritas rápidas durante sessões, diários, contexto de curto prazo |
| **Acervo curado** | `/root/2nd-brain/` | Conhecimento permanente, promovido manualmente ou pelo cron 22h, sincronizado no GitHub |

## Fluxo de promoção

```
workspace/memory/    →  (cron 22h)  →  /root/2nd-brain/06-agents/flavia/
  context/pending.md                     pending.md
  context/decisions.md                   decisions.md
  context/lessons.md                     lessons.md
  2026-MM-DD.md        (não promovido — diários ficam aqui)
```

## Regras

- **Escreva aqui** quando for nota de sessão, rascunho, contexto temporário.
- **Escreva no 2nd-brain diretamente** quando for decisão permanente, conhecimento curado, contexto de projeto.
- **Nunca copie newsletters ou emails de marketing** para pending.md — descarte direto.
- O cron `flavia:manutencao-memoria-22h` cuida da promoção e sincronização diária.
