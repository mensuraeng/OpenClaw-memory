# Lições Aprendidas

> Erros recorrentes, armadilhas e padrões úteis da operação.

_Atualizado em 2026-04-13_

## Permanentes

### Microsoft 365 não aceita auth básica (2026-04-01)
Clientes IMAP/SMTP tradicionais falham para essas contas. O padrão é Microsoft Graph API com client credentials.

### Script de monitor deve ser testado antes de ir para cron (2026-04-01)
Rodar manualmente antes evita agendar saída quebrada, formato ruim ou dado errado.

### Configuração do OpenClaw deve ser agrupada antes de restart (2026-04-01)
Mudanças de config aplicam após restart. Melhor consolidar alterações e reiniciar uma vez.

### Auditoria de cron não pode olhar só o estado atual (2026-04-07)
Jobs one-shot com `deleteAfterRun: true` somem depois de executar. Conferir `jobs.json`, backup e histórico de runs antes de concluir que não existiram.

### Segredo não pertence à memória operacional (2026-04-07)
Se um segredo parar em `memory/`, isso deve ser tratado como contenção temporária. O destino correto é o cofre.

### Migração de credenciais deve ser controlada (2026-04-07)
Varredura cega arrasta lixo, duplicata e contexto errado. Auditar primeiro, migrar depois.

### Script multi-conta não pode fixar usuário padrão no código (2026-04-13)
Quando a conta muda, o script deve puxar `defaultUser` da config ou exigir `--user`. Hardcode silencioso gera falso negativo e mascara integração saudável.

### Fallback silencioso em automação operacional é erro de desenho (2026-04-13)
Se faltar parâmetro essencial, o script deve falhar com mensagem clara. Cair para valor padrão genérico mascara problema de configuração e atrasa diagnóstico.

### Cron consolidado exige validação de pacote completo (2026-04-14)
Ao fundir ou simplificar cron, não basta ajustar horário ou texto da instrução. Validar sempre em conjunto: `schedule`, `payload.message`, `payload.model` e `toolsAllow`. Se uma dessas partes ficar para trás, o job pode parecer certo e continuar operacionalmente incompleto.

### Correção explícita do Alê deve virar prevenção reutilizável (2026-04-14)
Quando o Alê corrigir um padrão de execução, transformar a correção em regra operacional curta e reaproveitável. O objetivo não é registrar bronca de sessão, e sim evitar reincidência em tarefas futuras semelhantes.

### Ordem declarada exige execução real ou bloqueio explícito (2026-04-15)
Se eu disser que vou seguir uma ordem de execução, preciso começar de fato por ela e marcar progresso até concluir ou declarar bloqueio. Não devo usar promessa de sequência como resposta vazia.

### Planejamento demais vira burocracia; de menos vira improviso (2026-04-15)
No nosso processo, plano explícito vale para tarefa não trivial, ambígua, arriscada ou multi-etapas. Tornar plano obrigatório para tudo gera atrito desnecessário; pular plano em trabalho complexo aumenta erro e retrabalho.

### Elegância sem utilidade é sofisticação precoce (2026-04-15)
Buscar solução limpa é bom, mas não pode virar desculpa para over-engineering. Primeiro consolidar o essencial que ajuda decisão ou operação, depois refinar.

### Workspaces separados exigem política explícita de skills (2026-04-16)
Quando cada agente roda em workspace próprio, não dá para assumir que toda skill do workspace principal estará operacionalmente disponível e homogênea para todos. O desenho precisa separar biblioteca transversal compartilhada de skill específica por domínio para evitar duplicação burra e ambiguidade de manutenção.

### Delegação para agente especializado só vale depois de teste real (2026-04-16)
Não basta o desenho existir no papel. Se `main` disser que vai coordenar e delegar para marketing, jurídico ou outro agente, isso precisa estar validado com spawn real e política efetiva. Arquitetura sem prova operacional ainda é premissa.

### Allowlist ou memória antiga não provam topologia atual (2026-04-16)
Quando houver dúvida sobre quais agentes realmente existem e operam no desenho atual, conferir o config/runtime vigente antes de afirmar estrutura. IDs históricos em allowlist e memória de sessões anteriores podem sobreviver à mudança e induzir diagnóstico errado.

### Segundo cérebro só funciona se inbox e consolidação forem separados (2026-04-14)
Se o mesmo espaço tentar ser captura bruta e memória final ao mesmo tempo, o sistema vira acúmulo desorganizado. A arquitetura precisa separar claramente o que entra rápido durante o dia do que é consolidado à noite como memória institucional de longo prazo.

## Temporárias

### `openclaw thinking` não existe nesta versão (2026-04-01 | revisar depois de upgrade)
O controle de reasoning disponível está no chat via `/reasoning`, não em comando CLI `openclaw thinking`.

### `reserveTokensFloor` fica em `agents.defaults.compaction` (2026-04-01 | revisar depois de upgrade)
O path correto atual é `agents.defaults.compaction.reserveTokensFloor`.

## Regra de manutenção

- Promover para `decisions.md` o que deixar de ser só lição e virar regra permanente.
- Remover lição temporária quando o ambiente mudar e ela deixar de ser verdade.
- Não registrar aqui detalhe de sessão que só importa uma vez.
