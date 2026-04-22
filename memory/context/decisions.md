# Decisões Permanentes

> Decisões que a Flávia deve respeitar sempre.

_Atualizado em 2026-04-13_

## Operação

### Princípio de padrão 10/10 para tudo que importa (2026-04-18)
_Status: [ATIVA]_
Como princípio permanente, tudo que a Flávia estruturar, operar, entregar, automatizar ou institucionalizar deve buscar patamar 10/10. Não aceitar solução morna, meia-boca ou "boa o bastante" como padrão final. Quando algo estiver abaixo disso, tratar como estágio transitório com plano explícito para elevar o nível.

### Frentes internas da Flávia entram em loop contínuo até 10/10 (2026-04-19)
_Status: [ATIVA]_
Tudo que for claramente de responsabilidade interna da Flávia, sem depender de decisão do Alê nem de terceiro, deve rodar em ciclo contínuo até atingir 10/10 operacional.

Condição de parada:
- chegou em 10/10 com prova proporcional
- ou surgiu bloqueio grave que exige opinião, decisão ou autorização do Alê

Regra de comunicação:
- não interromper o Alê com microstatus
- só escalar quando houver bloqueio grave, risco real, decisão necessária ou entrega material concluída

### Ações externas sempre exigem confirmação (2026-04-01)
_Status: [ATIVA]_
Enviar email, mensagem, post em rede social, apagar arquivo, alterar configuração crítica ou agir fora do ambiente controlado exige confirmação do Alê.

### Microsoft Graph é o padrão para email e calendário (2026-04-01)
_Status: [ATIVA]_
Microsoft 365 bloqueia auth básica. Email e calendário devem usar Graph API com client credentials flow. Não usar IMAP/SMTP direto como padrão.

### E-mails operacionais devem sair via Microsoft Graph usando a conta da Flávia (2026-04-14, reforçado em 2026-04-18)
_Status: [ATIVA]_
Para envio de e-mails operacionais, usar sempre Microsoft Graph e priorizar a conta `flavia@mensuraengenharia.com.br` como remetente padrão da Flávia. Evitar Himalaya/IMAP/SMTP básico como caminho operacional.

Regra reforçada em 18/04/2026: envio de e-mail externo deve ser sempre pelo remetente da Flávia por padrão. Se o Alê quiser que o envio saia do e-mail dele, isso precisa ser solicitado explicitamente no próprio pedido.

### KeePassXC é o cofre principal da operação (2026-04-07)
_Status: [ATIVA]_
Credenciais persistentes devem viver no cofre, não espalhadas em memória operacional ou documentação.

### Segredos migram por lote aprovado, nunca por varredura cega (2026-04-07)
_Status: [ATIVA]_
Migração de credenciais deve acontecer com auditoria e recorte aprovado, para evitar lixo, duplicata ou segredo fora de contexto.

## Modelo e automação

### Heartbeats e checagens leves devem usar Haiku (2026-04-07)
_Status: [ATIVA] - ATIVA - complementada por decisao de crons GPT4o_
Monitoramentos recorrentes e tarefas simples de rotina devem preferir Haiku por custo-benefício.

### Crons novos devem ser explícitos e auditáveis (2026-04-07)
_Status: [ATIVA]_
Toda cron nova deve ter nome claro e único, tipo explícito, destino explícito, `deleteAfterRun` explícito e recibo com ID/status após criação.

### Crons devem usar GPT 4o Mini por padrão (2026-04-13)
_Status: [ATIVA]_
Para crons novos, adotar GPT 4o Mini como modelo padrão, salvo exceção justificada.

### Heartbeat operacional passa a seguir o ritmo Mensura + MIA + PCS v2.0 (2026-04-13)
_Status: [ATIVA]_
Adotar o heartbeat operacional com ciclos diários, semanal, gatilhos imediatos, silêncio inteligente e uso de GPT 4o Mini como modelo dos crons associados.

