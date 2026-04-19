# OpenClaw Skills — Estrutura em Camadas

Atualizado em: 2026-04-18

## Hierarquia de Acesso

| Camada | Path | Acesso |
|--------|------|--------|
| shared/ | skills/shared/ | Todos os agentes |
| shared/whatsapp/ | skills/shared/whatsapp/ | Todos os agentes (protocolo WhatsApp) |
| core/ | skills/core/ | Mecânica interna do OpenClaw |
| agents/mensura/skills/ | agents/mensura/skills/ | Agente Mensura (domínio fechado) |
| agents/finance/skills/ | agents/finance/skills/ | Agente Finance (domínio fechado) |
| agents/pcs-agent/skills/ | agents/pcs-agent/skills/ | Agente PCS (domínio fechado) |

## Inventário Completo

### shared/ — Genérico (todos os agentes)

| Skill | Categoria | Descrição |
|-------|-----------|-----------|
| academic-research-hub | util | Pesquisa acadêmica |
| active-maintenance | util | Manutenção ativa do sistema |
| aeo-analytics-free | analytics | Analytics AEO gratuito |
| afrexai-inventory-supply-chain | integ | Supply chain Afrex AI (inventário) |
| afrexai-supply-chain | integ | Supply chain Afrex AI (base) |
| agent-context-system | system | Gerenciamento de contexto entre agentes |
| agent-task-tracker | system | Rastreamento de tarefas |
| arc-trust-verifier | security | Verificação de confiança |
| biz-reporter | reporting | Relatórios de negócio |
| docling | docs | Processamento e parsing de documentos |
| notion | integ | Integração Notion |
| slack | integ | Integração Slack |
| superpowers | system | Capacidades expandidas do agente |
| weather | util | Dados de clima |
| youtube-publisher | integ | Publicação YouTube |

### shared/whatsapp/ — Protocolo WhatsApp

| Skill | Descrição |
|-------|-----------|
| openclaw-whatsapp | Core WhatsApp OpenClaw |
| whatsapp-chats | Gerenciamento de chats |
| whatsapp-styling-guide | Guia de estilo de mensagens |
| whatsapp-utils | Utilitários WhatsApp |

### core/ — Mecânica OpenClaw (sistema interno)

| Skill | Descrição |
|-------|-----------|
| agent-audit-trail | Rastreamento de auditoria de ações |
| agent-daily-planner | Planejamento diário do agente |
| capability-evolver | Evolução dinâmica de capacidades |
| capability-evolver-src | Código-fonte do evoluidor de capacidades |
| check-analytics | Verificação de analytics do sistema |

### agents/mensura/skills/ — Domínio Mensura (fechado)

| Skill | Descrição |
|-------|-----------|
| mensura-autopilot | Piloto automático Mensura |
| mensura-relatorio-semanal | Geração de relatório semanal de obras |
| orcamentista | Orçamentação e medição de obras |

### agents/finance/skills/ — Domínio Financeiro (fechado)

| Skill | Descrição |
|-------|-----------|
| cs-financial-analyst | Analista financeiro CS |
| financial-analyst | Analista financeiro base |

### agents/pcs-agent/skills/ — Domínio PCS (fechado)

(Vazio — aguardando skills específicas do agente PCS)

## Convenção de Path

Ao referenciar skills em configs de agente, use paths relativos ao workspace:

  shared:         skills/shared/<skill-name>
  core:           skills/core/<skill-name>
  agente-próprio: agents/<agent-id>/skills/<skill-name>

## Regras de Domínio

- Skills em agents/<agente>/skills/ são EXCLUSIVAS daquele agente
- Skills em shared/ podem ser importadas por QUALQUER agente
- Skills em core/ são carregadas pela mecânica interna do OpenClaw
- Nunca mover skill de domínio fechado para shared/ sem revisão arquitetural
