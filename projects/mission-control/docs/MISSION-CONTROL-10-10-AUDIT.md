# Mission Control 10/10 — Auditoria contra benchmark do vídeo

_Atualizado em 2026-04-29_

## Decisão executiva

O vídeo confirma uma direção correta, mas a nossa adaptação não deve copiar o dashboard dele. Para o Alê, o Mission Control 10/10 precisa conectar:

```text
missão → projetos → tarefas → agentes → memória → documentos → evidência → decisão
```

O Mission Control atual já tem boa parte da infraestrutura. A lacuna principal não é falta de telas; é integração entre telas, dados canônicos e critérios de decisão.

## Nota atual

| Camada | Nota | Diagnóstico |
|---|---:|---|
| Mission Control atual | 8,1/10 | Muitas telas já existem, mas ainda com integração parcial entre projeto, tarefa, memória, docs e agentes. |
| Mission Control + `/openclaw` v1 | 8,8/10 | Ganhou cockpit de memória, validadores e busca com fonte. |
| Mission Control 10/10 alvo | 10/10 | Exige grafo operacional unificado e automação segura orientada por missão. |

## Benchmark do vídeo vs nossa realidade

| Ferramenta do vídeo | Já temos? | Nota atual | Adaptação necessária |
|---|---|---:|---|
| Task board / Kanban | Sim: `/tasks`, `/kanban`, Task Board Lite | 8,2 | Unificar tarefas com `WORKING.md`, `pending.md`, sessões e subagentes. Criar lane de revisão do Alê apenas para decisões reais. |
| Live activity feed | Sim: `/activity`, `/logs`, eventos de tasks | 7,5 | Amarrar cada evento a task/projeto/agente/documento. Hoje ainda parece feed solto. |
| Calendar / cron visibility | Sim: `/calendar`, `/cron` | 8,5 | Marcar quais crons são saúde, growth, financeiro, projeto, memória. Health limpo deve ficar silencioso. |
| Project screen | Parcial: projetos existem no 2nd-brain, mas não há `/projects` executivo forte | 5,8 | Criar tela de projetos a partir de `/root/2nd-brain/04-projects`, com progresso, última ação, riscos, docs, tarefas e memórias ligadas. |
| Memory screen | Sim: `/memory`, `/memory-health`, `/openclaw` | 8,8 | Evoluir busca lexical para embeddings/blocos e consolidar ranking por autoridade. |
| Docs tool | Parcial: `/files`, `/reports`, docs em pastas | 6,2 | Criar biblioteca `/docs` categorizada para PRD, proposta, relatório, apresentação, runbook, evidência, rascunho comercial. |
| Team screen | Sim: `/agents`, matriz/AGENT-MAPs | 7,6 | Criar visão org chart 10/10 com missão, papéis, autoridade, modelo, canal, status e quando delegar. |
| Mission statement | Parcial em SOUL/AGENTS/USER | 6,8 | Exibir missão operacional no topo de `/openclaw` e `/agents`; usar como filtro para tarefas proativas. |
| Office visual | Sim: `/office` | 8,0 | Conectar visual ao estado real de tarefas/sessões, não só estética. |
| Reverse prompting | Conceito existe, mas não está operacionalizado | 5,5 | Criar prompts/botões: “qual tarefa avança projeto crítico?”, “o que está parado?”, “qual risco estou ignorando?”. |
| Custom tools sob demanda | Sim: Mission Control + skills | 7,4 | Criar processo de proposta → PRD curto → implementação → validação → commit. |

## O que realmente aumenta nosso padrão

### 1. Grafo operacional unificado

Cada item relevante deve poder responder:

```text
Projeto relacionado?
Tarefas relacionadas?
Agente responsável?
Documentos gerados?
Memórias/decisões ligadas?
Última evidência?
Próximo passo?
```

Sem isso, o Mission Control vira painel bonito, mas não vira cérebro operacional.

### 2. `/projects` executivo

Tela prioritária a criar.

Dados de origem:
- `/root/2nd-brain/04-projects/`
- `/root/2nd-brain/02-context/pending.md`
- `/root/2nd-brain/06-agents/flavia/WORKING.md`
- `runtime/tasks/`
- documentos em `docs/`, `reports/`, `projects/*/docs/`

Campos mínimos:
- projeto;
- empresa/domínio;
- status;
- prioridade;
- última movimentação;
- próximo passo;
- risco;
- owner/agente;
- tarefas abertas;
- documentos vinculados;
- decisões vinculadas.

