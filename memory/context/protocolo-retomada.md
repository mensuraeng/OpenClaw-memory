# Protocolo de retomada operacional

_Atualizado em 2026-04-21 14:16 BRT_

## Objetivo
Padronizar a retomada de qualquer frente crítica para reduzir perda de contexto, resposta com memória velha e confusão entre preparação e execução.

## Etapas obrigatórias
1. identificar a frente correta
2. localizar o arquivo canônico da frente
3. ler o estado operacional atual
4. classificar a frente em um único estado:
   - planejado
   - preparado
   - executado
   - bloqueado com causa real
5. confirmar:
   - padrão atual
   - fallback
   - nível de productização
6. validar a última evidência real
7. checar bloqueio real atual, se existir
8. identificar o próximo passo correto
9. só então responder, agir ou escalar

## Regra de verdade operacional
- nunca chamar de executado aquilo que está apenas preparado
- nunca tratar memória histórica como prova operacional atual
- nunca responder integração como viva sem evidência real recente

## Regra de promoção de memória
Toda capacidade validada ou corrigida no ciclo atual deve subir para memória durável no mesmo ciclo.

## Arquivos canônicos atuais prioritários
- `memory/projects/linkedin-pessoal/estado-operacional.md`
- `memory/projects/pcs/estado-operacional.md`
- `memory/projects/audio-inbound/estado-operacional.md`
- `memory/integrations/antigravity-mcp-estado-operacional.md`
- `memory/integrations/scheduler-autonomias-criticas-estado-operacional.md`
- `memory/integrations/xp-estado-operacional.md`
- `memory/context/autonomia-operacional.md`
