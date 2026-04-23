# Playbook operacional - emissão fiscal via Sistema do Milhão

_Atualizado em 2026-04-20_

## Escopo
Playbook inicial para MIA e MENSURA, ambas com emissão manual via Sistema do Milhão.

## Objetivo
Padronizar a emissão antes de automatizar qualquer etapa mais sensível.

## Fluxo operacional-alvo
1. receber solicitação de emissão
2. identificar empresa emissora: MIA ou MENSURA
3. identificar cliente/tomador
4. confirmar tipo de nota aplicável
5. preencher dados da operação
6. revisar retenções, descrição e valores
7. emitir no Sistema do Milhão
8. salvar PDF e XML
9. registrar resumo estruturado
10. abrir ou atualizar contas a receber

## Campos mínimos de pré-emissão
- empresa emissora
- cliente/tomador
- CNPJ/CPF do tomador
- serviço ou operação
- data de competência
- valor
- vencimento
- retenções
- centro de custo / obra, se aplicável
- observações padrão

## Regras iniciais
- não emitir sem empresa emissora definida
- não emitir sem tomador validado
- salvar PDF e XML sempre que disponíveis
- registrar a nota emitida em trilha estruturada
- vincular emissão ao financeiro

## Próximo nível de implantação
Depois do playbook consolidado, criar:
- formulário de pré-emissão
- biblioteca de textos padrão
- cadastro de tomadores recorrentes
- integração da nota com contas a receber
