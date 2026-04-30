# Consulta, baixa e notificação de notas fiscais contra empresas

_Atualizado em 2026-04-29_

## Objetivo

Consultar e baixar notas fiscais emitidas contra MENSURA, MIA e PCS, salvar PDF/XML/metadados e avisar no grupo operacional correspondente quando houver documento novo relevante.

## Regra de prioridade

Consulta e baixa fiscal read-only vêm antes de emissão.

Motivo: gera valor operacional imediato com menor risco, melhora conciliação financeira e cria base fiscal auditável antes de qualquer automação de emissão.

## Escopo

- notas emitidas contra a empresa;
- XML, PDF/DANFE ou comprovante disponível;
- metadados estruturados;
- classificação por empresa, fornecedor, competência, valor, tipo de nota e centro de custo/obra quando possível;
- notificação no grupo correto.

## Fontes possíveis

### NFS-e municipal

Depende do município/sistema emissor.

Para MIA/MENSURA, hipótese atual: Sistema do Milhão.

A mapear:

- se existe API;
- se existe exportação de XML/PDF;
- se a consulta exige certificado;
- se a consulta é por CNPJ/tomador;
- se é possível baixar lote por competência.

### NF-e / CT-e / MDF-e

Possível trilha com DFe.NET e certificado digital, quando aplicável.

Usos prováveis:

- consultar/baixar XML de NF-e recebida;
- ler XML;
- gerar JSON normalizado;
- gerar DANFE/visualização;
- cruzar com financeiro.

## Roteamento de notificação por empresa

Canais canônicos conhecidos:

- MENSURA Engenharia — Telegram `telegram:-1003366344184`, tópico `1`.
- PCS Engenharia — Telegram `telegram:-1003146152550`, tópico `1`.

Pendente de confirmação canônica:

- MIA Engenharia — confirmar chat_id/tópico antes de notificação automática. Há indícios históricos de grupo MIA, mas o mapa canônico atual ainda não lista MIA.

## Regra de envio

A notificação em grupo é permitida somente quando:

1. a nota foi detectada por fonte read-only confiável;
2. há identificação clara da empresa tomadora;
3. a mensagem não assume responsabilidade, aprovação ou aceite;
4. não contém segredo, certificado, token, dados bancários sensíveis ou link privado que não deva circular;
5. o grupo de destino está confirmado.

## Formato da mensagem

```text
Nota fiscal detectada contra [EMPRESA]

Fornecedor: [RAZÃO SOCIAL]
CNPJ fornecedor: [CNPJ]
Tipo: [NFS-e/NF-e/etc.]
Número: [número]
Emissão: [data]
Valor: R$ [valor]
Competência: [competência, se houver]
Status: documento baixado / pendente de XML / pendente de PDF

Arquivos salvos:
- XML: [caminho interno]
- PDF/DANFE: [caminho interno]

Próximo passo sugerido: classificar centro de custo/obra e validar lançamento financeiro.
```

## O que nunca enviar automaticamente

- “nota aprovada”;
- “pode pagar”;
- “aceitamos o serviço/produto”;
- “está correto”;
- dados de certificado;
- token/API key;
- dados bancários sensíveis;
- anexo externo sem revisão.

## Armazenamento sugerido

```text
runtime/fiscal/notas-recebidas/<empresa>/<YYYY-MM>/
  <data>_<fornecedor>_<numero>.xml
  <data>_<fornecedor>_<numero>.pdf
  <data>_<fornecedor>_<numero>.json
```

## Próximos dados necessários

Para cada empresa:

- CNPJ emissor/tomador correto;
- tipo de nota recebida mais comum: NFS-e, NF-e ou ambas;
- município/sistema de NFS-e;
- credencial ou certificado necessário para consulta;
- confirmação do grupo Telegram de destino, especialmente MIA;
- regra de quem classifica centro de custo/obra.
