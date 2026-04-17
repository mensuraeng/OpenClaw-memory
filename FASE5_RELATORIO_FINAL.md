# FASE 5 — Relatório Final

_Encerrada em 2026-04-17. Refactor de scripts para padrão "gerar payload → Flávia consolida → saída final"._

---

## Contexto

A FASE 3 reescreveu a identidade da Flávia (cérebro central) e formalizou a regra de ouro no `AGENTS.md`:

> Toda saída externa (email, mensagem, post, anúncio) passa por mim antes.
> Scripts e crons NUNCA falam diretamente com Telegram, email ou qualquer canal externo.
> Lógica padrão: `gerar dados → eu recebo → eu decido → saída final`.

A FASE 4 auditou `scripts/` e identificou 8 scripts ativos violando a regra (categoria 3) + 1 com migração incompleta + 1 helper canônico quebrado.

A FASE 5 corrigiu tudo, em sub-fases cirúrgicas com aprovação ponto a ponto do Alê.

---

## Tabela consolidada

| Sub-fase | Script | Antes (bytes) | Depois (bytes) | Cron real | Domínio | Helper canônico usado | Commit |
|---|---|---:|---:|---|---|---|---|
| 5.0 | `send_to_flavia.py` (helper) | 550 | 2.040 | — | — | (criou o canônico) | `c3c9369` |
| 5.1 | `ccsp_relatorio_semanal.py` | 1.890 | 1.769 | seg 8h BRT | MIA / CCSP | `send_to_flavia` | `c3c9369` |
| 5.2 | `ccsp_rdo_cobranca.py` | 4.083 | 4.752 | seg-sex 16:30 BRT | MIA / CCSP | `send_to_flavia` + `msgraph_email` | `8ab6bfc` |
| 5.3 | `ccsp_manha_victor.py` | 15.414 | 15.795 | seg-sex 8h BRT | MIA / CCSP | `send_to_flavia` + `msgraph_email` | `bc85721` |
| 5.4 | `relatorio_cursos_telegram.py` | 4.940 | 5.357 | sex 16h BRT | formação | `send_to_flavia` | `cbcbd0b` |
| 5.5 | `contas_pagar_telegram.py` | 4.493 | 5.072 | seg 10h BRT | financeiro | `send_to_flavia` | `cbcbd0b` |
| 5.6 | `relatorio_analytics.py` | 11.025 | 12.054 | manual | BI / analytics web | `send_to_flavia` | `750c914` |
| 5.7 | `licitacoes_email.py` | 9.757 | 10.762 | seg 9h BRT (lock semanal) | PCS / licitações | `send_to_flavia` + `msgraph_email` | `750c914` |
| 5.8 | `send_relatorio_cursos.sh` | 539 | 1.052 | manual | formação | `send_to_flavia` | `750c914` |
| 5.9 | `monitor_semanal.py` | 10.811 | 12.119 | seg 8h BRT | monitoramento executivo (multi) | `send_to_flavia` | `8f994ad` |

**Total:** 1 helper canônico criado, 9 scripts migrados.

---

## Helpers canônicos

### `scripts/send_to_flavia.py`

Ponto único de entrega de payload à Flávia. Lê dict JSON de stdin (ou recebe via `send_to_flavia(payload)` quando importado), serializa, dispara `openclaw agent --agent main --message <json>`. Captura resposta + erros, exit code real, timeout configurável.

Convenção sugerida de payload:
```json
{
  "source":   "<nome_do_script>",
  "kind":     "<tipo_de_evento>",
  "project":  "<projeto> | null",
  "company":  "MENSURA | MIA | PCS | null",
  "domain":   "<domínio_funcional>",
  "urgency":  "low | normal | high | critical",
  "scheduled_at": "<isoformat>",
  "body":     "<conteúdo principal>",
  "external_action": { /* opcional, p/ rotinas pré-autorizadas */ }
}
```

### `scripts/msgraph_email.py` (já existia, agora canônico)

Helper de envio MS Graph. Não foi modificado nesta fase — passou a ser invocado via `subprocess` pelos scripts que mantêm rotina pré-autorizada de email (5.2, 5.3, 5.7).

---

## Padrões formalizados

### Fluxo padrão (regra de ouro)
```
script → gera payload → send_to_flavia.py → Flávia consolida → saída final
```

