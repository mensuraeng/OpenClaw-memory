# Regras de Dados e Confiança

_Atualizado em 2026-04-28_

## Princípio

Dado bruto não é verdade operacional. Todo indicador executivo deve carregar fonte, método, janela, confiança e risco de erro.

## Todo número relevante deve informar

- Fonte
- Janela temporal
- Método de coleta/contagem
- Confiança: alta / média / baixa
- Riscos conhecidos: paginação, permissão, duplicidade, dado parcial, fonte fora do sistema
- Próxima verificação, se houver dúvida

## Regra de paginação

Toda API paginável deve paginar explicitamente ou declarar limitação.

Aplica-se a:
- Microsoft Graph
- Supabase
- HubSpot
- Phantombuster
- Meta Ads
- LinkedIn
- Sienge
- Backblaze B2
- qualquer endpoint de relatório/listagem

## Alertas precisam separar

```text
Dado observado:
Interpretação:
Exceções conhecidas:
Confiança:
Próxima verificação:
```

## Exemplos

### Obra sem atualização

Errado:
> Obra parada há 10 dias.

Certo:
> Não encontrei atualização no sistema X há 10 dias. Confiança média: pode haver atualização por e-mail/WhatsApp/arquivo fora do sistema. Próxima checagem: inbox + pasta da obra.

### Lead sem resposta

Errado:
> Lead abandonado.

Certo:
> HubSpot não registra resposta desde D+3. Confiança média: ainda não cruzei LinkedIn/WhatsApp. Próxima checagem: logs de outreach.

### Financeiro

Errado:
> Pagamento sem obra.

Certo:
> Comprovante registrado sem centro de custo confirmado. Categoria sugerida por fornecedor/contexto; precisa conciliação.

## Quando salvar lição

Sempre que um falso positivo, bug de contagem, exceção de cliente legado, falha de paginação ou regra de negócio nova for identificado, salvar em `2nd-brain/02-context/lessons.md` ou memória temática adequada.
