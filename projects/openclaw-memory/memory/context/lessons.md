# Lições Aprendidas

> Erros recorrentes, armadilhas e padrões úteis da operação.

_Atualizado em 2026-04-17_

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

### Relatório publicado precisa ser corrigido na fonte, não no artefato gerado (2026-04-17)
Quando um site estático for publicado por build, correções em `dist/` ou no HTML servido localmente não bastam. O ajuste precisa ir no arquivo-fonte versionado, depois `build`, `commit`, `push` e checagem do domínio público.

### Atualização de relatório executivo exige substituir bloco antigo, não empilhar seção nova (2026-04-17)
Se uma deliberação nova substitui a leitura anterior, o correto é remover a seção velha e promover a nova para o lugar dela. Criar uma seção extra com a versão atualizada gera duplicidade, confusão visual e leitura errada do cliente.

### Deliberação validada em ata deve entrar com status final, não como pendência herdada (2026-04-17)
Quando a ata já fecha um item como definido ou concluído, o relatório e as cobranças futuras precisam refletir esse status final. Não carregar automaticamente a redação antiga de urgência ou pendência para a próxima versão.

### Rotina datada precisa ser validada pela data-alvo, não pelo dia corrente (2026-04-17)
Em scripts de cobrança ou alinhamento diário, um `dry-run` no dia atual só prova o bloco daquela data. Para validar mensagens futuras, a rotina precisa aceitar data-alvo explícita ou outro mecanismo equivalente; senão a validação fica enganosa.

### Publicação só conta quando o domínio público reflete a revisão pedida (2026-04-17)
`Build ok` e `push ok` não bastam para declarar entrega publicada. É obrigatório checar o bundle/título/conteúdo no domínio público e separar claramente: repositório atualizado, deploy em propagação e site efetivamente servido.

### Pages direto e domínio roteado podem divergir mesmo com status 200 (2026-04-17)
Quando houver Worker ou roteador na frente de um site estático, validar separadamente o `*.pages.dev` e o domínio customizado. Um `200` no domínio final não prova que o conteúdo certo está sendo servido; o roteador pode estar devolvendo o fallback da SPA principal.

### Categorizar inbox ruim só acelera erro visual (2026-04-18)
Antes de ativar categoria Graph em produção, validar a qualidade da classificação em dry-run. Se a lógica ainda joga newsletter, marketing e aviso automático em `operacional` ou `urgente`, aplicar label na mailbox só institucionaliza ruído.

### Organization API do LinkedIn não falha por bug quando falta aprovação, falha por produto (2026-04-19)
Se os endpoints de organização retornarem `403 ACCESS_DENIED` com token humano válido, isso pode ser bloqueio deliberado da LinkedIn Community Management API e não erro de implementação. Antes de insistir em código, confirmar escopo aprovado e política do produto.

### Token funcional em arquivo de config é incidente, não conveniência (2026-04-19)
Se um access token com poder de postar em nome do Alê estiver salvo em plaintext no workspace, tratar como risco operacional imediato. Funcionar não valida o desenho; nesse caso, o certo é migrar para variável de ambiente/cofre ou endurecer acesso antes de ampliar automação.

## Temporárias

### `openclaw thinking` não existe nesta versão (2026-04-01 | revisar depois de upgrade)
O controle de reasoning disponível está no chat via `/reasoning`, não em comando CLI `openclaw thinking`.

### `reserveTokensFloor` fica em `agents.defaults.compaction` (2026-04-01 | revisar depois de upgrade)
O path correto atual é `agents.defaults.compaction.reserveTokensFloor`.

## Regra de manutenção

- Promover para `decisions.md` o que deixar de ser só lição e virar regra permanente.
- Remover lição temporária quando o ambiente mudar e ela deixar de ser verdade.
- Não registrar aqui detalhe de sessão que só importa uma vez.
