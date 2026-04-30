# ADR-001 — Trilha fiscal: DFe.NET vs NFS-e municipal

_Status: aceita para implantação controlada_
_Data: 2026-04-29_

## Contexto

O Alê autorizou implantar uma frente para emissão de nota fiscal após análise do repositório `ZeusAutomacao/DFe.NET`.

O DFe.NET é uma biblioteca C#/.NET madura para emissão, leitura, transmissão e impressão de documentos fiscais eletrônicos como NF-e, NFC-e, CT-e e MDF-e.

A operação recorrente de MIA/MENSURA, porém, provavelmente envolve prestação de serviços de engenharia, que normalmente usa NFS-e municipal. NFS-e não é o foco principal do DFe.NET e costuma depender do município/portal/sistema emissor.

## Decisão

Implantar a frente fiscal com duas trilhas separadas:

1. **NFS-e municipal / Sistema do Milhão**
   - trilha principal inicial para MIA/MENSURA, se confirmado que emitem serviços;
   - foco em padronização, pré-emissão, captura de PDF/XML e contas a receber;
   - automação só depois de mapear portal/API/sistema real.

2. **DFe.NET / NF-e-DFe**
   - trilha técnica para NF-e, NFC-e, CT-e e MDF-e;
   - começar em modo laboratório/homologação;
   - usar como microserviço .NET isolado quando houver operação aderente.

## Consequências

- Evita adotar DFe.NET para problema errado.
- Permite aproveitar DFe.NET se houver NF-e/CT-e/MDF-e real.
- Mantém emissão fiscal sob aprovação humana nas fases iniciais.
- Preserva rastreabilidade fiscal e financeira.

## Critério para avançar DFe.NET

Só avançar para implementação DFe.NET real quando houver pelo menos um caso confirmado de:

- emissão NF-e/NFC-e/CT-e/MDF-e;
- certificado digital A1/A3 validado;
- ambiente de homologação definido;
- dados fiscais da empresa completos;
- responsável fiscal/contábil ciente;
- aprovação explícita do Alê.

## Critério para avançar NFS-e

Para NFS-e, mapear:

- município de emissão;
- sistema/portal usado;
- se existe API;
- credenciais/certificado;
- campos obrigatórios;
- serviços recorrentes;
- retenções;
- padrão de PDF/XML;
- fluxo de aprovação.
