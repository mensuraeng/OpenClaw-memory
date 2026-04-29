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

## Credenciais Sienge
- Protocolo: `/root/.openclaw/workspace/docs/operacao/KEESPACE-SECRETS-PROTOCOL.md`
- Mapa: `/root/.openclaw/workspace/memory/integrations/credentials-map.md`
- Fallback local atual: `/root/.secrets/sienge-pcs.env`
- Configs técnicas: `/root/.openclaw/workspace/config/sienge-pcs-public.json` e `/root/.openclaw/workspace/config/sienge-pcs.json`
- Entrada KeeSpace/KeePassXC sugerida: `OpenClaw/PCS/Sienge/api-basic`

Nunca imprimir senha/token em chat, log público, memória ou commit.

## Ativação
- Cron: seg-sex 08:00 BRT
- Trigger manual: "status pcs"

## Output padrão
- Resumo por obra: status semáforo + top 3 pendências + ação necessária

