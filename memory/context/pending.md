# Pendências

> Visão executiva — apenas itens reais com ação pendente.
> Spam, newsletters e emails de marketing: descartar direto, nunca entram aqui.

_Flush realizado em 2026-04-25_

---

## 🔴 Críticas

- [ ] **Confirmar SSH key do VPS** — pré-requisito antes de endurecer SSH com `PermitRootLogin prohibit-password`
- [ ] **Token LinkedIn em plaintext** — `config/linkedin-mensura.json` com access token ativo em texto aberto; mover para variável de ambiente ou restringir permissões
- [ ] **Limpar segredos expostos** — revisar memória, configs e docs para remover texto sensível sem quebrar integrações
- [ ] **Revalidar fallback de modelos** — cadeia alternativa de modelos precisa de teste fora do healthcheck curto

---

## 🟡 Aguardando Alê

- [ ] **SPTrans — 1ª OS**: quando receber, criar alertas D+10 (cronograma detalhado) e D+30 (Plano BIM). Ref: `memory/projects/pcs/contratos-e-lastro.md` seção 4
- [ ] **Instagram integration** — confirmar conta Business, Facebook Page vinculada, domínio e escopos do app antes de review
- [ ] **WhatsApp QR scan** — acessar Mission Control (100.124.198.120:18789) e fazer scan para ativar canal
- [ ] **Preencher `people.md`** — adicionar equipe e parceiros relevantes conforme surgirem

---

## 📅 Com prazo

| Item | Prazo | Fonte |
|---|---|---|
| **IRPF 2026** — entregar declaração | **29/05/2026** | confirpdigital@confirp.com |
| **Documentos Confirp** — recebido 23/04 | **28/04/2026** | confirpdigital@confirp.com |
| **CPA Diretrizes adicionais** — SPObras | **28/04/2026** | dyonisiojpf@spobras.sp.gov.br |
| **CCSP Casa 7** — conclusão da obra | **22/05/2026** | Contrato |

---

## 🔵 Em andamento interno

- [ ] **Classificar base PCS↔Sienge** — separar em `obra executável`, `centro de custo administrativo` e `ambíguo/validar`
- [ ] **Calibrar triagem inbox PCS** — ajustar regras de categorização antes de desligar dry-run
- [ ] **Concluir pairing WhatsApp PCS** — QR scan pendente
- [ ] **Consolidar financeiro MIA** — aguardando romaneio para cruzar com comprovantes
- [ ] **Incorporar checklist cliente Casa 7 na página principal** — após estabilizar rota/domínio
- [ ] **Descobrir rota financeira Teatro Suzano no Sienge** — mapear endpoint válido para obra `1354`
- [ ] **Popular memória documental MENSURA/MIA/PCS** — estruturar `apresentacao.md`, `ficha-cadastral.md`, `dados-institucionais.md`

---

## ⏳ Aguardando terceiros

- [ ] **LinkedIn Community API** — aprovação do app `OpenClaw - Community API` para publicação em páginas institucionais
- [ ] **Romaneio MIA** — material para cruzar comprovantes e consolidar status de pagamento

---

## Regra de manutenção

- Item resolvido → remover imediatamente
- Item de projeto específico → manter detalhe no projeto, aqui só resumo executivo
- Newsletters, marketing, spam → **descartar direto, nunca entram aqui**
- Revisar este arquivo toda segunda-feira
