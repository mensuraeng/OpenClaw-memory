# OpenClaw Skills — radar de infraestrutura

Atualizado em 2026-04-30.

## Fonte consultada

- Repositório: `https://github.com/openclaw/skills`
- Observação crítica do próprio README: o repositório é um arquivo histórico do ClawdHub e pode conter skills suspeitas/maliciosas. Portanto, qualquer skill externa deve passar por auditoria estática antes de instalação.

## Decisão executiva

Não instalar skills externas diretamente a partir desse repositório.

Caminho correto para salto de infraestrutura:

1. usar o repositório como radar de padrões;
2. auditar a skill candidata sem executar;
3. extrair a ideia útil;
4. transformar em skill interna enxuta ou script interno auditável;
5. versionar e validar no workspace/2nd-brain.

## Candidatas relevantes encontradas

### 1. `alon-github-security-audit`

Uso potencial: auditoria estática de repositórios/skills antes de confiar ou instalar.

Valor para a infra: alto. Resolve o risco de supply chain de skills externas.

Recomendação: criar/adaptar uma skill interna `skill-security-audit` para revisar qualquer skill antes de instalação.

### 2. `claw-security-scanner`

Uso potencial: scanner de skills para detectar backdoors, mineradores, roubo de credenciais e comportamento suspeito.

Valor para a infra: alto.

Risco: precisa auditoria forte antes de uso, justamente por ser uma skill que opera sobre segurança.

Recomendação: não instalar direto; usar como referência para scanner interno.

### 3. `doro-git-secrets-scanner`

Uso potencial: varredura de segredos em Git/API keys/tokens antes de commit.

Valor para a infra: alto, especialmente porque já houve alerta de token LinkedIn plaintext.

Recomendação: implantar capability interna baseada em `gitleaks`/regras próprias e integrar no health operacional.

### 4. `security-monitor` / `openclaw-security-monitor`

Uso potencial: auditoria de deployment OpenClaw, Docker, SSH, portas, firewall, permissões e exposição.

Valor para a infra: médio-alto.

Observação: já temos skill local `healthcheck` e `scripts/operational_health.py`; melhor evoluir o health interno do que instalar direto.

### 5. `openclaw-git-backup` e `myopenclaw-backup-restore`

Uso potencial: backup/recovery e git backup agendado.

Valor para a infra: médio.

Observação: já temos backup VPS/B2 e padrão local de backup antes de mudança. O ganho real é melhorar restaurabilidade testada e não só acumular mais mecanismo.

### 6. `session-health-monitor`

Uso potencial: monitorar saúde de contexto, compactação e perda de memória de sessão.

Valor para a infra: médio.

Observação: útil como ideia para alertas internos, mas não deve gerar ruído no Telegram.

### 7. `agentic-workflow-automation` / `n8n-workflow-automation`

Uso potencial: padronizar workflows com retries, logs, idempotência e fila de revisão humana.

Valor para a infra: médio-alto.

Observação: encaixa com ClawFlows/Mission Control, mas deve virar padrão interno, não dependência externa.

### 8. `spec-workflow-guide`

Uso potencial: requisitos → design → tarefas para mudanças médias/grandes.

Valor para a infra: médio.

Observação: já temos PRD→QA e Task Board Lite. Útil para endurecer mudanças estruturais.

## Gaps internos identificados

1. Falta uma skill interna formal para **auditoria de skills externas** antes de instalação.
2. Falta um scanner operacional integrado para **segredos em Git/workspace**.
3. Falta rotina clara de **restore drill**: backup existe, mas teste periódico de restauração deve virar evidência.
4. Falta um padrão único para **mudança estrutural** com backup, rollback, validação, commit e memória.
5. Falta integrar higiene de contexto/sessão ao Mission Control sem gerar ruído.

## Próximas skills internas recomendadas

### Prioridade 1 — `skill-security-audit`

Objetivo: auditar qualquer skill externa antes de instalação.

Deve verificar:

- scripts executáveis;
- chamadas de rede;
- leitura de credenciais;
- escrita fora do workspace;
- comandos destrutivos;
- prompt injection;
- instruções para alterar AGENTS/SOUL/MEMORY;
- dependências suspeitas;
- hooks/cron/autoexec.

### Prioridade 2 — `secret-hygiene`

Objetivo: varrer workspace/2nd-brain/configs/commits por tokens e credenciais.

Deve produzir:

- relatório interno;
- classificação de severidade;
- caminho lógico da credencial, sem imprimir segredo;
- recomendação de rotação/migração KeeSpace;
- bloqueio antes de commit quando aplicável.

### Prioridade 3 — `restore-drill`

Objetivo: testar restaurabilidade dos backups, não só existência.

Deve cobrir:

- SQLite crítico;
- 2nd-brain;
- workspace runtime relevante;
- manifestos B2;
- restore em diretório temporário;
- validação por hash/contagem/integrity_check.

## Recomendação final

O salto de nível não é baixar mais skills. É criar três capacidades internas auditáveis:

1. auditoria de skills externas;
2. higiene de segredos;
3. restore drill recorrente.

Essas três reduzem risco sistêmico e melhoram a infraestrutura de verdade.
