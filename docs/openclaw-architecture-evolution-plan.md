# Plano de Evolução da Arquitetura OpenClaw

_Data: 2026-04-20_
_Status: draft operacional_

## Objetivo

Transformar os aprendizados recentes sobre OpenClaw, Mission Control, especialização por agentes e operação em canais reais em um plano prático de evolução em 3 fases:

1. endurecer
2. provar
3. escalar

O foco não é inventar uma arquitetura nova do zero. É reduzir risco, tornar capacidades observáveis e crescer sem perder controle.

---

## Resumo executivo

A direção atual está correta em quatro frentes:
- agentes especializados com `main` como coordenador
- memória documental separada por frente
- preocupação real com validação em runtime
- orientação para trabalho operacional real, não só demo

Os maiores gaps atuais não são de visão, e sim de maturidade operacional:
- permissões por superfície ainda precisam endurecer
- falta um catálogo explícito de capacidades com status real
- improvisação/fallback ainda não está suficientemente observável
- falta separar melhor o que está desenhado, testado, robusto e pronto para produção

---

## Diagnóstico rápido

### Já temos forte
- especialização (`main` + agentes por frente)
- memória documental por empresa
- princípio de validação real, não só desenho
- regra shared vs específica para skills
- postura operacional orientada a entrega

### Falta fortalecer
- guardrails por canal/superfície
- modos explícitos de operação (`internal`, `operational`, `public`, `demo`)
- kill switch e contenção real
- mapa vivo de capacidades
- prova recorrente de runtime
- UX nativa por superfície

---

# Fase 1, endurecer

## Objetivo

Reduzir risco e aumentar previsibilidade antes de ampliar autonomia ou escala.

## Resultados esperados
- matriz de permissão por canal e modo
- ações sensíveis claramente bloqueadas fora do contexto certo
- contenção real para ambientes públicos ou semiabertos
- política unificada de confirmação para ações externas

## 1.1 Matriz canal × permissão × risco

Criar uma matriz oficial com pelo menos estes contextos:
- privado confiável
- grupo operacional
- grupo público
- demo
- dashboard/control UI
- subagente sandboxed

Para cada contexto, definir:
- leitura permitida
- ações leves permitidas
- ações sensíveis permitidas
- ações proibidas
- necessidade de confirmação
- nível de autonomia

### Entregável
`docs/openclaw-channel-risk-matrix.md`

---

## 1.2 Modos explícitos de operação

Formalizar modos operacionais do sistema:
- `internal`
- `operational`
- `public`
- `demo`

Cada modo deve declarar:
- se pode agir ou só observar
- se pode usar ferramentas de escrita
- se pode usar exec/shell
- se pode falar com terceiros
- quando precisa de confirmação do Alê
- qual nível de logging/auditoria exige

### Entregável
`docs/openclaw-operating-modes.md`

---

## 1.3 Kill switch e contenção

Revisar o que realmente acontece quando um fluxo precisa parar.

Checklist:
- o sistema para mesmo ou reativa por outro caminho?
- existe task resiliente que reaparece após cancelamento?
- existe fluxo assíncrono sem trilha clara de interrupção?
- o operador entende como interromper com segurança?

### Entregável
`docs/openclaw-containment-and-kill-switch.md`

---

## 1.4 Política única para ações externas

Consolidar numa regra simples e inequívoca:
- enviar e-mail
- enviar mensagem
- publicar post
- alterar integração crítica
- apagar/modificar recurso sensível

Tudo isso deve seguir uma política única de confirmação e trilha de auditoria.

### Entregável
`docs/openclaw-external-actions-policy.md`

---

## Critério de conclusão da Fase 1
- existe matriz de risco por superfície
- existe definição oficial de modos
- existe política clara para ações externas
- existe revisão de contenção e parada
- superfícies públicas ou semiabertas operam em deny-by-default

---

# Fase 2, provar

## Objetivo

Separar arquitetura bonita de capacidade realmente operacional.

## Resultados esperados
- catálogo vivo de capacidades
- checklist padrão de validação
- diferenciação entre desenho, teste, robustez e produção
- fallback/improviso mais observável

## 2.1 Catálogo de capacidades

Criar um inventário das capacidades importantes do ecossistema. Exemplo inicial:
- triagem de inbox
- memória documental
- skill audit
- delegação entre agentes
- WhatsApp
- LinkedIn pessoal
- LinkedIn institucional
- Sienge/PCS
- Mission Control/dashboard
- crons operacionais
- consolidação de memória

Para cada capacidade, marcar:
- dono
- objetivo
- dependências
- status: `desenhada | testada | validada em runtime | robusta | produção`
- evidência mais recente
- riscos conhecidos
- fallback

