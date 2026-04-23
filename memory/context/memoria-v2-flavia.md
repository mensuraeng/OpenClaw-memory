# Memória v2 da Flávia

_Proposta inicial — 2026-04-22_

## Objetivo

Elevar a qualidade da memória operacional da Flávia sem trocar a fonte de verdade atual.

A Memória v2 não substitui a arquitetura existente.
Ela reorganiza a operação para melhorar quatro coisas:
- captura
- consolidação
- recuperação
- governança

## Princípios

### 1. Arquivo versionado continua sendo a fonte de verdade
A memória oficial continua em arquivos do workspace, especialmente em `memory/context/`, `memory/projects/`, `memory/integrations/`, `memory/content/` e `memory/YYYY-MM-DD.md`.

### 2. Captura bruta não pode disputar lugar com memória final
O que entra rápido durante o dia não deve ser tratado como memória institucional consolidada.

### 3. Memória permanente só entra por promoção explícita
Toda informação nova precisa cair em uma destas saídas:
- lição
- decisão
- pendência
- memória de projeto
- memória documental
- histórico bruto local

### 4. Recall precisa acontecer em camadas
A recuperação correta não é “abrir arquivo grande e reler tudo”, e sim:
1. índice executivo
2. contexto/timeline
3. detalhe completo

### 5. Nem toda informação merece persistência longa
Persistir tudo gera ruído e reduz utilidade. A memória boa não é a que guarda mais; é a que recupera melhor o que importa.

## Estrutura-alvo

### Camada 1 — Painel executivo
**Arquivo:** `MEMORY.md`

Função:
- mostrar estado atual
- apontar onde está cada contexto
- refletir só o que está ativo e relevante

Regra:
- não carregar detalhe operacional
- não competir com arquivos temáticos
- ser curto, confiável e sincronizado

### Camada 2 — Memória consolidada temática
**Arquivos:** `memory/context/*.md`

Função:
- guardar regras permanentes
- guardar decisões estáveis
- guardar pendências executivas reais
- guardar contexto transversal reutilizável

Exemplos:
- `lessons.md`
- `decisions.md`
- `pending.md`
- arquivos temáticos como `pcs-sienge-obras-centros-de-custo.md`

Regra:
- conteúdo estável, reutilizável e de alto valor
- sem despejar log bruto ou histórico redundante

### Camada 3 — Memória por frente / empresa / projeto
**Arquivos:** `memory/projects/**`

Função:
- guardar contexto específico de empresa, projeto ou trilha operacional
- servir como documentação, índice ou histórico por domínio

Regra:
- quando um conteúdo deixa de ser específico e vira base recorrente transversal, a fonte principal sobe para `memory/context/`
- o arquivo de projeto passa a ser ponte, índice ou trilha local

### Camada 4 — Diário operacional bruto
**Arquivos:** `memory/YYYY-MM-DD.md`

Função:
- capturar flushes
- registrar fatos duráveis do dia
- servir como caixa-preta operacional

Regra:
- append-only
- não virar aterro definitivo
- o que for permanente deve ser promovido depois

## Fluxo operacional

### Etapa 1 — Captura
Durante o dia, entra material como:
- decisões em conversa
- comprovantes
- diagnósticos técnicos
- bloqueios
- resultados de teste
- links, referências, fatos operacionais

Destino inicial:
- arquivo de projeto
- memória diária
- documento índice
- histórico bruto

### Etapa 2 — Triagem
Antes de consolidar, cada item deve responder:
- isso é permanente?
- isso é só do projeto?
- isso depende de decisão futura?
- isso é histórico bruto e deve permanecer bruto?
- isso é ruído?

### Etapa 3 — Promoção
Se for relevante e reutilizável:
- erro/padrão → `memory/context/lessons.md`
- decisão estável/preferência → `memory/context/decisions.md`
- tarefa aberta/bloqueio/input → `memory/context/pending.md`
- contexto específico → `memory/projects/...`
- fato do dia → `memory/YYYY-MM-DD.md`

### Etapa 4 — Recall progressivo
Recuperação futura deve seguir esta ordem:
1. `MEMORY.md` para orientação rápida
2. arquivo temático em `memory/context/`
3. arquivo específico em `memory/projects/`
4. diário do dia ou dias relevantes

## Regras de promoção

### Vai para `lessons.md` quando:
- houver erro recorrente
- surgir padrão útil
- houver insight técnico reaproveitável
- a lição puder prevenir reincidência futura

### Vai para `decisions.md` quando:
- o Alê definir preferência estável
- uma regra operacional mudar
- uma arquitetura ou critério for validado
- a decisão precisar ser respeitada em sessões futuras

### Vai para `pending.md` quando:
- a tarefa estiver aberta de verdade
- depender do Alê, de terceiro ou de execução interna ainda não concluída
- houver próximo passo claro

### Vai para `memory/projects/` quando:
- o conteúdo for específico de empresa/projeto/trilha
- o histórico detalhado fizer sentido localmente
- a memória precisar preservar contexto documental

### Fica só no diário quando:
- for fato útil do dia, mas não regra
- for registro histórico de uma sessão
- ainda não houver sinal de permanência

## O que automatizar na Memória v2

### 1. Checklist de promoção no flush
Toda consolidação deve checar:
- o que virou lição?
- o que virou decisão?
- o que virou pendência?
- o que continua só como histórico?

### 2. Detecção de drift entre painel e fonte temática
Sempre que `MEMORY.md` divergir de `pending.md` ou outro arquivo-fonte, isso precisa aparecer como inconsistência a corrigir.

### 3. Separação entre pendência executiva e ruído de inbox
`pending.md` não deve ser depósito de emails brutos. O backlog de inbox precisa ter trilha própria, mantendo `pending.md` como visão executiva.

### 4. Índice curto para bases operacionais recorrentes
Quando uma base crescer, manter:
- fonte principal clara
- ponte documental curta
- índice apontando para a origem oficial

## Piloto inicial recomendado

### Domínio: financeiro MIA

Motivo:
- recorrência real
- histórico crescente
- valor prático imediato
- critério de sucesso claro

Escopo do piloto:
- comprovantes entram como histórico bruto
- romaneio/notas entram como base de confronto
- consolidação futura gera visão `pago`, `pendente`, `parcial`, `ambíguo`
- memória final continua auditável em arquivos

## Ordem de implantação

### Fase 1 — saneamento
- sincronizar `MEMORY.md`
- limpar `memory/context/pending.md`
- promover conteúdo permanente preso no diário
- reduzir duplicação entre `context/`, `projects/` e flushes

### Fase 2 — disciplina operacional
- aplicar checklist de promoção em todo flush
- reforçar diferença entre bruto, consolidado e documental
- formalizar regras para subir conteúdo de `projects/` para `context/`

### Fase 3 — recall melhor
- estruturar recuperação por camadas
- criar índices curtos onde houver base recorrente grande
- reduzir necessidade de releitura manual extensa

### Fase 4 — piloto de captura + consolidação
- testar primeiro em um domínio pequeno
- medir ganho real de clareza, recuperação e governança
- só expandir depois de prova operacional

## Critério de sucesso

A Memória v2 será melhor se entregar:
- menos duplicação
- painel mais confiável
- pendências mais legíveis
- recuperação mais rápida
- promoção mais disciplinada
- continuidade real entre sessões sem virar aterro

## Regra final

Toda melhoria futura na memória precisa passar em 4 testes:
1. melhora captura, recuperação, consolidação ou governança?
2. mantém fonte de verdade clara?
3. preserva auditabilidade?
4. reduz ruído em vez de aumentar?

Se falhar nesses testes, não entra.
