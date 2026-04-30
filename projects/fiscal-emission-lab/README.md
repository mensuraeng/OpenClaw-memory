# Fiscal Emission Lab — MIA / MENSURA / PCS

_Atualizado em 2026-04-29_

## Objetivo

Implantar uma frente controlada para emissão fiscal eletrônica, começando por emissão assistida e rastreável, sem automatizar transmissão fiscal antes de validação tributária, certificado digital e homologação.

## Decisão executiva

- Implantar a frente fiscal.
- Separar trilha **NFS-e municipal** da trilha **NF-e/DFe estadual/federal**.
- Usar DFe.NET apenas onde ele é aderente: NF-e, NFC-e, CT-e e MDF-e.
- Para MIA/MENSURA, assumir como hipótese inicial que a emissão recorrente tende a ser **NFS-e de serviço**, a validar.

## Guardrail

Nenhuma nota fiscal será emitida, transmitida, cancelada, inutilizada ou enviada a cliente por automação sem confirmação explícita do Alê e checklist fiscal aprovado.

## Arquitetura-alvo

```text
Solicitação de emissão
→ pré-emissão estruturada
→ validação fiscal / aprovação humana
→ emissão no canal correto
   ├─ NFS-e municipal / Sistema do Milhão / prefeitura
   └─ NF-e/CT-e/MDF-e via DFe.NET, quando aplicável
→ captura PDF/XML
→ resumo estruturado JSON
→ contas a receber
→ evidência no 2nd-brain/runtime
```

## Escopo v0

1. Consolidar dados fiscais por empresa.
2. Criar formulário/template de pré-emissão.
3. Criar registro estruturado de nota emitida.
4. Mapear se a operação é NFS-e, NF-e ou ambas.
5. Preparar trilha DFe.NET para NF-e apenas em homologação.

## Fora do escopo v0

- transmissão automática para SEFAZ;
- cancelamento automático;
- inutilização automática;
- envio automático ao cliente;
- uso de certificado digital em automação;
- emissão de NFS-e por portal municipal sem mapeamento específico.

## Fontes atuais

- `docs/fiscal-emissao/roadmap-emissao-mia-mensura.md`
- `docs/fiscal-emissao/checklist-coleta-mia-mensura.md`
- `docs/fiscal-emissao/playbook-operacional-sistema-do-milhao.md`
- Repositório avaliado: `https://github.com/ZeusAutomacao/DFe.NET`

## Consulta e baixa de notas contra empresas

A frente fiscal passa a incluir consulta/baixa read-only de notas emitidas contra MENSURA, MIA e PCS, com notificação no grupo operacional correspondente quando houver documento novo. Ver `docs/CONSULTA-BAIXA-NOTIFICACOES.md`.

## Capacidade implantada — Fiscal Ops read-only v0

Entregue em 2026-04-29:

- estrutura local `runtime/fiscal/` para notas recebidas, ledger e outbox de notificações sugeridas;
- schema normalizado `templates/nota-recebida.schema.json`;
- fixture sintética explícita `fixtures/nfe-recebida-sintetica.xml`;
- CLI read-only `scripts/fiscal_nfe_received_parser.py`;
- testes locais em `tests/test_fiscal_nfe_received_parser.py`;
- plano técnico de DFe.NET/DistribuicaoDFe em `docs/DISTRIBUICAO-DFE-READONLY-PLAN.md`.

Validação executada:

```bash
python3 -m py_compile projects/fiscal-emission-lab/scripts/fiscal_nfe_received_parser.py
python3 -m unittest discover -s projects/fiscal-emission-lab/tests -v
python3 projects/fiscal-emission-lab/scripts/fiscal_nfe_received_parser.py \
  --xml projects/fiscal-emission-lab/fixtures/nfe-recebida-sintetica.xml \
  --runtime-dir runtime/fiscal \
  --company-slug mensura-fixture \
  --origin fixture-sintetica \
  --copy-xml
```

Resultado de evidência local gerado com dado sintético:

- `runtime/fiscal/notas-recebidas/mensura-fixture/2026-04/2026-04-29_fornecedor-sintetico-ltda_1234.json`
- `runtime/fiscal/notas-recebidas/mensura-fixture/2026-04/2026-04-29_fornecedor-sintetico-ltda_1234.xml`
- `runtime/fiscal/ledger/notas-recebidas.jsonl`

Nenhum certificado, SEFAZ, Telegram, email ou sistema externo foi acessado.
