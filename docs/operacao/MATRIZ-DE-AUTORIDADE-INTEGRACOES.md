# Matriz de Autoridade — Integrações OpenClaw / Flávia

_Atualizado em 2026-04-28_

## Regra-mãe

- **READ** é o padrão.
- **WRITE interno** só quando reversível, logado e dentro de política pré-aprovada.
- **WRITE externo** exige aprovação explícita do Alê, salvo exceções já formalizadas.
- **DELETE permanente** exige aprovação explícita. Padrão: mover para `.trash/`/quarentena.
- Toda automação com side effect precisa de evidência, rollback/contenção e owner.

## Matriz inicial

| Integração | Nível autorizado | O que pode sem pedir | O que exige aprovação | Observação |
|---|---|---|---|---|
| Microsoft Graph — e-mail Mensura/MIA/PCS | read + categorias | ler, classificar, gerar relatório, aplicar categorias visuais | responder, encaminhar, mover, apagar, arquivar, marcar como lido | Monitor executivo 7h/14h segue essa regra |
| Microsoft Graph — calendário | read-only | consultar agenda e preparar contexto | criar, alterar, cancelar evento | Agenda é superfície externa |
| Telegram/WhatsApp | send controlado | responder ao Alê; enviar a canais internos quando já previsto | mensagens a terceiros/clientes/canais públicos | Direct do Alê só gerencial |
| Backblaze B2 | write controlado | subir backup criptografado; listar/validar | apagar conjunto remoto, alterar retenção/cap | Apagar parcial só com autorização |
| Arquivos workspace/2nd-brain | read/write interno | criar docs, registrar memória, atualizar artefatos operacionais | apagar permanente, alterar bootstrap/config crítica | Preferir `.trash/` |
| KeeSpace | cofre oficial | buscar/usar segredo por referência segura | exportar ou copiar segredo para memória/docs | Alvo de migração gradual dos `.env` locais |
| LinkedIn pessoal | write pré-aprovado | publicar dentro do plano editorial aprovado | tema sensível/fora do plano, edição/perfil | Token precisa ficar fora de texto/memória |
| LinkedIn institucional | bloqueado | monitorar aprovação | publicar como página | Aguardar Community Management API |
| Meta Ads | read-only | diagnóstico, campanhas, insights | criar/editar/pausar/ativar campanha, orçamento, público ou criativo | Sem conta ativa/vinculada ainda |
| HubSpot | read/write controlado | ler funil, contatos, deals; sugerir atualização | criar/mover deal em massa, alterar pipeline | Preferir dry-run no começo |
| Phantombuster/LinkedIn outbound | read/controlado | ler status, logs e métricas | iniciar disparo/cadência nova | Risco reputacional/comercial |
| Sienge/ERP | read/write alto risco | leitura, validação, dry-run | upload, alteração de orçamento, contrato, centro de custo | Sempre com confirmação específica |
| Supabase Mensura Schedule | read/write interno | importar/analisar cronogramas com validação | apagar massa, migração destrutiva | Usar migrations/versionamento |
| Supabase Trade | read/write interno restrito | registrar dados/análises | ordem financeira/aplicação/resgate | Trade não executa decisão financeira |
| Git/GitHub | write controlado | branch/commit interno com escopo claro | merge produção, PR externo, alteração sensível | Subagente nunca fire-and-forget |

## Exigências para qualquer WRITE

1. owner claro;
2. escopo limitado;
3. log/evidência;
4. dry-run quando possível;
5. rollback/contenção;
6. confirmação explícita quando houver impacto externo, financeiro, jurídico, reputacional ou destrutivo.
