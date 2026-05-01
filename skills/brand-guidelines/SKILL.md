---
name: brand-guidelines
description: Use when creating, reviewing, styling, or adapting visual artifacts, presentations, PDFs, landing pages, social posts, proposals, dashboards, one-pagers, or institutional materials for MENSURA, MIA, or PCS. Applies local brand colors, typography, layout tone, visual hierarchy, and guardrails. Adapted from Anthropic's brand-guidelines skill pattern, but uses MENSURA/MIA/PCS identity rules.
license: Local adaptation; source pattern from Apache-2.0 Anthropic skills brand-guidelines.
metadata:
  version: 0.1.0
  source: adapted-from-anthropics-skills-brand-guidelines
---

# Brand Guidelines — MENSURA / MIA / PCS

Use this skill whenever a deliverable needs brand-consistent visual or verbal styling.

## Default workflow

1. Identify the brand: MENSURA, MIA, PCS, or neutral Flávia/OpenClaw.
2. Read only the relevant reference:
   - MENSURA → `references/mensura.md`
   - MIA → `references/mia.md`
   - PCS → `references/pcs.md`
   - Cross-brand/unknown → `references/cross-brand.md`
3. Apply brand colors, typography direction, spacing, layout tone and voice.
4. Preserve factual/legal/commercial guardrails.
5. If official asset/color is missing, label the choice as provisional or inferred.

## Core guardrails

- Never mix MIA luxury language into PCS institutional material.
- Never make MENSURA look like generic construction/fiscalização.
- Never make PCS look like aggressive growth marketing.
- Never overclaim performance, guarantee dates, accept responsibility, approve cost, or imply legal/technical acceptance.
- Use official brand documents from `2nd-brain` first when available.

## Artifact guidance

### Presentations / PDFs

- Use fewer words per slide.
- One idea per page/section.
- Strong hierarchy: title, key assertion, evidence, action.
- Prefer calm precision over decorative complexity.

### Social posts

- Preserve brand voice before visual novelty.
- Use brand accent sparingly.
- CTA must match channel and risk level.

### Landing pages / one-pagers

- Hero must state buyer pain + outcome.
- Use proof, process, and next step.
- Brand visuals should support trust, not decorate emptiness.

## Output pattern

When reviewing or creating brand material, return:

1. **Marca aplicada**
2. **Paleta/tipografia/layout**
3. **Ajustes recomendados**
4. **Riscos de marca ou tom**
5. **Próximo passo**

## Attribution

This skill adapts the pattern of Anthropic's Apache-2.0 `brand-guidelines` skill. It does not use Anthropic's brand identity; it defines local MENSURA/MIA/PCS guidelines.
