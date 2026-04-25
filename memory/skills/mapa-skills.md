# Mapa de Skills — Ecossistema OpenClaw

_Atualizado: 2026-04-25 | Inventário completo de skills disponíveis_

---

## Skills por Agente

### Agente MENSURA
| Skill | Propósito |
|---|---|
| `analista-tecnico-documentos` | Análise de documentos técnicos de obra |
| `control-tower-cronograma` | Torre de controle de cronograma — EVM, baseline, LPS |
| `mensura-autopilot` | Operação autônoma do agente MENSURA |
| `mensura-os-torre-controle` | Ordens de serviço e torre de controle |
| `mensura-relatorio-semanal` | Relatório semanal de obra (MIA/TOOLS/CCSP) |
| `orcamentista` | Elaboração e análise de orçamentos |
| `redator-executivo-obra` | Redação de documentos executivos de obra |
| `relatorio-preditivo-obras` | Relatório preditivo com alertas antecipados |

### Agente Finance
| Skill | Propósito |
|---|---|
| `financial-analyst` | Análise financeira geral |
| `cs-financial-analyst` | Análise financeira especializada (Customer Success) |

### Agente PCS
| Skill | Propósito |
|---|---|
| `pcs-autopilot` | Operação autônoma do agente PCS |

---

## Skills Core (infraestrutura do ecossistema)

_Path: `projects/openclaw-memory/skills/core/`_

| Skill | Propósito |
|---|---|
| `capability-evolver` | Evolução de capacidades do agente — auto-melhoria |
| `agent-daily-planner` | Planejamento diário do agente |
| `agent-audit-trail` | Rastreabilidade de ações e decisões |
| `check-analytics` | Verificação de analytics (GA4) |

---

## Skills Compartilhadas (shared)

_Path: `projects/openclaw-memory/skills/shared/`_

| Skill | Propósito |
|---|---|
| `academic-research-hub` | Pesquisa acadêmica e científica |
| `whatsapp-utils` | Utilitários para WhatsApp |

---

## Skills de Protocolo (2nd Brain)

_Path: `memory/skills/`_

| Skill | Propósito |
|---|---|
| `reindexacao.md` | Protocolo de reindexação após troca de LLM |

---

## Paths de referência

| Tipo | Path |
|---|---|
| Skills do agente Mensura | `agents/mensura/skills/` |
| Skills do agente Finance | `agents/finance/skills/` |
| Skills do agente PCS | `agents/pcs/skills/` |
| Skills core | `projects/openclaw-memory/skills/core/` |
| Skills shared | `projects/openclaw-memory/skills/shared/` |
| Skills de protocolo | `memory/skills/` |

---

## Como criar uma nova skill

1. Fazer o processo passo a passo com o agente
2. Corrigir todos os erros na execução real
3. Pedir ao agente: "documente este processo como uma skill em `SKILL.md`"
4. Testar em 3 execuções diferentes antes de considerar estável
5. Adicionar neste mapa
