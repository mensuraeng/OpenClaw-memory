# Resumo para o Claude, acessar a mesma memória operacional da Flávia

## Objetivo
Fazer o Claude operar com o mesmo contexto útil da Flávia, sem depender de histórico bruto de chat, e ajudar a elevar esse sistema de memória para um segundo cérebro operacional 10/10.

## Princípio central
A memória canônica não está em NotebookLM, nem em transcript solto.
A fonte de verdade operacional está no workspace do OpenClaw, principalmente nestes arquivos:

- `/root/.openclaw/workspace/AGENTS.md`
- `/root/.openclaw/workspace/SOUL.md`
- `/root/.openclaw/workspace/IDENTITY.md`
- `/root/.openclaw/workspace/USER.md`
- `/root/.openclaw/workspace/MEMORY.md`
- `/root/.openclaw/workspace/HEARTBEAT.md`
- `/root/.openclaw/workspace/memory/context/*.md`
- `/root/.openclaw/workspace/memory/projects/*.md`
- `/root/.openclaw/workspace/memory/YYYY-MM-DD.md`

## Como a memória está organizada

### 1. Arquivos de identidade e operação
- `SOUL.md` → personalidade, valores, forma de operar, regras de delegação.
- `IDENTITY.md` → papel da Flávia, limites, integrações, posição na arquitetura.
- `USER.md` → perfil do Alê, estilo de trabalho, aversões, prioridades.
- `AGENTS.md` → regras operacionais, limites de autonomia, protocolos de registro e uso de memória.

### 2. Painel executivo
- `MEMORY.md` é o painel de continuidade.
Não é depósito de conteúdo. Ele responde:
  - o que está ativo
  - o que está travado
  - o que está faltando
  - onde está cada contexto

### 3. Memória temática
- `memory/context/decisions.md` → decisões permanentes
- `memory/context/lessons.md` → lições aprendidas
- `memory/context/pending.md` → pendências reais
- `memory/context/people.md` → pessoas relevantes
- `memory/projects/*.md` → contexto por projeto

### 4. Nota diária
- `memory/YYYY-MM-DD.md` é rascunho operacional do dia
- não deve virar depósito permanente
- o que importa precisa ser promovido depois para arquivos temáticos

## Regra de boot da Flávia
Ao iniciar sessão principal, o contexto-base carregado é:
1. `SOUL.md`
2. `IDENTITY.md`
3. `USER.md`
4. nota diária de hoje
5. nota diária de ontem, se existir
6. `HEARTBEAT.md`
7. `MEMORY.md` (apenas sessão direta com o Alê)

## O que o Claude precisa fazer para operar alinhado

### Leitura mínima inicial
Se for atuar como copiloto operacional, ele precisa ler antes:
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `MEMORY.md`
- nota diária atual
- `memory/context/decisions.md`
- `memory/context/pending.md`
- `memory/context/lessons.md`

### Regra de ouro
Não usar histórico inteiro de conversa como memória principal.
Usar os arquivos do workspace como memória institucional.

## Estado atual importante da operação

### Frentes ativas
- Setup OpenClaw + Flávia em andamento
- Microsoft Graph ativo para Mensura, MIA e Flávia
- Mission Control evoluído até as 12 fases de task tracking
- OpenClaw Memory saiu do MVP e está em transição para segundo cérebro maduro
- NotebookLM definido como camada auxiliar de pesquisa/síntese, não memória canônica
- PCS ↔ Sienge avançou muito na descoberta real, mas segue bloqueado por permissão/admin OAuth

### Bloqueios reais atuais
- NotebookLM ainda bloqueado por autenticação Google no host atual
- produção do Mission Control ainda não teve paridade de versão comprovada no domínio público
- PCS ↔ Sienge agora tem causa raiz clara: tenant usa Sienge ID, não provedor local
- não existe aplicação OAuth cadastrada para PCS SERVICES
- usuário do Alê aparece como `Usuário padrão` no admin.sienge.com.br da organização, bloqueando criação da aplicação OAuth

### Último avanço concreto em PCS ↔ Sienge
- diagnóstico real fechou que o tenant usa `Sienge ID`
- o endpoint local `/sienge/oauth/token` não serve nesse tenant
- a solução correta é criar aplicação OAuth em `admin.sienge.com.br`
- como o perfil exibido está como `Usuário padrão`, foi enviado e-mail para `philippe.santos@pcsengenharia.com.br` pedindo liberação/permissão administrativa ou criação da aplicação OAuth
- cópia foi enviada para `alexandre@pcsengenharia.com.br` e `andre@pcsengenharia.com.br`

## Regras permanentes que o Claude precisa respeitar

### Saída externa
- toda saída externa deve passar pela Flávia/coordenação central
- exceção apenas para bindings institucionais já formalizados

### E-mail
- por padrão, e-mail externo deve sair do remetente da Flávia
- se for para sair do e-mail do Alê, isso precisa ser pedido explicitamente
- nesta operação específica da PCS, o Alê pediu explicitamente envio em nome dele para o Philippe

### Padrão 10/10
Tudo que importa deve ser estruturado, operado e entregue em padrão 10/10.
Nada meia-boca como estado final.

### Modo agente
Se a tarefa for interna, reversível e segura, executar de ponta a ponta sem ficar pedindo checkpoint.
Parar apenas em caso de:
- bloqueio real
- erro real
- risco alto
- irreversibilidade
- necessidade de autorização primordial

## O que melhorar agora na memória
Se o Claude for ajudar, o melhor foco não é criar outra memória paralela.
É fortalecer esta.

### Melhorias prioritárias
1. ampliar captura automática de eventos reais do OpenClaw, Mission Control, e-mail e tarefas
2. melhorar promoção automática de notas diárias para memória institucional
3. enriquecer consultas executivas como:
   - o que mudou hoje?
   - o que mudou na semana?
   - quais decisões seguem abertas?
   - quais riscos cresceram?
4. reduzir dependência de leitura manual de arquivos dispersos
5. fortalecer deduplicação e classificação de eventos
6. manter separação clara entre:
   - memória canônica
   - rascunho diário
   - síntese auxiliar de NotebookLM

## Sugestão prática para o Claude
Se ele tiver acesso ao repositório/workspace, peça para ele:
1. mapear a arquitetura atual da memória
2. identificar gargalos de captura, promoção, consulta e dedupe
3. propor melhorias que reutilizem o sistema existente, sem criar um stack paralelo
4. priorizar robustez operacional, auditabilidade e continuidade entre sessões
5. entregar recomendações em cima de:
   - `/root/.openclaw/workspace/projects/openclaw-memory`
   - `/root/.openclaw/workspace/MEMORY.md`
   - `/root/.openclaw/workspace/memory/context/*`

## Pedido pronto para colar no Claude
"Quero que você me ajude a evoluir o sistema de memória operacional abaixo, sem criar uma memória paralela. A fonte de verdade está no workspace do OpenClaw, especialmente em AGENTS.md, SOUL.md, IDENTITY.md, USER.md, MEMORY.md, HEARTBEAT.md, memory/context/*, memory/projects/* e memory/YYYY-MM-DD.md. Analise a arquitetura atual, identifique gargalos de captura, promoção, deduplicação, consulta executiva e continuidade entre sessões, e proponha melhorias concretas para levar esse sistema a um segundo cérebro operacional 10/10. Priorize robustez, simplicidade, auditabilidade e utilidade executiva real. Considere também o projeto /root/.openclaw/workspace/projects/openclaw-memory como núcleo técnico dessa evolução."