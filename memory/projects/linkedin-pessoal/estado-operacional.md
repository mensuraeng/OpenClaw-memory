# Estado operacional - LinkedIn pessoal do Alexandre

_Atualizado em 2026-04-21 13:55 BRT_

## Objetivo
Operar o LinkedIn pessoal do Alê como ativo de autoridade profissional/B2B, seguindo o plano de marketing aprovado e publicando posts 10/10 sem depender de validação post a post, exceto em casos sensíveis fora do plano.

## Estado operacional atual
- status: **executado e operacional**
- publicação pessoal via API: **validada em produção**
- agendamento automático recorrente: **não comprovado**
- coleta sistemática de performance pós-publicação: **ainda não consolidada**

## Regra de verdade operacional
Sempre distinguir explicitamente entre:
- planejado
- preparado
- executado
- bloqueado

Nunca declarar publicação como concluída quando houver apenas copy pronta ou janela definida.

## Capacidade validada
### Ferramenta: publicação pessoal LinkedIn
- padrão: publicação via API do projeto `/root/.openclaw/workspace/projects/openclaw-linkedin`
- fallback: nova reautorização OAuth quando houver revogação do token
- nível de productização: operacional validado, mas ainda não endurecido para refresh/reuso automático e coleta sistemática de link/performance
- limitações: depende de token OAuth válido; se houver `REVOKED_ACCESS_TOKEN`, precisa nova autorização
- última validação real: 2026-04-21 13:37 BRT
- evidência: `urn:li:share:7452395072463233024`
- URL do post validado: `https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7452395072463233024`

## Autorização operacional vigente
O Alê autorizou publicação sem validação prévia post a post, desde que eu:
- siga o plano de marketing pessoal
- mantenha o eixo de governança de obras como proteção patrimonial e operacional
- preserve tom técnico, elegante, sóbrio e não apelativo
- pare e consulte em caso sensível, ambíguo, reputacionalmente arriscado ou fora do plano

## Horários operacionais aprovados
- terça: 12:00–13:00 BRT, alvo 12:15
- quinta: 08:30–09:30 BRT, alvo 09:05
- reserva: 17:00–18:00 BRT

## Último ciclo executado
- tema: falsa sensação de controle em obra de alto padrão
- formato: texto puro
- status: publicado
- id do post: `urn:li:share:7452395072463233024`
- horário real publicado: 2026-04-21 13:37 BRT

## Bloqueios reais atuais
- não há bloqueio para publicação imediata enquanto o token atual seguir válido
- bloqueio estrutural remanescente: falta refresh/reuso endurecido para reduzir dependência de reautorização manual futura
- bloqueio analítico remanescente: ainda falta rotina consolidada de captura de performance e aprendizado por horário/formato
- bloqueio de qualidade identificado em 2026-04-21: a revisão de renderização do texto no feed ainda não estava formalizada no workflow, o que permitiu publicar um texto com formatação visual ruim

## Regra adicional de qualidade
Antes de cada publicação pessoal no LinkedIn:
- normalizar quebras de linha
- revisar o texto em preview por parágrafos
- evitar blocos excessivamente longos
- tratar renderização como critério de qualidade obrigatório, não cosmético

## Próximo passo correto
1. monitorar sinais iniciais do post publicado
2. registrar link final e primeiros indicadores úteis
3. preparar o post de quinta em estado final
4. endurecer a trilha OAuth para reuso mais robusto
