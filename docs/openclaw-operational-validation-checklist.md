# Checklist Padrão de Validação Operacional

_Data: 2026-04-20_
_Status: padrão inicial_

## Objetivo

Padronizar como uma capacidade do OpenClaw sai de “parece boa” para “está realmente validada”.

Esse checklist serve para integrações, agentes, skills, canais, crons, dashboards e fluxos operacionais.

---

## Escala de maturidade

- **desenhada**: existe no papel
- **testada**: houve teste pontual controlado
- **validada em runtime**: executou caso real recente
- **robusta**: repetiu bem, com limites conhecidos
- **produção**: pronta para uso recorrente sob risco controlado

---

## Template de validação

### 1. Identificação
- nome da capacidade:
- dono principal:
- superfícies/canais envolvidos:
- dependências críticas:
- data da validação:

### 2. Caso real executado
- qual cenário real foi usado?
- era caso interno, externo, demo ou produção?
- qual era o objetivo operacional?

### 3. Evidência
- qual output foi produzido?
- onde está a evidência? (arquivo, log, mensagem, artefato)
- o resultado foi completo, parcial ou inconclusivo?

### 4. Limites conhecidos
- o que essa capacidade faz bem?
- onde ela falha?
- o que ainda depende de humano, credencial, aprovação ou contexto especial?

### 5. Risco operacional
- risco de segurança
- risco de reputação
- risco de dado incorreto
- risco de automação excessiva
- risco de dependência externa

### 6. Guardrails
- o que exige confirmação do Alê?
- o que está bloqueado por default?
- quais superfícies não devem usar essa capacidade?

### 7. Fallback / rollback
- se falhar, qual o fallback?
- se piorar o ambiente, como reverter?
- existe modo degradado aceitável?

### 8. Próximo status possível
- o que falta para sair de `desenhada` para `testada`?
- o que falta para virar `validada em runtime`?
- o que falta para virar `robusta`?
- o que falta para virar `produção`?

---

## Critérios mínimos por status

### Para marcar como `testada`
- houve execução controlada
- existe evidência mínima
- o comportamento básico foi observado

### Para marcar como `validada em runtime`
- houve caso real recente
- o output foi útil de verdade
- a dependência principal funcionou no ambiente real
- a limitação principal ficou explícita

### Para marcar como `robusta`
- repetiu bem mais de uma vez
- limites conhecidos foram documentados
- fallback existe
- risco está proporcionalmente controlado

### Para marcar como `produção`
- uso recorrente aceitável
- guardrails definidos
- risco operacional claro
- rollback/fallback conhecido
- evidência recente de estabilidade

---

## Sinais de alerta

Não promover status quando:
- só existe desenho bonito
- o teste foi artificial demais
- faltou evidência
- depende de credencial ausente
- depende de aprovação de terceiro ainda não obtida
- falhou e o fallback não está claro
- o ambiente mudou desde a última prova

---

## Exemplo curto

### Capacidade
Skill audit OpenClaw

### Status atual
Testada

### Evidência
- spec criada
- script funcional criado
- rodada real em 53 skills do OpenClaw

### Limites conhecidos
- falso positivo ainda alto em `examples_thin`, `scope_ambiguity`, `hidden_dependencies`

### Próximo passo
- segunda calibração
- nova rodada
- decisão sobre adoção oficial

---

## Regra final

Arquitetura sem prova é hipótese.
Capacidade sem evidência recente não deve ser tratada como madura.
