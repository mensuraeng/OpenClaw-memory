# RevOps — Lead to Revenue

Use for CRM, lifecycle, scoring, routing and commercial handoff.

## Lifecycle

- Lead: identified contact/account.
- Qualified Lead: basic fit verified.
- MQL: fit + engagement or trigger.
- SQL: accepted by sales/operator after validation.
- Opportunity: concrete pain, timing, next step and decision path.
- Proposal: scoped commercial proposal.
- Closed Won/Lost: outcome logged with reason.

## Scoring dimensions

Fit:
- company type, segment, region, obra volume/CAPEX, role/seniority.

Intent:
- reply, meeting request, pricing/proposal interest, project pain, deadline pressure.

Negative:
- generic email, bounced domain, supplier/vendor, student, irrelevant segment, spam complaint.

## SLA recommendations

- Positive reply: same business day, ideally under 4h.
- High-intent inbound: under 1h during business hours.
- No owner: route to Flávia/MENSURA review queue; never let it disappear.

## HubSpot guardrails

- Read-only by default.
- Any contact/company/deal update is external CRM write and requires approval unless already covered by explicit workflow authorization.
- Log import source, run id, fields changed and rollback/export before bulk writes.
