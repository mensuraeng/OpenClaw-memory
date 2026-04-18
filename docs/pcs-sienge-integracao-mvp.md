# PCS ↔ Sienge — Arquitetura Funcional e MVP de Implantação

_Atualizado em 2026-04-18_

## Objetivo

Implantar uma integração operacional entre a PCS Engenharia e o ERP Sienge, cobrindo o núcleo mínimo necessário para suprimentos e financeiro com base técnica limpa, auditável e expansível.

## Escopo inicial aprovado

### Suprimentos
- cadastro de insumos
- solicitação de compra
- cotação
- pedido de compra

### Financeiro
- contas a pagar
- contas a receber

### Cadastros de base
- credores / fornecedores
- centros de custo
- obras / projetos

## Princípios da integração

1. Não copiar repositórios externos como base final.
2. Reaproveitar apenas padrões úteis de arquitetura e consumo da API.
3. Separar claramente:
   - autenticação
   - coleta
   - normalização
   - persistência
   - orquestração
4. Cada fluxo deve ser idempotente.
5. Logs e rastreabilidade são obrigatórios.
6. O MVP deve validar operação real com dados reais, não apenas conectividade.

## Leitura funcional

A integração deve nascer em três camadas.

### Camada 1 — Cadastro mestre
Responsável por manter entidades-base consistentes.

Entidades prioritárias:
- fornecedores / credores
- insumos
- centros de custo
- obras / projetos

Sem essa camada, suprimentos e financeiro nascem acoplados e frágeis.

### Camada 2 — Suprimentos
Fluxos prioritários:
- criar e consultar solicitações de compra
- consultar cotações
- autorizar negociações de cotação quando aplicável
- consultar e evoluir pedidos de compra

### Camada 3 — Financeiro
Fluxos prioritários:
- consultar contas a pagar
- consultar contas a receber
- posteriormente criar ou atualizar títulos quando o desenho operacional estiver estável

## Sistema mestre por entidade

### Fornecedores / credores
- mestre inicial: Sienge
- integração inicial: leitura para a camada PCS
- escrita futura: somente após governança de duplicidade e validação cadastral

### Insumos
- mestre inicial: definir com a operação PCS
- recomendação atual: Sienge como mestre operacional quando o cadastro oficial já existir lá
- se a PCS tiver cadastro paralelo, criar staging e rotina de conciliação antes de escrita

### Centros de custo
- mestre: Sienge

### Obras / projetos
- mestre: Sienge

### Solicitações de compra
- mestre operacional: Sienge
- origem de disparo pode ser sistema externo, mas o registro oficial precisa existir no Sienge

### Cotações
- mestre operacional: Sienge

### Pedidos de compra
- mestre operacional: Sienge

### Contas a pagar / receber
- mestre operacional: Sienge

## Fluxos do MVP

## MVP Fase 1 — Base confiável
Objetivo: criar visão consistente da operação.

1. autenticação validada
2. leitura de fornecedores / credores
3. leitura de centros de custo
4. leitura de obras / projetos
5. leitura de contas a pagar
6. leitura de contas a receber
7. leitura bulk de cotações

Saída esperada:
- base local normalizada
- logs estruturados
- checkpoints de sincronização
- primeira validação operacional com dados reais PCS

## MVP Fase 2 — Suprimentos operacional
Objetivo: integrar a frente de compras.

1. leitura de solicitações de compra
2. criação controlada de solicitações de compra
3. leitura de pedidos de compra
4. leitura das negociações e cotações que originam pedidos
5. autorização de negociação via API quando houver regra aprovada

Saída esperada:
- fluxo operacional de solicitação até pedido rastreável
- vínculo com obra, centro de custo e fornecedor

## MVP Fase 3 — Financeiro vinculado
Objetivo: conectar compras e títulos financeiros.

1. mapear vínculo entre pedido, fornecedor e título
2. validar contas a pagar originadas dos pedidos
3. consolidar visão de contas a pagar por obra / centro de custo
4. posteriormente avaliar escrita segura em títulos

## Arquitetura técnica recomendada

```text
integrations/
  sienge/
    config.py
    auth.py
    client.py
    errors.py
    models.py
    endpoints/
      creditors.py
      cost_centers.py
      projects.py
      resources.py
      purchase_requests.py
      purchase_quotations.py
      purchase_orders.py
      payables.py
      receivables.py
    normalizers/
      creditors.py
      cost_centers.py
      projects.py
      resources.py
      purchase_requests.py
      purchase_quotations.py
      purchase_orders.py
      payables.py
      receivables.py
    storage/
      checkpoint_store.py
      json_store.py
      sqlite_store.py
    jobs/
      sync_master_data.py
      sync_supply.py
      sync_finance.py
```

## Regras técnicas obrigatórias

### Autenticação
- credenciais fora do código
- arquivo de config dedicado da PCS
- troca centralizada de auth

### Cliente HTTP
- timeout explícito
- retry com backoff
- tratamento padrão de 4xx e 5xx
- paginação centralizada
- suporte a bulk endpoints e endpoints REST

### Persistência
- staging primeiro
- normalização depois
- guardar metadados da coleta:
  - endpoint
  - horário
  - status
  - cursor / offset / filtro

### Observabilidade
- log por job
- log por endpoint
- duração da execução
- quantidade de registros
- falhas por recurso

### Idempotência
- reprocessar sem duplicar
- upsert quando necessário
- checkpoint por entidade

## Dependências operacionais ainda necessárias

Para sair do desenho e entrar em execução real, faltam os seguintes insumos:

1. subdomínio PCS no Sienge
2. usuário de API
3. senha ou token de API
4. confirmação de que a PCS está em ambiente compatível com APIs DC
5. decisão sobre sistema mestre dos insumos
6. lista de campos obrigatórios da operação PCS para:
   - insumo
   - solicitação
   - pedido
   - conta a pagar

## Critério de concluído

A implantação só conta como concluída por fase quando houver:

1. autenticação real validada
2. chamada real em endpoint PCS
3. resposta persistida com sucesso
4. dados normalizados
5. validação funcional mínima com evidência

## Próximo passo recomendado

Executar a preparação técnica da base de integração no workspace e criar os primeiros módulos do conector Sienge para PCS, começando por:
- config
- auth
- client
- creditors
- cost_centers
- payables
