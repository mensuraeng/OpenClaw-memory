# Roadmap de implantação - emissão fiscal MIA e MENSURA

_Atualizado em 2026-04-20_

## Objetivo
Implantar uma frente operacional única para emissão fiscal eletrônica da MIA Engenharia e da MENSURA, começando com padronização, rastreabilidade e emissão assistida, e evoluindo para integração com financeiro e cobrança.

## Princípios
- não automatizar emissão sem validar regra fiscal e operacional
- padronizar antes de integrar
- guardar PDF, XML e metadados estruturados
- ligar emissão ao contas a receber
- manter aprovação humana nas fases iniciais

## Escopo
- NFS-e, quando o município e a operação forem de serviço
- NF-e, quando houver operação sujeita à emissão estadual
- organização documental por empresa
- integração futura com cobrança e conciliação

## Situação conhecida hoje
### MIA
- empresa em São Paulo/SP
- regime declarado em ficha institucional: Simples Nacional
- possui CCM: 7.710.305-0
- possui credenciamento como emissor de NF-e desde 26/05/2023
- conta operacional na XP já mapeada para financeiro

### MENSURA
- documentação institucional já existe na memória, mas a trilha de emissão fiscal ainda precisa ser consolidada
- houve recebimento de DAS, o que indica necessidade de trilha fiscal/financeira mais estruturada

### Processo atual comum às duas empresas
- emissão hoje é manual
- sistema utilizado: Sistema do Milhão
- isso indica que a implantação deve começar por padronização operacional em torno do emissor atual, e não por tentativa prematura de trocar o emissor

## Arquitetura-alvo
1. cadastro fiscal base por empresa
2. biblioteca de tipos de emissão
3. checklist operacional pré-emissão
4. emissão assistida no canal/sistema correto
5. armazenamento automático de PDF + XML + resumo estruturado
6. criação/atualização de recebível
7. acompanhamento até recebimento

## Fase 1 - diagnóstico fiscal-operacional
### Meta
Entender exatamente como cada empresa emite hoje.

### Levantamento por empresa
- município de emissão da NFS-e
- se emite NFS-e, NF-e ou ambos
- sistema atual de emissão
- certificado digital A1 ou A3
- responsável atual pela emissão
- tipos recorrentes de nota
- natureza das operações mais comuns
- retenções e alíquotas recorrentes
- regras de aprovação
- destino atual de XML e PDF

### Entregáveis
- ficha de emissão MIA
- ficha de emissão MENSURA
- mapa de gargalos
- decisão da trilha técnica por empresa

## Fase 2 - padronização
### Meta
Parar de emitir cada nota do zero.

### Construir
- cadastro base por empresa
- cadastro de tomadores recorrentes
- modelos por tipo de serviço/produto
- biblioteca de descrições fiscais recorrentes
- tabela de retenções e observações padrão
- convenção de nomenclatura para XML/PDF
- estrutura de pastas e memória

### Entregáveis
- playbook operacional
- dados-base reutilizáveis
- checklist único por empresa

## Fase 3 - emissão assistida
### Meta
Operar emissão com baixa fricção e rastreabilidade.

### Fluxo desejado
1. selecionar empresa
2. selecionar cliente/tomador
3. selecionar tipo de emissão
4. sugerir campos recorrentes
5. validar impostos/retenções
6. aprovar
7. emitir
8. salvar PDF/XML
9. registrar resumo estruturado
10. abrir/atualizar recebível

## Fase 4 - integração com financeiro
### Meta
Fazer a emissão virar evento financeiro estruturado.

### Saídas automáticas desejadas
- criação de título a receber
- valor
- cliente
- vencimento
- status
- comprovantes/documentos vinculados
- alerta de inadimplência
- baixa quando houver recebimento

## Fase 5 - automação avançada
### Possíveis evoluções
- emissão a partir de contrato ou medição aprovada
- envio automático ao cliente
- follow-up de cobrança
- dashboard de faturamento e recebimento

## Ordem recomendada
1. consolidar dados fiscais base das duas empresas
2. mapear emissão atual real
3. padronizar modelos e cadastros
4. provar emissão assistida em 1 fluxo por empresa
5. conectar financeiro
6. só depois ampliar automação

## Critério de sucesso da primeira implantação
- uma operação real de emissão mapeada por empresa
- um cadastro fiscal base completo por empresa
- um padrão de armazenamento de XML/PDF definido
- um fluxo assistido definido e reproduzível
