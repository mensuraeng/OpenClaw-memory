# QA Checklist — Automações e Mudanças Operacionais

_Atualizado em 2026-04-28_

Antes de declarar uma mudança concluída:

## Segurança
- [ ] Não expôs token/segredo em arquivo, log, memória ou resposta.
- [ ] Respeitou matriz de autoridade.
- [ ] Side effects externos foram aprovados.
- [ ] Delete permanente não foi usado sem autorização.

## Dados
- [ ] Fonte declarada.
- [ ] Janela declarada.
- [ ] Paginação tratada ou limitação declarada.
- [ ] Confiança indicada quando há incerteza.

## Teste
- [ ] Dry-run executado quando possível.
- [ ] Teste mínimo real executado quando seguro.
- [ ] Logs/artefatos de evidência salvos.
- [ ] Falhas conhecidas documentadas.

## Operação
- [ ] Owner definido.
- [ ] Próximo passo definido.
- [ ] Rollback/contenção definido.
- [ ] WORKING/memória atualizados quando necessário.

## Comunicação
- [ ] Alê avisado apenas se houver decisão, risco, bloqueio ou conclusão relevante.
