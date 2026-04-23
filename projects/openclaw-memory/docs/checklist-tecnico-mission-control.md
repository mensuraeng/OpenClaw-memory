# Checklist técnico — Mission Control (Tailscale-first)

_Atualizado em 2026-04-13_

## Objetivo

Transformar o PRD do Mission Control em sequência técnica executável, com foco em:
- segurança
- observabilidade
- privilégios mínimos
- deploy privado via Tailscale

---

## Fase 0 — Decisão de produto

- [ ] Confirmar que a v1 é **read-only**
- [ ] Confirmar que a v1 é **produto de observabilidade**, não de administração ativa
- [ ] Confirmar que **não haverá terminal web** na v1
- [ ] Confirmar que **não haverá edição ampla de memória** na v1

---

## Fase 1 — Auditoria estática do repo base

### Código
- [ ] Revisar `middleware` e fluxo de autenticação
- [ ] Revisar todas as rotas `/api/*`
- [ ] Mapear uso de `child_process`, `exec`, `spawn`
- [ ] Mapear leitura e escrita em filesystem
- [ ] Mapear dependências que acessam host, SQLite, logs e config
- [ ] Revisar scripts shell e cron setup

### Segurança
- [ ] Confirmar se há terminal remoto
- [ ] Confirmar se há PUT/POST de edição genérica de arquivos
- [ ] Confirmar se há path traversal mitigado de forma robusta
- [ ] Confirmar se rendering de markdown/conteúdo é seguro
- [ ] Confirmar se há leitura excessiva de `openclaw.json` ou áreas sensíveis

### Resultado esperado
- [ ] Produzir mapa de superfícies perigosas
- [ ] Produzir lista fechada de patches obrigatórios

---

## Fase 2 — Hardening do código

### Remoções obrigatórias
- [ ] Remover terminal API da v1
- [ ] Remover escrita genérica de arquivos da v1
- [ ] Remover qualquer navegação livre no filesystem

### Restrições obrigatórias
- [ ] Implementar allowlist explícita de paths
- [ ] Tornar file browser read-only
- [ ] Bloquear escrita em:
  - [ ] `SOUL.md`
  - [ ] `AGENTS.md`
  - [ ] `MEMORY.md`
  - [ ] `USER.md`
  - [ ] `IDENTITY.md`
  - [ ] `TOOLS.md`
- [ ] Bloquear edição ampla em `memory/`
- [ ] Limitar leitura de `openclaw.json` ao mínimo necessário

### Sanitização
- [ ] Sanitizar renderização de markdown
- [ ] Garantir ausência de HTML/script ativo vindo de conteúdo lido
- [ ] Revisar qualquer preview ou parser com risco de execução indevida

---

## Fase 3 — Adaptação à arquitetura real

- [ ] Refletir os agentes reais:
  - [ ] `main`
  - [ ] `mensura`
  - [ ] `mia`
  - [ ] `pcs`
  - [ ] `finance`
  - [ ] `juridico`
  - [ ] `marketing`
  - [ ] `producao`
  - [ ] `bi`
  - [ ] `suprimentos`
  - [ ] `rh`
- [ ] Tratar `autopilot` como agente em revisão
- [ ] Exibir fronteira/função de cada agente
- [ ] Mapear workspaces reais sem hardcode genérico do repo upstream

---

## Fase 4 — Segurança de acesso

### Tailscale-first
- [ ] Confirmar que o acesso será apenas pela tailnet
- [ ] Evitar exposição pública aberta
- [ ] Configurar bind restrito do serviço
- [ ] Validar acesso pela VPS via Tailscale já instalada

### Auth do app
- [ ] Definir senha forte
- [ ] Definir secret forte
- [ ] Validar cookie seguro
- [ ] Validar rate limit
- [ ] Validar comportamento de sessão expirada

### Defesa em profundidade
- [ ] Tailscale como primeira barreira
- [ ] Auth do app como segunda barreira
- [ ] Logs mínimos de acesso

---

## Fase 5 — Sandbox

- [ ] Subir em diretório separado
- [ ] Evitar acoplamento direto com escrita na memória real
- [ ] Preferir modo somente leitura durante testes
- [ ] Validar comportamento com dados reais sem liberar ações perigosas

---

## Fase 6 — Validação funcional

### Host
- [ ] CPU ok
- [ ] RAM ok
- [ ] disco ok
- [ ] uptime ok
- [ ] gateway OpenClaw visível

### Agentes
- [ ] todos os agentes reais aparecem
- [ ] status coerente
- [ ] workspaces corretos
- [ ] última atividade coerente

### Sessões
- [ ] sessões recentes aparecem
- [ ] associação com agente correta
- [ ] resumo não vaza conteúdo indevido

### Crons
- [ ] jobs ativos aparecem
- [ ] próximo run aparece
- [ ] falhas recentes aparecem
- [ ] distinção entre silenciosos e notificáveis funciona

### Memória e docs
- [ ] leitura apenas de paths aprovados
- [ ] arquivos sensíveis seguem read-only
- [ ] nenhum acesso fora da allowlist

---

## Fase 7 — Aceite de segurança

- [ ] sem terminal web
- [ ] sem PUT genérico de arquivos
- [ ] sem edição de arquivos-raiz sensíveis
- [ ] sem exposição pública aberta
- [ ] sem navegação livre no filesystem
- [ ] sem superfície ampla de prompt injection persistente
- [ ] rollback simples validado

---

## Fase 8 — Produção restrita

- [ ] subir serviço final
- [ ] validar acesso via Tailscale
- [ ] validar auth do app
- [ ] registrar procedimento de restart
- [ ] registrar procedimento de rollback
- [ ] documentar atualização segura

---

## Entregáveis esperados

- [ ] repo/fork adaptado
- [ ] configuração segura de ambiente
- [ ] painel v1 read-only
- [ ] documentação de deploy
- [ ] documentação de rollback
- [ ] checklist de segurança assinado internamente
