# Financeiro MIA — conciliação operacional

_Atualizado em 2026-04-22_

## Objetivo

Este arquivo é a base operacional de conciliação financeira da MIA.

Ele não substitui o histórico bruto de comprovantes.
Ele existe para cruzar:
- comprovantes de pagamento
- romaneio de notas
- notas/documentos de suporte
- status consolidado por item

## Estrutura de uso

### 1. Histórico bruto
Fonte principal:
- `memory/projects/mia/comprovantes-pagamento.md`

Função:
- preservar cada comprovante recebido
- não apagar histórico anterior
- não forçar vínculo prematuro com obra ou nota

### 2. Base de confronto
Entradas esperadas:
- romaneio de notas
- notas fiscais
- planilhas de apoio
- lançamentos ou centros de custo quando existirem

Função:
- oferecer evidência para cruzamento
- permitir validação por fornecedor, CNPJ, valor, data e referência

### 3. Status consolidado
Status válidos:
- `pago`
- `pendente`
- `parcial`
- `ambíguo`

Regra:
- só sobe para status consolidado quando houver base mínima de confronto
- comprovante isolado não basta para atrelar gasto a obra específica

## Quadro consolidado atual

| Referência | Fornecedor | Valor documento | Valor pago | Data | Status | Evidência atual | Observação |
|---|---|---:|---:|---|---|---|---|
| 2026-04-22 / comprovante 7 Oliveiras | 7 OLIVEIRAS COM CONSTRUC LTDA | R$ 1.087,69 | R$ 1.110,16 | 22/04/2026 20:24 | ambíguo | comprovante bancário isolado | Pagamento confirmado, mas ainda sem romaneio/nota para conciliação definitiva. |

## Próximo gatilho operacional

Quando o Alê enviar o romaneio:
1. cruzar com `comprovantes-pagamento.md`
2. criar/atualizar linhas neste quadro
3. consolidar status por item
4. manter observação explícita quando houver dúvida ou vínculo incompleto

## Regra de integridade

- não apagar histórico bruto
- não reclassificar item sem evidência nova
- não assumir obra específica só por contexto solto
- se houver conflito entre comprovante e romaneio, marcar `ambíguo` até resolução
