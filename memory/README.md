# 2nd Brain — Mapa de Navegação

_Repositório: `mensuraeng/OpenClaw-memory` | Path local: `/root/.openclaw/workspace/memory/`_
_Sync: a cada 2h automático + commit diário 19:30 BRT_

---

## O que é este 2nd Brain

Sistema de memória persistente do ecossistema Alexandre + Flávia. Funciona como repositório GitHub para que todos os agentes (Flávia, MENSURA, Marketing, PCS, MIA, etc.) e ferramentas (Claude Code, OpenClaw) compartilhem o mesmo contexto permanente.

**Três pilares:** Contexto · Skills · Rotinas (Crons)

---

## Mapa de Pastas

```
memory/
├── README.md                    ← ESTE ARQUIVO — navegação raiz
│
├── context/                     ← Contexto permanente (carregar sempre)
│   ├── mapa-agentes.md          ← Todos os agentes, papéis, canais, Telegram
│   ├── mapa-crons.md            ← Todas as automações, horários, propósitos
│   ├── mapa-maquina-vendas-mensura.md ← Máquina Comercial MENSURA completa
│   ├── maquina-comercial-cfo-protocolo.md ← Protocolo CFO governança comercial
│   ├── linkedin-mensura-protocolo.md ← Prospecção LinkedIn, cadência, scripts
│   ├── business-context.md      ← Contexto multi-marca (MENSURA, MIA, PCS)
│   ├── memoria-v2-flavia.md     ← Estrutura de memória da Flávia
│   ├── decisions.md             ← Decisões operacionais permanentes
│   ├── pessoas.md               ← Pessoas-chave (clientes, parceiros, equipe)
│   └── credentials.md           ← Referências de credenciais (não as chaves em si)
│
├── projects/                    ← Contexto por projeto/empresa
│   ├── mensura/                 ← MENSURA Engenharia
│   ├── mia/                     ← MIA Engenharia
│   └── pcs/                     ← PCS Engenharia
│
├── areas/                       ← Contexto por área funcional
│   ├── financeiro/
│   ├── juridico/
│   ├── marketing/
│   └── obras/
│
├── obras/                       ← Obras em execução
│   └── ccsp-casa7/              ← CCSP Casa 7 (prazo: 22/05/2026)
│
├── integrations/                ← Integrações e automações
│
├── sessions/                    ← Resumos de sessões anteriores
│
├── feedback/                    ← Lições aprendidas e ajustes
│
├── 2026-MM-DD.md                ← Diários operacionais (não promovidos)
├── lessons.md                   ← Lições permanentes
├── decisions.md                 ← Log de decisões
├── pending.md                   ← Pendências operacionais
└── urgent_notifications.md      ← Notificações urgentes
```

---

## Mapas de Referência Rápida

| O que preciso saber | Onde está |
|---|---|
| Quais agentes existem e seus papéis | `context/mapa-agentes.md` |
| Quais crons rodam e quando | `context/mapa-crons.md` |
| Máquina de Vendas MENSURA completa | `context/mapa-maquina-vendas-mensura.md` |
| Protocolo LinkedIn + scripts | `context/linkedin-mensura-protocolo.md` |
| Protocolo CFO comercial | `context/maquina-comercial-cfo-protocolo.md` |
| Contexto das empresas (MENSURA/MIA/PCS) | `context/business-context.md` |
| Decisões permanentes da Flávia | `context/decisions.md` |
| Obras em andamento | `obras/` |
| Config HubSpot | `/root/.openclaw/workspace/config/hubspot-mensura.json` |
| Config Phantombuster | `/root/.openclaw/workspace/config/phantombuster-mensura.json` |
| Scripts de automação | `/root/.openclaw/workspace/scripts/` |

---

## Regras de Uso

- **Escreva em `context/`** para decisões e contextos permanentes
- **Escreva em `2026-MM-DD.md`** para notas de sessão e rascunhos do dia
- **Nunca coloque credenciais reais** nos arquivos .md — usar referência ao arquivo de config
- **Commit automático** acontece a cada 2h e às 19:30 BRT — não precisa commitar manualmente a menos que seja urgente
- **Reindexação:** se um agente ficar perdido, pedir para ele ler este README e os 3 mapas de contexto antes de continuar

---

## Status Atual (2026-04-25)

- ✅ Máquina de Vendas MENSURA operacional (HubSpot + Phantombuster + 3 scripts cron)
- ✅ Relatório diário HTML → Telegram grupo Mensura, tópico MKT (thread 43)
- ✅ CCSP Casa 7 em andamento (59% em 24/04, prazo 22/05/2026)
- ✅ Agente Marketing habilitado no tópico MKT
- 🔄 Mission Control — página Vendas Mensura (planejada, spec em `/projects/mission-control/docs/`)
