# Pendências

> Itens aguardando input, acesso, decisão ou saneamento operacional.

_Atualizado em 2026-04-13_

## Críticas

- [ ] **OpenAI API key válida** — necessária para Whisper, embeddings e `memory_search()`; hoje há erro de autenticação e a busca semântica está indisponível.
- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.

## Aguardando Alê

- [ ] **LinkedIn integration** — fornecer Client ID + Client Secret do app no LinkedIn Developer.
- [ ] **Instagram integration** — criar app no Meta Developer e fornecer App ID + Secret.
- [ ] **Novos contatos/equipe** — preencher `memory/context/people.md` conforme equipe e parceiros relevantes surgirem.

## Em andamento interno

- [ ] **Migrar lote 1 para cofre** — revisar saneamento posterior dos arquivos que ainda precisam manter compatibilidade operacional.
- [ ] **Trocar senha mestra do KeePassXC** — substituir a senha atual por uma forte.
- [ ] **Estruturar grupos do cofre** — consolidar grupos padrão: Email, APIs, Social, Infra, Financeiro.
- [ ] **Revisar falha do calendário Mensura** — investigar erro `ErrorInvalidUser` na consulta da conta quando houver janela.
- [ ] **Operacionalizar o segundo cérebro no GitHub** — definir a estrutura final do repositório de memória institucional, separar inbox de memória consolidada e implantar a consolidação noturna automática do OpenClaw.
- [ ] **Mapear captura automática por estação/agente** — decidir quais eventos, arquivos e registros entram no inbox bruto sem exigir processo manual do time.
- [ ] **Definir política de consolidação noturna** — critérios de promoção, deduplicação, vínculo entre itens relacionados e descarte de ruído.

## Aguardando terceiros

- [ ] **LinkedIn Developer** — aprovação do app para OAuth, pendente desde 2026-04-01.

## Regra de manutenção

- Tirar daqui o que já virou decisão permanente.
- Tirar daqui o que não é mais real.
- Se a pendência for de projeto específico, manter o detalhe no arquivo do projeto e deixar aqui só o resumo executivo.
