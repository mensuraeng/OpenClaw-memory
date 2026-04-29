---
name: marketing-proposals-presentations
description: Use para criar, revisar ou estruturar propostas comerciais, apresentações técnicas, decks institucionais, one-pagers, páginas e materiais de marketing para Mensura, MIA ou PCS com base em identidade de marca, design system, público-alvo e objetivo comercial. Acione quando o pedido envolver proposta, apresentação técnica, deck, material institucional, pitch, diagnóstico comercial, apresentação executiva ou transformação de briefing/roteiro em material visual alinhado à marca.
---

# Marketing Proposals & Presentations

## Princípio

Não comece pelo deck. Comece pela marca, pelo objetivo comercial e pela tese técnica.

A lógica é:

```text
briefing → identidade/posicionamento → design system → arquitetura narrativa → slides/proposta → revisão técnica → versão final
```

A ferramenta visual pode ser Claude Design, PowerPoint, Canva, Figma, Gamma, HTML/PDF ou outra. A skill não depende de uma ferramenta específica.

## Governança obrigatória

Esta é uma skill compartilhada: Mensura, MIA, PCS, Finance, Trade ou Flávia podem usá-la para estruturar material.

Mas toda peça de marketing passa por este fluxo antes de sair:

```text
agente solicitante → Marketing → Flávia → Alê / aprovação externa
```

Regras:

- O agente de domínio pode produzir insumo técnico, escopo, tese, dados e rascunho.
- O Marketing revisa posicionamento, narrativa, aderência de marca, clareza comercial e consistência visual.
- A Flávia só aprova depois da revisão do Marketing.
- Nada é enviado, publicado ou apresentado externamente sem aprovação explícita do Alê quando houver saída externa.
- Se o material for apenas interno, ainda assim deve ficar marcado como **rascunho interno** até passar pelo Marketing.

## Quando usar

Use para:
- proposta comercial;
- apresentação técnica;
- deck institucional;
- material de diagnóstico;
- apresentação de obra, cronograma, CAPEX, risco ou governança;
- transformação de roteiro em slides;
- criação de base para Cloud/Claude Design ou ferramenta equivalente.

## Entrada mínima obrigatória

Antes de produzir o material, obter ou inferir:

1. **Marca**: Mensura, MIA ou PCS.
2. **Objetivo**: vender, educar, convencer, reportar, aprovar decisão ou abrir conversa.
3. **Público**: diretoria, cliente final, incorporador, construtora, gestor de obra, órgão público etc.
4. **Oferta/tese**: o que precisa ficar claro.
5. **Formato**: proposta, deck, one-pager, apresentação técnica, relatório visual.
6. **Uso**: reunião, envio por PDF, palestra, WhatsApp, LinkedIn, e-mail.
7. **Restrições**: prazo, confidencialidade, tema jurídico, promessa comercial, obra sensível.

Se faltar algo crítico, faça no máximo 3 perguntas objetivas. Se der para seguir com premissas seguras, siga e declare as premissas.

## Fundamentos de marca antes do design

Para cada marca, confirme:

- posicionamento;
- tom de voz;
- cores, tipografia e logos quando disponíveis;
- repertório visual permitido;
- o que a marca nunca deve parecer;
- concorrentes ou alternativas conhecidas pelo cliente;
- fator de distintividade: em relação a quem o material precisa se diferenciar.

Se a marca não tiver design system explícito, crie um **design brief textual** antes do material visual.

## Referências de marca e domínio

Use só o necessário; não carregue tudo por padrão.

- **Marketing/comercial geral**: `/root/2nd-brain/04-projects/marketing/MAP.md`.
- **Mensura**: `/root/2nd-brain/04-projects/mensura/MAP.md` e skills em `/root/.openclaw/workspace/agents/mensura/skills/`.
- **MIA**: `/root/2nd-brain/04-projects/mia/MAP.md`, especialmente `brand-book-quiet-luxury.md` e `guia-aplicacao-documental.md` quando o material for premium/alto padrão.
- **PCS**: `/root/2nd-brain/04-projects/pcs/MAP.md`, `identidade-e-posicionamento.md`, `identidade-visual.md`, `guia-aplicacao-marca.md` e `base-comercial.md` quando o material for institucional, restauro, licitação ou patrimônio.

