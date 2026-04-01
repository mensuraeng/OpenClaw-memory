# Relatório de Cursos (toda sexta 16h BRT)

_Atualizado em 2026-04-01_

- **Status:** ativo
- **Próximo passo:** nenhum — funcionando
- **Bloqueios:** nenhum

## O que faz
Busca e curadoria semanal de cursos de construção civil no Brasil. Envia resumo via Telegram.

## Filtros
- ✅ Incluir: cursos curtos, workshops, certificações, eventos
- ❌ Excluir: MBAs, pós-graduações, especializações longas

## Cron
`0 19 * * 5` → toda sexta 19h UTC (16h BRT)

## Script
`scripts/relatorio_cursos_telegram.py`
