# Relatório CCSP - Casa 7

Use esta referência quando o pedido for:
- `Relatório CCSP - Casa 7`
- relatório semanal / executivo da Casa 7
- consolidar cronograma + ata + deliberações da Casa 7
- gerar atualização executiva no padrão MIA para a CCSP Casa 7

## Objetivo
Gerar um relatório executivo padronizado da obra **CCSP Casa 7** a partir de três insumos principais:
1. Cronograma
2. Ata de reunião
3. Deliberações consolidadas

O padrão visual e estrutural deve seguir o HTML de referência anexado pelo Alê na sessão de 2026-04-14.

## Regra de ativação
Sempre que o usuário pedir **Relatório CCSP - Casa 7**, assumir este formato como padrão, salvo instrução explícita em contrário.

## Insumos mínimos
### Obrigatórios
- dados atualizados do cronograma
- ata de reunião ou resumo de visita
- deliberações consolidadas / plano de ação

### Desejáveis
- data da visita
- responsável técnico de campo
- prazo contratual
- avanço global
- status por ambiente
- pendências críticas e bloqueios externos

## Estrutura obrigatória da saída

### 1. Header executivo
- marca MIA
- tipo do documento: `Relatório de Visita & Ata de Reunião`
- referência do documento
- título do projeto
- período da semana
- pills de semana e status executivo

### 2. Barra técnica
- data da visita
- engenheiro de campo
- prazo contratual
- duração total
- avanço global atual

### 3. Banner de alerta
- frase curta com o principal risco executivo da semana
- explicação de 1 parágrafo

### 4. Cronograma executivo
- KPIs por onda / frente
- tabela com frentes, responsável, datas, progresso e status
- destacar risco de prazo, caminho crítico e bloqueios externos

### 5. Leitura por frente executiva
- blocos por ambiente
- percentual por ambiente
- bullets classificados em concluído, pendência MIA, dependência de terceiro, bloqueio e risco

### 6. Foco operacional da semana
- cards numerados
- título curto da ação
- explicação objetiva
- responsável, prazo e prioridade

### 7. Ata de reunião
- tópicos numerados
- descrição executiva por tema
- bloco de decisão
- bloco de ação

### 8. Deliberações consolidadas
- lista final consolidada por criticidade
- responsável
- prazo ou condição
- marcar concluído, em aberto, urgência ou atenção

### 9. Footer
- assinatura institucional MIA
- referência do documento
- marca confidencialidade

## Regras de conteúdo
- Não inventar dado ausente. Se faltar dado, deixar explícito no texto.
- Priorizar leitura executiva, não narrativa longa.
- Separar claramente o que é:
  - executado
  - pendente da MIA
  - pendente de terceiros
  - decisão do cliente / gerenciadora
  - risco contratual
- Quando houver risco de prazo, dizer o motivo causal, não só o sintoma.
- Quando houver bloqueio externo, citar quem precisa responder.
- Quando houver decisão de reunião, converter em ação com responsável e prazo sempre que possível.

## Regra de formatação
Se o usuário pedir o relatório final, preferir gerar HTML estruturado no padrão do modelo de referência.

Template-base oficial desta obra:
- `assets/ccsp-casa7-relatorio-template.html`

Usar este arquivo como base visual e estrutural, adaptando apenas os dados variáveis da semana corrente.

## Mapeamento dos insumos para a saída
### Cronograma alimenta
- barra técnica
- KPIs
- cronograma executivo
- risco de prazo
- status por frente

### Ata de reunião alimenta
- seção de ata
- justificativa dos bloqueios
- decisões executivas
- explicação causal do risco

### Deliberações consolidadas alimentam
- foco operacional da semana
- deliberações consolidadas
- responsáveis, prazos e criticidade

## Regra de decisão
Se os insumos vierem incompletos:
- gerar o relatório com o que houver
- marcar o nível de completude implicitamente no texto
- explicitar lacunas relevantes
- nunca preencher lacuna crítica com invenção
