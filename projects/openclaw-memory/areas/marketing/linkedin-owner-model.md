# Owner Model — LinkedIn Operations

_Data: 2026-04-15_

## Decisão

O agente de **marketing** é o **owner funcional** da frente LinkedIn.

Isso significa que a responsabilidade principal de operação, desenho editorial e governança de publicação fica ancorada em marketing.

## Escopo do owner funcional

O agente de marketing passa a ser responsável por:

- definir o playbook operacional de LinkedIn
- separar pessoal x institucional
- estruturar o fluxo de rascunho, revisão, aprovação e publicação
- definir templates e linha editorial por marca
- organizar calendário e cadência
- manter padrão de voz por marca
- propor regras de aprovação
- cuidar da rotina das páginas MENSURA, MIA e PCS
- estruturar o uso do perfil pessoal do Alê como canal assistido

## O que não fica isolado com marketing

Marketing **não** é owner técnico absoluto da integração.

Permanecem fora do domínio exclusivo de marketing:

- app LinkedIn Developers
- OAuth
- tokens
- callback
- escopos
- segredo e cofre
- publicação via API
- política de segurança
- regras executivas sensíveis

## Distribuição correta de responsabilidade

### Marketing
Owner funcional de:
- conteúdo
- operação editorial
- governança de publicação
- playbook da frente

### Flávia / camada principal
Owner técnico-operacional de:
- integração
- credenciais
- automação
- segurança
- observabilidade
- continuidade do sistema

### Alexandre
Aprovador final de:
- uso do perfil pessoal
- regras sensíveis
- posicionamento reputacional relevante

## Regra prática

Se a pergunta for **"o que publicar, como publicar, para qual marca, com qual tom e em qual fluxo?"**, o owner é marketing.

Se a pergunta for **"como autenticar, publicar pela API, guardar credenciais, configurar callback e manter a integração segura?"**, o owner é Flávia.

## Aplicação imediata

A frente LinkedIn deve ser tratada como uma célula coordenada por marketing, com suporte técnico-operacional da Flávia.

O projeto `projects/openclaw-linkedin/` deve ser usado como base técnica dessa célula.
