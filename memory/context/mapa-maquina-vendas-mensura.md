# Mapa Permanente — Máquina de Vendas MENSURA Engenharia

_Criado em 2026-04-25 | Atualizado automaticamente — consulte este arquivo antes de qualquer tarefa comercial da MENSURA_

---

## 1. Tese Central

> "A MENSURA não vende apenas gerenciamento de obras. A MENSURA vende **previsibilidade executiva, controle técnico e governança de decisão** para obras onde prazo, custo, qualidade e risco não podem ser tratados no improviso."

**Posicionamento:** Torre de controle técnico-executivo de obras
**Tom:** técnico-executivo, direto, sóbrio, assertivo, centrado em risco, previsibilidade e governança
**Nunca:** commodity, generalista, "consultor"

---

## 2. Estrutura de Agentes

| Agente | Papel |
|---|---|
| **Flávia / Main / CFO** | Governança da máquina, priorização, controle financeiro, cobrança de resultados, monitor diário |
| **MENSURA** | Domínio técnico-comercial, guardião do posicionamento, oferta, argumentação, proposta |
| **Marketing** | Conteúdo, prospecção, CRM, campanhas, abordagens, follow-up, dossiês, relatórios |
| **Alexandre** | Decisões estratégicas, aprovações externas, responde LinkedIn pessoalmente |

---

## 3. Pipeline HubSpot (10 etapas)

| Etapa | Stage ID HubSpot | Significado |
|---|---|---|
| Lead identificado | `appointmentscheduled` | Encontrado, ainda sem contato |
| Abordagem enviada | `qualifiedtobuy` | Convite LinkedIn enviado |
| Conexão aceita | `1347867818` | Aceito no LinkedIn |
| Resposta recebida | `presentationscheduled` | Respondeu mensagem |
| Reunião agendada | `decisionmakerboughtin` | Call marcada |
| Diagnóstico em andamento | `contractsent` | Call realizada, diagnóstico ativo |
| Proposta enviada | `1347046829` | Proposta formal enviada |
| Negociação | `1347046830` | Em processo de fechamento |
| Fechado — Ganho | `closedwon` | Contrato assinado |
| Fechado — Perdido | `closedlost` | Perdido — registrar motivo |

**Portal:** 51386487 | **Pipeline:** "Pipeline MENSURA" (default)

---

## 4. Integrações e Credenciais

| Sistema | Finalidade | Config |
|---|---|---|
| **HubSpot** | CRM principal — deals, contatos, empresas | `config/hubspot-mensura.json` |
| **Phantombuster** | Automação LinkedIn — 15 convites/dia | `config/phantombuster-mensura.json` |
| **Make.com** | Webhooks de integração | Webhook: `hook.us2.make.com/nriwhmjs0o49p41452nk88wbp66t64k9` |
| **LinkedIn** | Prospecção pessoal do Alexandre | `config/linkedin-mensura.json` |
| **Mensura Commercial Intelligence** | Base versionada de contatos, campanhas, bounces, suppressions e higienização antes de envio/sync | `projects/mensura-commercial-intelligence/` |

### Agentes Phantombuster ativos
| Nome | ID |
|---|---|
| `linkedin_outreach` | 48056734572679 |
| `hubspot_contact_sender` | 5216683853663265 |
| `linkedin_search_export` | 7924684030325022 |

---

## 5. Automações (Scripts Cron)

| Script | Horário | O que faz |
|---|---|---|
| `scripts/monitoramento_comercial_mensura.py` | 08:00 BRT diário | Coleta HubSpot + Phantombuster → relatório CFO no Telegram |
| `scripts/operacional_marketing_mensura.py` | 09:00 BRT seg-sex | Dados operacionais → prompt para agente Marketing |
| `scripts/revisao_tecnica_mensura.py` | 08:30 BRT seg/qui | Revisão de posicionamento → prompt para agente MENSURA |

---

## 6. KPIs Monitorados Diariamente

- Leads novos (24h)
- Contatos qualificados
- Empresas adicionadas ao CRM
- Decisores identificados
- Abordagens enviadas
- Respostas recebidas
- Reuniões agendadas / realizadas
- Diagnósticos em andamento
- Propostas enviadas
- Follow-ups pendentes
- Oportunidades paradas 7+ dias
- Conteúdos publicados
- Interações relevantes LinkedIn
- Objeções / motivos de perda

