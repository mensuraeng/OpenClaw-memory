# Lições Aprendidas

> Erros, padrões e aprendizados do dia a dia com a Flávia.
> 🔒 Estratégicas = permanentes | ⏳ Táticas = expiram em 30 dias

_Atualizado em 2026-04-01_

---

## 🔒 Estratégicas

### Microsoft 365 não aceita basic auth (2026-04-01)
Himalaya CLI e qualquer cliente IMAP/SMTP padrão são bloqueados pelo Microsoft para contas Office 365. Sempre usar Microsoft Graph API com client credentials flow (app registration no Entra ID).

### Testar antes de commitar no monitor (2026-04-01)
Scripts de monitoramento devem ser testados com `python3 script.py` antes de ir para cron. O output no terminal é idêntico ao que vai para o Telegram — valida formato e dados de uma vez.

### Configurar via `openclaw config set` antes de reiniciar (2026-04-01)
Mudanças de config só aplicam após restart do gateway. Agrupar todas as mudanças de uma sessão e reiniciar uma vez só.

---

## ⏳ Táticas

### `openclaw thinking` não existe nessa versão (2026-04-01 | expira 2026-05-01)
O comando `openclaw thinking medium/off` não está disponível na versão atual. Reasoning é controlado com `/reasoning` dentro do chat.

### `reserveTokensFloor` fica em `compaction`, não em `agents.defaults` diretamente (2026-04-01 | expira 2026-05-01)
O path correto é `agents.defaults.compaction.reserveTokensFloor`, não `agents.defaults.reserveTokensFloor`.

---

*Revisão mensal: deletar táticas vencidas.*
