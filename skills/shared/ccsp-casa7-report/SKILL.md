---
name: ccsp-casa7-report
description: Processa relatórios semanais de obra HTML da Casa 7 (CCSP), executada pela MIA Engenharia. Use este skill quando o usuário encaminhar ou mencionar um relatório semanal da obra Casa 7 CCSP. O skill salva o relatório no histórico, extrai prazos e itens críticos do HTML, cria crons duráveis às 9h para cada prazo-chave e envia e-mails de lembrete para a equipe MIA. Também atualiza o INDEX.md e faz commit no git.
---

# CCSP Casa 7 — Processamento de Relatório Semanal

## Contexto da Obra

- **Obra:** Casa 7 — CCSP (Centro Cultural São Paulo)
- **Executor:** MIA Engenharia
- **Gerenciadora:** TOOLS (Rafael Dias, Gustavo)
- **Engenheiro de campo:** Victor Evangelista

## Diretório de Histórico

```
/root/.openclaw/workspace/projects/ccsp-casa7/relatorios/
```

Padrão de nome: `CCSP_Casa7_RevXXX_DD.MM.AAAA.html`

## Destinatários de E-mail

- **TO:** victor.evangelista@miaengenharia.com.br
- **CC:** alexandre@miaengenharia.com.br, andre@miaengenharia.com.br

## Fluxo de Execução

### 1. Salvar o Relatório

Copiar ou mover o arquivo HTML recebido para o diretório de histórico com o nome correto. Se o arquivo ainda não está no local certo, usar Bash para copiar:

```bash
cp <arquivo_origem> /root/.openclaw/workspace/projects/ccsp-casa7/relatorios/CCSP_Casa7_RevXXX_DD.MM.AAAA.html
```

### 2. Parsear o HTML

Usar Read para ler o HTML salvo. Extrair:
- **Data do relatório** (cabeçalho ou título)
- **Avanço global (%)** (ex: "59%")
- **Semana atual / total** (ex: "5/9")
- **Itens críticos com prazo** — especialmente da aba "Plano de Ação" e "Pontos Críticos":
  - Decisões pendentes com data-limite
  - Atividades no caminho crítico com data prevista
  - Pendências TOOLS com data de aprovação necessária
  - Qualquer item com prazo explícito em formato DD/MM ou DD/MM/AAAA

### 3. Criar Crons Duráveis

Para **cada prazo-chave** identificado, criar um cron durable com `CronCreate`:

```
durable: true
once: true (não recorrente)
schedule: 9h do dia anterior ao prazo (ou do próprio dia se urgente)
```

**Prompt do cron** (template):
```
Enviar e-mail via himalaya para a equipe MIA sobre prazo CCSP Casa 7:

himalaya --account mensura message send \
  --subject "CCSP Casa 7 — Lembrete: [DESCRIÇÃO DO ITEM] — prazo [DATA]" \
  --to "victor.evangelista@miaengenharia.com.br" \
  --cc "alexandre@miaengenharia.com.br" \
  --cc "andre@miaengenharia.com.br" \
  --body "Victor,

Lembrete de prazo crítico da obra Casa 7 — CCSP:

📋 Item: [DESCRIÇÃO COMPLETA DO ITEM]
📅 Prazo: [DATA]
📊 Contexto: Relatório [RevXXX] de [DATA_RELATORIO] — Avanço global [X]%

[OBSERVAÇÃO ADICIONAL SE HOUVER — ex: caminho crítico, risco de atraso na entrega]

Atenciosamente,
Sistema de Monitoramento MIA"
```

### 4. Atualizar INDEX.md

Adicionar nova linha na tabela do INDEX.md em `/root/.openclaw/workspace/projects/ccsp-casa7/relatorios/INDEX.md`:

```markdown
| RevXXX | DD/MM/AAAA | N/9 | XX% | [Destaque principal da semana] |
```

Adicionar também na seção "Arquivos":
```markdown
- [RevXXX — DD/MM/AAAA](CCSP_Casa7_RevXXX_DD.MM.AAAA.html)
```

### 5. Git Commit

```bash
git -C /root/.openclaw/workspace add projects/ccsp-casa7/relatorios/
git -C /root/.openclaw/workspace commit -m "feat(ccsp-casa7): relatório semanal RevXXX — DD/MM/AAAA, avanço XX%"
```

### 6. Confirmar ao Usuário

Resumir:
- Arquivo salvo
- Quantos crons criados e para quais datas/itens
- Situação atual da obra (avanço %, semana N/9, destaque principal)

## Envio de E-mail Manual (Himalaya)

Conta configurada: `mensura` (alexandre@mensuraengenharia.com.br)

```bash
himalaya --account mensura message send \
  --subject "ASSUNTO" \
  --to "destinatario@email.com" \
  --cc "copia@email.com" \
  --body "CORPO DO E-MAIL"
```

## Atualizar Memória do Projeto

Após processar o relatório, atualizar `/root/.claude/projects/-root--openclaw-workspace/memory/project_ccsp_casa7.md`:
- Tabela de relatórios salvos
- Situação atual (avanço, semana, destaques críticos)
