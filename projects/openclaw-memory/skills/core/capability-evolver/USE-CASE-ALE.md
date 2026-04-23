# Capability Evolver - Adaptação para operação do Alê

## Objetivo real
Usar o Evolver como motor de melhoria guiada para:
- refinar skills próprias como `control-tower-cronograma` e `relatorio-preditivo-obras`
- registrar padrões de erro recorrentes
- gerar propostas de melhoria auditáveis antes de qualquer mudança crítica

## Regra operacional
- Modo padrão: `--review`
- Estratégia padrão: `harden`
- Sem worker pool
- Sem auto-issue no GitHub
- Sem self-modify
- Sem integração obrigatória com EvoMap Hub

## Aplicações por negócio

### MENSURA
- melhorar prompts e rotinas de leitura de cronogramas
- capturar falhas recorrentes em análise de desvios, riscos e consistência de avanço
- transformar correções recorrentes em ativos reutilizáveis

### MIA
- melhorar geração de relatórios executivos e materiais técnicos para cliente premium
- reduzir respostas genéricas e aumentar padrão de clareza, defesa técnica e objetividade

### PCS
- adaptar rotinas operacionais, diagnóstico e governança conforme os fluxos reais da empresa
- consolidar aprendizados por tipo de projeto e por erro recorrente

## Guardrails recomendados
- rodar apenas sob revisão humana
- não permitir autoedição do próprio evolver
- não publicar nada para rede externa sem decisão explícita
- usar rollback conservador (`stash`)
- alimentar memória com logs operacionais úteis, não ruído bruto

## Resultado esperado
Não é "auto-magia". É uma camada de melhoria contínua auditável para reduzir retrabalho e acelerar refinamento das skills internas.