### 3. `/docs` como biblioteca de documentos

Não basta file browser. Precisa ser uma biblioteca executiva.

Categorias:
- PRD;
- arquitetura;
- proposta;
- apresentação;
- relatório;
- runbook;
- evidência;
- rascunho comercial;
- jurídico/contratual;
- financeiro.

Todo documento criado por agente deveria ter metadados mínimos:

```yaml
tipo:
empresa:
projeto:
autor_agente:
status: rascunho | revisao | aprovado | arquivado
sensibilidade:
origem:
```

### 4. Team / Agent Org 10/10

A tela `/agents` deve virar a fonte visual de roteamento operacional.

Campos mínimos por agente:
- missão;
- escopo;
- autoridade;
- limites;
- modelo/runtime;
- canal externo permitido ou não;
- quando acionar;
- evidência de última validação;
- tarefas abertas;
- riscos conhecidos.

### 5. Reverse prompts como botões de gestão

Criar Quick Actions internas:

- “Qual tarefa agora avança o projeto mais importante?”
- “Qual frente está parada há tempo demais?”
- “Qual risco operacional estou ignorando?”
- “Qual pendência depende realmente do Alê?”
- “O que pode ser resolvido pela Flávia em silêncio?”
- “Que documento precisa ser promovido para memória canônica?”

Essas ações não devem executar side effects externos. São análise/planejamento/triagem.

### 6. Heartbeat ligado ao task board, com silêncio inteligente

Adaptação aprovada com guardrail:

- heartbeat pode consultar tarefas atribuídas à Flávia/OpenClaw;
- pode avançar tarefas internas seguras;
- deve registrar evidência;
- só avisa Alê se houver problema, bloqueio, decisão necessária ou conclusão material;
- nunca executa ação externa sem aprovação.

## Roadmap recomendado

### Sprint 1 — Projetos e docs

1. Criar `/projects` executivo a partir do 2nd-brain.
2. Criar `/docs` library com indexação e categorias.
3. Criar schema de metadados para documentos.

### Sprint 2 — Integração operacional

1. Vincular task ↔ projeto ↔ agente ↔ documento ↔ memória.
2. Adicionar últimas evidências por projeto.
3. Adicionar alertas de projeto parado.

### Sprint 3 — Agentes e missão

1. Evoluir `/agents` para Team Screen 10/10.
2. Exibir missão operacional no topo.
3. Criar botões de reverse prompt orientados por missão.

### Sprint 4 — Automação segura

1. Heartbeat lê task board e executa tarefas internas seguras.
2. Consolidação noturna promove docs/memórias com validação.
3. QA gate antes de commit: segredo, sidecar, data, owner, próximo passo.

## Guardrails permanentes

- Mission Control não vira fonte de verdade acima do GitHub/2nd-brain.
- `/openclaw` e futuras telas internas devem ser protegidas por autenticação forte.
- Health limpo não manda mensagem ao Alê.
- External write continua exigindo confirmação explícita.
- Não criar ferramenta porque é bonita; criar porque reduz risco, aumenta decisão ou acelera execução.

## Conclusão

O que fizemos com `/openclaw` aumenta o padrão porque aproxima memória, validação e busca de uma camada executiva. Mas o salto 10/10 exige agora conectar o sistema em torno de projetos e documentos.

Próximo melhor passo: criar `/projects` e `/docs` antes de mexer em estética ou office visual.

## Registro de implantação — Executive Graph v1

_Atualizado em 2026-04-29_

Incremento implantado em modo read-only/protegido:

- `/projects`: cockpit executivo de projetos conectado a tarefas, documentos, evidências, decisões e agente sugerido.
- `/docs`: biblioteca executiva de documentos por categoria, empresa/domínio, status, sensibilidade e fonte.
- `/api/executive-graph`: API interna read-only para agregar dados de `2nd-brain`, `workspace`, `runtime` e task board.
- Guardrail mantido: Mission Control não vira fonte de verdade acima de GitHub/2nd-brain e não executa writes externos.

Validação local:

- `npm run build`: OK.
- Rotas sem autenticação em localhost: `/projects` e `/docs` retornam `307` para login.
- API sem autenticação retorna `401`.
- API autenticada local retorna `200`, com projetos/documentos/evidências indexados.