### Entregável
`docs/openclaw-capability-catalog.md`

---

## 2.2 Checklist padrão de validação operacional

Toda capacidade relevante deve ter um checklist padrão com:
- caso real executado
- evidência de output
- limite conhecido
- falhas conhecidas
- risco operacional
- rollback ou fallback
- data da última validação

### Entregável
`docs/openclaw-operational-validation-checklist.md`

---

## 2.3 Prova contínua

Capacidade crítica não pode depender só de uma validação antiga.

Definir quais frentes exigem revalidação periódica, por exemplo:
- canais externos
- publicação institucional
- integrações com autenticação
- rotinas financeiras
- Mission Control

Modelo sugerido:
- smoke tests leves para capacidade crítica
- revalidação manual quando houver mudança estrutural
- downgrade explícito de status quando a prova recente vencer

### Entregável
`docs/openclaw-capability-revalidation-policy.md`

---

## 2.4 Observabilidade do improviso

Quando o agente improvisar ou contornar problema, registrar pelo menos:
- o que faltou
- qual fallback usou
- se a saída foi completa, parcial ou arriscada
- se a solução deve virar regra permanente

### Entregável
`docs/openclaw-improvisation-and-fallback-observability.md`

---

## Critério de conclusão da Fase 2
- capacidades relevantes estão catalogadas
- existe status real de maturidade por capacidade
- existe checklist de validação padronizado
- existe política de revalidação
- improvisos e fallbacks relevantes ficam explicáveis

---

# Fase 3, escalar

## Objetivo

Crescer o ecossistema sem virar caos ou teatro arquitetural.

## Resultados esperados
- expansão disciplinada de agentes e skills
- memória mais acionável
- experiências mais nativas por superfície
- menos duplicação e mais reaproveitamento real

## 3.1 Especialização com prova

Expandir agentes especializados só quando houver:
- uso recorrente
- fronteira clara
- ganho operacional real
- prova de handoff útil com `main`

Evitar:
- multiplicar agentes por estética
- criar agente sem dono operacional
- agente sem memória ou skill próprias bem justificadas

### Entregável
revisão periódica da topologia de agentes

---

## 3.2 Skills como produto interno

Fortalecer o ecossistema de skills com:
- catálogo oficial
- auditoria calibrada
- política shared vs específica
- revisão periódica das skills mais críticas

### Entregáveis
- evolução do `openclaw-skill-audit`
- inventário oficial de skills
- política de revisão contínua

---

## 3.3 Memória acionável

A memória deve ser mais do que arquivo histórico.
Ela precisa alimentar execução.

Exemplos:
- `ficha-cadastral.md` virando base para formulários e propostas
- `dados-institucionais.md` virando fonte padrão para resposta e cadastro
- memória documental alimentando agentes por frente automaticamente

### Entregável
`docs/openclaw-actionable-memory-patterns.md`

---

## 3.4 UX por superfície

Formalizar comportamento nativo por canal:
- Telegram
- WhatsApp
- dashboard web
- outputs longos/documentais
- voz/áudio

Definir:
- tamanho padrão de resposta
- quando resumir
- quando usar estrutura mais formal
- anti-padrões por canal

### Entregável
`docs/openclaw-surface-behavior-policy.md`

---

## Critério de conclusão da Fase 3
- expansão de agentes ocorre com prova, não por intuição
- skills têm política clara de qualidade e posicionamento
- memória alimenta execução de forma reutilizável
- o comportamento do sistema parece nativo em cada superfície

---

# Ordem recomendada

## Agora
Fase 1, endurecer

## Depois
Fase 2, provar

## Só então
Fase 3, escalar

Razão: o maior risco atual não é falta de visão. É escalar antes de endurecer e provar.

---

# Próximos 3 artefatos práticos

## 1. Matriz canal × permissão × risco
Arquivo alvo: `docs/openclaw-channel-risk-matrix.md`

## 2. Catálogo de capacidades com status real
Arquivo alvo: `docs/openclaw-capability-catalog.md`

## 3. Checklist padrão de validação operacional
Arquivo alvo: `docs/openclaw-operational-validation-checklist.md`

Esses três artefatos são a ponte entre a estratégia e a operação.

---

# Critério 10/10

A arquitetura pode ser considerada próxima de 10/10 quando:
- canais e superfícies têm guardrails proporcionais ao risco
- capacidades críticas têm prova recente e status claro
- memória documental alimenta execução real
- especialização por agentes melhora a operação em vez de complicá-la
- improvisação existe, mas é segura, observável e auditável
