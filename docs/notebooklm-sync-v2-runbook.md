# NotebookLM daily sync — runbook

**Instalado em:** 2026-04-21
**Design:** [`notebooklm-sync-v2-design.md`](notebooklm-sync-v2-design.md)
**Substitui:** a tentativa anterior de 2026-04-18 (`docs/notebooklm-sync-operacao.md`,
agora em `scripts/legacy/`)

## O que este sync faz

Todo dia às **02:00 America/Sao_Paulo**, um cron systemd varre todos os
notebooks da conta NotebookLM, baixa a lista de notas de cada um, e
compara com o inventário do dia anterior. Somente o **delta** é
registrado na memória.

O conteúdo de cada nota é mantido como markdown em
`memory/integrations/notebooklm/notes/<notebook_id>/<note_id>.md`,
sobrescrito quando a nota muda e deletado quando a nota é removida.
Um changelog diário em `changes/YYYY-MM-DD.md` lista o que foi
`novo / editado / removido / renomeado` — só é criado quando há delta.

**Primeira execução de cada dia é silenciosa se o inventário está
vazio** (seed). Evita avalanche de "[novo]" no dia 1.

## Layout no disco

```
/root/.openclaw/
├── bin/
│   ├── nblm_sync.config.json    # config não-sensível (commitável)
│   └── nblm_sync.env            # TELEGRAM_BOT_TOKEN (0600, local only)
├── credentials/notebooklm/
│   └── storage_state.json       # cookies do Google (0600)
├── venvs/notebooklm/            # venv com notebooklm-py + pytest
└── workspace/
    ├── scripts/
    │   ├── nblm_sync.py         # script principal
    │   ├── test_nblm_sync.py    # pytest
    │   └── legacy/              # tentativa anterior arquivada
    └── memory/integrations/notebooklm/
        ├── _state/
        │   ├── inventory.json   # {nb_id → {note_id → {title, content_hash, …}}}
        │   └── errors.log       # append-only
        ├── notes/<nb_id>/<note_id>.md
        └── changes/YYYY-MM-DD.md

/etc/systemd/system/
├── notebooklm-sync.service
└── notebooklm-sync.timer
```

## Operação diária

### Status rápido

```bash
systemctl list-timers notebooklm-sync.timer --all
journalctl -u notebooklm-sync.service -n 30 --no-pager
```

### Rodar manualmente agora

```bash
systemctl start notebooklm-sync.service
# ou, direto:
set -a && . /root/.openclaw/bin/nblm_sync.env && set +a
/root/.openclaw/venvs/notebooklm/bin/python \
  /root/.openclaw/workspace/scripts/nblm_sync.py
```

### Dry-run (não escreve nada)

```bash
/root/.openclaw/venvs/notebooklm/bin/python \
  /root/.openclaw/workspace/scripts/nblm_sync.py --dry-run
```

### Ver o delta do dia

```bash
cat /root/.openclaw/workspace/memory/integrations/notebooklm/changes/$(date +%F).md
```

### Ver as notas indexadas

```bash
find /root/.openclaw/workspace/memory/integrations/notebooklm/notes -name '*.md'
```

## Quando a sessão do NotebookLM expira

Sintoma:
- `journalctl -u notebooklm-sync.service` mostra exit code 1 e a
  mensagem `NotebookLM sync: sessão expirada, rodar login`.
- Telegram recebe a mesma mensagem (chat_id `1067279351`).
- `memory/integrations/notebooklm/_state/errors.log` registra a
  falha.

**Como reautenticar** (requer browser headed visualizado via noVNC ou
qualquer cliente VNC):

```bash
# 1. subir Xvfb + x11vnc + noVNC
Xvfb :99 -screen 0 1280x960x24 -nolisten tcp &
x11vnc -display :99 -forever -shared \
       -passwd "$(openssl rand -base64 9)" \
       -rfbport 5900 -localhost -bg
websockify --web=/usr/share/novnc 100.124.198.120:6080 localhost:5900 &

# 2. rodar o login script (espera até 15 min pelo login)
DISPLAY=:99 /root/.openclaw/venvs/notebooklm/bin/python \
  /root/notebooklm_login_auto.py

# 3. abrir no browser:
#    http://100.124.198.120:6080/vnc.html?autoconnect=1&resize=scale
#    → login no Google → script salva cookies automaticamente

# 4. derrubar VNC quando terminar
pkill -f 'websockify.*6080'; pkill -f 'x11vnc.*5900'; pkill -f 'Xvfb :99'
```

Após o login bem-sucedido, rodar uma vez manualmente para validar:

```bash
systemctl start notebooklm-sync.service
journalctl -u notebooklm-sync.service -n 5
```

## Desabilitar temporariamente

```bash
systemctl disable --now notebooklm-sync.timer
```

Reabilitar:

```bash
systemctl enable --now notebooklm-sync.timer
```

## Desfazer tudo (descomissionar)

```bash
systemctl disable --now notebooklm-sync.timer
rm /etc/systemd/system/notebooklm-sync.{service,timer}
systemctl daemon-reload

rm -rf /root/.openclaw/workspace/memory/integrations/notebooklm
rm /root/.openclaw/bin/nblm_sync.{env,config.json}
rm /root/.openclaw/workspace/scripts/nblm_sync.py
rm /root/.openclaw/workspace/scripts/test_nblm_sync.py
```

(A credencial `storage_state.json` e o venv `venvs/notebooklm` não são
removidos — são compartilhados com outros usos do CLI NotebookLM.)

## Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Service sai com código 1 | Sessão NotebookLM expirada | Reautenticar (ver seção acima) |
| Service sai com código 2 | Exceção inesperada | `cat _state/errors.log`, ler stack trace |
| Service sai com código 3 | Problema com `nblm_sync.config.json` | Validar JSON e paths |
| `changes/<hoje>.md` não existe mas esperava delta | Seed silencioso (inventário estava vazio); ou não houve delta real | Conferir `_state/inventory.json` |
| `notify_telegram` não chega | `TELEGRAM_BOT_TOKEN` não setado no env do systemd | `systemctl show notebooklm-sync.service -p Environment` |
| Timer não dispara | Disabled, ou `Persistent=true` não acionou o catch-up | `systemctl list-timers --all` |

## Testes

```bash
# Unit tests (compute_diff — todos os cenários)
cd /root/.openclaw/workspace/scripts
/root/.openclaw/venvs/notebooklm/bin/python -m pytest test_nblm_sync.py -v
```

Hoje: **9/9 tests passando**, e o smoke contra a conta real deu
`18 notebooks / 1 nota / 0 deltas no 2º run`.

## Custo e desempenho

- Zero chamadas de LLM. Apenas RPC contra o NotebookLM.
- Uma run completa (18 notebooks) leva ~7 segundos.
- Log por run: uma linha no journald. Nenhum ruído.