### Protocolo de execução da Flávia adota planejamento condicional, validação forte e correção autônoma (2026-04-15)
_Status: [ATIVA]_
A Flávia deve usar plano curto com etapas verificáveis em tarefas não triviais, usar subagentes com foco e follow-up explícito quando houver ganho real, validar proporcionalmente antes de declarar conclusão, e atacar bugs internos a partir de logs, erro observável, causa raiz e prova de correção. Elegância é desejável, mas sem criar burocracia ou sofisticação precoce.

### LinkedIn pessoal e institucional seguem trilhas separadas (2026-04-15, reforçado em 2026-04-19)
_Status: [ATIVA]_
O app `OpenClaw - Mensura` permanece para OAuth/OIDC e publicação pessoal assistida. O fluxo institucional de páginas deve seguir no app `OpenClaw - Community API`, aguardando aprovação e novo OAuth/token antes de qualquer reteste.

Regra reforçada em 19/04/2026: o status oficial passa a ser
- publicação pessoal: operacional e validada em runtime
- páginas institucionais: bloqueadas por aprovação da Community Management API, sem workaround técnico aceitável no estado atual

### Skills do ecossistema seguem modelo híbrido com critério de desempate explícito (2026-04-18)
_Status: [ATIVA]_
Regra operacional:
1. Se a skill funciona em qualquer agente sem mudar uma linha, vai para `shared/`.
2. Se a skill carrega voz, processo ou ativo de negócio de um agente específico, vai para `agents/[nome]/skills/`.
3. Se empatar, vai para `agents/`.
4. Promoção para `shared/` exige uso confirmado por 2 ou mais agentes.
Canal externo sozinho não é critério. O critério é domínio codificado. Ex.: `whatsapp-sender` em `shared/`; `mensura-whatsapp-cobranca` em `agents/mensura/`.
Essa regra existe para evitar skill útil enterrada, skill específica poluindo o core e duplicação de lógica.

### Redirect oficial do LinkedIn do Mission Control é o domínio público do cockpit (2026-04-19)
_Status: [ATIVA]_
O redirect URL autorizado para OAuth do LinkedIn no fluxo do Mission Control deve usar `https://mc.mensuraengenharia.com.br/api/linkedin/callback`. Esse domínio público vira referência oficial do callback e deve ser mantido alinhado no app configurado para o fluxo correspondente.

### PCS usa basic auth como trilha operacional real do Sienge até prova contrária (2026-04-19)
_Status: [ATIVA]_
Para a integração PCS ↔ Sienge atualmente validada em runtime, a trilha oficial é `basic auth` contra `https://api.sienge.com.br/pcsservices/public/api/v1`. Não assumir OAuth2 para a PCS sem nova prova operacional específica do tenant.

### Integração Python PCS ↔ Sienge deve respeitar authType real do tenant (2026-04-19)
_Status: [ATIVA]_
O cliente Python da PCS deve bifurcar o fluxo de autenticação conforme `authType` configurado. Para `basic`, usar credencial básica diretamente nas chamadas da API; para tenants OAuth, manter `client_credentials`. Não impor um único fluxo a tenants com topologias diferentes.

### Mission Control deve subir via processo único controlado pelo PM2, com restart delay explícito (2026-04-19)
_Status: [ATIVA]_
A operação do Mission Control deve evitar processo órfão e restart storm. Subir o app via configuração explícita do PM2, com `next start` direto e `restart_delay` suficiente para liberar porta antes de nova tentativa. Após ajuste estável, persistir com `pm2 save`.

### Inbox PCS adota triagem leve com janela objetiva de urgência (2026-04-18)
_Status: [ATIVA]_
A inbox da PCS opera em Opção 1: triagem leve, com classificação interna entre `urgente`, `operacional` e `ruído`, sem ação externa automática.
Urgente: cliente, contrato, licitação, jurídico, cobrança, fornecedor crítico, problema financeiro relevante, órgão público (prefeitura, TCE, TCU, CONDEPHAAT, IPHAN) e prazo de 5 dias ou menos.
Ruído: newsletter, propaganda, cold email, aviso automático sem ação, conteúdo institucional sem prazo nem decisão.
Operacional: tudo entre os dois, incluindo orçamento em andamento, follow-up comercial, edital sem prazo imediato e fornecedor não crítico.
Prazo genérico não entra como urgente por padrão; o corte é janela objetiva de até 5 dias para evitar falso urgente recorrente.

