# Pendências

> Visão executiva — apenas itens reais com ação pendente.
> Spam, newsletters e emails de marketing: descartar direto, nunca entram aqui.

_Flush realizado em 2026-05-01 22:00_

---

## 🔴 Críticas

- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`
- [ ] **Token LinkedIn em plaintext** — `config/linkedin-mensura.json` com access token ativo em texto aberto; mover para variável de ambiente/cofre ou restringir permissões
- [ ] **Limpar segredos expostos** — revisar memória, configs e docs para remover texto sensível sem quebrar integrações
- [ ] **Revalidar fallback de modelos** — cadeia alternativa de modelos precisa de teste fora do healthcheck curto
- [ ] **Auditar crons após correção do croncheap** — confirmar se os 14 erros identificados em 27/04 foram sanados e separar remanescente real de `last -> no route`
- [ ] **Frente fiscal — confirmar escopo de emissão por empresa** — definir se MIA/MENSURA/PCS emitem NFS-e, NF-e ou ambas; mapear Sistema do Milhão/municipal, certificado A1/A3, aprovador humano e destino PDF/XML antes de qualquer emissão real

---

## 🟡 Aguardando Alê

- [ ] **SPTrans — 1ª OS**: quando receber, criar alertas D+10 (cronograma detalhado) e D+30 (Plano BIM). Ref: `memory/projects/pcs/contratos-e-lastro.md` seção 4
- [ ] **Instagram integration** — confirmar conta Business, Facebook Page vinculada, domínio e escopos do app antes de review
- [ ] **WhatsApp QR scan / PCS** — acessar Mission Control e fazer scan se a sessão PCS ainda estiver pendente
- [ ] **Preencher `people.md`** — adicionar equipe e parceiros relevantes conforme surgirem
- [ ] **Mensura campanha fria — nova lista** — Alê combinou enviar nova base em 28/04; não disparar novo lote antes de higienizar e preservar reputação do domínio/remetente
- [ ] **Teatro Suzano no Sienge — estratégia de total** — se o caminho via `workItemId` der 100% de cobertura, Alê precisa confirmar se aceita eventual divergência entre total Excel e total calculado pela base Sienge
- [ ] **Meta Ads — conexão MCP/AI Connector** — Alê pediu conexão ampla com trava por orçamento e definiu teto atual **R$ 0/dia**. Portanto, por enquanto só conexão, leitura, diagnóstico e preparação; ficam bloqueados ativação/publicação/gasto. Falta: `META_AD_ACCOUNT_ID=act_<id>`, autenticação Meta/OAuth/token e conta de anúncio vinculada ao Business correto. Plano registrado em `runtime/mensura-marketing/meta-ads/connection-plan-2026-04-30.md`.
- [ ] **PCS — fontes documentais institucionais** — obter apresentação, ficha cadastral, dados institucionais e fontes oficiais antes de preencher memória documental da PCS
- [ ] **Hostinger snapshot real / rotina diária** — token e consulta read-only validados; criação de snapshot sobrescreve o anterior e exige confirmação explícita antes de executar/ativar cron diário

---

## 📅 Com prazo

| Item | Prazo | Fonte |
|---|---|---|
| **Documentos Confirp** — recebido 23/04 | **28/04/2026** | confirpdigital@confirp.com |
| **CPA Diretrizes adicionais** — SPObras | **28/04/2026** | dyonisiojpf@spobras.sp.gov.br |
| **CCSP Casa 7** — conclusão da obra | **22/05/2026** | Contrato |
| **IRPF 2026** — entregar declaração | **29/05/2026** | confirpdigital@confirp.com |

---

## 🔵 Em andamento interno

- [ ] **Teatro Suzano — orçamento Sienge** — rodar novo dry-run após reset do rate limit; só executar upload se cobertura de códigos for 100% e estratégia de total estiver confirmada
- [ ] **MENSURA Commercial Intelligence** — manter base versionada no repo/SQLite; toda nova lista passa por deduplicação, DNS/domínio, suppression, bounces e score antes de campanha
- [ ] **Saneamento 2nd-brain Mia-CCSP-Casa-7** — tarefa própria com backup antes de remover/reestruturar conteúdo
- [ ] **Classificar base PCS↔Sienge** — separar em `obra executável`, `centro de custo administrativo` e `ambíguo/validar`
- [ ] **Calibrar triagem inbox PCS** — PCS Graph foi destravado; acompanhar qualidade das categorias antes de desligar qualquer dry-run/controle de segurança
- [ ] **Consolidar financeiro MIA** — aguardando romaneio para cruzar com comprovantes
- [ ] **Incorporar checklist cliente Casa 7 na página principal** — após estabilizar rota/domínio
- [ ] **Sistema Operacional 10/10** — evoluir WORKING, health, usage ledger e backlog leve com validação contínua, sem ruído no direct
- [ ] **Mission Control `/cron` — acompanhar edição em produção** — edição de crons foi implementada e buildada; observar primeiro uso real para validar UX e efeitos no scheduler
- [ ] **LLM Context Pack — integrar ao uso operacional seletivo** — helper implantado; usar para subagentes/Mission Control quando reduzir contexto sem substituir fonte de verdade

---

## ⏳ Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação da app dedicada/exclusiva `OpenClaw - Community API` (`77ke3c00urrpdv`) para publicação em páginas institucionais; Alê já confirmou admin/super admin das páginas MENSURA, MIA e PCS
- [ ] **Romaneio MIA** — material para cruzar comprovantes e consolidar status de pagamento
- [ ] **Sienge / Softplan — importação de orçamento com valores** — confirmar endpoint/procedimento para importar planilha preservando valores quando itens antigos têm vínculos/apropriações

---

## Regra de manutenção

- Item resolvido → remover imediatamente
- Item de projeto específico → manter detalhe no projeto, aqui só resumo executivo
- Newsletters, marketing, spam → **descartar direto, nunca entram aqui**
- Revisar este arquivo toda segunda-feira
