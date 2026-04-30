# Skill Intake Audit

Atualizado em 2026-04-30.

## Objetivo

Auditar skills candidatas antes de qualquer instalação ou adaptação, usando leitura estática e sem executar código da skill.

## Script

```bash
python3 scripts/skill_intake_audit.py <diretorio-da-skill> --json
```

Saídas:

- `runtime/skills-intake/<skill>/<timestamp>/report.json`
- `runtime/skills-intake/<skill>/<timestamp>/report.md`
- `runtime/skills-intake/<skill>/latest.json`
- `runtime/skills-intake/<skill>/latest.md`

## Guardrails

- Não executa código candidato.
- Não faz chamada externa.
- Não executa ação destrutiva.
- `trust-verifier` permanece como etapa separada quando houver pacote real de skill.

## O que detecta

- comando destrutivo;
- acesso a arquivos de segredo;
- execução remota via `curl|bash`/`wget|sh`;
- shell execution;
- chamadas de rede;
- payload codificado/eval;
- permission creep;
- risco `key_normalization_and_idempotency`.

## Critério

- `CLEAN`: sem achado relevante.
- `REVIEW`: precisa leitura humana.
- `SUSPECT`: risco material; não instalar sem análise.
- `BLOCK`: bloquear instalação/adaptação até correção.

## Validação atual

Rodado em `skills/shared/arc-trust-verifier` como amostra local.

Resultado: `SUSPECT`, score 45/100, por achados de revisão estática. Código candidato não foi executado.

`key_normalization_and_idempotency`: passou; `/googlechat`, `/googlechat/` e `/googlechat?foo=bar` convergem para a mesma chave canônica.