---

## 7. Protocolo LinkedIn — Prospecção Ativa

- **Volume:** 15 convites/dia para Diretores/CEOs de incorporadoras e construtoras de SP
- **Cadência automatizada:** D+3, D+8, D+15 via Phantombuster
- **Responsável por respostas:** Alexandre (pessoalmente) — Flávia redige o texto
- **Três cenários de resposta:**
  - **A (interesse positivo):** Oferecer pitch de 20 min → link da agenda
  - **B (neutro):** Clarificar o que a MENSURA faz → propor call de 20 min
  - **C (sem timing):** Permanecer disponível → aguardar contexto melhor

### Qualificação em 20 minutos
1. Abertura (2min): limitar a 20min, dar saída se necessário
2. Contexto (5min): quantas obras ativas? Principal desafio operacional? Mede baseline de cronograma?
3. Evidências (5min): casos por tipo de dor (prazo / custo / portfólio)
4. Próximo passo (3min): propor Diagnóstico Executivo de 5 dias
5. Encerramento (2min): enviar proposta / sumário

**Fit signal:** obras >R$5MM, 2+ simultâneas, dificuldade de controle declarada

---

## 8. Formato do Relatório Diário — CFO

```
RELATÓRIO DIÁRIO — MÁQUINA COMERCIAL MENSURA
Data: | Período:

1. Resumo executivo
   Situação geral | Principal avanço | Principal gargalo | Decisão crítica

2. Indicadores do dia
   [tabela com todos os KPIs]

3. Previsto x Realizado
   Atividade | Previsto | Realizado | Desvio | Causa | Ação corretiva

4. Oportunidades prioritárias
   Empresa | Decisor | Etapa | Nota ICP | Próxima ação | Responsável | Prazo

5. Gargalos identificados
   Gargalo | Evidência | Impacto | Causa | Correção

6. Plano de ação 24h
   Ação | Responsável | Prioridade | Prazo | Resultado esperado

7. Feedback de melhoria (3–5 aprendizados)

8. Comandos para MENSURA e Marketing
```

---

## 9. Regras Inegociáveis

- CRM vazio não é normal — cobrar atualização
- Lead sem próxima ação não existe
- Reunião sem objetivo não acontece
- Conteúdo sem CTA não é entrega
- Proposta sem hipótese de dor, valor e próximo passo não é proposta
- Classificar sempre: Alta / Média / Baixa
- Indicar sempre: responsável + prazo
- Nunca inventar métricas — usar dados disponíveis ou marcar "não informado"
- Preservar posicionamento premium, técnico, não comoditizado

---

## 10. Localização de Todos os Arquivos

| Documento | Path |
|---|---|
| **Este mapa** | `memory/context/mapa-maquina-vendas-mensura.md` |
| Protocolo CFO (governança) | `memory/context/maquina-comercial-cfo-protocolo.md` |
| Protocolo LinkedIn | `memory/context/linkedin-mensura-protocolo.md` |
| Apresentação MENSURA | `memory/projects/mensura/apresentacao.md` |
| Contexto de negócio (multi-marca) | `memory/context/business-context.md` |
| Config HubSpot | `config/hubspot-mensura.json` |
| Config Phantombuster | `config/phantombuster-mensura.json` |
| Config LinkedIn | `config/linkedin-mensura.json` |
| Script monitoramento diário | `scripts/monitoramento_comercial_mensura.py` |
| Script operacional marketing | `scripts/operacional_marketing_mensura.py` |
| Script revisão técnica | `scripts/revisao_tecnica_mensura.py` |
| Base comercial versionada | `projects/mensura-commercial-intelligence/MAP.md` |
| SQLite comercial | `projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite` |
| Exports comerciais | `projects/mensura-commercial-intelligence/exports/` |

---

## 11. Mission Control — Página Vendas (em construção)

**Rota:** `/mensura/vendas`
**Abordagem:** API direta (HubSpot ao vivo) + leitura do relatório diário do cron
**Seções planejadas:**
1. KPIs do dia (cards no topo)
2. Pipeline visual (10 etapas HubSpot)
3. Oportunidades ativas (tabela com alertas de deals paradas 7d+)
4. Radar LinkedIn / Phantombuster
5. Último relatório CFO gerado

---

_Fim do mapa — sempre consultar este arquivo antes de qualquer tarefa da Máquina de Vendas MENSURA_
