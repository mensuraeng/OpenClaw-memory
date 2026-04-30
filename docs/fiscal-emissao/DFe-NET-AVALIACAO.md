# DFe.NET — avaliação de aproveitamento

_Atualizado em 2026-04-29_

## Repositório

- `https://github.com/ZeusAutomacao/DFe.NET`
- Biblioteca C# para NFe, NFCe, CT-e e MDF-e.
- Licença: LGPL-2.1.
- Stack: .NET Framework / .NET Standard / .NET 6/7/8.

## Avaliação

A biblioteca é madura e aproveitável para documentos fiscais eletrônicos estaduais/federais, especialmente NF-e, NFC-e, CT-e e MDF-e.

Não deve ser assumida como solução para NFS-e municipal, que é provavelmente a demanda principal de MIA/MENSURA quando a operação for prestação de serviços de engenharia.

## Uso recomendado

- laboratório/homologação para NF-e/DFe;
- leitura de XML NF-e;
- geração de JSON normalizado;
- DANFE/HTML/PDF quando necessário;
- microserviço .NET isolado, não acoplado ao runtime principal da Flávia.

## Uso não recomendado agora

- emissão automática em produção;
- cancelamento/inutilização automática;
- substituir Sistema do Milhão antes de mapear NFS-e;
- manipular certificado digital sem cofre, política e aprovação.

## Decisão

Abrir frente `projects/fiscal-emission-lab/` com duas trilhas:

1. NFS-e municipal / Sistema do Milhão — principal para serviços.
2. DFe.NET / NF-e-DFe — laboratório técnico para casos aderentes.