Para temas de obra, prazo, EVM, CAPEX, risco ou governança, combine esta skill com as skills técnicas da marca antes de finalizar a narrativa.

## Arquitetura narrativa

Todo material deve responder:

1. Qual dor ou oportunidade abre a conversa?
2. Por que isso importa agora?
3. Qual leitura técnica diferencia nossa abordagem?
4. Qual solução/proposta é apresentada?
5. Que evidência sustenta a proposta?
6. Qual decisão ou próximo passo o cliente deve tomar?

Evite estética bonita sem tese. Slide bonito sem argumento é ruído.

## Regras por tipo de material

### Proposta comercial

Estrutura recomendada:

1. capa com promessa clara;
2. contexto do cliente;
3. diagnóstico / leitura técnica;
4. escopo proposto;
5. metodologia de execução;
6. diferenciais objetivos;
7. cronograma ou fases;
8. responsabilidades e premissas;
9. investimento, se autorizado;
10. próximos passos.

### Apresentação técnica

Estrutura recomendada:

1. abertura executiva;
2. problema técnico;
3. dados/evidências;
4. análise;
5. cenários ou alternativas;
6. recomendação;
7. riscos e mitigação;
8. decisão necessária.

### Deck institucional

Estrutura recomendada:

1. tese central da marca;
2. problema do mercado;
3. ponto de vista proprietário;
4. capacidades;
5. provas/cases;
6. modelo de trabalho;
7. chamada para conversa.

## Padrão de slide

- Pouco texto no slide; detalhe nas notas do apresentador.
- Um slide = uma ideia.
- Títulos devem ser conclusivos, não decorativos.
- Gráficos e diagramas só entram se acelerarem entendimento.
- Não inventar número, case, cliente, prazo ou resultado.
- Usar placeholders explícitos quando faltar imagem, dado ou case.

## Prompt-base para ferramenta visual

Use este padrão ao gerar em ferramenta de design:

```text
Crie uma apresentação em português para [objetivo], destinada a [público], usando o design system/brief da marca [marca].

Tom visual: [ex.: técnico, premium, institucional, executivo, discreto].
Tom verbal: [ex.: direto, consultivo, preciso, sem marketing vazio].
Duração/uso: [ex.: reunião de 20 min, PDF enviado por e-mail].
Regra: slides limpos, pouco texto, títulos conclusivos e notas do apresentador com o argumento completo.

Estrutura narrativa:
[cole a arquitetura aprovada]

Conteúdo-base:
[cole briefing, roteiro, proposta, dados ou tese]

Restrições:
[não prometer prazo; não admitir responsabilidade; usar placeholders; não citar clientes sem autorização etc.]
```

## Revisão obrigatória antes de entregar

Checklist:

- Passou pelo Marketing antes da aprovação da Flávia?
- O material tem tese clara?
- Está com a cara da marca?
- Está distinto das alternativas que o cliente conhece?
- Está tecnicamente defensável?
- Não promete o que não foi aprovado?
- Não usa dado sem fonte?
- Tem próximo passo claro?
- Para P&G Louveira ou tema jurídico: exigir revisão do Alê antes de qualquer envio.

## Saída recomendada

Ao entregar internamente, prefira este pacote:

1. **Arquitetura narrativa**: sequência de seções/slides.
2. **Texto executivo**: versão curta para proposta/deck.
3. **Notas do apresentador**: argumento completo, sem poluir slides.
4. **Prompt visual**: pronto para Claude Design/Canva/Figma/Gamma/HTML.
5. **Pendências**: imagens, dados, cases, preço ou aprovações faltantes.

Não envie material para cliente, lead ou canal público sem aprovação explícita.

## Referências opcionais

- Para briefing de proposta: `references/proposal-brief-template.md`.
- Para design brief textual: `references/brand-design-brief-template.md`.
