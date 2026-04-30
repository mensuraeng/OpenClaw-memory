# OpenClaw Skills — backlog de adaptação para a infra da Flávia

Atualizado em 2026-04-30.

## Intenção

Usar `https://github.com/openclaw/skills` como biblioteca de padrões, não como fonte para instalação direta.

Regra: ler → extrair padrão útil → adaptar internamente → validar → versionar.

Não instalar skill externa sem intake/auditoria.

## Leitura realizada

Foram mapeados `SKILL.md` do repositório externo por categorias relevantes:

- skill supply chain / security audit;
- secrets / credentials;
- backup / restore;
- ops monitoring;
- workflow orchestration;
- database / CRM / ETL;
- memory / context.

A leitura focada incluiu, entre outras:

- `skill-security-auditor`
- `alon-github-security-audit`
- `claw-security-scanner`
- `aig-skill-scanner`
- `security-skill-scanner`
- `permission-creep-scanner`
- `supply-chain-poison-detector`
- `doro-git-secrets-scanner`
- `secrets-scanner`
- `env-secrets-manager`
- `myopenclaw-backup-restore`
- `openclaw-git-backup`
- `workspace-backup`
- `afrexai-disaster-recovery`
- `session-health-monitor`
- `openclaw-security-monitor`
- `security-monitor-deploy`
- `agentic-workflow-automation`
- `n8n-workflow-automation`
- `crm-next-action`
- `memory-poison-auditor`
- `session-context-bridge`

## Padrões úteis para adaptar

### 1. Skill Intake / Supply Chain Gate

Fontes de padrão:

- `skill-security-auditor`
- `alon-github-security-audit`
- `aig-skill-scanner`
- `security-skill-scanner`
- `permission-creep-scanner`
- `supply-chain-poison-detector`
- imagem/análise ClawSweeper sobre normalização de chave antes de rate limit.

Ideia útil:

- criar score de risco 0–100;
- inventariar scripts, assets, dependências e chamadas externas;
- comparar descrição declarada da skill contra acessos reais;
- detectar permission creep;
- detectar payload codificado, comando destrutivo, leitura de `.env`, `.ssh`, credentials, tokens;
- detectar risco `key_normalization_and_idempotency`: chaves de rate limit, dedup, suppression, cache, manifest ou webhook geradas a partir de URL/path/email/domínio/input bruto sem canonicalização;
- classificar `CLEAN / REVIEW / SUSPECT / BLOCK`;
- gerar relatório local antes de qualquer instalação.

Adaptação para nós:

- criar `scripts/skill_intake_audit.py`;
- entrada: diretório local temporário da skill candidata;
- saída: `runtime/skills-intake/<skill>/<timestamp>/report.json` e `.md`;
- usar `trust-verifier` já instalado como etapa 1;
- adicionar etapa própria de estática e permission-creep;
- nunca executar scripts da skill candidata.

Prioridade: **P0**.

### 2. Secret Hygiene / Credential Guard

Fontes de padrão:

- `doro-git-secrets-scanner`
- `secrets-scanner`
- `env-secrets-manager`

Ideia útil:

- combinar regex, entropia e padrões por provedor;
- varrer working tree e histórico Git;
- gerar `.env.example`/inventário lógico sem expor segredo;
- fluxo detectar → escopar → rotacionar → migrar → validar.

Adaptação para nós:

- criar `scripts/secret_hygiene.py`;
- não imprimir segredo, só fingerprint parcial/sha e caminho;
- cobrir workspace, 2nd-brain, configs e commits recentes;
- integrar com `scripts/operational_health.py`;
- referência cruzada com KeeSpace protocol.

Prioridade: **P0**.

### 3. Restore Drill / Backup Prova de Vida

Fontes de padrão:

- `myopenclaw-backup-restore`
- `openclaw-git-backup`
- `workspace-backup`
- `afrexai-disaster-recovery`

Ideia útil:

- backup sem restore testado é ilusão operacional;
- todo backup crítico precisa de dry-run restore;
- manifestos com hash, contagem, permissões e rollback;
- rotina periódica com evidência curta.

Adaptação para nós:

- criar `scripts/restore_drill.py`;
- validar SQLite crítico em diretório temporário com `pragma integrity_check`;
- validar 2nd-brain por `git fsck`/status limpo quando aplicável;
- validar manifestos B2 e hashes locais;
- gerar `runtime/restore-drill/latest.json`;
- integrar no Mission Control/health.

