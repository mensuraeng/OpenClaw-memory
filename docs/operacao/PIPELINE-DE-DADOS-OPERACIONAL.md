# Pipeline de Dados Operacional

_Atualizado em 2026-04-28_

## Objetivo

Evitar que dado bruto vire ação. Todo sinal relevante passa por estágios antes de CRM, financeiro, obra ou alerta executivo.

## Fluxo padrão

```text
raw/staging → enriched → verified → system of record → action/outreach → archive
```

## Diretórios runtime

```text
runtime/data-pipeline/
├── staging/     # dado bruto recém-capturado
├── enriched/    # dado enriquecido, ainda não validado
├── verified/    # pronto para sistema de registro
├── rejected/    # descartado com motivo
├── crm/         # payloads prontos/registrados no CRM
├── outreach/    # payloads de abordagem, sempre com aprovação quando externo
└── archive/     # histórico fechado
```

## Regras por tipo

### Lead comercial

```text
lead bruto → staging
→ deduplicar domínio/empresa/contato
→ enriquecer cargo/empresa/canal
→ verificar e-mail/LinkedIn
→ CRM/HubSpot
→ sugestão de abordagem
→ envio só com política/aprovação
```

### Comprovante financeiro

```text
imagem/documento → staging
→ extrair metadados
→ verificar pagador/favorecido/valor/data
→ vincular empresa/obra/centro de custo
→ conciliação
→ archive
```

### E-mail operacional

```text
e-mail → staging implícito
→ classificar prioridade/natureza
→ vincular entidade: obra, lead, financeiro, contrato
→ criar/atualizar WORKING se exigir ação
→ alerta somente se gerencial
```

### Documento de obra

```text
documento → staging
→ identificar obra/projeto
→ extrair datas/marcos/risco
→ verificar consistência
→ atualizar objeto operacional
→ gerar tarefa/alerta se necessário
```

## Critérios para mover de estágio

### staging → enriched
- origem conhecida;
- arquivo/id preservado;
- nenhum segredo exposto;
- parsing inicial feito.

### enriched → verified
- deduplicação feita;
- campos mínimos presentes;
- confiança declarada;
- exceções conhecidas checadas.

### verified → system of record
- sistema correto definido: HubSpot, Supabase, 2nd-brain, financeiro, Mission Control;
- write autorizado pela matriz;
- payload salvo antes do envio.

## Campos mínimos de registro

```json
{
  "id": "",
  "kind": "lead|comprovante|email|documento|obra|campanha",
  "source": "",
  "created_at": "",
  "status": "staging|enriched|verified|rejected|archived",
  "entity": "",
  "confidence": "alta|media|baixa",
  "next_step": "",
  "owner": "",
  "evidence": []
}
```
