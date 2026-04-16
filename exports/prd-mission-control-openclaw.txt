# PRD — Mission Control para a estrutura OpenClaw da Flávia

_Atualizado em 2026-04-13_

## 1. Objetivo

Trazer um painel de Mission Control inspirado no repo `carlosazaustre/tenacitOS`, adaptado à estrutura real do ambiente OpenClaw do Alê, com foco em:
- visibilidade operacional centralizada
- leitura segura de agentes, sessões, crons e estado do host
- inspeção controlada de memória e arquivos
- baixo risco de prompt injection persistente
- baixo risco de exfiltração ou abuso do host

O objetivo não é instalar o repo original como está em produção.
O objetivo é absorver a proposta e fazer um deploy seguro, compatível com a arquitetura atual.

---

## 2. Problema que precisa ser resolvido

Hoje a operação tem boa capacidade de execução, mas pouca visualização consolidada em uma única superfície.

Faltam, em um painel só:
- saúde operacional do OpenClaw
- visão dos agentes ativos
- sessões recentes e atividade
- crons e histórico de execução
- estado de memória e arquivos centrais
- alertas operacionais relevantes
- visão rápida do host VPS

Sem isso, parte da operação depende de leitura manual, CLI e memória de contexto.

---

## 3. Resultado desejado

Criar um Mission Control privado, interno e seguro que funcione como camada de observabilidade operacional do ecossistema OpenClaw e permita:
- enxergar o estado do ecossistema OpenClaw em tempo real
- diagnosticar falhas rapidamente
- navegar contexto e memória sem expor superfícies perigosas
- reduzir dependência de shell manual no VPS
- apoiar operação executiva sem virar vetor de ataque ao host ou à memória da Flávia

### Tese do produto

Mission Control não é um painel genérico de administração.
É uma camada privada de observabilidade operacional para a estrutura da Flávia, com privilégios mínimos, foco em leitura e desenho anti-prompt-injection.

---

## 4. Escopo

### 4.1 Escopo inicial

Entregar uma primeira versão com:
- dashboard de saúde do host
- dashboard de agentes
- visão de sessões recentes
- visão de crons configurados
- leitura de arquivos operacionais permitidos
- logs e alertas resumidos
- autenticação forte
- deploy interno privado via Tailscale

### 4.2 Fora do escopo inicial

Não incluir na primeira versão:
- terminal com execução arbitrária
- edição livre de `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`
- escrita irrestrita em `memory/`
- automações destrutivas pelo painel
- controle de infraestrutura crítica pelo browser
- exposição pública aberta na internet sem camada adicional de proteção

---

## 5. Usuários

### Usuário principal
- Alê

### Usuária operacional indireta
- Flávia, como camada operacional e de observabilidade

### Usuários futuros possíveis
- acesso restrito para operação interna, se existir caso real

---

## 6. Requisitos funcionais

### RF1. Dashboard do host
Mostrar:
- CPU
- RAM
- disco
- uptime
- status do gateway OpenClaw
- processos relevantes do OpenClaw
- alertas de degradação

### RF2. Dashboard de agentes
Mostrar por agente:
- id
- nome
- workspace
- modelo principal
- status percebido
- última atividade
- fronteira/função
- vínculos de canal, quando útil

A arquitetura atual a refletir é:
- main
- mensura
- mia
- pcs
- finance
- juridico
- marketing
- producao
- bi
- suprimentos
- rh
- `autopilot` em revisão

### RF3. Sessões
Mostrar:
- sessões recentes
- agente responsável
- última atividade
- resumo curto da última interação
- estado de background task, se houver

### RF4. Crons
Mostrar:
- jobs ativos
- schedule
- último run
- próximo run
- falhas recentes
- crons silenciosos x crons notificáveis

### RF5. Memory browser seguro
Permitir leitura controlada de:
- `memory/*.md`
- `memory/context/*.md`
- `memory/projects/*.md`
- arquivos de documentação permitidos

### RF6. File browser restrito
Permitir leitura apenas de áreas aprovadas, por exemplo:
- `docs/`
- `memory/`
- arquivos markdown operacionais explícitos

### RF7. Alertas operacionais
Exibir alertas úteis como:
- gateway offline
- falha de auth
- cron falhando
- canais com política inconsistente
- perda de conectividade
- risco operacional detectado

### RF8. Busca operacional
Permitir busca textual em:
- docs
- memória
- arquivos markdown operacionais permitidos

### RF9. Observabilidade de custos e uso
Opcional na v1.1:
- uso por agente
- custo estimado
- tendência diária

---

