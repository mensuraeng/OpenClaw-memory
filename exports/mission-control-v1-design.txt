# Mission Control v1 — Design

_Data: 2026-04-13_

## Objetivo

Definir a v1 do Mission Control da Flávia como um painel interno, privado e operacionalmente seguro para observabilidade da operação OpenClaw, com refatoração moderada sobre a base do repo analisado.

## Decisões validadas

- Estratégia: **fork interno com refatoração moderada**
- Método de acesso: **Tailscale-first**
- Escopo de dados da v1:
  - host
  - agentes
  - sessões
  - crons
  - leitura controlada de `docs/`
  - leitura controlada de partes permitidas de `memory/`
- Logs e config na v1: **leitura controlada parcial**
- Ações manuais na v1: **ações operacionais leves**

## Princípios de produto

1. **Observabilidade primeiro**
   O painel existe para reduzir atrito operacional e acelerar diagnóstico.

2. **Superfície mínima de risco**
   Toda funcionalidade deve justificar o risco que adiciona.

3. **Arquitetura real antes de abstração bonita**
   O painel deve refletir o OpenClaw real do ambiente, não um modelo genérico.

4. **Sem confiança implícita no browser**
   O browser é interface de leitura e disparo controlado, não console de poder irrestrito.

5. **Rollback simples**
   O Mission Control não pode se tornar ponto crítico difícil de desligar.

## Escopo funcional da v1

### 1. Host dashboard
Exibir:
- CPU
- RAM
- disco
- uptime
- status do gateway OpenClaw
- estado de processos relevantes
- alertas simples de degradação

### 2. Agents dashboard
Exibir por agente:
- `id`
- nome/função
- workspace
- modelo principal, quando disponível
- última atividade percebida
- vínculos úteis de canal

Agentes-alvo iniciais:
- `main`
- `mensura`
- `mia`
- `pcs`
- `finance`
- `juridico`
- `marketing`
- `producao`
- `bi`
- `suprimentos`
- `rh`
- `autopilot` marcado como "em revisão"

### 3. Sessions view
Exibir:
- sessões recentes
- agente responsável
- última atividade
- resumo curto da última interação
- indicação de task/background quando existir

### 4. Crons view
Exibir:
- jobs ativos
- agendamento
- próximo run
- último run
- falhas recentes quando disponíveis
- distinção entre jobs silenciosos e notificáveis

### 5. Docs browser controlado
Permitir leitura apenas de paths aprovados em `docs/`.

### 6. Memory browser controlado
Permitir leitura apenas de partes aprovadas de:
- `memory/*.md`
- `memory/context/*.md`
- `memory/projects/*.md`

### 7. Logs/config parciais
Permitir apenas leitura controlada e parcial de:
- resumos operacionais de logs
- trechos permitidos de config
- indicadores derivados de saúde

Não haverá leitura irrestrita de logs brutos ou config completa.

### 8. Ações operacionais leves
A v1 pode incluir:
- refresh manual
- ack de alerta
- copiar comando seguro
- abrir link interno
- disparar ações leves explicitamente allowlisted

Possíveis ações allowlisted, sujeitas ao hardening final:
- refresh de status
- rerun de coleta de diagnóstico safe
- abrir detalhe de agente/job/sessão

## Fora do escopo da v1

- terminal web
- shell arbitrário
- edição ampla de arquivos
- edição de arquivos-raiz sensíveis
- navegação livre no filesystem
- leitura completa de logs brutos
- leitura completa de config sensível
- escrita ampla em `memory/`
- automações destrutivas

## Segurança e controle de acesso

### Camada de rede
- acesso apenas pela tailnet Tailscale
- sem exposição pública aberta
- bind restrito no host

### Camada de aplicação
- autenticação forte
- secret forte
- cookie seguro
- rate limit
- trilha mínima de acesso

### Camada de autorização
Tudo o que for lido ou acionado deve passar por allowlist explícita.

## Modelo de permissões da v1

### Leitura permitida
- métricas do host necessárias para diagnóstico
- inventário de agentes
- sessões recentes sanitizadas
- cron jobs e status
- paths aprovados em `docs/`
- subset aprovado de `memory/`
- subset aprovado de config/logs

### Escrita/ação permitida
- ack de alerta
- refresh manual
- ações leves e específicas incluídas em allowlist

### Escrita proibida
- `SOUL.md`
- `AGENTS.md`
- `MEMORY.md`
- `USER.md`
- `IDENTITY.md`
- `TOOLS.md`
- edição ampla de `memory/`
- qualquer ação destrutiva ou shell arbitrário

## Abordagem de arquitetura

### Estratégia recomendada
Usar o repo base como ponto de partida, mas com refatoração moderada para:
- remover superfícies perigosas cedo
- isolar leitura de dados por adaptadores específicos
- separar claramente UI, coleta e autorização

### Componentes propostos

#### 1. UI layer
Responsável por renderização do painel e navegação.

#### 2. Read adapters
Módulos pequenos e específicos para ler:
- host
- agentes
- sessões
- crons
- docs
- memory
- config/logs permitidos

#### 3. Action gateway
Camada pequena para ações manuais leves, sempre com allowlist fechada.

#### 4. Policy layer
Define:
- paths legíveis
- ações permitidas
- dados sanitizados
- campos de config visíveis

## Abordagens consideradas

### Abordagem A — adaptação mínima
Mais rápida, porém com maior risco de herdar acoplamentos e superfícies indevidas.

### Abordagem B — fork interno com refatoração moderada
Melhor equilíbrio entre velocidade, segurança e aderência arquitetural.

### Abordagem C — reimplementação enxuta do zero
Mais limpa e segura em tese, mas mais lenta e com custo maior de entrega inicial.

## Recomendação

Seguir a **Abordagem B**.

Justificativa:
- reaproveita o que for útil
- reduz risco estrutural cedo
- evita carregar toda a dívida do upstream sem necessidade
- mantém espaço para endurecimento real antes de produção

## Fluxo de dados

1. UI solicita dados ao backend.
2. Backend valida permissão pelo policy layer.
3. Backend consulta adapter específico.
4. Adapter sanitiza/recorta saída.
5. UI renderiza visão segura.
6. Se houver ação manual, a action gateway valida se a ação está allowlisted antes de executar.

## Tratamento de erro

- Falha de fonte individual não derruba o painel inteiro.
- Cada card/módulo deve degradar isoladamente.
- Erros sensíveis não devem vazar segredos ou caminhos indevidos.
- Falhas de permissão devem responder com negação explícita.

## Estratégia de testes

### Testes de segurança
- acesso negado fora da allowlist
- tentativa de path traversal bloqueada
- tentativa de ação não allowlisted bloqueada
- tentativa de leitura de arquivo sensível bloqueada

### Testes funcionais
- cards principais renderizam com dados válidos
- falha de uma fonte degrada só o módulo afetado
- filtros e navegação respeitam paths permitidos
- ações leves permitidas funcionam como esperado

### Testes de integração
- leitura dos agentes reais do ambiente
- leitura de sessões reais/sanitizadas
- leitura dos crons reais
- acesso via Tailscale + auth do app

## Critérios de aceite da design v1

A design v1 está correta se entregar:
- observabilidade útil
- superfície reduzida de risco
- aderência à arquitetura real do OpenClaw
- acesso privado via Tailscale
- ações leves apenas, sem terminal e sem edição ampla

## Próximo artefato

Com base nesta design, o próximo passo é gerar o plano de implementação com lista fechada de tarefas e patch list técnica por área do sistema.
