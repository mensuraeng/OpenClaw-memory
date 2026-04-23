# Regras de composição — Orçamentista

## Bases de referência

### SINAPI
- Nacional
- Base CAIXA / IBGE
- Pode ser desonerado ou não desonerado
- Usar em obras públicas federais, habitação e saneamento
- Sempre declarar: base, mês/ano, UF e regime quando aplicável

### CPOS
- Referência do Estado de São Paulo
- Atualização mensal
- Usar em obras habitacionais em SP quando fizer sentido
- Sempre declarar versão

### SIURB
- Referência da Prefeitura de São Paulo
- Usar em infraestrutura urbana no município de São Paulo
- Sempre declarar versão

### TCPO
- Tabela de composições Pini
- Referência privada ampla
- Usar como referência complementar em ambiente privado

### Própria / mercado
- Cotação direta
- Composição interna
- Usar em obras privadas ou quando não houver base oficial aplicável

### Mista
- Combinação de bases
- Declarar qual base foi usada em cada item

## Hierarquia de decisão

1. Base informada pelo usuário → usar sem substituir
2. Obra pública federal → SINAPI
3. Obra habitacional SP → CPOS como referência
4. Infraestrutura urbana SP → SIURB como referência
5. Sem composição na base → composição própria com justificativa de coeficientes

## Lógica de composição de custos

### Estrutura de preço unitário
`Preço unitário = Custo Direto × (1 + BDI)`

### Custo direto
Decompor em:
- material
- mão de obra
- equipamentos, quando houver

Nunca misturar MAT com MO em linha única sem decomposição.

### Encargos sociais
Aplicar sobre mão de obra, nunca sobre material.
Considerar o regime aplicável:
- horista
- mensalista
- desonerado
- não desonerado

### BDI
Declarar sempre:
- percentual
- componentes
- critério de aplicação

Nunca tratar BDI como caixa preta.

### Perdas
Aplicar conforme tipo de material e base utilizada.
Atenção: quando usar SINAPI, não aplicar perda adicional automaticamente se a própria base já embute perdas.

### Produtividade
Usar produtividade de referência por serviço quando necessário e declarar a origem ou o racional.

## Detecção obrigatória de inconsistências

### Inconsistências de unidade
- unidade do serviço incompatível com o que está sendo medido
- coeficiente de insumo incompatível com a unidade do serviço

Exemplo:
- m³ de piso quando o esperado seria m²

### Inconsistências de coeficiente
- coeficiente acima ou abaixo mais de 30% da referência sem justificativa
- coeficiente igual a 1,00 para insumo que deveria ser fracionário
- coeficiente sem perda quando o material tem perda relevante

### Inconsistências de preço
- preço unitário acima de 50% do mercado sem justificativa
- preço unitário abaixo de 30% do mercado, com risco de inexequibilidade
- BDI acima de 35% ou abaixo de 15% sem justificativa

## Itens faltantes mais comuns por tipo de serviço

### Alvenaria
- argamassa de assentamento
- verga / contraverga
- tela de reforço

### Estrutura de concreto
- desmoldante
- espaçadores
- vibrador

### Revestimento cerâmico
- rejunte
- impermeabilização de junta em áreas molhadas
- rodapé

### Pintura
- selador / fundo
- massa corrida, quando aplicável

### Instalações
- conexões
- suportes
- buchas
- abraçadeiras

### Geral
- mobilização
- EPI
- limpeza final
- placa de obra

### Pavimentação
Itens que frequentemente somem:
- regularização de sub-base
- recomposição de meio-fio
- sinalização horizontal
- desvio de tráfego
- areia de rejuntamento e reposição

## Regras invioláveis

- Nunca entregar número sem unidade.
- Nunca misturar MAT com MO em linha única sem decomposição.
- Nunca esconder premissa, declarar antes do resultado.
- Nunca somar itens de unidades incompatíveis sem conversão explícita.
- Nunca fingir precisão onde existe lacuna, declarar nível de confiança.
- Quando houver foto, não superestimar produção; extrapolação é estimativa.
- BDI sempre declarado com percentual e componentes.
- Encargos sociais sempre sobre MO, nunca sobre material.
- SINAPI já pode embutir perdas; não duplicar perda sem justificativa.
- Nunca corrigir inconsistência interna por conta própria.
- Item em verba deve ser registrado como verba; nunca abrir sem declarar que é estimativa.
- Medição com foto deve declarar explicitamente que a foto é apoio, não prova absoluta.

## Integração com a MENSURA Torre de Controle

### Torre de Controle
Responsável por:
- prazo
- cronograma
- Lean
- restrições
- riscos
- governança
- IAO

### Este skill
Responsável por:
- custo
- composição
- quantitativo
- medição
- compra
- BDI

### Pontos de conexão
- medições alimentam percentual físico da obra
- lista de compra pode gerar restrições de material no look ahead
- desvio de quantidade pode indicar impacto em prazo
