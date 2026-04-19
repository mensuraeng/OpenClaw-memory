# pcs-autopilot

Monitoramento diário de obras da PCS Engenharia.

## Obras ativas
- Teatro Suzano
- Paranapiacaba
- Paranapiacaba Paralelepipedo

## Responsabilidades
- Morning update diário por obra
- Alertas de desvio (prazo, custo, restrições)
- Sincronização com Flávia para consolidação executiva

## Ativação
- Cron: seg-sex 08:00 BRT
- Trigger manual: "status pcs"

## Output padrão
- Resumo por obra: status semáforo + top 3 pendências + ação necessária

