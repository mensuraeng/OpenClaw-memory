# Operating Loops — Flávia 10/10

_Atualizado em 2026-04-28_

## Loop-mãe

```text
Sinal → Classificação → Objeto/Tarefa → Ação controlada → Evidência → Follow-up → Fechamento
```

Nenhum relatório é considerado útil se não gerar pelo menos um destes efeitos:
- decisão;
- tarefa;
- alerta;
- registro;
- recomendação;
- fechamento explícito;
- confirmação de normalidade com evidência.

## Loop 1 — E-mail executivo

```text
email → classificar → vincular a empresa/obra/lead/financeiro → criar/atualizar WORKING se exigir ação → alertar só se gerencial → registrar evidência
```

## Loop 2 — Comprovante financeiro

```text
comprovante → extrair metadados → salvar arquivo → criar JSON → sugerir categoria → conciliar centro de custo → fechar pendência
```

## Loop 3 — Comercial / lead

```text
lead/resposta/campanha → classificar intenção → atualizar funil/pendência → sugerir resposta → aprovar antes de envio externo → registrar follow-up
```

## Loop 4 — Obra / cronograma / risco

```text
documento/RDO/cronograma/email → identificar obra → extrair status → detectar risco → criar tarefa ou alerta → acompanhar até evidência de fechamento
```

## Loop 5 — Integração / automação

```text
cron/script/API → health check → sucesso/falha → evidência → retry controlado ou alerta → lição se padrão novo
```

## Loop 6 — Melhoria operacional / software

```text
sinal recorrente → mini-PRD → aprovação → implementação em branch/artefato → QA separado → documentação → monitoramento
```

## Escalonamento

Avisar Alê apenas quando houver:
- decisão necessária;
- risco financeiro/jurídico/reputacional;
- bloqueio externo;
- falha operacional relevante;
- conclusão importante;
- oportunidade comercial concreta.