Prioridade: **P0/P1**.

### 4. Session / Context Health

Fontes de padrão:

- `session-health-monitor`
- `session-context-bridge`

Ideia útil:

- detectar perda/compactação de contexto;
- snapshot pré-compactação;
- ponte entre sessão e memória durável;
- alerta só quando houver risco real de perda.

Adaptação para nós:

- não gerar mensagens no Telegram por rotina;
- usar apenas como check interno do Mission Control;
- registrar fatos relevantes em `2nd-brain` e `WORKING.md`;
- evitar duplicar memória com ruído.

Prioridade: **P2**.

### 5. Security Monitor / Host Hardening

Fontes de padrão:

- `openclaw-security-monitor`
- `security-monitor-deploy`

Ideia útil:

- score de segurança;
- checar SSH, firewall, portas expostas, permissões, configs OpenClaw, credenciais e sessões;
- dashboard de achados.

Adaptação para nós:

- não substituir `healthcheck` local;
- evoluir `scripts/operational_health.py` com score e categorias;
- manter alertas só por exceção.

Prioridade: **P1**.

### 6. Workflow Blueprint / Idempotent Automation

Fontes de padrão:

- `agentic-workflow-automation`
- `n8n-workflow-automation`
- imagem/análise ClawSweeper sobre query string/trailing slash fragmentando bucket.

Ideia útil:

- blueprint de workflow com gatilho, passos, dependências, idempotência, retry, logs e fila humana;
- toda automação precisa de owner, rollback e evidência;
- qualquer idempotency key precisa nascer de identidade canônica, não de input bruto;
- exigir teste mínimo de estabilidade para variantes equivalentes: query string, trailing slash, case, path relativo/absoluto, email/domínio.

Adaptação para nós:

- padronizar ClawFlows/n8n/Kestra antes de criar automação;
- gerar contratos YAML/JSON para workflows;
- exigir `human_review_required` para qualquer saída externa.

Prioridade: **P1**.

### 7. CRM Next Action / Data Quality

Fontes de padrão:

- `crm-next-action`
- `etl-generator`
- skills database/CRM mapeadas

Ideia útil:

- cada lead/empresa precisa de próximo passo, motivo e motivo de não avanço;
- ETL deve ser reproduzível e auditável;
- dados comerciais precisam de camadas: bruto → normalizado → higienizado → ação sugerida.

Adaptação para nós:

- estender `lead_hygiene_*` para `commercial_state_current`;
- incluir `next_action_reason`, `hold_reason`, `owner`, `review_required`;
- Mission Control mostrar fila comercial por ação, não só CSV.

Prioridade: **P1**.

### 8. Memory Poison Audit

Fonte de padrão:

- `memory-poison-auditor`

Ideia útil:

- memória durável pode ser contaminada por instruções ocultas, steering indevido, bias e regras contraditórias;
- auditoria deve diferenciar fato, decisão, instrução e sugestão.

Adaptação para nós:

- criar auditoria periódica do `2nd-brain` e workspace memory;
- checar instruções conflitantes com AGENTS/SOUL;
- sinalizar blocos suspeitos sem apagar automaticamente.

Prioridade: **P1/P2**.

## Backlog recomendado

### P0 — agora

1. `skill_intake_audit.py` usando `trust-verifier` + estática própria + `key_normalization_and_idempotency`.
2. `secret_hygiene.py` com varredura segura e sem impressão de segredo + fingerprints/chaves canônicas.
3. `restore_drill.py` para SQLite + 2nd-brain + manifestos críticos + paths/manifest keys canônicos.
4. Padrão transversal documentado em `docs/operacao/KEY-NORMALIZATION-IDEMPOTENCY-STANDARD.md`.

### P1 — próximo ciclo

4. Evoluir `operational_health.py` com score de segurança/infra.
5. Criar contrato padrão de workflow idempotente para ClawFlows/n8n/Kestra.
6. Estender CRM/CDP para `commercial_state_current`.

### P2 — maturidade

7. Context/session health silencioso no Mission Control.
8. Memory poison audit do 2nd-brain.
9. Agent Audit Trail integrado a eventos críticos.

## Decisão

Não precisamos instalar as skills externas. Precisamos adaptar os melhores padrões em scripts internos pequenos, auditáveis e conectados ao Mission Control.

Ordem recomendada: **Skill Intake → Secret Hygiene → Restore Drill**.
