# Plano de implantação — emissão fiscal assistida

_Atualizado em 2026-04-29_

## Fase 0 — Segurança e escopo

- [x] Criar projeto `projects/fiscal-emission-lab/`.
- [x] Registrar decisão DFe.NET vs NFS-e.
- [x] Definir que emissão/transmissão/cancelamento exigem aprovação explícita.
- [ ] Confirmar tipo de nota por empresa: NFS-e, NF-e ou ambas.
- [ ] Confirmar sistema atual e credenciais operacionais sem expor segredo.

## Fase 0.5 — Consulta e baixa read-only

- [ ] Confirmar fonte de consulta por empresa.
- [ ] Confirmar grupo Telegram de destino por empresa.
- [x] Baixar/importar XML local de nota recebida sem alterar status fiscal — v0 com fixture sintética.
- [x] Gerar JSON normalizado da nota — v0 com `templates/nota-recebida.schema.json`.
- [ ] Notificar grupo correto sem aprovação/aceite automático.

## Fase 1 — Cadastro fiscal base

Para cada empresa:

- [ ] razão social;
- [ ] CNPJ;
- [ ] município de emissão;
- [ ] inscrição municipal/CCM;
- [ ] inscrição estadual;
- [ ] regime tributário;
- [ ] CNAEs usados na emissão;
- [ ] certificado A1/A3 e localização segura;
- [ ] responsável por aprovar emissão.

## Fase 2 — Pré-emissão assistida

- [ ] Criar formulário/template de solicitação de emissão.
- [ ] Criar biblioteca de tomadores recorrentes.
- [ ] Criar biblioteca de descrições de serviço/produto.
- [ ] Criar tabela de retenções e observações padrão.
- [ ] Definir nomenclatura para PDF/XML.

## Fase 3 — Registro pós-emissão

- [ ] Salvar PDF/XML em caminho padronizado.
- [ ] Gerar resumo JSON da nota.
- [ ] Vincular nota a cliente, contrato, obra/centro de custo e contas a receber.
- [ ] Registrar evidência no runtime e memória quando material.

## Fase 4 — DFe.NET laboratório

- [ ] Instalar .NET SDK no ambiente correto ou usar container.
- [ ] Criar microserviço/CLI .NET isolado — planejado; v0 entregue em Python local sem DFe.NET real.
- [x] Testar leitura de XML NF-e de exemplo — fixture sintética local.
- [ ] Testar geração de DANFE/HTML/PDF, se útil.
- [ ] Só testar transmissão em homologação após aprovação.

## Fase 5 — Automação controlada

- [ ] Emissão assistida com revisão humana.
- [ ] Integração com contas a receber.
- [ ] Dashboard de notas emitidas e pendentes.
- [ ] Automação de envio ao cliente somente após aprovação formal.

## Evidência Fiscal Ops read-only v0

Entregue internamente em 2026-04-29:

- `runtime/fiscal/README.md`
- `projects/fiscal-emission-lab/templates/nota-recebida.schema.json`
- `projects/fiscal-emission-lab/scripts/fiscal_nfe_received_parser.py`
- `projects/fiscal-emission-lab/fixtures/nfe-recebida-sintetica.xml`
- `projects/fiscal-emission-lab/tests/test_fiscal_nfe_received_parser.py`
- `projects/fiscal-emission-lab/docs/DISTRIBUICAO-DFE-READONLY-PLAN.md`

Validação: `py_compile` e `unittest` passaram. Parser gerou JSON/XML/ledger local a partir de fixture sintética, com `source.real_data=false`.
