# Meta Ads — Diagnóstico Mensura/MIA

## Objetivo
Usar Meta Ads inicialmente em modo **read-only** para melhorar marketing e conversão de novos clientes.

## Skill adotada
- `skills/openclaw-meta-ads`
- Uso inicial: auditoria, insights, campanhas, conjuntos, anúncios, criativos, formulários e leads.

## Política operacional
- Começar por leitura/análise.
- Não criar, pausar, ativar, editar orçamento, editar campanha, editar criativo ou mexer em público sem aprovação explícita do Alê.
- Não salvar tokens em arquivos rastreados, docs, memória ou mensagens.
- Usar token com menor escopo possível: preferencialmente `ads_read` para diagnóstico inicial.

## Variáveis esperadas no runtime seguro
- `META_ADS_API_KEY` ou bearer token equivalente.
- `META_AD_ACCOUNT_ID` em formato `act_<id>`.

## Primeiro diagnóstico 10/10
Quando o acesso estiver disponível, levantar:
1. Conta: gasto, impressões, alcance, cliques, leads e custo por resultado nos últimos 30 dias.
2. Campanhas ativas: objetivo, status, gasto, resultados, CPL/CPA, CTR, frequência.
3. Conjuntos: público, posicionamentos, orçamento, gasto, resultado, sinais de underdelivery.
4. Anúncios/criativos: CTR, frequência, fadiga, diferença entre criativos.
5. Leads: volume por formulário/campanha e aderência ao CRM/pipeline.
6. Recomendações: separar achados em problema claro, causa provável, próxima checagem e mudança que exigiria aprovação.

## Saída esperada
Relatório executivo curto em `runtime/mensura-marketing/meta-ads/`, com:
- 3 a 5 principais achados;
- desperdícios prováveis;
- gargalos de conversão;
- hipóteses de melhoria;
- ações que podem ser feitas sem risco;
- ações que exigem aprovação do Alê.
