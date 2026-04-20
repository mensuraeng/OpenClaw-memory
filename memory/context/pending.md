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
- [ ] **Concluir pairing do WhatsApp no Mission Control** — stack foi estabilizada e o bloqueio remanescente é humano: acessar o dashboard e fazer o QR scan para validar a trilha real.
- [ ] **Popular memória documental por empresa** — resumir e estruturar os documentos já mapeados de MENSURA, MIA e PCS (`apresentacao.md`, `ficha-cadastral.md`, `dados-institucionais.md`) conforme novos arquivos forem entrando.

## Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação do app institucional `OpenClaw - Community API` para destravar `rw_organization_admin`, Organization APIs e publicação em páginas.

## Segurança / saneamento

- [ ] **Remover token LinkedIn em plaintext do workspace** — `config/linkedin-mensura.json` está com access token pessoal ativo em texto aberto; mover para variável de ambiente ou endurecer permissão/acesso antes de ampliar uso por agentes.

## Regra de manutenção

- Tirar daqui o que já virou decisão permanente.
- Tirar daqui o que não é mais real.
- Se a pendência for de projeto específico, manter o detalhe no arquivo do projeto e deixar aqui só o resumo executivo.

## [PENDENTE] Documentos - 19/04/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-04-19
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 18/04/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-04-18
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 19/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-19
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre! ☕ O Google acabou de liberar o Personal Intelligence para TODOS (e outras 5 bombas)
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-03-18
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 18/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-18
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Retirement notice: Migrate to Azure Monitor Agent before 31 March 2026
- **De:** azure-noreply@microsoft.com
- **Recebido:** 2026-03-17
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [CRITICA] DECLARAÇÃO DE IRPF-2026 - REGRAS PARA APRESENTAÇÃO - PRAZO VAI ATÉ 29/05/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-17
- **Prazo:** 29/05/2026
- **Ação:** A definir

## [PENDENTE] Solicitações de Compra com insumos desautorizados
- **De:** naoresponder@sistemas.sienge.com.br
- **Recebido:** 2026-03-16
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 16/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-16
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 14/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-14
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Medição da obra pelo celular? É possível!
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-03-13
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [Atenção] Acompanhar a obra pode ser mais simples
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-03-13
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre!  Yann LeCun vs OpenAI: a guerra de $1 bilhão que vai definir o futuro da IA ☕🧠
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-03-13
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 13/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-13
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] +850 downloads: Planilha Linha de Balanço
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-03-12
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Documentos - 12/03/2026
- **De:** confirpdigital@confirp.com
- **Recebido:** 2026-03-12
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Concretagem sem rastreabilidade é risco estrutural!
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-03-11
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [AVISO IMPORTANTE] Atenção, a partir de hoje nossos e-mails são @starian.com
- **De:** relacionamentosienge@softplan.com.br
- **Recebido:** 2026-03-11
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre!  Meta compra rede social para robôs (e mais)
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-03-11
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] 3ª edição: Prevision Day + Sienge Plataforma
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-03-10
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre! GPT-5.4 venceu humanos | Excel com ChatGPT | Google criando apps SOZINHO
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-03-09
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [AVISO IMPORTANTE] Atualização sobre nossos canais de e-mail
- **De:** relacionamentosienge@softplan.com.br
- **Recebido:** 2026-03-06
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Kit disponível: Planejamento para Orçamento de Obra em 2026
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-03-03
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] [Construsummit] Novo lote, mesma vantagem para clientes Sienge
- **De:** construsummit@softplan.com.br
- **Recebido:** 2026-03-03
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Medição do MCMV sem papel nem planilha
- **De:** marketing@prevision.com.br
- **Recebido:** 2026-03-02
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] ☕ Café Com IA - Bom dia Alexandre! 💣 GUERRA declarada na IA: Governo bane rival da OpenAI e fecha acordo com Pentágono
- **De:** contact@allessandrasinisgalli.com.au
- **Recebido:** 2026-03-02
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] 🔓 Diário de Obras Digital liberado para usar agora
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-27
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

## [PENDENTE] Isso que diferencia obras que escalam x que apagam incêndio
- **De:** marketing@construmarket.com.br
- **Recebido:** 2026-02-27
- **Prazo:** estimado 24/04/2026
- **Ação:** A definir

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
