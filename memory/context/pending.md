# Pendências

> Itens aguardando input, acesso, decisão ou saneamento operacional.

_Atualizado em 2026-04-18_

## Críticas

- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.
- [ ] **Revalidar fallback real além do microteste de agentes** — o runtime principal dos agentes especializados voltou a responder, mas a cadeia alternativa de modelos ainda precisa de prova operacional específica fora do healthcheck curto.
- [ ] **Corrigir roteamento do domínio de relatórios MIA** — `relatorios.miaengenharia.com.br/ccsp-casa-7/*` ainda cai no fallback da SPA principal em vez de servir páginas estáticas extras como o checklist.

## Aguardando Alê

- [ ] **Instagram integration** — confirmar arquitetura final 10/10: conta Instagram Business exata, Facebook Page vinculada, domínio/subdomínio público das páginas legais e objetivo/escopos reais do app antes de live/review.
- [ ] **Novos contatos/equipe** — preencher `memory/context/people.md` conforme equipe e parceiros relevantes surgirem.

## Em andamento interno

- [ ] **Migrar lote 1 para cofre** — revisar saneamento posterior dos arquivos que ainda precisam manter compatibilidade operacional.
- [ ] **Trocar senha mestra do KeePassXC** — substituir a senha atual por uma forte.
- [ ] **Estruturar grupos do cofre** — consolidar grupos padrão: Email, APIs, Social, Infra, Financeiro.
- [ ] **Revisar falha histórica do calendário Mensura** — houve erro `ErrorInvalidUser` em ciclo anterior; confirmar se foi definitivamente sanado ou se ainda reaparece em alguma rota/conta.
- [ ] **Validar e operacionalizar o segundo cérebro no GitHub** — fortalecer captura automática, promoção de memória e deduplicação entre agentes.
- [ ] **Mapear captura automática por estação/agente** — decidir quais eventos, arquivos e registros entram no inbox bruto sem exigir processo manual do time.
- [ ] **Definir política de consolidação noturna** — critérios de promoção, deduplicação, vínculo entre itens relacionados e descarte de ruído.
- [ ] **Padronizar catálogo de skills do ecossistema** — inventário oficial, classificação compartilhada vs específica e convenção para futuras instalações.
- [ ] **Incorporar checklist cliente na página principal da Casa 7** — manter como próximo passo depois de estabilizar a rota/domínio do checklist.
- [ ] **Calibrar triagem da inbox PCS antes de live** — categorização Graph foi implementada, mas ainda há falso `operacional`/`urgente`; ajustar ordem das regras, fortalecer `ruído/arquivo` e só então ativar sem dry-run.

## Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação do app institucional `OpenClaw - Community API` para destravar `rw_organization_admin`, Organization APIs e publicação em páginas.

## Segurança / saneamento

- [ ] **Remover token LinkedIn em plaintext do workspace** — `config/linkedin-mensura.json` está com access token pessoal ativo em texto aberto; mover para variável de ambiente ou endurecer permissão/acesso antes de ampliar uso por agentes.

## Regra de manutenção

- Tirar daqui o que já virou decisão permanente.
- Tirar daqui o que não é mais real.
- Se a pendência for de projeto específico, manter o detalhe no arquivo do projeto e deixar aqui só o resumo executivo.
