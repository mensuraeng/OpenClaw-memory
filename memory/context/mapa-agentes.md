# Mapa de Agentes — Ecossistema OpenClaw

_Atualizado: 2026-04-28 | Consultar antes de acionar ou criar agentes_

---

## Regra principal

Não renomear agentes. A arquitetura nova é funcional, não cosmética.

Agentes ativos de referência:
- `main` — Flávia
- `finance`
- `mensura`
- `mia`
- `pcs`
- `trade`

Frentes como Growth/Marketing/Authority são **funções operacionais**, não exigem agente novo até haver necessidade real.

---

## Agentes ativos

| ID | Nome/Persona | Papel funcional | Canal principal |
|---|---|---|---|
| `main` | Flávia | COO/CoS digital, orquestração, WORKING queue, health, memória, decisão e consolidação externa | Telegram DM Alê |
| `finance` | Finance | Financeiro, comprovantes, contas, fluxo, conciliação e fiscal | Grupo Finance |
| `mensura` | Mensura | Operação técnica/comercial MENSURA: cronograma, prazo, risco, CAPEX, medição, controle executivo e Growth técnico | Grupo Mensura |
| `mia` | MIA | Obras premium, pré-construção, cliente alto padrão, comunicação e governança MIA | Grupo MIA |
| `pcs` | PCS | Licitações, obras públicas, Sienge, SPObras, contratos, patrimônio/restauro | Grupo PCS |
| `trade` | Trade | Projeto pessoal do Alê: mercado, carteira, radar, ouro, notícias, Strategy Lab e Risk Gate | Grupo Investimento / DM via Flávia |

---

## Agentes legados / não canônicos nesta fase

Os IDs abaixo podem existir em histórico, allowlist, sessões ou arquivos antigos, mas **não devem ser tratados como topologia ativa sem validar config/runtime atual**:

- `marketing`
- `autopilot`
- `juridico`
- `bi`
- `producao`
- `rh`
- `suprimentos`
- `pessoal`
- aliases como `mkt`

Regra: antes de responder sobre organograma ou capacidade operacional, validar estado real com `agents_list`, config/runtime ou mapa no 2nd-brain.

---

## Hierarquia funcional

```text
Alexandre — decisão estratégica e aprovação de alto risco
    │
    ▼
Flávia / main — COO digital e camada central de decisão
    ├── finance — financeiro e conciliação
    ├── mensura — MENSURA técnico/comercial/obras
    ├── mia — MIA premium/pré-construção/obra
    ├── pcs — PCS licitações/Sienge/obras públicas
    └── trade — investimentos pessoais/mercado
```

---

## Funções transversais sem criar agente novo

| Função | Onde mora inicialmente | Quando virar agente separado |
|---|---|---|
| Growth / Marketing | Flávia + Mensura/MIA conforme frente | quando houver volume recorrente de campanhas, CRM, ads e conteúdo exigindo executor próprio |
| Authority / Conteúdo | Flávia + Mensura/MIA/PCS | quando pipeline de transcrição→post→artigo→carrossel estiver recorrente |
| Lead enrichment | runtime/data-pipeline + HubSpot/Phantombuster | quando houver uso intensivo de Apollo/Clay/Hunter/Meta/LinkedIn com custo mensurável |
| QA operacional | Flávia + checklist QA | quando implementação por subagente ficar frequente |

---

## Sistema Operacional 10/10

Artefatos canônicos:

- Projeto: `/root/2nd-brain/04-projects/openclaw-sistema-operacional-10x.md`
- WORKING Flávia: `/root/2nd-brain/06-agents/flavia/WORKING.md`
- Organograma funcional: `/root/.openclaw/workspace/docs/operacao/ORGANOGRAMA-FUNCIONAL-AGENTES.md`
- Matriz de autoridade: `/root/.openclaw/workspace/docs/operacao/MATRIZ-DE-AUTORIDADE-INTEGRACOES.md`
- Regras de dados: `/root/.openclaw/workspace/docs/operacao/REGRAS-DE-DADOS-E-CONFIANCA.md`
- Loops: `/root/.openclaw/workspace/docs/operacao/OPERATING-LOOPS.md`
- Pipeline: `/root/.openclaw/workspace/docs/operacao/PIPELINE-DE-DADOS-OPERACIONAL.md`
- Usage ledger: `/root/.openclaw/workspace/docs/operacao/USAGE-LEDGER.md`
- Backlog leve: `/root/.openclaw/workspace/docs/operacao/BACKLOG-LEVE.md`

---

## Loops obrigatórios

Todo agente deve respeitar:

```text
sinal real → classificar → vincular entidade/tarefa → agir com autoridade correta → registrar evidência → acompanhar até fechar → salvar lição se houver aprendizado
```

## Autoridade

- Read é padrão.
- Write externo exige aprovação explícita do Alê, salvo exceção formalizada.
- Delete permanente exige aprovação; usar `.trash/`/quarentena quando possível.
- Segredos devem migrar para KeeSpace/KeePassXC; docs/memória não guardam token.
- Dados executivos precisam de fonte, janela, método, confiança e risco de erro.

## Segredos / KeeSpace

Mapa obrigatório para qualquer agente que precise entender credenciais:

- Protocolo operacional: `/root/.openclaw/workspace/docs/operacao/KEESPACE-SECRETS-PROTOCOL.md`
- Mapa de credenciais: `/root/.openclaw/workspace/memory/integrations/credentials-map.md`
- Vault local existente: `/root/.secrets/flavia-vault.kdbx`
- Resolver canônico: `/root/.openclaw/workspace/scripts/secret_config.py`

Regra: agente nunca deve procurar token/API key em conversa, memória ou Git. Deve procurar referência no mapa, resolver via `secret_config.py`/env/KeeSpace, ou pedir desbloqueio do cofre se estiver inacessível.

## Subagentes

Subagente só vale se aumentar precisão, cobertura, velocidade, confiabilidade ou capacidade de teste.

Nunca fire-and-forget:
1. escopo claro;
2. evidência;
3. validação;
4. fechamento;
5. memória se houver decisão/lição.

---

## Grupos Telegram

| Grupo | ID | Agente/Função | Tópicos |
|---|---|---|---|
| MENSURA Engenharia | `-1003366344184` | `mensura`; MKT como função no tópico 43 | 1 = Geral, 43 = MKT |
| Finance | `-1003818163425` | `finance` | 13 = Finance |
| MIA | `-1003704703669` | `mia` | 1 = Geral |
| PCS | `-1003146152550` | `pcs` | 1 = Geral |
| Investimento | `-1003794434256` | `trade` | 1 = Notícias |

---

## Referências

- Mapas por agente: `/root/2nd-brain/06-agents/<agent>/AGENT-MAP.md`
- Projeto 10/10: `/root/2nd-brain/04-projects/openclaw-sistema-operacional-10x.md`
- Regra operacional central: `/root/.openclaw/workspace/AGENTS.md`
