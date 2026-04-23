# Plano de integração XP - MIA

_Atualizado em 2026-04-20_

## Objetivo inicial
Começar pela integração da XP da MIA em modo seguro e incremental.

## Escopo Fase 1
### Obrigatório
- leitura de saldo
- leitura de extrato
- leitura de transações
- identificação de pagamento realizado
- conciliação com controle local

### Desejável
- leitura de comprovantes
- leitura de metadados de Pix/transferência

## Escopo Fase 2
### Somente se suportado
- preparação de pagamento
- proposta de pagamento em chat
- aprovação explícita do Alê
- execução assistida
- baixa automática no controle

## Arquitetura sugerida
1. Conector XP
   - autentica
   - consulta endpoints permitidos
   - normaliza dados
2. Camada financeira local
   - cruza extrato com planilha/documentos
   - marca status: pendente, pago, inconsistente
3. Camada de aprovação
   - mostra proposta de pagamento
   - aguarda aprovação explícita
4. Auditoria operacional
   - registra id da transação
   - registra horário
   - registra comprovante quando disponível

## Critério de sucesso da Fase 1
A integração consegue provar:
- saldo lido com sucesso
- extrato carregado
- ao menos um pagamento conciliado com o controle local

## Critério de sucesso da Fase 2
A integração consegue:
- montar uma proposta de pagamento correta
- aguardar aprovação humana
- executar somente após aprovação
- registrar comprovante
