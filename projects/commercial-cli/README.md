# commercial CLI

CLI automática/controlada para comercial/marketing Mensura/MIA.

```bash
./bin/commercial status
./bin/commercial pipeline report --execute
./bin/commercial marketing daily --execute
./bin/commercial linkedin check-config
./bin/commercial linkedin preview --text "..."
./bin/commercial linkedin publish-auto --execute --text "..."
./bin/commercial ga4 status
./bin/commercial guardrails
```

Regras:
- LinkedIn pessoal e rotinas comerciais podem publicar/enviar automaticamente quando chamadas pelos subcomandos dedicados.
- `publish-auto` sempre renderiza preview antes do live post e bloqueia texto curto acidental.
- Sem `delete`, `remove` ou `upload`.
- Páginas institucionais ainda dependem de mapear `organization URN`/admin antes de publicação por página.
