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
- [ ] Baixar XML/PDF de nota recebida sem alterar status fiscal.
- [ ] Gerar JSON normalizado da nota.
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
- [ ] Criar microserviço/CLI .NET isolado.
- [ ] Testar leitura de XML NF-e de exemplo.
- [ ] Testar geração de DANFE/HTML/PDF, se útil.
- [ ] Só testar transmissão em homologação após aprovação.

## Fase 5 — Automação controlada

- [ ] Emissão assistida com revisão humana.
- [ ] Integração com contas a receber.
- [ ] Dashboard de notas emitidas e pendentes.
- [ ] Automação de envio ao cliente somente após aprovação formal.
