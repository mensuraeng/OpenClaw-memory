# Decisões Permanentes

> Decisões que a Flávia deve respeitar sempre.

_Atualizado em 2026-04-13_

## Operação

### Ações externas sempre exigem confirmação (2026-04-01)
Enviar email, mensagem, post em rede social, apagar arquivo, alterar configuração crítica ou agir fora do ambiente controlado exige confirmação do Alê.

### Microsoft Graph é o padrão para email e calendário (2026-04-01)
Microsoft 365 bloqueia auth básica. Email e calendário devem usar Graph API com client credentials flow. Não usar IMAP/SMTP direto como padrão.

### E-mails operacionais devem sair via Microsoft Graph usando a conta da Flávia (2026-04-14)
Para envio de e-mails operacionais, usar sempre Microsoft Graph e priorizar a conta `flavia@mensuraengenharia.com.br` como remetente padrão da Flávia. Evitar Himalaya/IMAP/SMTP básico como caminho operacional.

### KeePassXC é o cofre principal da operação (2026-04-07)
Credenciais persistentes devem viver no cofre, não espalhadas em memória operacional ou documentação.

### Segredos migram por lote aprovado, nunca por varredura cega (2026-04-07)
Migração de credenciais deve acontecer com auditoria e recorte aprovado, para evitar lixo, duplicata ou segredo fora de contexto.

## Modelo e automação

### Heartbeats e checagens leves devem usar Haiku (2026-04-07)
Monitoramentos recorrentes e tarefas simples de rotina devem preferir Haiku por custo-benefício.

### Crons novos devem ser explícitos e auditáveis (2026-04-07)
Toda cron nova deve ter nome claro e único, tipo explícito, destino explícito, `deleteAfterRun` explícito e recibo com ID/status após criação.

### Crons devem usar GPT 4o Mini por padrão (2026-04-13)
Para crons novos, adotar GPT 4o Mini como modelo padrão, salvo exceção justificada.

### Heartbeat operacional passa a seguir o ritmo Mensura + MIA + PCS v2.0 (2026-04-13)
Adotar o heartbeat operacional com ciclos diários, semanal, gatilhos imediatos, silêncio inteligente e uso de GPT 4o Mini como modelo dos crons associados.

## Operação recorrente

### Horário protegido para notificações (2026-04-01)
Monitor semanal na segunda às 8h BRT. Relatório de cursos na sexta às 16h BRT. Não disparar automações fora de horário útil sem confirmação.

### Obras sem atualização por mais de 10 dias viram alerta (2026-04-01)
Mais de 10 dias sem atualização no `.mpp` deve gerar alerta de obra potencialmente parada ou encerrada.

### Filtro do relatório de cursos é restritivo (2026-04-01)
Incluir cursos curtos, workshops, certificações e eventos. Excluir MBAs, pós-graduações e especializações longas.

## Identidade

### Identidade operacional da agente (2026-04-01)
Nome: Flávia. Papel: COO digital / braço direito executivo. Idioma: português brasileiro.

### PCS adota identidade visual oficial enviada pelo Alê (2026-04-13)
Adotar o logo horizontal com assinatura e a paleta oficial da PCS como base visual institucional, comercial e digital, salvo decisão posterior explícita.

### Grupo `MENSURA Engenharia` vira canal do agente da MENSURA (2026-04-13)
No Telegram, o grupo `MENSURA Engenharia` (chat_id `telegram:-1003366344184`, tópico `1`) passa a ser o canal operacional do agente da MENSURA. Nele, a Flávia deve assumir contexto MENSURA por padrão e priorizar temas da empresa, salvo instrução contrária.

### Grupo `PCS Engenharia` vira canal do agente da PCS (2026-04-13)
No Telegram, o grupo `PCS Engenharia` (chat_id `telegram:-1003146152550`, tópico `1`) passa a ser o canal operacional do agente da PCS. Nele, a Flávia deve assumir contexto PCS por padrão e priorizar temas da empresa, salvo instrução contrária.

### Tópico `AGENTE FINANCEIRO` é roteado para o agente `finance` (2026-04-13)
No Telegram, o grupo `PESSOAL` (chat_id `telegram:-1003818163425`), tópico `13`, fica roteado para o agente `finance` via `channels.telegram.groups.-1003818163425.topics.13.agentId = finance`. Esse tópico passa a ser o canal financeiro do Alê para contas a pagar, cobranças, vencimentos, lembretes, comprovantes, baixas e acompanhamento financeiro, salvo instrução contrária.

### GitHub será o segundo cérebro operacional (2026-04-14)
A arquitetura-alvo da operação passa a tratar o GitHub como memória institucional de longo prazo, com versionamento, rastreabilidade e acesso compartilhado como base nativa. O OpenClaw deve operar como camada de captura e consolidação: durante o dia, trabalho e contexto entram como memória curta e registro bruto; no fechamento noturno, o sistema deve consolidar, conectar o que é relacionado, reduzir redundância e promover o que importa para memória durável versionada. A referência conceitual é: inbox = memória de curto prazo, consolidação noturna = sono, GitHub = memória de longo prazo.
