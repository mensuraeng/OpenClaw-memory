---
name: redator-executivo-obra
description: >
  Transforma informação dispersa em comunicação profissional pronta para envio — sem reescrita.
  Use este skill SEMPRE que o pedido central for escrever, redigir, montar, estruturar ou formatar
  comunicação profissional de obra: e-mail, ata, comunicado, notificação, cobrança, resumo executivo,
  alinhamento com cliente, registro formal, resposta a reclamação, solicitação técnica,
  comunicado de atraso, paralisação, não conformidade, relatório de pendências.
  Acionar também quando outro skill técnico concluiu a análise e o resultado precisa virar mensagem.
  Híbrido análise+comunicação: skill técnico entra primeiro, este skill entra por último.
  Entrega: texto pronto para envio (e-mail, WhatsApp ou documento formal), nível de confiança
  declarado, placeholders sinalizados, versão alternativa quando contexto for ambíguo.
---

# Redator Executivo de Obra v2.0 — MENSURA Engenharia

Transforma informação dispersa em comunicação profissional, objetiva e acionável — pronta para
envio sem reescrita. Calibra tom, formalidade e estrutura conforme destinatário, objetivo e
nível de tensão da situação.

---

## FRONTEIRA DE ATIVAÇÃO

Este skill é o certo quando o núcleo do pedido é **escrever, resumir, organizar ou estruturar
comunicação profissional** — e o usuário já sabe o conteúdo que precisa comunicar.

### Quando este skill entra diretamente

| Pedido | Este skill? |
|--------|-------------|
| "Escreve um e-mail cobrando o cliente" | ✅ Sim |
| "Monta uma ata da reunião de ontem" | ✅ Sim |
| "Preciso de um comunicado de atraso" | ✅ Sim |
| "Resume essa situação para mandar para a diretoria" | ✅ Sim |
| "Manda pelo WhatsApp pro fornecedor" | ✅ Sim — ver Passo 6 |

### Quando outro skill entra primeiro

| Foco central do pedido | Skill correto |
|------------------------|---------------|
| Analisar cronograma, identificar atraso, definir recuperação | control-tower-cronograma |
| Abrir orçamento, medir, conferir quantitativos ou composição | orcamentista-medidor-obras |
| Analisar edital, contrato, proposta, laudo, escopo | analista-tecnico-documentos |
| Gerar relatório preditivo semanal de obra | relatorio-preditivo-obras |

### Pedidos híbridos — regra de sequência

Quando o pedido mistura análise técnica com comunicação:
1. **Skill técnico** entra primeiro — análise, diagnóstico, plano de ação
2. **Este skill** entra por último — transforma a decisão em mensagem pronta

---

## PASSO 1 — Classificar objetivo, destinatário e tensão

### 1.1 Objetivo do texto

| Objetivo | O que define a estrutura |
|----------|--------------------------|
| Informar | Contexto → fato → próximo passo |
| Cobrar | Contexto → pendência → impacto → solicitação + prazo |
| Registrar formalmente | Fato → evidência → consequência declarada |
| Solicitar | Contexto → pedido específico → prazo → quem decide |
| Responder | Referência à mensagem original → posição → encaminhamento |
| Notificar (contratual) | Base contratual → fato → consequência prevista → prazo de cura |
| Alinhar próximos passos | Resumo do acordado → ações → responsáveis → prazos |
| Agradecer / encerrar etapa | Reconhecimento objetivo → próxima fase |

### 1.2 Destinatário e nível de formalidade

| Destinatário | Formalidade padrão | Ajustar quando |
|---|---|---|
| Cliente corporativo / incorporadora | Executivo formal | Relação próxima → técnico objetivo |
| Cliente pessoa física | Técnico objetivo | Tensão alta → executivo formal |
| Projetista / consultoria | Técnico objetivo | Notificação → executivo formal |
| Fornecedor / subempreiteiro | Firme e direto | Inadimplência → formal registrado |
| Equipe interna / obra | Direto e acionável | Comunicado geral → objetivo formal |
| Diretoria / sócios | Executivo conciso | Crise → formal com contexto completo |
| Órgão público / fiscalização | Formal registrado | Sempre — sem exceção |

### 1.3 Nível de tensão da situação

| Nível | Situação típica | Tom resultante |
|-------|-----------------|----------------|
| Baixo | Alinhamento, atualização, agradecimento | Cordial, direto, sem urgência |
| Médio | Cobrança de pendência, solicitação com prazo, atraso comunicado | Firme, factual, sem carga emocional |
| Alto | Inadimplência, atraso grave, não conformidade, conflito de responsabilidade | Formal registrado, factual, sem adjetivos, com base contratual |
| Crítico | Notificação extrajudicial, paralisação, rescisão | Formal máximo — indicar assessoria jurídica |

> ⚠️ **Nível Crítico**: sempre incluir nota explícita recomendando revisão jurídica antes do envio. Nunca suprimir essa nota por brevidade.

### 1.4 Regra de decisão: pedir informação vs. prosseguir

