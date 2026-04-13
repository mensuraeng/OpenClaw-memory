# Lições Aprendidas

> Erros recorrentes, armadilhas e padrões úteis da operação.

_Atualizado em 2026-04-13_

## Permanentes

### Microsoft 365 não aceita auth básica (2026-04-01)
Clientes IMAP/SMTP tradicionais falham para essas contas. O padrão é Microsoft Graph API com client credentials.

### Script de monitor deve ser testado antes de ir para cron (2026-04-01)
Rodar manualmente antes evita agendar saída quebrada, formato ruim ou dado errado.

### Configuração do OpenClaw deve ser agrupada antes de restart (2026-04-01)
Mudanças de config aplicam após restart. Melhor consolidar alterações e reiniciar uma vez.

### Auditoria de cron não pode olhar só o estado atual (2026-04-07)
Jobs one-shot com `deleteAfterRun: true` somem depois de executar. Conferir `jobs.json`, backup e histórico de runs antes de concluir que não existiram.

### Segredo não pertence à memória operacional (2026-04-07)
Se um segredo parar em `memory/`, isso deve ser tratado como contenção temporária. O destino correto é o cofre.

### Migração de credenciais deve ser controlada (2026-04-07)
Varredura cega arrasta lixo, duplicata e contexto errado. Auditar primeiro, migrar depois.

### Script multi-conta não pode fixar usuário padrão no código (2026-04-13)
Quando a conta muda, o script deve puxar `defaultUser` da config ou exigir `--user`. Hardcode silencioso gera falso negativo e mascara integração saudável.

### Fallback silencioso em automação operacional é erro de desenho (2026-04-13)
Se faltar parâmetro essencial, o script deve falhar com mensagem clara. Cair para valor padrão genérico mascara problema de configuração e atrasa diagnóstico.

## Temporárias

### `openclaw thinking` não existe nesta versão (2026-04-01 | revisar depois de upgrade)
O controle de reasoning disponível está no chat via `/reasoning`, não em comando CLI `openclaw thinking`.

### `reserveTokensFloor` fica em `agents.defaults.compaction` (2026-04-01 | revisar depois de upgrade)
O path correto atual é `agents.defaults.compaction.reserveTokensFloor`.

## Regra de manutenção

- Promover para `decisions.md` o que deixar de ser só lição e virar regra permanente.
- Remover lição temporária quando o ambiente mudar e ela deixar de ser verdade.
- Não registrar aqui detalhe de sessão que só importa uma vez.
