# Protocolo de Validação de Subagentes

_Atualizado em 2026-04-29_

## Objetivo

Validar que subagentes especializados conseguem executar escopos pequenos, com evidência, limite de autoridade e próximo passo, sem efeitos externos.

## Guardrails obrigatórios

- Sem envio de mensagens, e-mails, posts ou qualquer saída externa.
- Sem delete permanente.
- Sem alteração de configuração crítica.
- Preferir leitura local e artefatos internos.
- Toda resposta externa/sensível continua passando pela Flávia e, quando necessário, pelo Alê.

## Prompt mínimo padrão

Cada validação deve ter:

1. escopo único e pequeno;
2. arquivos locais explícitos para leitura;
3. proibição clara de side effects;
4. formato de resposta fixo:
   - `status`
   - `evidencia`
   - `limite_de_autoridade`
   - `proximo_passo`
   - `tempo_aproximado`

## Timeout padrão

- Para escopos mínimos: `runTimeoutSeconds=600` e `timeoutSeconds=700`.
- Não usar o timeout curto anterior de ~4m24s como critério de falha operacional.

## Tratamento de timeout no spawn

Se `sessions_spawn` retornar gateway timeout curto, mas trouxer `childSessionKey`/`runId`, não tratar imediatamente como falha do agente.

Procedimento:

1. aguardar retorno push quando houver;
2. checar `sessions_list` sob demanda;
3. se a sessão aparecer como `done` com resposta útil, classificar como **spawn aceito com ack timeout**, não como falha de execução;
4. só fazer retry se não houver sessão recuperável ou se a resposta vier inválida.

## Critério 100%

Validação aprovada quando pelo menos 3 subagentes especializados retornarem, dentro do prazo, com:

- status claro;
- evidência com caminho/achado;
- limite de autoridade;
- próximo passo;
- sem side effects externos.

Falhas ou timeouts devem ter causa provável e mitigação documentadas.

## Resultado da rodada de 2026-04-29 02:00 BRT

Subagentes testados: `finance`, `mensura`, `pcs`, `mia`, `trade`.

Resultado: 5/5 retornaram respostas úteis em escopos mínimos read-only.

Evidências consolidadas:

| Agente | Status | Evidência principal | Próximo passo |
|---|---|---|---|
| `finance` | validado parcialmente | comprovante Pix MIA/Aluga Bem em `runtime/finance/comprovantes/2026-04-28_pix_600_aluga-bem_mia.json` | vincular centro de custo/obra na conciliação MIA |
| `mensura` | validado | CRM/CDP com 477 empresas, 1242 contatos, 474 suppressions, 767 contatos verificados; reconciliação HubSpot com 967 contatos, 366 empresas, 2 deals e gaps materiais | criar ledger por lead e rotina de diff local ↔ HubSpot |
| `pcs` | validado | `ORGANOGRAMA-FUNCIONAL-AGENTES.md` e `agents/pcs-agent/AGENT.md` confirmam papel PCS/limites | consolidar evidência na validação 100% |
| `mia` | validado | `agents/mia/AGENT.md`, WORKING FLV-WORK-004 e comprovante MIA/Aluga Bem confirmam papel e pendência | Flávia/Finance vincular centro de custo/obra |
| `trade` | concluído | organograma define trade como inteligência de mercado/investimentos pessoais | manter atuação read-only/analítica salvo autorização explícita |

Observação operacional: três spawns retornaram gateway timeout inicial de ~10s, mas as sessões foram criadas e concluíram com resposta útil em ~30–40s. A mitigação correta é verificar sessão recuperável antes de retry.