### Main pode delegar por subagent aos agentes especializados com política explícita (2026-04-16)
_Status: [ATIVA]_
O agente `main` deve poder delegar a agentes especializados por subagent com `allowAgents` explícito, `requireAgentId=true`, limites de spawn controlados e validação real de runtime. Delegação declarada sem capacidade prática validada não conta como arquitetura funcionando.

### Topologia de agentes deve ser validada no config/runtime atual antes de qualquer resposta estrutural (2026-04-16)
_Status: [ATIVA]_
Antes de responder sobre delegação, organograma, parque de agentes ou capacidade operacional, validar primeiro o estado real no config/runtime atual. Allowlist histórica, memória antiga ou IDs legados não valem como prova de topologia vigente.

## Operação recorrente

### Horário protegido para notificações (2026-04-01)
_Status: [ATIVA]_
Monitor semanal na segunda às 8h BRT. Relatório de cursos na sexta às 16h BRT. Não disparar automações fora de horário útil sem confirmação.

### Obras sem atualização por mais de 10 dias viram alerta (2026-04-01)
_Status: [ATIVA]_
Mais de 10 dias sem atualização no `.mpp` deve gerar alerta de obra potencialmente parada ou encerrada.

### Filtro do relatório de cursos é restritivo (2026-04-01)
_Status: [ATIVA]_
Incluir cursos curtos, workshops, certificações e eventos. Excluir MBAs, pós-graduações e especializações longas.

## Identidade

### Identidade operacional da agente (2026-04-01)
_Status: [ATIVA]_
Nome: Flávia. Papel: COO digital / braço direito executivo. Idioma: português brasileiro.

### PCS adota identidade visual oficial enviada pelo Alê (2026-04-13)
_Status: [ATIVA]_
Adotar o logo horizontal com assinatura e a paleta oficial da PCS como base visual institucional, comercial e digital, salvo decisão posterior explícita.

### Grupo `MENSURA Engenharia` vira canal do agente da MENSURA (2026-04-13)
_Status: [ATIVA]_
No Telegram, o grupo `MENSURA Engenharia` (chat_id `telegram:-1003366344184`, tópico `1`) passa a ser o canal operacional do agente da MENSURA. Nele, a Flávia deve assumir contexto MENSURA por padrão e priorizar temas da empresa, salvo instrução contrária.

### Grupo `PCS Engenharia` vira canal do agente da PCS (2026-04-13)
_Status: [ATIVA]_
No Telegram, o grupo `PCS Engenharia` (chat_id `telegram:-1003146152550`, tópico `1`) passa a ser o canal operacional do agente da PCS. Nele, a Flávia deve assumir contexto PCS por padrão e priorizar temas da empresa, salvo instrução contrária.

### Tópico `AGENTE FINANCEIRO` é roteado para o agente `finance` (2026-04-13)
_Status: [ATIVA]_
No Telegram, o grupo `PESSOAL` (chat_id `telegram:-1003818163425`), tópico `13`, fica roteado para o agente `finance` via `channels.telegram.groups.-1003818163425.topics.13.agentId = finance`. Esse tópico passa a ser o canal financeiro do Alê para contas a pagar, cobranças, vencimentos, lembretes, comprovantes, baixas e acompanhamento financeiro, salvo instrução contrária.

