# Uso do agent-audit-trail no stack do Alê

## Papel
Criar trilha verificável de ações sensíveis do agente em formato append-only com encadeamento por hash.

## Onde usar
- instalação de skills
- alterações de workflows
- mudanças relevantes em automações
- mudanças estruturais no OS operacional
- futuras ações críticas com impacto operacional

## O que ele faz bem
- registra eventos de forma imutável
- permite verificação de integridade
- aumenta auditabilidade do stack

## O que ele não faz
- não decide por você
- não substitui revisão humana
- não bloqueia ação por conta própria

## Fluxo recomendado
1. identificar ação sensível
2. registrar evento importante
3. em auditoria futura, verificar cadeia de integridade

## Regra prática
Se a ação muda comportamento, automação, skill ou governança, vale trilhar.
