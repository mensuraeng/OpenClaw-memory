# Meta Ads — Estrutura pronta para campanhas MENSURA/MIA

_Atualizado em 2026-04-28_

## Situação atual

- Nenhum Business Manager verificado possui conta de anúncios vinculada:
  - Alê Aguiar: 0 contas
  - Best Wind Atins: 0 contas
  - MIA Engenharia: 0 contas
  - Mensura Engenharia: 0 contas
- Provável: ainda não há campanha ativa, ou eventual conta de anúncio é pessoal/legada.
- Objetivo agora: deixar a fundação correta antes de investir mídia.

## Decisão recomendada

Não começar campanha em conta pessoal solta.

Criar ou vincular a conta de anúncios ao Business correto antes de rodar verba:
- campanhas MENSURA → Business `Mensura Engenharia` (`1736670143049009`)
- campanhas MIA → Business `MIA Engenharia` (`819868261690628`)
- PCS só entra depois, se houver estratégia específica.

## Estrutura mínima antes da primeira campanha

### 1. Conta de anúncios

Para cada frente que for anunciar:
- Business correto dono da conta;
- conta de anúncio vinculada ao Business;
- forma de pagamento ativa;
- fuso horário Brasil/São Paulo;
- moeda BRL;
- Alê como admin;
- Flávia/OpenClaw com acesso read-only inicialmente.

### 2. Token/API para diagnóstico

Antes de rodar diagnóstico via OpenClaw:
- `META_AD_ACCOUNT_ID=act_<id>`
- token com `ads_read`
- opcional para leads: `leads_retrieval`

Regra: read-only primeiro. Nenhuma criação/edição/pausa/ativação/orçamento sem aprovação explícita do Alê.

### 3. Padrão de naming

Campanha:
`<MARCA>_<OBJETIVO>_<PUBLICO>_<OFERTA>_<YYYYMM>`

Exemplos:
- `MENSURA_LEAD_CONSTRUTORAS-SP_DIAGNOSTICO-PRAZO_202605`
- `MIA_LEAD_ALTO-PADRAO_PRE-CONSTRUCAO_202605`

Conjunto de anúncios:
`<REGIAO>_<SEGMENTO>_<SENIORIDADE>_<AUDIENCIA>`

Exemplo:
- `SP_CONSTRUTORAS_DIRETORIA_BROAD-ENGENHARIA`

Anúncio:
`<ANGULO>_<CRIATIVO>_<VERSAO>`

Exemplo:
- `RISCO-PRAZO_TEXTO-ESTATICO_V01`

### 4. UTMs obrigatórias

Todo link deve sair com UTM:

```text
utm_source=meta
utm_medium=paid_social
utm_campaign=<nome_da_campanha>
utm_content=<nome_do_anuncio>
utm_term=<publico_ou_conjunto>
```

### 5. Conversão e lead flow

Antes de subir verba, definir o destino:

Opção A — formulário Meta Lead Ads:
- mais rápido;
- exige checar qualidade do lead;
- precisa rotina de captura e integração CRM.

Opção B — landing page:
- melhor qualificação;
- exige tracking/Pixel/CAPI;
- melhor para diagnóstico executivo ou conteúdo técnico.

Recomendação inicial MENSURA:
- começar com oferta de **Diagnóstico Executivo de Previsibilidade de Obra**;
- CTA: conversa de 20 min ou diagnóstico rápido;
- qualificação mínima: tipo de empresa, cargo, nº de obras, maior dor: prazo/custo/visibilidade.

### 6. Métricas executivas

Não otimizar por curtida.

Métricas mínimas:
- gasto;
- alcance;
- CTR;
- frequência;
- CPL;
- leads qualificados;
- custo por lead qualificado;
- reunião marcada;
- proposta gerada;
- oportunidade real.

### 7. Rotina semanal de decisão

Toda semana, relatório curto:

1. O que gastou.
2. O que gerou lead.
3. O que gerou lead qualificado.
4. Onde houve desperdício.
5. Criativo com fadiga.
6. Próximo teste recomendado.
7. Ação que exige aprovação do Alê.

## Checklist antes de lançar a primeira campanha

- [ ] Conta de anúncio criada/vinculada ao Business correto.
- [ ] Forma de pagamento ativa.
- [ ] `act_<id>` registrado em credencial segura.
- [ ] Token read-only validado.
- [ ] Oferta definida.
- [ ] Público inicial definido.
- [ ] Lead flow definido: formulário ou landing page.
- [ ] UTMs padronizadas.
- [ ] CRM/HubSpot ou planilha de captura definida.
- [ ] Relatório semanal configurado.
- [ ] Aprovação explícita do Alê para qualquer campanha real.

## Primeiras campanhas recomendadas

### MENSURA — Diagnóstico Executivo de Previsibilidade

Público:
- diretores/CEOs/engenharia/planejamento de construtoras e incorporadoras SP;
- empresas com obras simultâneas ou CAPEX relevante.

Dor:
- cronograma bonito, mas sem poder de decisão;
- falta de previsibilidade de prazo;
- diretoria sem leitura executiva de risco.

Oferta:
- diagnóstico de 20 min ou diagnóstico executivo inicial.

### MIA — Pré-construção como proteção patrimonial

Público:
- proprietários/representantes/arquitetos de alto padrão;
- incorporadores ou famílias com obra residencial premium.

Dor:
- custo emocional e financeiro de obra mal planejada;
- decisões ruins antes da obra começar;
- falta de governança técnica independente.

Oferta:
- conversa de pré-construção ou checklist de blindagem técnica.

## Regra de ouro

Campanha sem CRM/lead flow é vazamento de dinheiro.

Antes de subir verba, a pergunta é:
> Quando o lead chegar, quem responde, em quanto tempo, com qual roteiro e onde isso fica registrado?
