# PRD — OpenClaw Memory Control

_Atualizado em 2026-04-29_

## Decisão executiva

Criar o cockpit `/openclaw` como camada visual e operacional read-only sobre o `2nd-brain`, sem passar por Obsidian.

Fonte de verdade continua sendo:

```text
/root/2nd-brain
GitHub: mensuraeng/2nd-brain
```

Interface recomendada para publicação protegida:

```text
openclaw.mensuraengenharia.com.br
```

Alternativa aceitável:

```text
mensuraengenharia.com.br/openclaw
```

## Guardrails

- V1 é read-only.
- Não expor publicamente memória operacional, health, integrações, agentes, próximos passos ou riscos.
- Publicação externa exige proteção por login, Cloudflare Access, Tailscale ou camada equivalente.
- Nenhuma ação externa, envio, deploy público, alteração de CRM, alteração de Sienge ou escrita em canais externos sai do painel sem aprovação explícita.

## Objetivo

Elevar a arquitetura de memória de `8,7/10` para faixa `9,5+`, criando:

1. dashboard executivo de memória;
2. validadores automáticos de qualidade;
3. busca no `2nd-brain` com fonte e linha;
4. visualização dos caminhos canônicos;
5. preparação para consolidação noturna auditável.

## Escopo v1 implementado

- Rota: `/openclaw` no Mission Control.
- API: `/api/openclaw-memory`.
- Fonte: `/root/2nd-brain`.
- Métricas:
  - pendências;
  - decisões;
  - lições;
  - WORKING aberto;
  - arquivos por agente;
  - capturas inbox.
- Validadores:
  - captura sem sidecar;
  - decisão sem data explícita;
  - pendência pouco acionável;
  - padrão sensível/segredo em markdown/yaml/json;
  - presença de AGENT-MAP e padrão de captura.
- Busca:
  - lexical/intent v0;
  - ranking por autoridade: decisões e pendências pesam mais que diário/inbox;
  - retorno com `path#line`.

## Próximas melhorias para 10/10

1. Embeddings persistentes por bloco do `2nd-brain`.
2. Consolidação noturna com relatório de promoção automática.
3. Index de entidades: pessoas, empresas, projetos, obras, riscos, decisões e agentes.
4. Tela de diff GitHub entre última memória e estado atual.
5. QA gate antes de commit: segredo, sidecar, pendência sem dono, decisão sem data.
6. Modo write controlado apenas depois de autenticação, aprovação e trilha de auditoria.