## 7. Requisitos não funcionais

### RNF1. Segurança primeiro
A solução deve ser desenhada como painel de observabilidade com superfícies mínimas de escrita.

### RNF2. Deploy privado via Tailscale
Acesso apenas interno pela tailnet já existente na VPS.

Diretriz:
- sem exposição pública aberta
- sem Cloud Tunnel
- autenticação do app continua obrigatória como segunda barreira
- Tailscale funciona como primeira barreira de rede

### RNF3. Performance suficiente
O painel deve carregar rápido e funcionar bem em VPS modesto.

### RNF4. Operação simples
Deploy, restart e rollback precisam ser simples.

### RNF5. Auditabilidade
Ações de escrita, se existirem, devem ser poucas e auditáveis.

### RNF6. Read-only por padrão
A v1 deve nascer como produto de observabilidade, não de administração ativa.

---

## 8. Riscos centrais

### R1. Prompt injection persistente
Esse é um dos maiores riscos para o nosso ambiente.

Se o painel puder editar ou facilitar alteração de:
- `SOUL.md`
- `AGENTS.md`
- `MEMORY.md`
- `memory/*.md`

então uma instrução hostil pode se tornar persistente e contaminar o comportamento da Flávia.

### R2. Superfície de shell no browser
Qualquer terminal web que execute shell no host aumenta muito o risco.
Mesmo com allowlist, bypass ou erro de validação vira incidente grave.

### R3. Exposição de segredos e topologia
Ler `openclaw.json`, workspaces, bindings e estruturas de canais expõe topologia sensível.

### R4. Escrita indevida em memória operacional
Uma UI de edição aparentemente inocente pode virar vetor para:
- prompt injection
- corrupção de memória
- perda de contexto
- mudança silenciosa de regra operacional

### R5. Dependência direta do host produtivo
Rodar sem sandbox no mesmo host produtivo aumenta o impacto de qualquer falha.

---

## 9. Fixes obrigatórios antes de deploy

Esses fixes devem entrar no plano e não podem ser esquecidos.

### F1. Remover terminal remoto na v1
A rota de terminal não deve entrar na primeira versão em produção.

**Decisão:**
- v1 sem terminal browser
- diagnóstico por APIs seguras e leituras pré-definidas

### F2. Tornar o file browser read-only por padrão
Nada de edição genérica no browser para arquivos operacionais.

**Decisão:**
- leitura controlada na v1
- escrita bloqueada por padrão

### F3. Bloquear escrita em arquivos-raiz sensíveis
Arquivos abaixo devem ser explicitamente read-only:
- `SOUL.md`
- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `IDENTITY.md`
- `TOOLS.md`

### F4. Restringir escrita em `memory/`
Se houver escrita futura, deve ser apenas em áreas muito específicas, com trilha de auditoria e regras de append.

### F5. Criar allowlist de paths
Somente paths aprovados devem ser legíveis pela UI.
Nada de navegação livre no filesystem.

### F6. Endurecer autenticação
Obrigatório:
- senha forte
- secret forte
- cookie seguro
- rate limit
- proteção adicional de rede

### F7. Isolar pela tailnet Tailscale
Modelo recomendado:
- serviço acessível apenas pela rede Tailscale
- bind local ou interface restrita
- proxy local opcional apenas se agregar organização operacional
- sem exposição pública aberta

### F8. Sanitizar rendering de markdown/conteúdo
Evitar qualquer execução ativa ou renderização permissiva demais de conteúdo vindo de memória e docs.

### F9. Criar modo observabilidade primeiro
A primeira entrega deve ser “observe, não altere”.

### F10. Validar compatibilidade com a nossa arquitetura real
O painel não pode assumir workspaces genéricos do repo original.
Precisa refletir:
- `main`
- `mensura`
- `mia`
- `pcs`
- `finance`
- demais agentes ativos
- `autopilot` como item em revisão

---

## 10. Arquitetura proposta

### 10.1 Estratégia recomendada
Não usar o repo original em produção sem adaptação.

Melhor caminho:
- fork interno ou cópia controlada
- remover superfícies perigosas
- adaptar à estrutura OpenClaw real
- subir como painel interno privado via Tailscale

### 10.1.1 Princípios de design
- observabilidade antes de ação
- read-only por padrão
- privilégios mínimos
- anti-prompt-injection by design
- arquitetura real antes de UI genérica
- rollback simples antes de expansão de escopo

### 10.2 Modo de operação
O painel deve operar em três níveis:

#### Nível 1. Observabilidade
- leitura de estado do host
- leitura de agentes
- leitura de sessões
- leitura de crons
- leitura de alertas

