# Feedback Loop Operacional

## Objetivo
Registrar aprovações e rejeições para evitar repetir sugestão ruim e reforçar padrão que já funcionou.

## Arquivos
- `content.json` → feedback sobre conteúdo, tom e formato
- `recommendations.json` → feedback sobre sugestões, ferramentas e abordagens
- `tasks.json` → feedback sobre execução, cadência e forma de operar

## Regra
1. Se o usuário aprovar ou rejeitar explicitamente uma sugestão, registrar.
2. Antes de sugerir novamente algo parecido, consultar primeiro o domínio relevante.
3. Se houver rejeição parecida, adaptar a sugestão ou dizer claramente que já foi rejeitada antes e por quê.

## CLI local
### Registrar reject
```bash
python3 scripts/feedback_memory.py add \
  --domain recommendations \
  --decision reject \
  --context "Sugeri usar skill X para tarefa Y" \
  --reason "Sem proveniência confiável" \
  --tags skills,proveniencia
```

### Consultar histórico
```bash
python3 scripts/feedback_memory.py query "skills proveniencia"
```

## Como isso aparece na prática
- Histórico diz: rejeitado porque a skill não é confiável.
- Nova sugestão parecida surge.
- A resposta correta deixa de ser "usa essa skill" e passa a ser algo como: "não vou te empurrar essa skill de novo, porque você já rejeitou esse caminho por falta de confiabilidade; melhor fazer manualmente ou usar ferramenta com proveniência clara."
