# LLM Context Pack Standard — Flávia/OpenClaw

_Atualizado em 2026-04-29_

## Decisão

A fonte de verdade continua sendo Markdown, YAML, JSON, CSV e os arquivos canônicos do `2nd-brain`.

Context packs são artefatos temporários, read-only, usados apenas para enviar contexto limpo a LLMs, subagentes e análises do Mission Control.

## Regra operacional

- Prompt simples → linguagem natural objetiva.
- Contexto executivo → Markdown curto.
- Dados estruturados pequenos/médios → JSON compacto.
- Tabelas grandes → CSV ou JSONL com campos mínimos.
- Memória canônica → Markdown + sidecar YAML.
- APIs/configs → JSON normal.
- Pretty JSON só quando humano precisa ler; não usar como payload padrão para LLM.

## Ferramenta

Script:

```bash
scripts/llm_context_pack.py
```

Modos:

- `summary` — resumo executivo compacto.
- `agent` — pacote para subagente.
- `audit` — evidência, status, risco e detalhe mínimo.
- `table` — lista/tabela compactada.

Saídas:

- `json`
- `jsonl`
- `csv`
- `markdown`

## Exemplos

Health operacional compacto:

```bash
scripts/llm_context_pack.py runtime/operational-health/latest.json --mode audit --output json --meta
```

Ledger CRM/CDP em amostra tabular:

```bash
scripts/llm_context_pack.py runtime/data-pipeline/crm/mensura-crm-import-candidates-latest.csv --mode table --output csv --limit 20 --meta
```

LinkedIn Community API como resumo:

```bash
scripts/llm_context_pack.py runtime/linkedin-institutional/community-api-email-check-latest.json --mode summary --output markdown --meta
```

Campos explícitos:

```bash
scripts/llm_context_pack.py arquivo.json --keys id,name,status,evidence --output jsonl
```

## Guardrails

- Não altera a fonte de verdade.
- Não executa ação externa.
- Não substitui validação humana para decisões sensíveis.
- Não deve ser usado para esconder ausência de evidência.
- Não deve carregar segredo para contexto LLM; antes de usar, reduzir campos e revisar fontes sensíveis.
- Para texto externo não confiável, manter separação clara entre dado externo e instrução interna.

## Métrica mínima

Todo pack pode emitir metadados com `--meta`:

- registros de entrada;
- registros de saída;
- caracteres de entrada e saída;
- estimativa simples de tokens;
- redução estimada;
- hash curto da fonte.

A métrica é comparativa, não contábil. Para cobrança precisa, usar tokenizer específico do modelo quando necessário.
