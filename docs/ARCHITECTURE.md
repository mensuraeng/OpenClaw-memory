# Arquitetura — OpenClaw Memory

## Camadas

### 1. Inbox por agente
Captura rápida, bruta e tolerante a ruído.

### 2. Consolidação noturna
Processa os inboxes do dia, conecta itens relacionados, remove redundâncias e promove o que importa.

### 3. Memória institucional
Conhecimento durável, compartilhado e versionado no GitHub.

## Estrutura inicial

```text
memory/
  inbox/
    YYYY-MM-DD/
      main/
      mensura/
      mia/
      pcs/
      finance/
  consolidation/
    YYYY-MM-DD/
```

## Regras

- inbox não é memória final
- consolidar antes de promover
- decisão, lição e pendência sobem para memória durável
- ruído não sobe
- memória longa precisa continuar legível e reutilizável
