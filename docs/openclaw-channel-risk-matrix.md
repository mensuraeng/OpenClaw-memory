# Matriz Canal × Permissão × Risco

_Data: 2026-04-20_
_Status: draft operacional_

## Objetivo

Definir o nível de autonomia, risco e permissões por superfície de interação do OpenClaw.

Princípio central: ambientes mais expostos operam com menos autonomia e menos capacidade de escrita. Ambientes mais confiáveis podem operar com mais poder, mas continuam auditáveis.

---

## Níveis de risco

- **R0, mínimo**: leitura/observação interna controlada
- **R1, baixo**: ação leve sem impacto externo direto
- **R2, moderado**: alteração interna reversível
- **R3, alto**: ação externa, escrita sensível ou mudança operacional relevante
- **R4, crítico**: ação destrutiva, credencial, config crítica, execução host ampla

Regra geral:
- R3 e R4 exigem confirmação explícita do Alê
- R4 deve ser deny-by-default fora de contexto extremamente controlado

---

## Superfícies

| Superfície | Exemplo | Risco-base | Autonomia padrão | Observação |
|---|---|---:|---|---|
| DM privada confiável | Telegram DM do Alê | R2 | média | melhor contexto para coordenação operacional |
| Grupo operacional | grupos MENSURA / PCS | R2 | média-baixa | pode orientar, resumir, triar; ação externa ainda exige confirmação |
| Grupo público / semiaberto | comunidade, canal aberto | R3 | baixa | modo conservador, sem ferramentas sensíveis |
| Demo | ambiente de apresentação | R3 | baixa | efeito wow controlado, sem poder real perigoso |
| Dashboard / Control UI | Mission Control | R2 | baixa na v1 | preferir read-only na v1 |
| Subagente sandboxed | execução isolada | R2 | média | útil para trabalho interno, sem host access amplo |
| Sessão interna altamente confiável | ambiente técnico controlado | R3 | média-alta | ainda requer confirmação para externo/destrutivo |

---

## Matriz de permissões

### 1. DM privada confiável

**Exemplo:** DM do Alê no Telegram.

**Leitura permitida**
- memória allowlisted
- docs allowlisted
- status de sessão
- histórico relevante
- relatórios e artefatos internos

**Ações leves permitidas**
- escrever drafts internos
- organizar memória autorizada
- rodar análise local
- spawn de subagente sandboxed
- executar auditorias e diagnósticos

**Ações sensíveis**
- envio externo: só com confirmação
- mudança de config: só com confirmação
- restart/update: só com confirmação
- deleção: só com confirmação

**Ações proibidas por default**
- divulgação pública automática
- alteração irreversível sem confirmação
- leitura ampla de segredos

---

### 2. Grupo operacional

**Exemplo:** grupos da MENSURA e PCS.

**Leitura permitida**
- contexto do grupo
- memória/documentação da frente
- status operacional resumido

**Ações leves permitidas**
- triagem
- resumo
- checklist
- follow-up interno proposto
- geração de rascunho

**Ações sensíveis**
- contato com terceiros: só com confirmação
- mudanças em sistemas externos: só com confirmação
- uso de exec com efeito material: só quando claramente justificado

**Ações proibidas por default**
- publicar/postar externamente
- enviar mensagem externa por conta própria
- editar config crítica

---

### 3. Grupo público ou semiaberto

**Exemplo:** Discord público, comunidade, canal com participantes não controlados.

**Leitura permitida**
- apenas contexto estritamente necessário
- nada de memória sensível por default

**Ações leves permitidas**
- responder perguntas
- orientar uso
- demonstrar capacidade segura

**Ações sensíveis**
- bloqueadas por default

**Ações proibidas**
- ferramentas de escrita sensível
- mudanças de config
- ações externas
- leitura de memória interna sensível
- acesso host/elevado

**Modo recomendado**
- `public`

---

### 4. Demo

**Objetivo:** mostrar valor sem abrir poder real demais.

**Permitido**
- fluxos guiados
- leitura sanitizada
- exemplos controlados
- outputs preparados

**Proibido**
- qualquer ação perigosa com dado real
- escrita irreversível
- execução host ampla

**Modo recomendado**
- `demo`

---

### 5. Dashboard / Control UI

**Princípio para v1**
- read-only ou quase read-only
- sem terminal web
- sem navegação livre no filesystem
- sem edição ampla de memória

**Permitido**
- status
- observabilidade
- leitura allowlisted
- ack leve de alertas, se explicitamente seguro

**Proibido**
- shell arbitrário
- PUT genérico de arquivos
- edição de arquivos-raiz sensíveis
- leitura irrestrita de config/logs

---

### 6. Subagente sandboxed

**Permitido**
- análise e síntese
- edição no workspace permitido
- execução em sandbox
- exploração controlada de código/doc

**Restrições**
- sem host access amplo
- sem dependência de permissão invisível
- sem agir fora da tarefa delegada

**Uso ideal**
- trabalhos médios e longos
- tarefas com exploração
- auditoria, refatoração, documentação, consolidação

---

## Tabela resumida

| Contexto | Ler memória | Escrever memória | Exec | Externo | Config crítica | Observação |
|---|---|---|---|---|---|---|
| DM confiável | sim, allowlisted | sim, controlado | sim, com critério | só com confirmação | só com confirmação | contexto principal de trabalho |
| Grupo operacional | sim, da frente | limitado | limitado | só com confirmação | não por padrão | priorizar coordenação |
| Grupo público | mínimo | não por padrão | não por padrão | não | não | deny-by-default |
| Demo | sanitizado | mínimo | controlado | não | não | show seguro |
| Dashboard v1 | allowlisted | quase não | não / muito limitado | não | não | observabilidade |
| Subagente sandboxed | sim, necessário | no escopo | sim, sandbox | não por padrão | não | execução interna |

---

## Regras transversais

### Confirmação obrigatória
Sempre exigir confirmação do Alê para:
- e-mail externo
- mensagem externa
- post em rede social
- alteração crítica de config
- deleção ou overwrite sensível
- restart com risco material
- qualquer ação R3 ou R4

### Deny-by-default
Aplicar deny-by-default em:
- superfícies públicas
- demos
- dashboards
- qualquer contexto com identidade/participantes ambíguos

### Auditoria mínima
Sempre que houver ação sensível, registrar pelo menos:
- pedido/origem
- ação executada
- contexto/canal
- necessidade de confirmação
- resultado

---

## Próximos ajustes sugeridos
- cruzar esta matriz com os modos `internal`, `operational`, `public`, `demo`
- mapear tools por modo
- derivar checklist de hardening por superfície
