# memory/ — legado local, não fonte de verdade

_Atualizado em 2026-05-01_

## Status

Esta pasta **não é mais o 2nd-brain oficial**.
Ela permanece no workspace como camada local/legada para:

- feedback do Alê ainda não migrado;
- credenciais e mapas locais não versionáveis;
- histórico técnico antigo;
- material transitório usado por scripts legados.

A fonte canônica atual é:

```text
/root/2nd-brain/
```

## Regra de prioridade

1. Para identidade, decisões, pendências, lições, projetos, agentes e regras operacionais, consultar primeiro `/root/2nd-brain/`.
2. Usar `memory/` apenas quando o assunto for explicitamente legado, local, técnico ou ainda não migrado.
3. Se uma informação de `memory/` continuar válida operacionalmente, promover para o destino correto no 2nd-brain antes de tratá-la como fonte de verdade.
4. Se houver conflito entre `memory/` e `/root/2nd-brain/`, vence `/root/2nd-brain/`.

## Destinos canônicos no 2nd-brain

- Identidade: `/root/2nd-brain/01-identity/`
- Pendências, decisões e lições: `/root/2nd-brain/02-context/`
- Conhecimento permanente: `/root/2nd-brain/03-knowledge/`
- Projetos: `/root/2nd-brain/04-projects/`
- Journal: `/root/2nd-brain/05-journal/`
- Agentes: `/root/2nd-brain/06-agents/`
- Sistema: `/root/2nd-brain/_system/`
- Capturas cruas: `/root/2nd-brain/00-inbox/` com sidecar `.meta.yaml`

## Exceções locais permitidas

- `memory/feedback/` — feedback direto do Alê.
- `memory/context/credentials.md` e mapas locais de credenciais — apenas referências, nunca segredo real.
- `memory/integrations/` — notas técnicas locais ainda não migradas.
- Diários antigos `memory/YYYY-MM-DD.md` — histórico, não decisão canônica.

## Regra simples

Se precisa continuar valendo amanhã para a operação, não fica aqui: vai para `/root/2nd-brain/`.
