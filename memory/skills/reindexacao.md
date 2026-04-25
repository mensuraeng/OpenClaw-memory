# Protocolo de Reindexação do 2nd Brain

_Use quando: trocar de LLM, agente ficar desorientado, memória desatualizada, ou contexto inconsistente_

---

## Quando executar

- Ao trocar modelo (ex: Sonnet → Opus → GPT)
- Quando o agente não reconhece arquivos ou contextos que deveriam existir
- Após longo período sem uso (>7 dias)
- Quando solicitado explicitamente: "reindexe o 2nd Brain"

---

## Protocolo (executar na ordem)

### Passo 1 — Leitura do mapa raiz
```
Leia: memory/README.md
```
Identifique todas as pastas e seus propósitos.

### Passo 2 — Leitura dos mapas de contexto
```
Leia (nesta ordem):
1. memory/context/mapa-agentes.md
2. memory/context/mapa-crons.md
3. memory/context/mapa-maquina-vendas-mensura.md
4. memory/context/business-context.md
5. memory/context/decisions.md
```

### Passo 3 — Verificação de consistência
Para cada mapa, verificar:
- [ ] Os arquivos referenciados existem?
- [ ] Os crons estão no crontab? (`crontab -l`)
- [ ] Os agentes estão no openclaw.json?
- [ ] Os configs existem em `config/`?

### Passo 4 — Diagnóstico
Listar:
- O que está desatualizado
- O que está faltando
- O que está inconsistente

### Passo 5 — Correção e commit
Corrigir os problemas encontrados e commitar:
```bash
git add -A && git commit -m "chore(reindex): atualização pós-reindexação $(date +%Y-%m-%d)"
```

### Passo 6 — Confirmação de 100%
Responder: "Reindexação completa. Estou 100% mapeado. [lista do que foi verificado/corrigido]"

---

## Checklist de 100% mapeado

- [ ] Conheço todos os agentes e seus papéis (`mapa-agentes.md`)
- [ ] Conheço todos os crons e seus horários (`mapa-crons.md`)
- [ ] Conheço a Máquina de Vendas MENSURA completa
- [ ] Conheço o pipeline HubSpot (10 etapas)
- [ ] Sei onde ficam todos os scripts
- [ ] Sei os canais Telegram de cada agente
- [ ] Conheço as obras em andamento (CCSP Casa 7)
- [ ] Conheço o status atual do ecossistema

---

## Nota sobre LLMs

Cada LLM interpreta o contexto de forma diferente. Após trocar de modelo:
1. Execute este protocolo completo
2. Peça ao agente para resumir o que entendeu sobre o ecossistema
3. Corrija qualquer interpretação errada antes de continuar trabalhando
