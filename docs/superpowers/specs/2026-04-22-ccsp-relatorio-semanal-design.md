# CCSP Casa 7 — Relatório Semanal Automatizado

**Data:** 2026-04-22  
**Status:** Aprovado  
**Empresa:** MIA Engenharia  
**Operado por:** OpenClaw (Flávia)

---

## Objetivo

Automatizar a geração semanal do relatório HTML da obra CCSP Casa 7, a partir de um Excel de cronograma (Baseline 1 vs. real) e ata de reunião enviados via Telegram. O relatório é publicado no Cloudflare Pages em `relatorios.miaengenharia.com.br`.

---

## Arquitetura

```
Alê/Equipe (Telegram)
    │  Excel (.xlsx) + ata (texto) + MPP (opcional)
    ▼
Flávia (agente OpenClaw)
    │  detecta arquivos → salva em /tmp/ccsp-inputs/
    │  aciona ccsp_gerar_relatorio.py
    ▼
ccsp_gerar_relatorio.py
    ├─ lê Excel → % avanço por atividade, datas (openpyxl)
    ├─ lê MPP (opcional, via mpxj subprocess)
    ├─ calcula: PPC, avanço global, SPI, look ahead, desvios
    ├─ renderiza template.html → index.html + relatorios/YYYY-MM-DD.html
    ├─ preserva inputs em dados/YYYY-MM-DD_semana-NNN.xlsx + _ata.txt
    ├─ git commit + push → mensuraeng/ccsp-relatorios
    └─ send_to_flavia (link público + resumo)
    ▼
Cloudflare Pages (auto-deploy no push, ~30s)
    └─ relatorios.miaengenharia.com.br (ou ccsp.miaengenharia.com.br)
    ▼
Flávia envia link no Telegram/email para o cliente
```

---

## Estrutura do Repositório GitHub

```
mensuraeng/ccsp-relatorios/
├── index.html                         ← relatório mais recente (CF Pages serve aqui)
├── template.html                      ← template base versionado
├── relatorios/
│   ├── 2026-04-21_semana-016.html
│   ├── 2026-04-28_semana-017.html
│   └── ...
├── dados/
│   ├── 2026-04-21_semana-016.xlsx     ← Excel original preservado
│   ├── 2026-04-21_semana-016_ata.txt
│   └── ...
└── ccsp-casa7.json                    ← config: nomes de colunas, thresholds
```

---

## Estrutura de Dados — Excel (Baseline 1)

O Excel traz a programação comprometida na semana anterior (Baseline 1) e a atualização da semana atual. Colunas esperadas (nomes configuráveis em `ccsp-casa7.json`):

| Coluna | Descrição |
|---|---|
| `atividade` | Descrição da atividade / WBS |
| `pct_programado` | % programado (Baseline 1) |
| `pct_realizado` | % efetivamente executado |
| `data_inicio_plan` | Data de início planejada |
| `data_fim_plan` | Data de fim planejada |
| `data_fim_real` | Data de fim real ou prevista atualizada |
| `status` | Realizado / Não cumprido / Em andamento |
| `responsavel` | Responsável pela atividade |

Campos ausentes no Excel são tratados como `None` — o script sinaliza lacunas no relatório em vez de falhar silenciosamente.

---

## Cálculos Gerados pelo Script

| Indicador | Fórmula |
|---|---|
| **PPC** | `Σ(itens cumpridos) / Σ(itens programados) × 100` |
| **Avanço físico global** | Média ponderada das atividades com `pct_realizado` |
| **SPI** | `avanço_real / avanço_planejado` |
| **Itens não cumpridos** | `status == "Não cumprido"` → lista com responsável + nova data |
| **Look ahead (3 semanas)** | Atividades com `data_inicio_plan ≤ hoje+21d` ainda não iniciadas |
| **Desvios críticos** | `data_fim_real - data_fim_plan > threshold_dias` (configurável em ccsp-casa7.json) |

---

## Arquivo de Configuração `ccsp-casa7.json`

```json
{
  "obra": "CCSP Casa 7",
  "empresa": "MIA",
  "github_repo": "mensuraeng/ccsp-relatorios",
  "relatorio_url": "https://relatorios.miaengenharia.com.br",
  "sheet_name": "Cronograma",
  "colunas": {
    "atividade": "Atividade",
    "pct_programado": "% Programado",
    "pct_realizado": "% Realizado",
    "data_inicio_plan": "Início Planejado",
    "data_fim_plan": "Fim Planejado",
    "data_fim_real": "Fim Real/Previsto",
    "status": "Status",
    "responsavel": "Responsável"
  },
  "thresholds": {
    "desvio_critico_dias": 7,
    "look_ahead_dias": 21
  }
}
```

---

## Script Principal — `ccsp_gerar_relatorio.py`

