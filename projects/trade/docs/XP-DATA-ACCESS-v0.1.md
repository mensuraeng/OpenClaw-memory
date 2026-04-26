# Trade — XP Data Access v0.1

## Objetivo

Definir como o Trade pode acessar e organizar dados da XP para análises futuras de carteira, fundos, renda fixa, estruturados e oportunidades.

## Conclusão executiva

Existem quatro caminhos viáveis, em ordem recomendada:

1. **Exportação manual/CSV/PDF da XP** — melhor caminho imediato.
2. **Dados públicos CVM/ANBIMA/B3/BCB** — para enriquecer fundos, benchmarks e mercado.
3. **Open Finance Investimentos** — caminho regulado para posições/movimentações, mas depende de fluxo de consentimento e integração com participante receptor/TPP.
4. **XP Inc Developer Portal / APIs XP** — existe portal com APIs de captação, posição, movimentação, produto, conta e comissão para parceiros; provável necessidade de cadastro/aprovação e credenciais. Não assumir acesso para pessoa física sem validação.

## Pesquisa web — achados

### XP Developer Portal

Busca encontrou o portal `developer.xpinc.com`, com descrição pública indicando APIs para parceiros XP consumirem dados de:

- captação;
- posição;
- movimentação;
- produto;
- conta;
- comissão.

Também aparece área de documentação/login e lista de APIs. O site bloqueou acesso direto do servidor por CDN, então a confirmação granular de endpoints precisa ser feita em navegador logado ou com documentação liberada pela XP.

### XP Securities Services

Busca encontrou documentação pública/semipública de `XP Securities Services` citando APIs como boletas de cota de fundo, criação/consulta de ordens de investimento em cotas de fundo. Isso parece mais voltado a serviços/integrações institucionais e execução, não ao MVP pessoal do Trade.

Guardrail: não usar APIs de boleta/ordem nesta fase. Se aparecer API XP, usar apenas leitura/consulta.

### Open Finance Brasil

A documentação pública de Open Finance Brasil inclui APIs de Investimentos, com categorias como:

- Renda Fixa Bancária;
- Renda Fixa Crédito;
- Títulos do Tesouro Direto;
- Fundos de Investimento;
- Renda Variável.

Achado relevante: tempestividade indicada de até uma hora para APIs de Renda Fixa Bancária, Renda Fixa Crédito, Tesouro Direto e Fundos de Investimento; renda variável tende a posição/movimentações de fechamento D-1.

Esse é o caminho mais correto para automação regulada, mas exige consentimento e instituição receptora/integradora compatível.

### CVM Dados Abertos

CVM fornece Informe Diário de Fundos de Investimento com:

- valor total da carteira do fundo;
- patrimônio líquido;
- valor da cota;
- captações do dia;
- resgates pagos;
- número de cotistas.

Atualização: diária; arquivos M e M-1 atualizados diariamente com reapresentações, geralmente de segunda a sábado às 08:00 UTC, considerando dados enviados até 23:59 do dia anterior. Administradores têm prazo de um dia útil para envio.

Uso no Trade: enriquecer fundos da carteira XP por CNPJ, cota, PL, captação/resgate e histórico.

### ANBIMA Developers

ANBIMA tem APIs de Fundos v2 RCVM 175 e APIs de preços/índices para:

- fundos: lista, detalhes, histórico, série histórica, fundos por instituição;
- títulos públicos;
- debêntures;
- CRI/CRA;
- FIDC;
- letras financeiras;
- índices.

Uso no Trade: complementar CVM e criar benchmarks/comparáveis, principalmente para crédito privado e fundos.

## Arquitetura de ingestão recomendada

### Fase 1 — Manual XP Export

- Alê exporta extratos/posição da XP em CSV/PDF/print.
- Trade importa para `portfolio_positions`, `investment_products`, `portfolio_snapshots`.
- Trade cruza produtos com CVM/ANBIMA/BCB/B3.
- Sem login XP automatizado.

### Fase 2 — Enriquecimento público

- Fundos: CVM Informe Diário + ANBIMA Fundos.
- Renda fixa privada: ANBIMA preços/índices quando disponível.
- Tesouro: Tesouro Direto público + BCB.
- CDI/Selic/IPCA: BCB SGS.
- Bolsas/commodities: Yahoo/Stooq/FRED/brapi.

### Fase 3 — Open Finance

- Avaliar se a XP permite compartilhar investimentos via Open Finance com instituição/app receptor.
- Implementar apenas leitura após consentimento explícito.
- Guardar consentimentos e escopos, nunca senha da XP.

### Fase 4 — XP Developer Portal

- Verificar se o Alê tem acesso como parceiro/assessor/conta elegível.
- Solicitar/cadastrar aplicação se permitido.
- Usar somente endpoints de consulta de posição/movimentação/produto no MVP.
- Bloquear boletas/ordens/execução.

## Dados mínimos para análise de fundos XP

Para cada fundo:

- nome completo;
- CNPJ do fundo;
- classe/categoria;
- gestor;
- administrador;
- taxa de administração/performance;
- benchmark;
- prazo de cotização e liquidação;
- aplicação mínima;
- resgate mínimo;
- valor aplicado;
- valor atual/líquido;
- data da posição;
- histórico de cotas;
- PL;
- captação/resgate;
- número de cotistas;
- drawdown, volatilidade e retorno vs benchmark.

## Dados mínimos para renda fixa XP

Para CDB/LCI/LCA/CRI/CRA/debênture/estruturado:

- emissor;
- tipo;
- indexador;
- taxa contratada;
- vencimento;
- liquidez;
- FGC sim/não quando aplicável;
- rating se houver;
- preço/PU ou marcação se disponível;
- valor aplicado;
- valor atual;
- imposto/isenção;
- concentração por emissor;
- documentação do produto, especialmente estruturados.

## Guardrails

- Não guardar senha XP.
- Não automatizar login sem autorização explícita e sem avaliar risco.
- Não usar endpoint de ordem/boleta no MVP.
- Não executar resgate/aplicação.
- Não recomendar produto sem benchmark, liquidez, risco e fonte.
- Dados pessoais/financeiros devem ficar em Supabase com RLS e service role restrita.

## Próximo passo prático

Pedir ao Alê:

1. CSV ou PDF de posição consolidada da XP;
2. CSV/PDF detalhado de renda fixa e estruturados;
3. lista dos fundos com CNPJ, se disponível;
4. se existe acesso ao XP Developer Portal ou somente conta PF comum;
5. se deseja autorizar tentativa futura de conexão Open Finance apenas leitura.
