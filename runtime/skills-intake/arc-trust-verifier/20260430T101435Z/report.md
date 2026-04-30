# Skill Intake Audit

- Candidata: `/root/.openclaw/workspace/skills/shared/arc-trust-verifier`
- Status: `SUSPECT`
- Score: 45/100
- Arquivos varridos: 4
- Achados por severidade: `{'review': 3}`

## Guardrails
- Código candidato não executado.
- Sem chamada externa.
- Sem ação destrutiva.

## [key_normalization_and_idempotency]
- Status: `pass`
- Achado: skill intake normaliza path/query/trailing slash antes de gerar chave de auditoria
- Risco: rate-limit bypass | dedup fragmentation

## Achados principais
- `review` `permission_creep_hint` em `_meta.json:8`
- `review` `permission_creep_hint` em `_meta.json:14`
- `review` `shell_execution` em `scripts/trust_verifier.py:103`