**Interface CLI:**
```bash
python3 scripts/ccsp_gerar_relatorio.py \
  --xlsx /tmp/ccsp-inputs/semana-017.xlsx \
  --ata  /tmp/ccsp-inputs/semana-017_ata.txt \
  [--mpp /tmp/ccsp-inputs/semana-017.mpp] \
  [--semana 017] \
  [--dry-run]
```

**Responsabilidades:**
1. Validar e ler os arquivos de input
2. Extrair dados do Excel via openpyxl
3. Processar MPP opcional via mpxj (subprocess Java) se disponível
4. Calcular todos os indicadores
5. Renderizar `template.html` → `index.html` via Jinja2
6. Salvar cópia histórica em `relatorios/YYYY-MM-DD_semana-NNN.html`
7. Preservar inputs originais em `dados/`
8. `git add + commit + push` com mensagem padronizada
9. Verificar deploy Cloudflare Pages (HEAD request)
10. `send_to_flavia(payload)` com link + resumo de indicadores

**Flags:**
- `--dry-run`: valida inputs e mostra plano, sem commit/push/notificação
- `--skip-push`: gera HTML mas não faz push
- `--skip-flavia`: pula notificação à Flávia

**Contrato de saída (send_to_flavia):**
```json
{
  "source": "ccsp_gerar_relatorio.py",
  "kind": "relatorio_gerado",
  "project": "CCSP Casa 7",
  "company": "MIA",
  "semana": "017",
  "data": "2026-04-28",
  "indicadores": {
    "ppc": 87.5,
    "avanco_global": 43.2,
    "spi": 0.94,
    "itens_nao_cumpridos": 2,
    "desvios_criticos": 1
  },
  "github_url": "https://github.com/mensuraeng/ccsp-relatorios/blob/main/relatorios/2026-04-28_semana-017.html",
  "relatorio_url": "https://relatorios.miaengenharia.com.br"
}
```

---

## Git Flow

- **Auth:** token GitHub configurado via `~/.netrc` ou `GH_TOKEN` (já padrão no servidor)
- **Branch:** `main` (único, sem feature branches para relatórios)
- **Commit:** `CCSP Casa 7 — Semana 017 — 2026-04-28\nPPC: 87.5% | Avanço: 43.2% | Desvios: 1`
- **Histórico:** nunca sobrescreve arquivos de semanas anteriores (append-only em `relatorios/`)
- **`index.html`:** sobrescrito a cada semana (é o que Cloudflare Pages serve na raiz)
- **Sem force-push, sem rebase**

---

## Integração Flávia

A Flávia aciona o script quando recebe os inputs no Telegram. Não existe agendamento rígido — o relatório é gerado quando os dados chegam (geralmente segunda/terça).

**Cron job de lembrete (segunda 8h BRT):**  
Dispara apenas se a Flávia não tiver registrado recebimento de inputs na semana corrente. Envia lembrete ao Alê via Telegram:
> *"CCSP Casa 7 — ainda não recebi o Excel da semana. Pode enviar quando estiver pronto?"*

---

## Cloudflare Pages

- **Repo:** `mensuraeng/ccsp-relatorios`, branch `main`
- **Build command:** nenhum (HTML puro)
- **Output dir:** `/` (raiz)
- **Domínio:** `relatorios.miaengenharia.com.br` (ou `ccsp.miaengenharia.com.br`)
- **Deploy:** automático a cada push (~30s)

---

## MPP (Opcional)

Se o arquivo `.mpp` for enviado, o script tenta processá-lo via `mpxj` (biblioteca Java, invocada via subprocess). Se `mpxj` não estiver disponível ou falhar, o script continua com os dados do Excel e sinaliza no relatório que o MPP não foi processado. Nunca bloqueia a geração por ausência do MPP.

---

## Tratamento de Erros

| Situação | Comportamento |
|---|---|
| Excel não encontrado | Aborta, notifica Flávia com erro |
| Coluna do Excel ausente | Marca campo como `[FALTA]` no relatório, continua |
| MPP inválido ou mpxj ausente | Ignora MPP, continua com Excel, adiciona aviso no relatório |
| Push GitHub falhou | Notifica Flávia com erro, HTML gerado localmente em `/tmp/` |
| Cloudflare Pages não responde | Log de aviso, não bloqueia — deploy pode estar em andamento |

---

## Dependências Python

```
openpyxl     # leitura de Excel
jinja2       # renderização do template HTML
requests     # verificação do deploy CF Pages
```

MPP (opcional): `mpxj` via JAR executado por subprocess (Java deve estar disponível no servidor).

---

## Fora de Escopo

- Geração automática sem input humano (o relatório exige dados reais da obra)
- Integração direta com SharePoint/OneDrive (futuro, se necessário)
- Múltiplas obras no mesmo script (cada obra tem seu próprio script dedicado)
- Autenticação OAuth no GitHub (usa token pré-configurado no servidor)
