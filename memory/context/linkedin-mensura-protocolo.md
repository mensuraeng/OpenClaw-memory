# LinkedIn MENSURA — Protocolo Operacional da Flávia

_Criado em 2026-04-24_

## Contexto

O LinkedIn do Alexandre (conta principal) está com prospecção ativa via Phantombuster:
- 15 convites/dia útil para Diretores/CEOs de incorporadoras e construtoras SP
- Cadência automática: D+3, D+8, D+15
- Make.com sincroniza eventos → HubSpot Pipeline MENSURA

**Função da Flávia:** quando um lead responder no LinkedIn, redigir a resposta correta e encaminhar ao Alexandre para envio.

---

## Gatilhos que ativam este protocolo

Quando o Alexandre disser:
- "lead respondeu no LinkedIn"
- "alguém aceitou a conexão e mandou mensagem"
- "o que respondo para [Nome] da [Empresa]"
- Qualquer mensagem com print ou texto de resposta recebida no LinkedIn

---

## Identificar o cenário e escolher o script

### Cenário A — Resposta positiva ("interesse, pode falar mais?")

> [Nome], obrigado pelo retorno.
>
> Em 20 minutos consigo mostrar como fazemos o controle de prazo e CAPEX para empresas no perfil da [Empresa] — sem apresentação genérica, direto no que é relevante para vocês.
>
> Tenho disponibilidade terça ou quarta desta semana. Qual horário funciona melhor?
> Se preferir, aqui está meu Calendly: calendly.com/alexandre-mensuraengenharia

---

### Cenário B — Resposta neutra ("o que vocês fazem exatamente?")

> [Nome], boa pergunta — vou ser direto.
>
> A MENSURA atua como PMO externo para obras de capital relevante. Entregamos três coisas: previsibilidade de prazo (PPC semanal auditável), controle de CAPEX (EAC com precisão de ±3%) e visão consolidada de portfólio para quem tem 2+ obras simultâneas.
>
> Não é consultoria. É operação — com ritos quinzenais, dashboards executivos e métricas que você apresenta para sócio ou investidor.
>
> Vale uma conversa de 20 minutos para ver se faz sentido para a [Empresa]?

---

### Cenário C — Resposta negativa ("não é o momento")

> [Nome], entendo — timing é tudo nesse tipo de decisão.
>
> Fico à disposição quando o contexto mudar. Se surgir uma obra com prazo apertado ou desvio de orçamento que precise de controle rápido, pode me chamar diretamente.

---

## Roteiro de Qualificação — Primeira Ligação (20 min)

**Objetivo:** confirmar fit, identificar dor principal, propor Diagnóstico Executivo.

### Abertura (2 min)
> "[Nome], obrigado pelo tempo. Vou ser objetivo — tenho 20 minutos preparados, mas se em 10 você sentir que não faz sentido, me diz e encerramos sem problema."

### Bloco 1 — Entender o contexto (5 min)

1. *"Quantas obras vocês têm ativas hoje?"*
2. *"Qual é o maior desafio operacional agora — prazo, custo ou visibilidade de portfólio?"*
3. *"Vocês têm baseline de cronograma formalizado? Conseguem medir desvio semana a semana?"*

**Sinal de fit:** obra acima de R$5MM, 2+ obras simultâneas, dificuldade de controle declarada.
**Sinal de desqualificação:** obra única pequena, equipe interna de PMO consolidada.

### Bloco 2 — Apresentar evidência (5 min)

| Se a dor for... | Use este caso |
|---|---|
| Prazo | *"Tivemos uma obra com PPC de 42%. Em 12 semanas chegamos a 75%. O que mudou foi o método, não a equipe."* |
| Custo | *"Orçamento de R$80MM com 22% de desvio. Fechamos com precisão de ±3% usando EAC quinzenal."* |
| Portfólio | *"5 obras descentralizadas, diretoria sem visão consolidada. Um dashboard Power BI — toda segunda o CEO via o status real de tudo."* |

### Bloco 3 — Propor próximo passo (3 min)

> *"O que faz sentido como próximo passo é um Diagnóstico Executivo de Previsibilidade — 5 dias úteis, entrego um relatório com a situação real da obra: prazo, custo, produtividade e top 3 riscos com recomendação de ação."*
>
> *"Você teria acesso ao cronograma atual e ao orçamento para a gente trabalhar?"*

### Fechamento (2 min)

Se sim: *"Perfeito. Vou te mandar uma proposta de escopo ainda hoje. Prefere receber por email ou WhatsApp?"*

Se hesitar: *"Posso te mandar um resumo de como funciona o diagnóstico para você avaliar com calma — leva 2 minutos ler. Faz sentido?"*

---

## Atualizar HubSpot após cada resposta

Quando redigir uma resposta, sempre orientar o Alexandre a:
1. Abrir o contato no HubSpot
2. Mover o deal para o estágio correto:
   - Respondeu positivo → **Resposta recebida** → depois **Reunião agendada**
   - Respondeu neutro → **Resposta recebida**
   - Respondeu negativo → **Fechado — Perdido** (motivo: Timing)
3. Adicionar nota com resumo da conversa

---

## Referências

- Config HubSpot: `/root/.openclaw/workspace/config/hubspot-mensura.json`
- Radar de empresas: `/root/.openclaw/workspace-mensura/memory/comercial/base-comercial-mensura.md`
- Fluxo comercial: `/root/.openclaw/workspace-mensura/memory/comercial/fluxo-comercial-operacional.md`
