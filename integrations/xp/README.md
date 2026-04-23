# Integração XP - MIA

_Atualizado em 2026-04-20_

## Objetivo
Implementar integração inicial da conta XP da MIA em modo seguro, começando por leitura e evoluindo para operação assistida com aprovação humana.

## Princípio
Nenhum pagamento automático silencioso.
Toda evolução operacional deve passar por:
1. leitura confiável
2. proposta estruturada
3. aprovação explícita
4. execução
5. comprovante e baixa

## Fase 1 - Descoberta técnica
Validar no portal da XP:
- se a conta/organização da MIA tem acesso ao ecossistema developer
- quais APIs estão realmente disponíveis para esse perfil
- quais scopes existem: conta, saldo, extrato, movimentação, Pix, pagamentos, comprovantes
- modelo de autenticação e credenciais
- necessidade de whitelisting, app registration ou parceria formal

## Fase 2 - Leitura
Meta mínima:
- saldo
- extrato
- transações
- confirmação de pagamentos
- conciliação com controle financeiro local

## Fase 3 - Operação assistida
Meta desejada, somente se suportado pela XP:
- preparar pagamento
- pedir aprovação ao Alê
- executar pagamento após aprovação
- registrar comprovante
- atualizar controle local

## Estrutura sugerida
- `xp-discovery.md` -> o que a XP realmente suporta
- `xp-integration-plan.md` -> arquitetura, escopo e rollout
- `xp-checklist.md` -> checklist operacional de implantação
- `xp-secrets-template.md` -> campos necessários sem guardar segredos em claro

## Regra de segurança
Segredos ficam em KeePassXC ou mecanismo seguro equivalente.
Nunca registrar token, client secret, senha ou certificado em memória textual.