### Quando há email institucional preservado (rotinas pré-autorizadas — 5.2, 5.3, 5.7)
```
script → 1. envia payload em paralelo à Flávia (visibilidade + veto)
       → 2. envia email via msgraph_email.py (helper canônico)

policy = "pre_authorized_routine" no payload sinaliza explicitamente
que é rotina automática autorizada (destinatário/cc/cadência/template
estáveis), Flávia tem visibilidade e pode interromper.
```

### Flags padronizadas adicionadas
- `--dry-run` → não envia email; mostra preview no stderr (5.2, 5.3, 5.7)
- `--skip-email` → só entrega payload à Flávia (5.2, 5.3, 5.7)
- `--skip-flavia` → só executa parte local; não entrega à Flávia (5.4, 5.5, 5.6, 5.9)
- `--skip-scan` → pula coleta de dados externos (5.5)
- `--print` → alias retrocompat para `--skip-flavia` (5.6, 5.9)
- `--force` → ignora janela e lock semanal (5.7, já existia)

---

## Commits

```
8f994ad fase 5.9: finaliza migração de monitor_semanal.py
750c914 fase 5.6+5.7+5.8: migra analytics, licitacoes_email e cursos.sh
cbcbd0b fase 5.4+5.5: migra relatorio_cursos_telegram e contas_pagar_telegram
bc85721 fase 5.3: migra ccsp_manha_victor.py (opção B - email pré-autorizado)
8ab6bfc fase 5.2: migra ccsp_rdo_cobranca.py (opção B - email pré-autorizado)
c3c9369 fase 5.0+5.1: corrige helper send_to_flavia e migra ccsp_relatorio_semanal
```

Mais 2 commits relacionados de SOUL.md (regra `Execução técnica densa`):
```
7d820a2 soul: ajusta regra "Execução técnica densa" para usar --session-id
d131221 soul: adiciona regra "Execução técnica densa (modo análise)"
```

---

## Backups disponíveis (`scripts/*.bak`)

Cada script tem backup com timestamp UTC do momento da edição. Pattern:
`<script>.pre-flavia-fase5.<TS>.bak` ou `<script>.bak-<TS>`.

| Script | Backup |
|---|---|
| `send_to_flavia.py` | `send_to_flavia.py.bak-20260417T133930Z` |
| `ccsp_relatorio_semanal.py` | `.pre-flavia-fase5.20260417T134616Z.bak` |
| `ccsp_rdo_cobranca.py` | `.pre-flavia-fase5.20260417T140014Z.bak` |
| `ccsp_manha_victor.py` | `.pre-flavia-fase5.20260417T141123Z.bak` |
| `relatorio_cursos_telegram.py` | `.pre-flavia-fase5.20260417T141548Z.bak` |
| `contas_pagar_telegram.py` | `.pre-flavia-fase5.20260417T141727Z.bak` |
| `relatorio_analytics.py` | `.pre-flavia-fase5.20260417T142407Z.bak` |
| `licitacoes_email.py` | `.pre-flavia-fase5.20260417T142407Z.bak` |
| `send_relatorio_cursos.sh` | `.pre-flavia-fase5.20260417T142407Z.bak` |
| `monitor_semanal.py` | `.pre-flavia-fase5.20260417T143929Z.bak` |

---

## Rollback

### Reverter sub-fase específica
```bash
cd /root/.openclaw/workspace
git revert <commit>      # ex.: git revert bc85721 (5.3 sozinha)
```

### Reverter toda a FASE 5 de uma vez
```bash
cd /root/.openclaw/workspace
git revert --no-commit 8f994ad 750c914 cbcbd0b bc85721 8ab6bfc c3c9369
git commit -m "rollback fase 5 completa"
```

### Restaurar 1 script via backup direto
```bash
cp scripts/<script>.pre-flavia-fase5.<TS>.bak scripts/<script>
chmod +x scripts/<script>
```

---

## Estado atual do sistema

### Scripts ativos verificados (zero chamadas diretas a canal externo)
```bash
grep -l "api\.telegram\|graph\.microsoft\.com.*sendMail" \
  scripts/*.py scripts/*.sh | grep -v "\.bak$" | grep -v "msgraph_email.py"
# → vazio
```

### Validação por script (3 critérios obrigatórios)