| Situação | Decisão |
|---|---|
| Falta o destinatário | Prosseguir com placeholder [DESTINATÁRIO] — declarar |
| Falta valor ou prazo em cobrança | Pedir — sem eles a cobrança é inócua |
| Falta base contratual em notificação formal | Pedir — sem ela a notificação não tem respaldo |
| Contexto ambíguo | Prosseguir com interpretação mais provável, declarar premissa, oferecer versão alternativa |
| Informações contraditórias | Apontar contradição, pedir esclarecimento antes de redigir |

---

## PASSO 2 — Verificar consistência antes de redigir

| Inconsistência | O que fazer |
|---|---|
| Prazo indicado já passou | Apontar e perguntar se deve ser atualizado — nunca usar prazo vencido sem marcação |
| Cobrança sem valor declarado | Pedir o valor — cobrança sem valor não é cobrança |
| Ata sem participantes | Registrar como "participantes não informados" e sinalizar |
| Notificação sem referência contratual | Sinalizar como fragilidade — sugerir incluir cláusula ou número de contrato |
| Solicitação sem prazo e sem responsável | Completar com placeholder e avisar que o usuário deve preencher |
| Tom solicitado incompatível com a situação | Sinalizar a incompatibilidade e oferecer duas versões |

---

## PASSO 3 — Ajustar formalidade e tom

### Escalas de formalidade

**Executivo formal** — clientes corporativos, diretoria, órgãos, notificações:
- Tratamento: "Prezado [Nome]," / "Prezados Senhores,"
- Sujeito + verbo + objeto, sem ambiguidade
- Sem contrações, sem informalidade, sem gíria
- Fechamento: "Atenciosamente," / "Respeitosamente,"

**Técnico objetivo** — projetistas, consultores, equipe técnica:
- Tratamento: "Olá [Nome]," ou "Caro [Nome],"
- Foco no fato técnico, sem cerimônia excessiva
- Pode usar listas numeradas para itens de ação
- Fechamento: "Att," / "Abraços,"

**Firme e direto** — fornecedores, subempreiteiros, cobrança:
- Sem abertura longa — ir direto ao ponto
- Factual: datas, valores, pendências — sem adjetivos
- Consequência declarada com clareza, sem ameaça velada
- Fechamento: "Aguardo retorno até [data]."

**Direto e acionável** — equipe interna, obra, WhatsApp operacional:
- Sem tratamento formal
- Uma instrução por frase
- Conclusão com o que se espera de quem

### Clichês proibidos (nunca usar)

- "Venho por meio desta comunicar..."
- "Conforme combinado anteriormente..."
- "Qualquer dúvida estou à disposição."
- "Desde já agradeço a atenção."
- "Em tempo, gostaria de informar..."
- "No que tange ao assunto em pauta..."
- "Espero que este e-mail o encontre bem."
- "Certo de vossa compreensão..."
- "Sem mais para o momento..."
- "Atendendo ao solicitado, segue em anexo..."

Substituir por: frase direta que diz o que precisa ser dito.

---

## PASSO 4 — Estruturar o texto

### Estrutura universal

1. **ABERTURA** — 1 frase. Contexto mínimo, sem elogio, sem preâmbulo.
2. **MOTIVO** — 1 parágrafo. O que está sendo comunicado / solicitado / cobrado.
3. **CORPO** — 1 ideia por parágrafo. Máximo 3 parágrafos. Se houver lista, usar marcadores.
4. **ENCAMINHAMENTO** — o que se espera, de quem, até quando.
5. **FECHAMENTO** — 1 linha. Sem clichê.

### Regras de construção

- Primeira frase do e-mail: diz o assunto principal. Não é "Espero que esteja bem."
- Parágrafos: máximo 4 linhas. Se passou de 4, quebrar em dois ou transformar em lista.
- Listas: usar quando há 3 ou mais itens do mesmo tipo. Não listar 2 itens.
- Negrito: apenas para prazo, valor ou ação crítica — máximo 2 por texto.
- Assunto: [OBRA] — [Assunto principal] — [Data ou referência]. Sem artigo no início.

---

## PASSO 5 — Fechar com ação definida

Todo texto deve terminar com pelo menos um dos elementos abaixo:

| Elemento | Quando obrigatório |
|---|---|
| Ação esperada | Sempre — o que o destinatário deve fazer |
| Responsável | Quando há múltiplos destinatários |
| Prazo | Sempre que houver cobrança, solicitação ou notificação |
| Referência de confirmação | Em notificações e registros formais — pedir acuse de recebimento |
| Próxima reunião ou contato | Em alinhamentos e atas |

---

## PASSO 6 — Canal de envio e formatação

### E-mail (padrão executivo)

Estrutura completa com assunto, saudação, corpo, encaminhamento e fechamento.
Entrega pronto para colar no cliente de e-mail.

> **Integração OpenClaw**: quando o usuário confirmar envio, a Flávia despacha via
> **Microsoft Graph API** (conta configurada em `memory/context/credentials.md`).
> Nunca enviar sem confirmação explícita do Alê.

### WhatsApp (canal operacional)

Quando o destinatário for equipe interna, fornecedor ou obras — e o usuário indicar WhatsApp:

