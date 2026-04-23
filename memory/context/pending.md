# Pendências

> Itens aguardando input, acesso, decisão ou saneamento operacional.

_Atualizado em 2026-04-22_

## Críticas

- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`.
- [ ] **Limpar segredos expostos após migração** — revisar memória, configs e documentação para remover texto sensível sem quebrar integrações.
- [ ] **Revalidar fallback real além do microteste de agentes** — o runtime principal dos agentes especializados voltou a responder, mas a cadeia alternativa de modelos ainda precisa de prova operacional específica fora do healthcheck curto.
- [ ] **Remover token LinkedIn em plaintext do workspace** — `config/linkedin-mensura.json` está com access token pessoal ativo em texto aberto; mover para variável de ambiente ou endurecer permissão/acesso antes de ampliar uso por agentes.

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
- [ ] **Concluir pairing do WhatsApp no Mission Control** — stack foi estabilizada e o bloqueio remanescente é humano: acessar o dashboard e fazer o QR scan para validar a trilha real.
- [ ] **Popular memória documental por empresa** — resumir e estruturar os documentos já mapeados de MENSURA, MIA e PCS (`apresentacao.md`, `ficha-cadastral.md`, `dados-institucionais.md`) conforme novos arquivos forem entrando.
- [ ] **Classificar base PCS↔Sienge** — separar registros em `obra executável`, `centro de custo administrativo` e `ambíguo/validar`.
- [ ] **Descobrir rota financeira real do Teatro Suzano no Sienge** — mapear endpoint válido para obter gastos/títulos/payables da obra `1354` sem inventar relatório.
- [ ] **Sincronizar `MEMORY.md` com fontes temáticas** — recalibrar painel executivo para refletir o estado real de `pending.md`, decisões recentes e destaques válidos.
- [ ] **Promover conteúdos permanentes do diário de 22/04** — mover o que for estável de `memory/2026-04-22.md` para `lessons.md`, `decisions.md` e `pending.md`.
- [ ] **Aplicar Fase 1 da Memória v2** — saneamento inicial do painel, pendências e promoção do que está preso no diário.
- [ ] **Consolidar financeiro MIA quando chegar o romaneio** — usar `memory/projects/mia/financeiro-conciliacao.md` para cruzar comprovantes, romaneio e documentos de suporte.

## Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação do app institucional `OpenClaw - Community API` para destravar `rw_organization_admin`, Organization APIs e publicação em páginas.
- [ ] **Romaneio de notas da MIA** — aguardar material para cruzar com comprovantes e consolidar status `pago`, `pendente`, `parcial` e `ambíguo`.

## Inbox / backlog bruto

A trilha bruta de inbox foi movida para:
`memory/projects/setup-openclaw-flavia/inbox-backlog-bruto.md`

Regra:
- `pending.md` fica só com visão executiva
- backlog massivo, mal classificado ou ainda não triado vai para a trilha bruta
- item que exigir ação real sobe depois para `pending.md`

## Regra de manutenção

- Tirar daqui o que já virou decisão permanente.
- Tirar daqui o que não é mais real.
- Se a pendência for de projeto específico, manter o detalhe no arquivo do projeto e deixar aqui só o resumo executivo.

## [PENDENTE] Documentos - 27/02/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-02-27
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] O erro que já custou milhões em obras
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-26
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] O duo que a sua obra precisa está aqui
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-26
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Novos palestrantes confirmados no Construsummit
- **De:** construsummit@softplan.com.br
- **Recebido:** 2026-02-25
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Obra em dia, mas caixa no vermelho? Webinar 04/03 às 16h
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-24
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Kit grátis: 6 materiais para planejar a obra
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-24
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [Construsummit] Últimas horas com preço de 1º lote 🚨
- **De:** construsummit@softplan.com.br
- **Recebido:** 2026-02-23
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre!  🤯 Canva virou estúdio de vídeo, Google GRÁTIS e o futuro chegou
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-02-23
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 22/02/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-02-22
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [Construsummit] Restam 3 dias para garantir o melhor preço
- **De:** construsummit@softplan.com.br
- **Recebido:** 2026-02-21
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Nem toda falha aparece na obra. Algumas estão no processo
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-20
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] 8 modelos prontos para acompanhar sua obra
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-19
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] O gargalo que mais trava a obra não aparece no cronograma
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-19
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 18/02/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-02-18
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [Curso gratuito] Como criar um cronograma Gantt eficiente em 2026
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-13
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Por que algumas obras fluem e outras empacam?
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-12
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] 5 passos do cronograma de sucesso
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-12
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] O mercado já virou essa chave. E você?
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-11
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Webinar: Dinheiro No Tempo | 25/02 às 16h
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-11
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Último lembrete: checklist gratuito de obras para evitar atrasos
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-02-10
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] 🚧 Não é só um evento. É onde a construção decide seu futuro.
- **De:** construsummit@softplan.com.br
- **Recebido:** 2026-02-10
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] É assim que a obra sai do controle sem ninguém perceber.
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-06
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] DECLARAÇÃO DE IRPF-2026 - REGRAS PARA APRESENTAÇÃO - PRAZO VAI ATÉ 29/05/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-17
- **Prazo:** 29/05/2026
- **Ação:** A definir
