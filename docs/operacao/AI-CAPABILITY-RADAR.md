# AI Capability Radar — MENSURA / MIA / PCS / OpenClaw

_Atualizado em 2026-04-29_

## Critério

Este radar não é catálogo de tecnologia. É filtro executivo para escolher iniciativas de IA/automação que aumentam capacidade real da operação.

Uma iniciativa só entra como prioridade se cumprir pelo menos 3 critérios:

1. reduz trabalho manual recorrente;
2. melhora decisão operacional;
3. usa dado/fonte que já temos ou conseguimos acessar sem projeto longo;
4. reduz risco fiscal, financeiro, comercial ou operacional;
5. gera evidência auditável;
6. pode ser implantada em até 30 dias em modo interno/read-only.

## Tese

Não precisamos de “mais IA”. Precisamos de mais capacidade operacional confiável.

A ordem correta é:

```text
dado confiável → leitura automática → classificação → evidência → decisão assistida → automação com aprovação
```

## Prioridade 1 — Fiscal Ops Read-only

### Capacidade nova

Detectar notas fiscais emitidas contra MENSURA, MIA e PCS; baixar XML/PDF/DANFE; estruturar metadados; avisar grupo correto sem aprovar pagamento ou aceite.

### Por que muda patamar

Transforma fiscal de processo manual/reativo em radar permanente. Reduz perda de nota, atraso de lançamento, ruído com contador e risco de pagamento sem documento.

### Alavancas técnicas

- DFe.NET para NF-e/NFC-e/CT-e/MDF-e;
- Sistema do Milhão ou portal municipal para NFS-e;
- OCR/LLM apenas como fallback para PDF sem XML;
- JSON normalizado interno.

### Entrega v1

- coletor manual/read-only por empresa;
- parser XML/PDF;
- ledger fiscal local;
- notificação controlada por grupo;
- vínculo futuro com financeiro.

### Status

Em implantação documental. Próximo salto: protótipo de parser + armazenamento local.

## Prioridade 2 — Mission Control Executive Graph

### Capacidade nova

Conectar missão → projetos → tarefas → agentes → documentos → memória → evidência → decisão.

### Por que muda patamar

Hoje existem módulos bons, mas ainda fragmentados. O salto é parar de navegar por arquivos e passar a operar por cockpit executivo.

### Alavancas técnicas

- leitura de `2nd-brain`;
- task board;
- documentos institucionais;
- cron/health;
- evidências runtime;
- busca semântica ou compactação por contexto.

### Entrega v1

- `/projects` executivo;
- `/docs` biblioteca documental;
- tela de projeto com tarefas, últimas evidências, decisões e próximos passos;
- nada de write externo na v1.

### Status

Mission Control já tem `/openclaw`, `/cron`, `/tasks` e base protegida. Próximo salto: `/projects` + `/docs`.

## Prioridade 3 — CRM/CDP Diff + Lead Intelligence

### Capacidade nova

Comparar ledger local de leads com HubSpot/CRM, detectar divergência material, classificar respostas de campanha e sugerir próximo passo comercial.

### Por que muda patamar

Transforma prospecção de disparo pontual em operação comercial com memória, higienização e aprendizado.

### Alavancas técnicas

- ledgers CSV/JSON já existentes;
- classificação de resposta por NLP/LLM;
- scoring simples por ICP, segmento, cargo, engajamento e resposta;
- alerta só por exceção.

### Entrega v1

- rotina read-only local ↔ CRM;
- relatório de divergências;
- classificação automática de respostas;
- lista diária/semanal de ações comerciais sugeridas.

### Status

Implantado v1 read-only em `scripts/mensura_crm_lead_intelligence.py`, com diff local ↔ CRM via snapshot HubSpot, classificação de respostas da campanha e alerta interno em `runtime/data-pipeline/crm/lead-intelligence/`. Próximo salto: transformar em rotina recorrente e conectar ao Mission Control sem writes externos.

## Prioridade 4 — Mensura Schedule/Risk Intelligence

### Capacidade nova

Gerar leitura preditiva de cronograma/custo: risco de atraso, desvio de curva S, frentes críticas e próximos 14/30 dias.

### Por que muda patamar

É o coração da tese MENSURA: obra atrasa por falta de sistema. Isso vira produto, não só controle interno.

### Alavancas técnicas

- cronogramas existentes;
- EVM;
- curva S;
- lookahead;
- regressão/forecast simples antes de ML pesado;
- histórico por obra quando houver.

### Entrega v1

- análise determinística primeiro;
- score de risco por frente;
- resumo executivo;
- recomendação de ação;
- sem prometer previsão probabilística sofisticada antes de base histórica.

### Status

Frente existe. Próximo salto: padronizar dados de entrada e relatório recorrente.

## Prioridade 5 — Document Intelligence para financeiro/obra

### Capacidade nova

Ler documentos recebidos — notas, boletos, comprovantes, medições, propostas, contratos — e extrair campos úteis com trilha de evidência.

### Por que muda patamar

Reduz dependência de leitura manual e cria ponte entre documento, financeiro, obra e decisão.

### Alavancas técnicas

- OCR/LLM;
- schemas por tipo documental;
- validação humana antes de qualquer lançamento;
- armazenamento por empresa/projeto.

### Entrega v1

- classificador de tipo documental;
- extração estruturada;
- score de confiança;
- fila de revisão;
- sem escrita automática em sistemas externos.

### Status

Útil, mas deve vir depois do Fiscal Ops read-only e CRM/CDP diff.

## O que não entra agora

- treinar modelo próprio do zero;
- integrar catálogos genéricos de projetos de IA;
- AutoML sem dado consolidado;
- visão computacional complexa sem caso de uso imediato;
- emissão fiscal automática;
- escrita automática em CRM, Sienge, banco, SEFAZ ou portal municipal.

## Sequência recomendada de implantação

### Sprint 1 — 7 dias

1. Fiscal Ops parser v0: XML/PDF → JSON normalizado.
2. CRM/CDP diff v0: ledger local x CRM com divergências.
3. Mission Control `/projects` escopo e primeira tela read-only.

### Sprint 2 — 14 dias

1. Fiscal Ops notificação controlada por grupo.
2. CRM resposta/classificação comercial.
3. Mission Control `/docs` com documentos institucionais por empresa.

### Sprint 3 — 30 dias

1. Mensura schedule/risk intelligence v0.
2. Document Intelligence fila de revisão.
3. Integração de evidências por projeto no Mission Control.

## Decisão executiva

O maior ganho de patamar vem de três frentes em paralelo controlado:

1. **Fiscal Ops Read-only** — reduz risco e trabalho recorrente.
2. **Mission Control Executive Graph** — aumenta comando da operação inteira.
3. **CRM/CDP + Lead Intelligence** — transforma comercial em máquina com memória.

Não começar com ML sofisticado. Começar com automação confiável, classificação estruturada e evidência.