**Regras específicas para WhatsApp:**
- Sem saudação formal — começar direto com o assunto
- Parágrafos curtos — máximo 3 linhas cada
- Usar *negrito* para datas e valores críticos (asterisco simples no WhatsApp)
- Sem assinatura corporativa — terminar com nome + função se necessário
- Emojis: apenas 🔴 para urgente / ✅ para confirmado / ⚠️ para atenção — máximo 2
- Cobrança via WhatsApp: tom mais direto que e-mail, mas nunca agressivo
- Versão WhatsApp sempre separada da versão e-mail

> **Integração OpenClaw**: despacho via integração WhatsApp da Flávia.
> Aguardar confirmação do Alê antes de enviar.

### Documento formal (PDF / Word)

Para atas, notificações extrajudiciais, comunicados de paralisação:
- Entregar texto estruturado para o usuário formatar no template da empresa
- Indicar se deve gerar arquivo via skill docx

---

## PASSO 7 — Nível de confiança da saída

| Nível | Critério |
|---|---|
| ALTO | Contexto completo, destinatário identificado, objetivo claro, sem ambiguidade |
| MÉDIO | Contexto parcial, premissas assumidas declaradas, placeholder(s) indicados |
| BAIXO | Informação insuficiente — texto gerado como rascunho base, requer revisão antes do envio |

---

## FORMATO DE ENTREGA

```
NÍVEL DE CONFIANÇA: [Alto / Médio / Baixo]
[Justificativa se Médio ou Baixo — 1 linha]

ASSUNTO: [linha de assunto completa]        ← e-mail / omitir em WhatsApp

[Texto completo pronto para envio]

---
CANAL SUGERIDO: [E-mail / WhatsApp / Documento formal]
NOTAS DE USO (quando aplicável):
- [placeholder que o usuário deve preencher]
- [premissa assumida]
- [versão alternativa disponível se contexto mudar]
```

### Saídas por tipo de documento

| Tipo | Campos obrigatórios na entrega |
|---|---|
| E-mail executivo | Assunto + corpo + encaminhamento |
| E-mail de cobrança | Assunto + referência da pendência + valor/prazo + consequência + solicitação |
| Ata de reunião | Tema + data + participantes + pontos discutidos + deliberações + to-dos com responsável e prazo |
| Comunicado de atraso | Referência contratual + causa + impacto em dias + ação de recuperação + novo prazo previsto |
| Notificação de não conformidade | Descrição do fato + data de ocorrência + base contratual + exigência + prazo de cura |
| Comunicado de paralisação | Causa + data de início + impacto no cronograma + condição para retomada + responsável pela resolução |
| Resumo executivo de reunião | Contexto em 2 linhas + ponto central + pendências + próximo passo |
| Mensagem WhatsApp operacional | Assunto direto + ação esperada + prazo (sem saudação formal) |
| Versão interna vs. externa | Entregar as duas quando o contexto tiver informação sensível que não deve ir ao cliente |

---

## REGRAS INVIOLÁVEIS

1. **Primeira frase diz o assunto.** Nunca começa com cumprimento, contexto histórico ou elogio.
2. **Frases curtas.** Se uma frase tem mais de 25 palavras, quebrar em duas.
3. **Um parágrafo, uma ideia.** Nunca misturar cobrança com atualização no mesmo parágrafo.
4. **Nunca esconder a cobrança.** Se é cobrança, "pendência" ou "prazo" aparece no primeiro parágrafo.
5. **Nunca terminar sem próximo passo.** Todo texto tem encaminhamento.
6. **Clichês são proibidos.** Ver lista no Passo 3.
7. **Nível Crítico:** sempre recomendar revisão jurídica antes do envio — essa nota nunca é suprimida.
8. **Prazo vencido nunca é usado sem marcação** — sempre sinalizar e pedir atualização.
9. **Nunca gerar texto com informação contraditória sem declarar a contradição.**
10. **Contexto ambíguo:** oferecer versão alternativa — nunca suprimir a ambiguidade escolhendo por conta própria.
11. **WhatsApp ≠ e-mail** — sempre entregar versões separadas quando o canal for WhatsApp.
12. **Envio via OpenClaw** (e-mail Graph API ou WhatsApp): sempre aguardar confirmação explícita do Alê antes de despachar.

---

## ARQUIVOS DE REFERÊNCIA

- `references/checklist.md` — checklist pré-envio para qualquer tipo de texto
- `references/modelos.md` — modelos completos por tipo de documento
- `references/regras-tom.md` — tom por destinatário e situação, com exemplos frase boa vs. ruim

## INTEGRAÇÃO COM OUTROS SKILLS

Este skill é o **último da cadeia** em pedidos híbridos:

```
relatorio-preditivo-obras → diagnóstico de atraso → redator-executivo-obra → e-mail/WhatsApp ao cliente
control-tower-cronograma  → plano de recuperação  → redator-executivo-obra → comunicado formal
orcamentista-medidor      → divergência detectada → redator-executivo-obra → notificação ao fornecedor
analista-tecnico-docs     → risco contratual      → redator-executivo-obra → carta de contestação
```
