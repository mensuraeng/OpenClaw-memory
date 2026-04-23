# Padrão de triagem de e-mails e documentos financeiros

_Atualizado em 2026-04-20_

## Objetivo
Estabelecer o padrão operacional para tratar e-mails recebidos, classificar o assunto, extrair o que importa, guardar no local correto e transformar anexos financeiros em controle utilizável.

## Regra-mãe
Sempre que chegar e-mail relevante:
1. identificar a frente responsável
2. classificar o tipo do assunto
3. extrair ação, prazo, valor e documento
4. guardar no local respectivo
5. consolidar o que vira controle operacional

## Classificação padrão
### 1. Financeiro
Entram aqui:
- nota fiscal
- boleto
- cobrança
- comprovante
- romaneio com itens pagáveis
- vencimento
- contas a pagar
- contas a receber
- baixa
- reembolso

### 2. Documental durável
Entram aqui:
- apresentação institucional
- cartão CNPJ
- ficha cadastral
- contrato-base
- certidão
- documento societário
- ART
- licenças e equivalentes

### 3. Operacional
Entram aqui:
- pedido de ação
- follow-up
- pendência com prazo
- alinhamento de obra
- contratação
- decisão executiva

### 4. Ruído
Entram aqui:
- newsletter
- propaganda
- cold email
- aviso automático sem ação
- duplicata sem valor novo

## Destino por tipo
### Financeiro
- consolidar em planilha/controle quando houver pagamento, cobrança ou programação
- separar `a pagar` e `a receber`
- extrair: emissor, valor, data de emissão, vencimento, forma de pagamento, banco, agência, conta, pix, linha digitável, comprovante, status
- quando houver comprovante, atualizar o controle marcando como pago/recebido

### Documental durável
- guardar na memória da entidade correspondente em `memory/projects/`
- atualizar índice documental e resumo reutilizável

### Operacional
- registrar como ação, pendência, decisão ou contexto de trabalho na frente correta

### Ruído
- não poluir memória estrutural
- só registrar se houver valor estratégico claro

## Regra de roteamento por frente
- MIA → `memory/projects/mia/`
- MENSURA → `memory/projects/mensura/`
- PCS → `memory/projects/pcs/`
- pessoal do Alê → `memory/projects/pessoal-ale/`
- financeiro transversal / controles → controles e artefatos financeiros correspondentes

## Regra financeira prática
### A pagar
Entram pagamentos a fornecedores, prestadores, boletos, NFs recebidas e cobranças contra a operação.

### A receber
Entram notas emitidas pela própria empresa, cobranças ativas, recebíveis e comprovantes de entrada.

### Campos mínimos do controle
- tipo do documento
- fornecedor / cliente
- CNPJ / CPF
- número do documento
- data de emissão
- vencimento
- valor bruto
- valor líquido
- forma de pagamento
- dados bancários
- linha digitável
- status
- pago em / recebido em
- comprovante
- observações

## Regra de atualização
- e-mail novo com documento novo → incluir no controle
- comprovante novo → atualizar linha existente
- informação complementar → enriquecer a linha já existente, não duplicar
- vencimento sem dados suficientes → marcar pendente de confirmação

## Regra de resposta
Quando útil ao usuário, devolver:
- resumo curto do assunto
- tabela consolidada
- Excel atualizado
- alerta de prazo, risco ou inconsistência

## Princípios
- não inventar dado ausente
- marcar pendência explicitamente
- separar documento pagável de documento apenas informativo
- diferenciar claramente `a pagar` e `a receber`
- guardar cada item no local certo, sem poluir memória errada
