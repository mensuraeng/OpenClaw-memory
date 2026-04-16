# Pendências

> Itens aguardando input, acesso, decisão ou saneamento operacional.

_Atualizado em 2026-04-16_

## Críticas

- [ ] **OpenAI API key / quota válida para embeddings** — `memory_search()` segue indisponível por `insufficient_quota`, comprometendo memória semântica e parte dos fluxos de Whisper/OCR.
- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.
- [ ] **Corrigir cadeia real de fallback de modelos** — hoje `openai/gpt-4o-mini` falha por quota e `anthropic/claude-sonnet-4-6` falha por auth; fallback configurado ainda não está operacionalmente confiável.

## Aguardando Alê

- [ ] **Instagram integration** — criar app no Meta Developer e fornecer App ID + Secret.
- [ ] **Novos contatos/equipe** — preencher `memory/context/people.md` conforme equipe e parceiros relevantes surgirem.
- [ ] **Decidir política final das skills** — padronizar o que fica compartilhado no workspace principal e o que deve morar por agente/workspace específico.

## Em andamento interno

- [ ] **Migrar lote 1 para cofre** — revisar saneamento posterior dos arquivos que ainda precisam manter compatibilidade operacional.
- [ ] **Trocar senha mestra do KeePassXC** — substituir a senha atual por uma forte.
- [ ] **Estruturar grupos do cofre** — consolidar grupos padrão: Email, APIs, Social, Infra, Financeiro.
- [ ] **Revisar falha do calendário Mensura** — investigar erro `ErrorInvalidUser` na consulta da conta quando houver janela.
- [ ] **Validar e operacionalizar o segundo cérebro no GitHub** — fortalecer captura automática, promoção de memória e deduplicação entre agentes.
- [ ] **Mapear captura automática por estação/agente** — decidir quais eventos, arquivos e registros entram no inbox bruto sem exigir processo manual do time.
- [ ] **Definir política de consolidação noturna** — critérios de promoção, deduplicação, vínculo entre itens relacionados e descarte de ruído.
- [ ] **Padronizar catálogo de skills do ecossistema** — inventário oficial, classificação compartilhada vs específica e convenção para futuras instalações.
- [ ] **Corrigir warnings estruturais do Mission Control** — migrar `middleware` para `proxy` e mover `themeColor` para `viewport` nas rotas afetadas.

## Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação do app institucional `OpenClaw - Community API` para destravar Organization APIs e publicação em páginas.

## Regra de manutenção

- Tirar daqui o que já virou decisão permanente.
- Tirar daqui o que não é mais real.
- Se a pendência for de projeto específico, manter o detalhe no arquivo do projeto e deixar aqui só o resumo executivo.
