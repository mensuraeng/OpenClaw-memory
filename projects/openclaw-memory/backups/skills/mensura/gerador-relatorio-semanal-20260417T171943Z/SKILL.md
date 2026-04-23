# SKILL — Gerador de Relatório Semanal MENSURA

_Skill do agente `mensura`. Não roda sozinho — é invocado pela Flávia quando ela delega "gerar relatório da semana de \<obra\>"._

---

## Quando esta skill é acionada

A Flávia me invoca quando recebe input com:

- cronograma atualizado (arquivo `.mpp`, planilha, ou texto estruturado)
- ata de reunião semanal da obra
- pacote de dados (texto/markdown/JSON) com indicadores e plano de ação

E o objetivo é **publicar o relatório executivo semanal** da obra no GitHub + GitHub Pages, com snapshot versionado em `mensuraeng/openclaw-context`.

Hoje a única obra mapeada é **`pg-louveira`** (Laboratório Sensorial P&G — Louveira-SP, construtora SUM Engenharia). Outras obras podem ser adicionadas ao mapping `OBRAS` em `scripts/gerar_relatorio.py`.

---

## O que eu faço (passo a passo)

### 1. Recebo o pacote de inputs

A Flávia me entrega:

- cronograma (com data-base, % previsto, % executado, atividades não cumpridas)
- ata da reunião (decisões, escalações, novos riscos, ações)
- comparação com semana anterior (executado anterior, SPI anterior)

### 2. Extraio os indicadores obrigatórios

Para cada relatório, eu extraio (ou peço à Flávia se faltar):

| Campo | Tipo | Origem usual |
|---|---|---|
| % executado geral | número | cronograma — curva S |
| % previsto geral | número | cronograma — curva S |
| desvio (pp) | calculado | executado − previsto |
| SPI | número | EVM — EV / PV |
| BEI | número | indicador customizado MENSURA |
| Tarefas pendentes | inteiro | filtro do cronograma (status ≠ concluído) |
| Tarefas no caminho crítico | inteiro | atividades críticas com % < 100 |
| Top 5–11 riscos | lista | matriz P×I da ata + cronograma |
| Plano de ação | lista | ata: responsável + descrição + prazo |
| Lookahead 3 semanas | lista | cronograma: próximas 3 janelas |
| Comparativo semanal | tabela | dado da semana atual vs anterior |
| Diagnóstico geral | texto | resumo da Flávia/Alê |
| Indicador crítico | texto | apontamento mais grave da semana |
| Áreas de avanço | lista | breakdown por frente da obra |
| Metas baseline não cumpridas | lista | atividades que iam fechar e não fecharam |
| Cenários preditivos | provável + pessimista | projeção de término |
| Diretrizes da semana | lista | comandos executivos do Alê |

Se algum campo obrigatório não veio no input, **eu pergunto à Flávia antes de prosseguir**. Não invento número.

### 3. Preencho o `relatorio.json`

Path: `~/.openclaw/workspace/knowledge/<repo-da-obra>/src/data/relatorio.json`
(para `pg-louveira` é `~/.openclaw/workspace/knowledge/P-G---Louveira/src/data/relatorio.json`)

Schema obrigatório (não invento campos novos sem validar com a Flávia):

```json
{
  "meta": {
    "numero": "002",
    "data": "YYYY-MM-DD",
    "semana": "002",
    "projeto": "...",
    "cliente": "...",
    "local": "...",
    "construtora": "...",
    "termino_meta": "YYYY-MM-DD",
    "termino_meta_label": "DD/MM/YYYY",
    "dias_restantes": 80,
    "status_data": "YYYY-MM-DD",
    "emissao": "YYYY-MM-DD",
    "avanco_previsto": 81.03,
    "avanco_executado": 45.49,
    "desvio_acumulado": -35.54
  },
  "dashboard": {
    "executado_geral": 45.49,
    "laboratorio_sensorial": 63,
    "tarefas_pendentes": 395,
    "tarefas_total": 681,
    "caminho_critico": 25,
    "spi": 0.56,
    "bei": 0.42,
    "gap": -35.54,
    "cards": [ { "label", "value", "detail", "delta", "color" } ]
  },
  "diagnostico": {
    "status_geral": "critico|alerta|ok",
    "resumo": "...",
    "indicador_critico": "...",
    "complemento": "...",
    "paralisacoes": [ { "duracao_dias", "causa", "status" } ]
  },
  "avanco_areas": [ { "label", "current", "target", "prevLabel" } ],
  "metas_baseline": [ { "title", "tasks": [ { "pct", "name", "date" } ] } ],
  "lookahead": [ { "semana", "tarefas": [ { "color", "text" } ] } ],
  "comparativo": [ { "name", "s1", "s2", "delta", "up", "semana_1_label", "semana_2_label" } ],
  "acoes": [ { "responsavel", "descricao", "prazo", "status": "critico|andamento|concluido|pendente" } ],
  "riscos": [ { "id", "categoria", "descricao", "probabilidade", "impacto", "score", "status": "aberto|andamento|mitigado|fechado", "prazo", "detalhe" } ],
  "preditivo": [ { "label", "probabilidade_pct", "data", "color", "descricao" } ],
  "diretrizes": [ { "color", "text" } ]
}
```

