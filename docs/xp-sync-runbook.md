# XP Experiência daily sync — runbook

**Instalado:** 2026-04-22
**Propósito:** todo dia às 07:00 BRT, baixar o extrato (OFX) da conta corrente PJ da MIA Engenharia na XP, ingerir, conciliar com `contas_pagar.json`, gravar em `memory/integrations/xp/` e notificar o Alê no Telegram.

## Arquitetura

```
Alê's Windows (alesurface, 100.88.24.55)          |  Server (srv1546384, 100.124.198.120)
─────────────────────────────────────────────────── ┼ ────────────────────────────────────────
Chrome (--remote-debugging-port=9222 ,            |  07:00 BRT — systemd timer fires
        --user-data-dir=%TEMP%\chrome-xp-capture) |  xp-sync.service → xp_sync.py
  aba em experiencia.xpi.com.br/bankline/#/extrato |     connect via CDP → 100.88.24.55:9222
                   ↑                              |     drive Exportar → 30 dias → OFX → Exportar
                   │           Tailscale          |     intercept /statements API response
                   └──────────────────────────────┼──── decode base64 → OFX file
                                                  |     parse → JSON in memory/integrations/xp/
                                                  |     conciliate vs memory/contas_pagar.json
                                                  |     write daily-reports/YYYY-MM-DD.md
                                                  |     send Telegram summary
```

**Por que passa pelo Chrome do Alê (CDP) em vez de Chromium no servidor:**
a XP usa Akamai/CDN com anti-bot. O IP do servidor foi temporariamente blacklistado durante o desenvolvimento. Chamar a API direto do servidor retorna 403 "Acesso Bloqueado". Passar pelo Chrome do Alê (na residencial dele, via Tailscale) resolve e é legítimo — é a sessão dele sendo usada.

## Pré-requisito diário (recorrente)

**Chrome do Alê precisa estar aberto com CDP habilitado, e logado na XP**, quando o timer dispara. Se ele desligar a máquina à noite, a sync pula.

### Setup inicial no Windows

1. Feche todas as janelas do Chrome.
2. Abra PowerShell e cole:
   ```powershell
   $dir = "$env:TEMP\chrome-xp-capture"
   New-Item -ItemType Directory -Force -Path $dir | Out-Null
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" `
     --remote-debugging-port=9222 `
     --remote-debugging-address=0.0.0.0 `
     --user-data-dir="$dir"
   ```
3. Expor a porta 9222 pela Tailscale (1x, persistente entre boots se desejar):
   ```powershell
   netsh interface portproxy add v4tov4 listenport=9222 listenaddress=0.0.0.0 connectport=9222 connectaddress=127.0.0.1
   ```
4. Entre em `https://experiencia.xpi.com.br/`, faça login (CPF+senha+token), marque **"Lembrar dispositivo"**.
5. A partir daí, a máquina de dev permanece logada por 30-90 dias (até XP invalidar).

### Quando a sessão expirar

- O cron diário emite alerta no Telegram: `"XP session expired — open Chrome, log in, retry"`.
- Abra o Chrome (mesmo `--user-data-dir=%TEMP%\chrome-xp-capture`), loga de novo (token do app).
- No próximo dia, volta ao normal.

### Automatizar startup no Windows (opcional)

Crie um script `chrome-cdp-autostart.bat` em `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`:
```batch
@echo off
set DIR=%TEMP%\chrome-xp-capture
if not exist "%DIR%" mkdir "%DIR%"
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 --user-data-dir="%DIR%"
```
Assim o Chrome abre automaticamente ao iniciar o Windows.

## Layout no servidor

```
/root/.openclaw/
├── bin/
│   ├── xp_sync.config.json     # paths, timezone, telegram, cdp_url
│   └── xp_sync.env             # TELEGRAM_BOT_TOKEN (0600)
├── credentials/xp-experiencia/
│   ├── storage_state.json      # fallback cookies (não usado no modo CDP)
│   └── browser_profile/        # idem (não usado no modo CDP)
├── mia-finance/raw/xp/
│   └── YYYY-MM-DD.ofx          # OFXs baixados (histórico)
└── workspace/
    ├── scripts/
    │   ├── xp_sync.py           # pipeline principal
    │   └── xp_login_capture.py  # reserva: capturar sessão via noVNC se CDP falhar
    ├── integrations/xp/
    │   └── templates/           # 4 planilhas-modelo (PIX chave/dados, Boleto, TED)
    └── memory/integrations/xp/
        ├── transactions/YYYY-MM-DD.json
        └── daily-reports/YYYY-MM-DD.md

/etc/systemd/system/
├── xp-sync.service
└── xp-sync.timer
```

## Operação

### Status

```bash
systemctl list-timers xp-sync.timer --all
journalctl -u xp-sync.service -n 30 --no-pager
```

### Rodar manualmente

```bash
systemctl start xp-sync.service
# ou direto:
set -a && . /root/.openclaw/bin/xp_sync.env && set +a
/root/.openclaw/venvs/notebooklm/bin/python /root/.openclaw/workspace/scripts/xp_sync.py
```

### Rodar com OFX manualmente baixado (quando CDP não está disponível)

```bash
# Coloca o arquivo em /root/.openclaw/mia-finance/raw/xp/
/root/.openclaw/venvs/notebooklm/bin/python /root/.openclaw/workspace/scripts/xp_sync.py \
    --ofx /root/.openclaw/mia-finance/raw/xp/extrato-XX-XX-XXXX.ofx
```

### Desabilitar temporariamente

```bash
systemctl disable --now xp-sync.timer
```

## Troubleshooting

| Sintoma | Causa | Ação |
|---|---|---|
| `XP session expired` | JWT/cookies expiraram | Abrir Chrome na Windows, re-logar, rodar `systemctl start xp-sync.service` |
| `Exportar toolbar not clickable` | Drawer aberto de run anterior | Script já tem retry; se persistir, fechar/reabrir Chrome |
| Conexão CDP falha | Chrome do Alê fechou | Reabrir Chrome com o PowerShell snippet acima |
| `Acesso Bloqueado` no HTML | Chamada direta sem CDP acionou CDN block | Só usar modo CDP; nunca rodar fluxos headless no servidor |
| Nenhuma transação nova | Período repetido | Esperado: dedupe por `tx_id` (hash data+desc+valor+fitid) |
| 0 conciliações | `contas_pagar.json` sem campo `valor` numérico | Backlog: enriquecer extração de emails pra capturar valores |

## Evolução futura

- **Fase 2 (pagamentos em lote)** — geração programática de XLSX pros 4 formatos XP a partir de `contas_pagar.json`. Requer enrichment primeiro.
- **Enrichment de contas_pagar.json** — extrair valores numéricos e datas dos emails triados.
- **Fallback sem CDP** — noVNC + `xp_login_capture.py` caso Chrome do Alê não esteja disponível.
- **Histórico de saldos** — armazenar LEDGERBAL do OFX pra trend.
