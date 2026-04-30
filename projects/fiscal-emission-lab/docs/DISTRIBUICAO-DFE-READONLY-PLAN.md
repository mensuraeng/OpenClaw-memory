# DFe.NET / DistribuicaoDFe — plano técnico read-only

_Atualizado em 2026-04-29_

## Objetivo

Preparar a trilha técnica para consulta/baixa de documentos fiscais eletrônicos de interesse das empresas, sem usar certificado real nesta fase e sem qualquer transmissão, emissão, cancelamento ou inutilização.

## Escopo permitido v0

- estudar integração DFe.NET em microserviço/CLI .NET isolado;
- definir contrato de entrada/saída;
- processar XML local já disponível;
- gerar JSON normalizado no schema `templates/nota-recebida.schema.json`;
- gerar DANFE HTML/PDF futuramente a partir de XML já baixado;
- registrar evidência local no runtime.

## Fora do escopo v0

- certificado A1/A3 real;
- consulta real à SEFAZ;
- manifestação do destinatário;
- emissão/transmissão;
- cancelamento/inutilização;
- envio automático por Telegram, email ou cliente;
- aprovação de pagamento/aceite.

## Arquitetura futura proposta

```text
OpenClaw / Fiscal Ops
  → chama CLI/microserviço .NET isolado
  → DFe.NET DistribuicaoDFe com certificado em cofre
  → baixa XML autorizado
  → parser normaliza JSON
  → runtime/fiscal/notas-recebidas
  → outbox local de notificação para revisão
```

## Contrato esperado do adaptador .NET futuro

Entrada segura:

```json
{
  "company_slug": "mensura",
  "cnpj": "somente se necessário no runtime seguro",
  "environment": "homologacao|producao",
  "last_nsu": "opcional",
  "mode": "read_only_distribution"
}
```

Saída esperada:

```json
{
  "status": "ok|no_new_documents|error",
  "documents": [
    {
      "access_key": "...",
      "document_type": "NFe",
      "xml_path": "runtime/fiscal/notas-recebidas/...xml",
      "downloaded_at": "...",
      "read_only": true
    }
  ],
  "next_nsu": "...",
  "errors": []
}
```

## Segurança de certificado

- certificado nunca entra em GitHub, memória, chat, log consolidado ou fixture;
- senha/caminho ficam em cofre/KeeSpace ou secret local `0600` temporário;
- logs devem registrar apenas `credential_status=exists|not_found|not_validated`;
- primeira execução real exige aprovação explícita do Alê e checklist fiscal.

## Estado atual

- Não foi usado certificado real.
- Não houve acesso SEFAZ.
- Não houve efeito externo.
- Capacidade entregue: parser local read-only para XML NF-e e estrutura runtime fiscal.
