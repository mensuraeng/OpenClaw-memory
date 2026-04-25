# Mapa de Agentes — Ecossistema OpenClaw

_Atualizado: 2026-04-25 | Consultar antes de acionar ou criar agentes_

---

## Agentes Principais

| ID | Nome/Persona | Papel | Canal principal |
|---|---|---|---|
| `main` | **Flávia** | CFO, orquestradora central, governança do ecossistema | Telegram DM (Alexandre) |
| `mensura` | **MENSURA** | Domínio técnico-comercial, posicionamento, propostas | Grupo Mensura (topic 1) |
| `marketing` | **Marketing** | Conteúdo, CRM, prospecção, follow-up, campanhas | Grupo Mensura — tópico MKT (thread 43) |
| `mia` | **MIA** | Projetos ultra-premium, governança de obras AAA | Grupo MIA |
| `pcs` | **PCS** | Obras públicas, licitações, contratos, Sienge | Grupo PCS |
| `finance` | **Finance** | Financeiro, contas a pagar, fluxo de caixa | Grupo Finance (topic 13) |
| `juridico` | **Jurídico** | Contratos, compliance, análise legal | — |
| `bi` | **BI** | Business intelligence, relatórios analíticos | — |
| `producao` | **Produção** | Gestão de obras em execução | — |
| `rh` | **RH** | Recursos humanos, onboarding | — |
| `suprimentos` | **Suprimentos** | Compras, fornecedores, cotações | — |
| `pessoal` | **Pessoal** | Assuntos pessoais do Alexandre | — |

## Agentes de Infraestrutura

| ID | Função |
|---|---|
| `autopilot` | Autopilot — execução autônoma de tarefas longas |
| `croncheap` | Agente de crons econômicos (GPT 4o Mini) — tarefas recorrentes de baixo custo |
| `claude-code` | Claude Code — desenvolvimento de software |
| `mkt` | Alias marketing |

---

## Configuração de Grupos Telegram

| Grupo | ID | Agente(s) | Tópicos |
|---|---|---|---|
| MENSURA Engenharia | `-1003366344184` | mensura (topic 1), marketing (topic 43) | 1 = Geral, 43 = MKT |
| Finance | `-1003818163425` | finance | 13 = Finance |
| MIA | `-1003704703669` | mia | 1 = Geral |
| PCS | `-1003146152550` | pcs | 1 = Geral |

---

## Hierarquia e Fluxo de Trabalho

```
Alexandre (decisão estratégica)
    │
    ▼
Flávia / Main (CFO — orquestra tudo)
    ├── MENSURA → posicionamento técnico, proposta, argumento
    ├── Marketing → conteúdo, CRM, abordagem, follow-up
    ├── Finance → contas, fluxo, cobranças
    ├── MIA → obras premium
    ├── PCS → obras públicas
    ├── Jurídico → contratos
    └── BI → relatórios e análise
```

---

## Responsabilidades da Máquina de Vendas

| Função | Responsável |
|---|---|
| Governança e cobrança de resultados | Flávia |
| Posicionamento, oferta, argumento técnico | MENSURA |
| Conteúdo, CRM, prospecção LinkedIn, follow-up | Marketing |
| Decisões estratégicas, aprovações, respostas LinkedIn | Alexandre |

---

## Modelos por Agente (padrão)

- **Flávia / Main:** claude-sonnet-4-6 (padrão), claude-opus-4-7 (tarefas complexas)
- **Croncheap:** GPT-4o Mini (economia em tarefas recorrentes)
- **Outros agentes:** claude-sonnet-4-6

---

## Skills por Agente

| Agente | Skills principais |
|---|---|
| mensura | orcamentista, relatorio-preditivo-obras, redator-executivo-obra, analista-tecnico-documentos, mensura-os-torre-controle, control-tower-cronograma, mensura-relatorio-semanal |
| marketing | linkedin-outreach, crm-hubspot, conteudo-linkedin |
| pcs | inbox_triage, juridico-contratos |

_Localização das skills: `/root/.openclaw/workspace/agents/<agentId>/skills/`_
_Skills compartilhadas: `/root/.openclaw/workspace/projects/openclaw-memory/skills/shared/`_
