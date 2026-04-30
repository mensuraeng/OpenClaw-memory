# Restore Drill — prova de restauração segura

Atualizado em 2026-04-30.

## Objetivo

Validar periodicamente que os ativos críticos têm prova mínima de restauração sem restaurar nada sobre produção.

Este drill é **read-only** para dados reais: copia somente para sandbox temporário, valida e descarta o temporário automaticamente.

## Comando

```bash
python3 scripts/restore_drill.py --json
```

Saídas:

- `runtime/restore-drill/latest.json`
- `runtime/restore-drill/latest.md`
- `runtime/restore-drill/restore-drill-<timestamp>.json`
- `runtime/restore-drill/restore-drill-<timestamp>.md`

## Guardrails

- Não restaura sobre caminhos reais.
- Não apaga backups.
- Não executa `rm`.
- Não chama B2 nem serviços externos.
- Não imprime segredos.
- Usa `tempfile` para cópia/validação.

## Checks implantados

### 1. Key normalization & idempotency

Antes de considerar o drill válido, o script testa estabilidade de chaves para:

- path relativo vs absoluto;
- trailing slash;
- manifest key com query string/trailing slash;
- backup id com trailing slash;
- diferença real entre paths distintos.

Critério: variantes equivalentes devem gerar a mesma chave canônica; variantes diferentes devem continuar diferentes.

### 2. SQLite crítico

Se existir:

`projects/mensura-commercial-intelligence/data/commercial-intelligence.sqlite`

O script:

1. copia o arquivo para diretório temporário;
2. abre em modo read-only;
3. executa `PRAGMA integrity_check`;
4. lista tabelas não internas;
5. registra contagem de linhas por tabela.

A produção nunca é aberta para escrita.

### 3. `/root/2nd-brain`

Se `/root/2nd-brain` for repositório Git, o script executa apenas:

- `git status --porcelain=v1`
- `git fsck --no-progress`

Resultado `attention` indica repositório íntegro mas com working tree suja. Resultado `fail` indica erro de comando ou `fsck`.

### 4. Manifestos locais

O script procura manifestos apenas dentro de:

`runtime/backups/`

A busca é limitada por Python, com diretórios pesados ignorados (`.git`, `node_modules`, caches, temporários e `vps-full-stream-tmp`) e limite de quantidade/tamanho.

Para cada `manifest*.json` ou `*.manifest.json`, o script:

- lê JSON local;
- extrai entradas conhecidas (`files`, `entries`, `objects`, `items`, `parts`);
- canonicaliza keys e hashes antes de comparação;
- aponta duplicidade de chave canônica.

## Interpretação do overall

- `ok`: checks aplicáveis passaram.
- `attention`: há condição operacional relevante, mas não necessariamente quebra de restauração. Ex.: repo Git sujo ou manifestos com duplicidade de chave canônica.
- `fail`: check crítico falhou.
- `skipped`: nada aplicável foi encontrado.

## Integração recomendada

Rodar como health check interno recorrente e consumir `runtime/restore-drill/latest.json` no Mission Control/health.

Não enviar saída externa automaticamente. Se houver `fail`, a Flávia consolida o achado e pede validação antes de qualquer ação sensível.
