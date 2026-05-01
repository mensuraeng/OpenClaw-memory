# Avaliação e implantação — Anthropic `brand-guidelines`

_Data: 2026-04-30_
_Origem: https://github.com/anthropics/skills/tree/main/skills/brand-guidelines_
_Caminho local inspecionado: `/root/.openclaw/workspace/tmp/anthropic-skills-brand-guidelines/skills/brand-guidelines`_

## O que a skill original faz

A skill original aplica diretrizes visuais da Anthropic: cores, tipografia e estilo para artefatos como apresentações e documentos. É simples e útil como padrão de estrutura: uma skill leve com paleta, tipografia, regras de aplicação e fallback.

## O que aproveitamos

- Estrutura curta de skill para identidade visual.
- Separação entre cores, tipografia, formas/acento e regras de aplicação.
- Ideia de aplicar guideline em qualquer artefato visual.
- Padrão de manter SKILL.md enxuto e referências sob demanda.

## O que não aproveitamos

- Cores e fontes da Anthropic.
- Qualquer look-and-feel Anthropic.
- Qualquer suposição de que uma única identidade serve para todas as marcas.

## Implantação local

Criada skill local:

`/root/.openclaw/workspace/skills/brand-guidelines/SKILL.md`

Referências:

- `references/mensura.md`
- `references/mia.md`
- `references/pcs.md`
- `references/cross-brand.md`

## Estado das marcas

### MIA

Tem brand book forte e paleta/tipografia oficiais:

- `#F9F9F7`, `#050505`, `#A0A0A0`, `#1C1917`, `#737373`.
- Playfair Display + Lato.
- Quiet luxury técnico.

### PCS

Tem identidade visual oficial com paleta exata:

- `#37444A`, `#E74133`, `#F8F7F7`.
- Direção institucional, sóbria e robusta.

### MENSURA

Tem apresentação e voz fortes, mas paleta exata ainda precisa canonização. A skill usa paleta provisória inferida da apresentação: preto/off-white/cinzas técnicos. Próximo passo recomendado: extrair tokens oficiais a partir do arquivo-fonte ou aprovar paleta canônica.

## Uso recomendado

- Revisão visual de apresentações.
- Geração de one-pagers.
- Landing pages.
- Posts sociais.
- Propostas e relatórios.
- Dashboards e Mission Control com aparência institucional.

## Guardrail

A skill só orienta visual/tom. Não autoriza comunicação externa nem afirmações comerciais, jurídicas ou técnicas sem validação.