**Regras inegociáveis ao preencher:**

- `meta.semana` em formato `NNN` (zero-padded 3 dígitos) — `002` não `2`
- `meta.data` ISO `YYYY-MM-DD` — não DD/MM/YYYY
- `riscos[].score = probabilidade × impacto` (validar)
- `comparativo` com mesmos labels de semana em todas as linhas (UI usa só a primeira)
- `status` em PT-BR conforme enums acima

### 4. Disparo o build + upload

```bash
cd /root/.openclaw/workspace
python3 scripts/gerar_relatorio.py --obra <obra>
```

Isso, sequencialmente:

1. Lê o `relatorio.json` para extrair `data` e `semana`
2. Roda `npm run build` no template (Vite + React + Tailwind)
3. Copia `dist/` para `openclaw-context/relatorios/<dominio>/<obra>/<YYYY-MM-DD_semana-NNN_<obra>>/`
4. `git add + commit + push` no openclaw-context
5. Verifica `https://mensuraeng.github.io/<repo-da-obra>/` está respondendo
6. Notifica a Flávia com payload completo

Se eu quiser validar antes sem efeitos: `--dry-run`. Se quiser só buildar sem subir: `--skip-upload`.

### 5. Devolvo para a Flávia

Ela recebe o payload via `send_to_flavia` com:

- `github_url` — link do snapshot versionado em `openclaw-context`
- `github_pages_url` — link do GitHub Pages (visualização interativa)
- `github_pages_status` — `ativo` / `inativo` / `desconhecido`

Eu também devolvo à sessão da Flávia:

- **Resumo executivo em até 5 linhas** com os indicadores-chave da semana
- **Alertas críticos destacados** (riscos score ≥ 20, ações `critico`, status_geral `critico`)
- **Link do GitHub Pages** quando ativo (formato visual para o cliente)

---

## O que eu não faço

- ❌ Não envio o relatório por email/Telegram a cliente — quem decide saída externa é a Flávia + Alê (regra de ouro do `AGENTS.md`)
- ❌ Não invento dado quando o input está incompleto — pergunto à Flávia
- ❌ Não comito o `relatorio.json` no repo P-G---Louveira sem antes validar que o build passa localmente
- ❌ Não modifico o template React (`App.tsx`, `ReportComponents.tsx`) — só edito o JSON. Mudanças estruturais no template são tarefa separada de engenharia.
- ❌ Não mexo em outras obras sem instrução — meu mapping atual cobre só `pg-louveira`
- ❌ Não ativo GitHub Pages programaticamente. Se `github_pages_status` voltar `inativo`, sinalizo à Flávia para o Alê ativar manualmente em **Settings → Pages** do repo (Source: `main` ou `gh-pages`, branch que serve `dist/`)

---

## Bandeiras vermelhas — paro e devolvo à Flávia

- Cronograma ou ata sem data-base clara
- Indicador inconsistente (ex.: SPI > 1 mas executado < previsto)
- Risco com score que não bate com `probabilidade × impacto`
- Status inválido (fora dos enums PT-BR)
- Ação sem responsável nominal
- `npm run build` falha (output vai para o log, eu sinalizo qual módulo quebrou)
- `git push` no openclaw-context falha (autenticação SSH? conflito?)
- GitHub Pages 404 quando deveria estar ativo (alerto, mas não tento ativar)

---

## Ativação inicial do GitHub Pages (uma vez, manual)

Para o `mensuraeng/P-G---Louveira` servir o relatório como SPA:

1. Abrir https://github.com/mensuraeng/P-G---Louveira/settings/pages
2. **Source:** GitHub Actions (recomendado) ou Deploy from a branch
3. Se "branch": criar branch `gh-pages` com conteúdo de `dist/` (workflow CI ou manual)
4. Se "GitHub Actions": configurar workflow `.github/workflows/pages.yml` que roda `npm install && npm run build` e publica `dist/`
5. Após primeiro deploy, o URL `https://mensuraeng.github.io/P-G---Louveira/` fica ativo

**Nota:** o `dist/` está no `.gitignore` do repo P-G---Louveira (padrão Vite). Sem workflow CI/CD ou branch específica, o GitHub Pages **não tem o que servir**. Solução cleanest: GitHub Action que builda e publica.

---

## Referências

- Script orquestrador: `~/.openclaw/workspace/scripts/gerar_relatorio.py`
- Template React: `~/.openclaw/workspace/knowledge/P-G---Louveira/`
- Snapshot versionado: `~/.openclaw/workspace/knowledge/openclaw-context/relatorios/mensura/pg-louveira/`
- Helper canônico de entrega à Flávia: `~/.openclaw/workspace/scripts/send_to_flavia.py`
- Log de execuções: `~/.openclaw/workspace/logs/cron/upload-relatorios.log`
- Identidade institucional MENSURA: `~/.openclaw/workspace-mensura/IDENTITY.md` + `SOUL.md` + `AGENTS.md`