Cada sub-fase foi validada com payload real (ou sintético quando dependia de venv externo) através do helper. A Flávia precisou demonstrar:
1. **recebeu o payload** (citou dados específicos do conteúdo)
2. **identificou o domínio** (empresa/projeto correto)
3. **tomou decisão correta** (resolveu direta / delegou / bloqueou)

Resultado: **10/10 sub-fases passaram nos 3 critérios**. Detalhamento das respostas da Flávia está nas mensagens de commit individuais.

### Comportamentos observados como bonus
- 5.5 (contas): identificou ruído no JSON (marketing classificado como conta a pagar)
- 5.6 (analytics): extraiu insight estratégico (MENSURA mais encontrável, MIA depende de marca)
- 5.7 (licitações): priorizou 3 urgentes do dia + classificou alerta como "alto"
- 5.8 (cursos): descartou MBA da rotina ("foge do critério de cursos curtos")
- 5.9 (monitor): cruzou com contexto financeiro da fase 5.5 (memória de sessão)

### Próximas execuções reais de cron
- **hoje sex 16h BRT:** 5.4 (cursos) — 1ª pelo novo fluxo
- **hoje sex 16:30 BRT:** 5.2 (RDO Victor) — 1ª via helper canônico de email
- **seg 20/04 8h BRT:** 5.3 (manhã Victor) + 5.9 (monitor) — 1ª pelo novo fluxo
- **seg 20/04 9h BRT:** 5.7 (licitações PCS) — 1ª via helper de email + lock semanal
- **seg 20/04 10h BRT:** 5.5 (contas) — 1ª via Flávia para domínio financeiro

### Próximo cron silencioso quebrado
Antes da FASE 5, `monitor_semanal.py` rodava toda segunda 8h BRT mas não enviava nada (estava silencioso desde 16/04 — 1 semana sem alerta de obras). A partir de segunda 20/04, volta a entregar à Flávia.

---

## Achados para fases seguintes

### FASE 6 (cron — não iniciada)
- Padronizar logs (alguns vão pra `/tmp/`, outros pra logs do workspace)
- Avaliar se o cron de 5.7 precisa ajuste agora que tem janela + lock interno
- Documentar dependências (5.6 precisa de venv com `google-analytics-data`)

### FASE 7 (limpeza — não iniciada)
- 5 backups antigos (`.pre-flavia.*.bak`, `.bak.<ts>`) de antes da FASE 5 ainda em `scripts/`. Avaliar promoção para `backups/`.
- Renomear `relatorio_contas_telegram.py` (não envia direto, nome enganoso) — flagrado na FASE 4
- Inconsistência de dados em `monitor_semanal.py`: usa "CCSP Casa 3" + site `CCSP-CasaCapela3`, mas AGENTS.md já corrigiu para "CCSP Casa 7"
- Refinar filtros `KEYWORDS_SUBJECT/IGNORE` em `contas_pagar.py` (Flávia sinalizou ruído na 5.5)
- Refinar `KEYWORDS_ALERTA` em `monitor_semanal.py` (Flávia sinalizou falso positivo na 5.9)
- 8 dirs `_old_*` em `~/.openclaw/agents/` continuam intocados (regra original: nunca remover agents)
- 38 transcripts órfãos em `agents/main/sessions` que o doctor quer arquivar

### Pendência arquitetural
- A regra "Execução técnica densa (modo análise)" no SOUL.md aponta para `openclaw agent --agent main --session-id <novo-id>` como mecanismo provisório. `sessions_spawn` nativo está previsto para versão futura do OpenClaw.

---

## Checklist final FASE 5

- [x] 1 helper canônico criado e funcional (`send_to_flavia.py`)
- [x] 9 scripts migrados (zero chamadas diretas a canal externo)
- [x] Cada migração validada com 3 critérios na resposta real da Flávia
- [x] Backups com TS preservados para todos os scripts modificados
- [x] Commits granulares no git do workspace
- [x] Rollback documentado por commit ou por arquivo
- [x] Email institucional preservado para rotinas pré-autorizadas (3 casos: Victor RDO, Victor manhã, alexandre@pcsengenharia)
- [x] Bindings de Telegram NÃO foram alterados (intocados desde a FASE 3)
- [x] Crons NÃO foram alterados (próxima fase)
- [x] Nenhum agente foi removido (`agents.list` segue main + finance + mia + mensura + pcs)

**FASE 5: encerrada.**
