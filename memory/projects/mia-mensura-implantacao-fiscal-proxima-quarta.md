# Implantação fiscal MIA + MENSURA - próxima quarta-feira

_Atualizado em 2026-04-20_

## Objetivo
Guardar o estado atual da frente de implantação da emissão fiscal eletrônica para retomar na próxima quarta-feira sem perder contexto.

## Decisões já consolidadas
- A frente cobre as duas empresas: **MIA** e **MENSURA**.
- A emissão atual das duas é **manual**.
- O sistema utilizado hoje pelas duas é o **Sistema do Milhão**.
- A implantação correta deve começar por **padronização operacional**, não por troca imediata de emissor ou automação prematura por API.
- A prioridade é organizar o fluxo de emissão, pré-emissão, arquivamento e ligação com o financeiro.

## Artefatos já criados
- `docs/fiscal-emissao/roadmap-emissao-mia-mensura.md`
- `docs/fiscal-emissao/checklist-coleta-mia-mensura.md`
- `docs/fiscal-emissao/playbook-operacional-sistema-do-milhao.md`
- `memory/projects/mia/emissao-fiscal-base.md`
- `memory/projects/mensura/emissao-fiscal-base.md`

## O que já sabemos
### MIA
- possui base fiscal institucional já consolidada
- São Paulo/SP
- possui CCM, IE e trilha documental consolidada
- emissão atualmente manual via Sistema do Milhão

### MENSURA
- emissão atualmente manual via Sistema do Milhão
- trilha fiscal ainda precisa de consolidação adicional
- já houve movimentação/documento fiscal-financeiro como DAS recebido na operação

## Pendências para a próxima retomada
- confirmar se no Sistema do Milhão as empresas emitem **NFS-e**, **NF-e** ou **ambos**
- confirmar se o certificado digital fica **dentro do sistema** ou **fora dele**
- mapear quem solicita a emissão, quem confere e quem emite hoje
- mapear onde PDF e XML são guardados hoje
- identificar o gatilho que faz nascer o contas a receber após emissão

## Próximo passo recomendado na retomada
Começar pela consolidação operacional real:
1. tipo de nota por empresa
2. certificado
3. responsáveis
4. armazenamento de XML/PDF
5. vínculo com financeiro

## Observação operacional
Na retomada, tratar esta frente como implantação fiscal assistida em cima do Sistema do Milhão, e não como projeto de API bancária ou emissor próprio.
