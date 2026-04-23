# Estado operacional - PCS contabilidade / Confirp

_Atualizado em 2026-04-21 13:55 BRT_

## Objetivo
Operar a leitura mensal da contabilidade da PCS a partir dos emails oficiais da Confirp, com histórico por competência, downloads reais de documentos, e geração de demonstrativo gerencial baseado nas melhores práticas de contabilidade.

## Estado operacional atual
- status: **parcialmente executado**
- leitura da caixa PCS via Graph: **validada**
- recuperação de documentos reais da Confirp: **validada**
- relatório HTML inicial da competência 03/2026: **gerado**
- histórico persistente por competência/CNPJ: **ainda não consolidado**
- recuperação completa de todos os arquivos listados: **ainda incompleta**

## Regra metodológica vigente
- usar somente documentos reais baixados da trilha oficial Confirp
- não inventar dado
- não misturar inbound geral com remessa oficial da PCS
- tratar documento indisponível como indisponível
- basear a leitura nas melhores práticas de contabilidade

## Capacidade validada
### Ferramenta: recuperação PCS via Microsoft Graph + Confirp
- padrão: listar e ler emails da PCS via `/root/.openclaw/workspace/scripts/msgraph_email.py` com `config/ms-graph-pcs.json`, extrair links do corpo HTML e baixar arquivos válidos
- fallback: testar emails anteriores da mesma competência quando o link mais recente expirar ou retornar erro
- nível de productização: operacional validado, mas ainda dependente de organização histórica e retry estruturado
- limitações: parte dos links da Confirp pode retornar `Arquivo não encontrado`; remessa pode ficar incompleta mesmo com email localizado
- última validação real: 2026-04-21
- evidência: downloads reais em `/tmp/confirp-pcs-2026-03/` e relatório em `/root/.openclaw/workspace/reports/pcs-relatorio-contabil-2026-03.html`

## Documentos reais já recuperados para 03/2026
- RECIBO EFD CONTRIBUIÇÕES
- RELATÓRIO REINF
- GUIA FGTS MENSAL
- GUIA E-CONSIGNADO
- `TOTALIZADOR.zip` com memórias de cálculo e totalizadores

## Itens ainda indisponíveis
- DEMONST ICMS
- demonstrativos EFD PIS/COFINS de apuração
- arquivo do CNPJ `07.753.834/0002-06`

## Bloqueios reais atuais
- o endpoint da Confirp ainda retorna `{"error":{"message":"Arquivo não encontrado","extra":null},"statusCode":500}` para parte dos documentos
- a estrutura final histórica por competência e CNPJ ainda não foi consolidada fora de staging temporário

## Próximo passo correto
1. mover os arquivos válidos para estrutura histórica definitiva
2. consolidar o HTML final da competência 03/2026 como versão operacional da PCS
3. manter retry estruturado para os arquivos indisponíveis
4. productizar monitoramento mensal da Confirp com histórico comparável
