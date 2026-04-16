# Opensquad — piloto prático para LinkedIn assistido

_Atualizado em 2026-04-16_

## Objetivo do piloto

Testar o opensquad como motor satélite para um fluxo assistido de LinkedIn, sem criar sistema paralelo e sem deslocar a governança do ecossistema principal.

## Caso de uso inicial

Produção assistida de post institucional ou pessoal para LinkedIn a partir de um insumo bruto.

Exemplos de insumo:
- notícia do setor
- insight operacional
- case interno
- reflexão executiva
- marco de obra ou entrega

## Escopo do piloto

### Dentro
- transformar um insumo em post LinkedIn
- estruturar pipeline com papéis claros
- criar checkpoints antes da saída final
- medir qualidade, retrabalho e clareza do fluxo

### Fora
- publicação automática sem aprovação
- memória paralela como fonte oficial
- gestão de calendário editorial completa
- operação institucional de páginas do LinkedIn antes da liberação da API apropriada

## Papel do opensquad no fluxo

O opensquad entra apenas como motor de pipeline criativo.

A decisão final, registro operacional e eventual publicação continuam no ecossistema principal.

## Fluxo recomendado

### Etapa 1 — Entrada
Receber um insumo bruto com contexto mínimo:
- tema
- objetivo do post
- ativo: pessoal, MENSURA, MIA ou PCS
- tom desejado
- CTA, se houver

### Etapa 2 — Pesquisa curta
Agente 1: **Pesquisador**

Responsabilidade:
- identificar contexto relevante
- levantar fatos, referências ou ângulos úteis
- evitar aprofundamento excessivo

Saída esperada:
- 3 a 5 bullets úteis
- riscos factuais
- ângulo recomendado

### Etapa 3 — Estratégia
Agente 2: **Estrategista**

Responsabilidade:
- escolher a linha editorial
- definir a estrutura da narrativa
- ajustar ao ativo e ao objetivo

Saída esperada:
- tese principal
- estrutura do post
- variação de gancho
- CTA sugerido

### Etapa 4 — Redação
Agente 3: **Redator**

Responsabilidade:
- gerar rascunho do post
- manter linguagem coerente com o ativo
- evitar excesso de jargão e texto genérico

Saída esperada:
- versão principal
- opcionalmente 1 versão alternativa curta

### Etapa 5 — Revisão
Agente 4: **Revisor**

Responsabilidade:
- verificar clareza
- cortar clichê
- apontar risco reputacional ou factual
- validar consistência do tom

Saída esperada:
- texto revisado
- lista curta de ajustes, se houver

## Checkpoints obrigatórios

### Checkpoint 1 — antes da redação final
Aprovar:
- ângulo
- tese
- estrutura

### Checkpoint 2 — antes de qualquer publicação
Aprovar:
- texto final
- ativo correto
- presença ou ausência de CTA
- risco reputacional

## Governança

### Fonte oficial continua sendo o ecossistema principal
Registrar no OpenClaw/Mission Control apenas:
- insumo usado
- saída aprovada
- decisão relevante
- próximos passos úteis

### O que não registrar
- cadeia inteira de testes irrelevantes
- memória paralela do opensquad como fonte de verdade

## Critérios de sucesso do piloto

### O piloto funciona se:
- reduzir tempo de produção
- aumentar clareza da linha editorial
- exigir pouco retrabalho
- manter checkpoints úteis
- não criar nova bagunça operacional

### O piloto falha se:
- consumir tokens demais para pouca vantagem
- gerar texto genérico demais
- exigir supervisão maior do que o fluxo atual
- criar arquivo, memória ou governança paralela

## Métricas mínimas

Avaliar em 5 a 10 execuções:
- tempo por post
- número de retrabalhos
- qualidade percebida
- aderência ao tom
- esforço de supervisão
- custo aproximado

## Ativos do piloto

### 1. Perfil pessoal do Alê
Modelo: assistido, sempre com aprovação explícita antes de publicar.

### 2. Marca institucional
- MENSURA
- MIA
- PCS

Observação:
No institucional, o piloto deve parar em rascunho/revisão até a trilha de API e governança estar completamente madura.

## Recomendação de implantação

### Rodada 1
Fazer 3 testes:
- 1 post pessoal
- 1 post MENSURA
- 1 post PCS ou MIA

### Rodada 2
Comparar com o fluxo atual:
- mais rápido?
- melhor?
- mais claro?
- mais caro?

### Rodada 3
Decidir:
- expandir
- manter restrito
- encerrar piloto

## Decisão operacional

Se gerar valor, o opensquad continua como ferramenta satélite de conteúdo.

Se não gerar valor claro, a operação mantém o ecossistema atual e absorve apenas os padrões conceituais úteis.