### GitHub será o segundo cérebro operacional (2026-04-14)
_Status: [ATIVA]_
A arquitetura-alvo da operação passa a tratar o GitHub como memória institucional de longo prazo, com versionamento, rastreabilidade e acesso compartilhado como base nativa. O OpenClaw deve operar como camada de captura e consolidação: durante o dia, trabalho e contexto entram como memória curta e registro bruto; no fechamento noturno, o sistema deve consolidar, conectar o que é relacionado, reduzir redundância e promover o que importa para memória durável versionada. A referência conceitual é: inbox = memória de curto prazo, consolidação noturna = sono, GitHub = memória de longo prazo.

### Memória documental deve ser separada por empresa e pela frente pessoal do Alê (2026-04-20)
_Status: [ATIVA]_
A memória institucional de documentos importantes passa a ter trilhas separadas para `MENSURA`, `MIA`, `PCS` e `pessoal do Alê`, dentro de `memory/projects/`. Sempre que entrar documento importante, como apresentação, cartão CNPJ, ficha cadastral ou equivalente, ele deve ser alocado na memória da entidade correspondente com índice do arquivo-fonte e resumo reutilizável para consulta futura.

## 2026-04-17 — Finance tag [[reply_to_current]]
O agente finance retorna respostas prefixadas com [[reply_to_current]].
É tag interna do OpenClaw — não afeta conteúdo.
A Flávia deve ignorar/filtrar essa tag ao processar output do finance.
Monitorar se persiste nas próximas execuções reais.

## 2026-04-17 — Relatório semanal P&G Louveira
Template React parametrizado via relatorio.json.
Fluxo: Flávia recebe cronograma + ata → MENSURA extrai
indicadores → preenche JSON → gerar_relatorio.py builda
e sobe para GitHub. GitHub Pages publica automaticamente.
Primeira execução real: semana 003 (semana de 20/04/2026).
Automação futura: integração Notion + MS Project.

## 2026-04-17 — Migração GitHub Pages → Cloudflare Pages (P&G Louveira)
Deploy ativo: https://relatorios.mensuraengenharia.com.br/
Fallback: https://p-g---louveira.pages.dev/
GitHub Actions desativada (deploy.yml.disabled).
Próximo: replicar para MIA CCSP Casa 7 em relatorios.miaengenharia.com.br

## 2026-04-22 — Roteamento MIA CCSP Casa 7 consolidado
Worker `mia-relatorios-router` corrigido para chamar URLs extensionless no
Pages (evita 308 canonical que antes vazava pro cliente e stripava o prefixo
`/ccsp-casa-7/`). Rotas públicas funcionando:

- https://relatorios.miaengenharia.com.br/ccsp-casa-7/relatoriosemanal → Rev003
- https://relatorios.miaengenharia.com.br/ccsp-casa-7/checklist

Padrão adotado: páginas estáticas extras do Casa 7 entram em
`Mia-CCSP-Casa-7/public/<slug>.html`, Cloudflare Pages faz build, e o Worker
tem uma linha para cada slug apontando pra URL extensionless no pages.dev.

## 2026-04-22 — Convenção de título e preview dos relatórios (MIA)
Todo relatório publicado sob `relatorios.miaengenharia.com.br/<obra>/<slug>`
deve ter o `<title>` no padrão `<Projeto> - <Tipo> DD/MM/AAAA` e metadata
Open Graph + Twitter Card para previews legíveis ao encaminhar.

- CCSP Casa 7 semanal → `CCSP Casa 7 - Relatório semanal DD/MM/AAAA`
- A data é a **data da revisão/atualização** do relatório (cabeçalho
  Rev.NNN · DD/MM/AAAA), **não** a data do push no Cloudflare.

Guia operacional completo com template HTML, checklist de publicação e
anti-checklist: `knowledge/Mia-CCSP-Casa-7/PUBLICATION.md`.

Motivo: ao encaminhar o link no WhatsApp/Telegram/LinkedIn/e-mail, o
preview puxa `<title>`/`og:title`, e o título-arquivo `CCSP_Casa7_Relatorio_
TOOLS_RevNNN` ficava ilegível. Mudança pedida pelo Alê em 2026-04-22.
