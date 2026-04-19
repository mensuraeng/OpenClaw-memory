# Uso do arc-trust-verifier no stack do Alê

## Papel
Camada inicial de due diligence para skills de terceiros antes de instalação ou habilitação.

## Quando usar
- antes de instalar nova skill de comunidade
- antes de habilitar workflow externo
- antes de confiar em skill pouco documentada

## O que ele faz bem
- verifica proveniência básica
- analisa sinais simples de confiança
- gera score inicial
- ajuda a formalizar processo de triagem

## O que ele não substitui
- leitura manual de SKILL.md e README
- revisão de scripts críticos
- análise de risco contextual
- julgamento operacional

## Fluxo recomendado
1. inspecionar skill
2. rodar trust verifier
3. ler código/arquivos críticos
4. classificar skill como aprovada, restrita ou reprovada
5. só então instalar

## Classificação recomendada
- aprovado para teste controlado
- aprovado com restrições
- reprovado

## Regra prática
Score bom sem leitura humana não basta.
Score ruim bloqueia rápido.
