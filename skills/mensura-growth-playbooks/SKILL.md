---
name: mensura-growth-playbooks
description: Use when operating MENSURA growth, commercial intelligence, outbound, RevOps, paid media planning, sales enablement, customer research, competitor research, landing pages, lead magnets, or marketing copy. Built from curated marketingskills patterns adapted to MENSURA/MIA/PCS guardrails. Always preserve approval gates for external sends, ads spend, CRM writes, and institutional claims.
metadata:
  version: 0.1.0
  source: adapted-from-coreyhaines31-marketingskills
---

# MENSURA Growth Playbooks

Use this skill for growth work that must convert into real pipeline without breaking governance.

## Default stance

- Start from business context, ICP, offer, channel, proof and next action.
- Use numbers before adjectives.
- Prefer one strong commercial motion over many scattered ideas.
- No external send, ad spend, CRM write, campaign activation or institutional claim without Alê approval.
- Never bypass suppression lists, bounce history, budget caps, or brand guardrails.

## Source of truth

Before writing strategy or copy, check current context if relevant:

- MENSURA positioning: `/root/2nd-brain/04-projects/mensura/` and `/root/.openclaw/workspace/docs/mensura-marketing/`
- MIA positioning: `/root/2nd-brain/04-projects/mia/`
- PCS positioning: `/root/2nd-brain/04-projects/pcs/`
- Commercial intelligence: `/root/.openclaw/workspace/projects/mensura-commercial-intelligence/`
- CRM/runtime outputs: `/root/.openclaw/workspace/runtime/mensura-marketing/`
- Meta Ads state: `/root/.openclaw/workspace/runtime/mensura-marketing/meta-ads/`

## Playbook selection

Read only the reference needed for the task:

- Product/ICP/positioning context → `references/product-marketing-context.md`
- Cold email / outbound / follow-up → `references/outbound-cold-email.md`
- Lead lifecycle / CRM / handoff / HubSpot → `references/revops.md`
- Meta/LinkedIn/Google Ads planning → `references/paid-ads.md`
- Sales deck / one-pager / objections / proposal support → `references/sales-enablement.md`
- Customer language / VOC / interview/review mining → `references/customer-research.md`
- Competitor research / battle cards / alternatives → `references/competitor-research.md`
- Landing page / forms / lead magnets / copy → `references/conversion-copy.md`

## Mandatory guardrails

### Outbound

- Every new list must pass dedupe, DNS/domain check, suppression, previous bounces, role-based filtering and ICP scoring before outreach.
- Cold emails must be short, human, specific and one-ask.
- No bulk send from draft. Draft → review → explicit approval → send.

### Paid media

- Current Meta Ads cap: **R$ 0/dia** until Alê changes it.
- With R$ 0/day, allowed: connect, read, audit, draft, structure, simulate.
- Blocked: activate, publish with spend, increase budget, or create any charge.

### CRM / HubSpot

- Read-only by default.
- Any import, lifecycle update, deal creation, automation or routing rule is a write and needs explicit approval.
- Keep logs/evidence for any accepted data change.

### Institutional claims

Do not claim guarantee, approval, acceptance, responsibility, or performance outcome unless validated and approved.
Use language of analysis, diagnosis, visibility, risk reduction, governance and decision support.

## Output pattern

For recommendations, return:

1. **Diagnóstico** — what is happening.
2. **Ação recomendada** — what to do next.
3. **Por quê** — commercial/operational rationale.
4. **Risco/trava** — approval, data, budget, legal/reputational issue.
5. **Próximo passo simples** — the smallest safe action.

## Attribution

This local skill adapts selected concepts from the MIT-licensed repo `coreyhaines31/marketingskills`, curated for OpenClaw/MENSURA/MIA/PCS operations.