#### Nível 2. Inspeção controlada
- leitura de memória aprovada
- leitura de docs aprovados
- busca textual aprovada

#### Nível 3. Escrita mínima futura
Somente depois:
- anotações controladas
- ack de alertas
- comentários operacionais

Nunca começar pelo nível 3.

---

## 11. Deploy recomendado

### Fase A — Auditoria estática completa
Antes de qualquer instalação:
- revisar rotas de API
- revisar middleware/auth
- revisar scripts
- revisar dependências
- revisar leitura/escrita de filesystem
- revisar acessos a shell e child_process

### Fase B — Hardening do código
Executar:
- remover terminal API
- remover PUT genérico de arquivos
- travar paths
- endurecer auth
- reduzir permissões
- sanitizar renderização

### Fase C — Sandbox
Subir primeiro em ambiente isolado:
- diretório separado
- sem acoplamento direto a edição de memória real
- preferencialmente com cópia de dados ou modo somente leitura

### Fase D — Pilot interno
Validar:
- qualidade das métricas
- aderência à arquitetura real
- risco residual
- utilidade operacional

### Fase E — Produção restrita
Subir com:
- acesso privado via Tailscale
- autenticação forte no app
- bind restrito
- logs mínimos de acesso
- rotina de atualização controlada

---

## 12. Critérios de aceite

O Mission Control só pode ir para produção se:
- não houver terminal remoto ativo
- arquivos-raiz sensíveis estiverem bloqueados para escrita
- navegação de arquivo estiver em allowlist restrita
- auth estiver endurecida
- acesso estiver restrito à tailnet Tailscale
- a arquitetura refletir os agentes reais do ambiente
- risco de prompt injection persistente estiver reduzido a nível aceitável
- houver plano de rollback simples

## 12.1 Critérios de segurança verificáveis
- sem terminal web ativo na v1
- sem PUT genérico de arquivos
- sem escrita em `SOUL.md`, `AGENTS.md`, `MEMORY.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`
- sem navegação fora da allowlist definida
- sem exposição pública aberta
- sem edição ampla de `memory/`

## 12.2 Zonas de acesso

### Zona verde — leitura segura
- métricas de host aprovadas
- estado de agentes
- sessões resumidas
- crons
- docs permitidos

### Zona amarela — leitura sensível e controlada
- partes de `memory/`
- partes de `openclaw.json`
- logs operacionais selecionados

### Zona vermelha — proibido na v1
- terminal remoto
- escrita ampla em memória
- edição de arquivos-raiz sensíveis
- navegação livre no filesystem
- ações destrutivas ou administrativas pelo browser

---

## 13. Métricas de sucesso

### Operacionais
- tempo de diagnóstico de falha cai
- menos necessidade de shell manual para checks básicos
- visibilidade mais rápida sobre agentes e crons
- menos atrito para auditoria operacional

### Segurança
- zero escrita acidental em arquivos-raiz sensíveis
- zero exposição pública indevida
- zero terminal web em produção na v1

---

## 14. Plano de implementação sugerido

### Etapa 1
Completar auditoria estática do repo `carlosazaustre/tenacitOS`.

### Etapa 2
Gerar lista fechada de mudanças obrigatórias no código.

### Etapa 3
Criar fork interno seguro ou cópia local adaptada.

### Etapa 4
Implementar versão v1 somente leitura.

### Etapa 5
Subir em sandbox e testar com a arquitetura atual.

### Etapa 6
Publicar internamente com proteção de rede.

---

## 15. Decisão recomendada

**Recomendação:** seguir com o Mission Control, mas não como deploy direto do repo original.

O caminho certo para a nossa estrutura é:
- usar a proposta como base
- adaptar à arquitetura real dos agentes
- remover superfícies perigosas
- lançar uma v1 read-only e privada

Esse é o equilíbrio certo entre ganho operacional e risco aceitável.

---

## 16. Próximo passo objetivo

Próximo passo recomendado:
- fazer a auditoria estática completa do repo
- transformar os achados em checklist técnico de hardening e implantação Tailscale-first
- só depois começar a adaptação/deploy

## 17. Rollback

Se o deploy falhar ou aumentar risco operacional:
- desligar o serviço do Mission Control
- remover o binding de proxy local, se existir
- manter OpenClaw principal intocado
- voltar para a versão anterior do diretório do Mission Control
- preservar logs mínimos para diagnóstico

Princípio:
O rollback do Mission Control não pode depender de intervenção delicada no OpenClaw principal.
