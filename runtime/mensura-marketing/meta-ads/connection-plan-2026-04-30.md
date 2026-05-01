# Meta Ads MCP/AI Connector — Plano de conexão controlada

_Data: 2026-04-30_

## Decisão operacional solicitada

Alê pediu deixar o Meta Ads conectado com operação ampla por IA, usando limite de orçamento como trava principal.

## Estado atual verificado localmente

- Ainda não há `META_AD_ACCOUNT_ID=act_<id>` validado no runtime seguro.
- Registro anterior indica que os Business Managers verificados apareciam sem contas de anúncio vinculadas.
- Não há token/API/OAuth de Meta Ads validado para operação real neste ambiente.

## Modo recomendado

Conectar em três camadas:

1. **Read-only imediato**
   - analisar campanhas, métricas, públicos, criativos, leads e desperdício.

2. **Write controlado por orçamento**
   - permitir criação/edição/otimização somente dentro do limite aprovado pelo Alê;
   - bloquear qualquer aumento acima do teto;
   - registrar toda ação em log interno.

3. **Travas mínimas obrigatórias**
   - orçamento máximo por dia ou por campanha definido antes de ativar;
   - conta de anúncios correta vinculada ao Business certo;
   - forma de pagamento ativa e conferida;
   - nenhuma campanha sem lead flow/CRM definido;
   - logs de campanha, orçamento e alterações mantidos em `runtime/mensura-marketing/meta-ads/`.

## Bloqueios para conexão 100%

Para ativar de fato, faltam:

1. `META_AD_ACCOUNT_ID` no formato `act_<id>`.
2. Autenticação Meta/OAuth/token com permissões adequadas.
3. Teto de orçamento aprovado pelo Alê:
   - **R$ 0/dia** neste momento;
   - operação permitida: conexão, leitura, diagnóstico, estruturação e preparação;
   - operação bloqueada: ativar campanha, publicar anúncio com gasto, aumentar orçamento ou gerar qualquer despesa.
4. Definição de escopo inicial: MENSURA, MIA ou ambas.

## Regra de segurança

Mesmo com conexão operacional, qualquer gasto acima do teto fica bloqueado. Com teto atual de **R$ 0/dia**, a operação deve permanecer **read-only/preparatória** até nova aprovação explícita de orçamento pelo Alê.
