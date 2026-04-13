# Revisão do PRD do Mission Control usando a lógica Brainstorm + Writing Plans

_Atualizado em 2026-04-13_

Documento de revisão do PRD `docs/prd-mission-control-openclaw.md` com a disciplina conceitual do fluxo Superpowers:
- Brainstorm
- Writing Plan

Objetivo: tensionar melhor o PRD antes de transformar isso em execução.

---

## 1. Brainstorm

### 1.1 Pergunta central

Qual é a forma certa de trazer um Mission Control para a estrutura da Flávia sem criar uma nova superfície de fragilidade operacional, segurança ou prompt injection?

---

### 1.2 O que estamos realmente tentando resolver

O problema real não é “ter um dashboard bonito”.

O problema real é:
- falta de observabilidade consolidada
- baixa ergonomia para diagnóstico
- dependência excessiva de CLI e contexto mental
- pouca visualização do estado dos agentes, crons, sessões e host

Se o projeto virar apenas interface visual, ele falha no objetivo.
Se virar uma central com privilégios demais, ele também falha.

---

### 1.3 Tensões principais

#### Tensão A — observabilidade vs superfície de ataque
Quanto mais o painel consegue fazer, mais perigoso ele fica.

#### Tensão B — conveniência vs disciplina operacional
Editar memória pelo browser é conveniente, mas perigoso demais no nosso caso.

#### Tensão C — velocidade de deploy vs desenho correto
Instalar o repo rápido é tentador. Adaptar direito é mais lento, mas é o caminho certo.

#### Tensão D — painel genérico vs arquitetura real
O repo original é genérico. Nossa estrutura é específica:
- vários agentes com fronteiras definidas
- memória operacional crítica
- heartbeat silencioso
- risco real de prompt injection persistente

---

### 1.4 Perguntas que o PRD precisa responder melhor

1. O produto é de observabilidade, operação ou administração?
2. Quais ações o painel pode executar sem criar risco desproporcional?
3. Quais dados sensíveis ele pode ler e quais não pode?
4. Onde exatamente ele roda?
5. Ele lê do ambiente real ou de uma camada espelhada/cacheada?
6. Qual é o modelo de autenticação e isolamento de rede?
7. Qual é o rollback se o deploy der errado?
8. Como impedir que o painel vire vetor de edição indevida da memória da Flávia?

---

### 1.5 Hipóteses de produto

#### Hipótese 1 — Painel somente leitura
Mais seguro. Melhor ponto de partida.

#### Hipótese 2 — Painel com escrita controlada
Viável só depois de maturidade, trilha de auditoria e escopo mínimo.

#### Hipótese 3 — Painel com terminal e ações administrativas
Não recomendado para a nossa v1. Risco alto demais.

**Conclusão do brainstorm:**
A v1 precisa ser claramente um produto de **observabilidade privada, read-only por padrão, com escrita quase nula**.

---

### 1.6 Riscos que merecem destaque maior no PRD

#### Risco 1 — prompt injection persistente
Hoje esse é um risco estrutural, não acessório.
Qualquer feature de edição de memória precisa ser tratada como risco crítico.

#### Risco 2 — leitura excessiva de contexto sensível
O painel não pode navegar livremente por tudo que existe em `~/.openclaw`.

#### Risco 3 — confiança excessiva no auth do app
Auth do app sozinha não basta. Precisa de camada adicional de rede.

#### Risco 4 — virar “painel de tudo” cedo demais
Misturar observabilidade, edição, terminal, automação e administração cedo demais degrada a segurança e a clareza do produto.

#### Risco 5 — acoplamento direto demais ao host real
Se o painel operar direto em cima do filesystem e processos reais sem contenção, qualquer bug tem impacto maior.

---

### 1.7 Oportunidades que o PRD pode explorar melhor

#### Oportunidade 1 — visão executiva multiagente
Transformar a arquitetura real dos agentes em algo inteligível em segundos.

#### Oportunidade 2 — mapa de saúde operacional
Um painel que mostre rápido:
- gateway
- crons
- memória
- canais
- custos
- alertas críticos

#### Oportunidade 3 — padronização operacional
O Mission Control pode virar o painel padrão de diagnóstico e governança do ecossistema.

#### Oportunidade 4 — camada de auditoria
Se bem desenhado, pode registrar leituras críticas, falhas e eventos de risco sem tocar no core do OpenClaw.

---

## 2. Writing Plan

### 2.1 Reenquadramento do PRD

O PRD atual está bom, mas pode ficar mais forte se for reorganizado em torno de uma tese clara:

> Mission Control não é um painel genérico de administração. É uma camada privada de observabilidade operacional para o ecossistema OpenClaw da Flávia, com privilégios mínimos e desenho anti-injeção.

Esse reenquadramento melhora o foco.

---

### 2.2 O que falta explicitar melhor no PRD

#### A. Princípios de produto
Adicionar uma seção curta com princípios como:
- observabilidade antes de ação
- read-only por padrão
- privilégios mínimos
- anti-prompt-injection by design
- arquitetura real antes de UI genérica

#### B. Modelo de dados/fonte da verdade
Explicitar de onde cada tela lê:
- `openclaw.json`
- arquivos de memória aprovados
- crons
- sessões
- métricas do host
- logs permitidos

#### C. Zonas de acesso
Separar o que o painel pode acessar em níveis:
- zona verde: leitura segura
- zona amarela: leitura sensível e controlada
- zona vermelha: proibido na v1

#### D. Rollback
Adicionar um plano explícito de rollback:
- desligar serviço
- remover proxy
- restaurar versão anterior
- zero impacto no OpenClaw principal

#### E. Critérios de segurança verificáveis
Trocar parte do texto genérico por checks objetivos:
- sem terminal web ativo
- sem PUT genérico de arquivos
- sem escrita em arquivos-raiz sensíveis
- sem navegação fora da allowlist
- sem exposição pública aberta

---

### 2.3 Estrutura melhorada sugerida para o PRD

1. Contexto e problema
2. Tese do produto
3. Princípios de design
4. Escopo da v1
5. Fora do escopo
6. Arquitetura e fontes de dados
7. Modelo de segurança
8. Fixes obrigatórios no código-base original
9. Plano de rollout
10. Critérios de aceite
11. Rollback
12. Roadmap v1 → v1.1 → v2

---

### 2.4 Roadmap sugerido

#### V1 — Observabilidade privada
- dashboard host
- agentes
- sessões
- crons
- alertas
- leitura aprovada de memória/docs
- zero terminal
- zero edição ampla

#### V1.1 — Busca e triagem melhores
- busca global segura
- filtros por agente
- alertas com severidade
- custo e uso por agente

#### V2 — Escrita mínima auditada
Só se houver necessidade real:
- comentários operacionais
- ack de alertas
- notas controladas em área específica

---

### 2.5 Decisões recomendadas após a revisão

#### Decisão 1
Classificar formalmente o Mission Control como **produto de observabilidade**, não de administração.

#### Decisão 2
Travar a v1 como **read-only**.

#### Decisão 3
Não usar o repo upstream como deploy direto.

#### Decisão 4
Criar checklist técnico obrigatório antes de qualquer instalação.

#### Decisão 5
Subir primeiro em sandbox com acoplamento reduzido ao ambiente real.

---

## 3. Conclusão da revisão

O PRD está na direção certa.

O principal ajuste é de nitidez:
- menos “dashboard genérico”
- mais “camada privada de observabilidade operacional com privilégios mínimos”

A recomendação final desta revisão é:
1. revisar o PRD com esses reforços
2. gerar checklist técnico de hardening
3. só então começar a adaptação do código
