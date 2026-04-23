# OpenClaw Skills Placement Policy

_Version: 1.0 — 2026-04-18_

## Decision Framework

### The Two Questions

> **Question 1:** "Does this skill work in any agent without changing a single line?" → YES → `shared/`
> **Question 2:** "Does this skill encode the voice, process, or business asset of a specific agent?" → YES → `agents/[name]/skills/`
> **Tiebreaker:** If unclear, goes to `agents/`. Promotion to `shared/` requires confirmed use by 2+ agents.

### Key Clarification

External channel alone is NOT the criterion — domain context is.

- `whatsapp-sender` → `shared/` (generic mechanic — any agent can send a WhatsApp)
- `mensura-whatsapp-cobranca` → `agents/mensura/` (encodes the obra billing process — domain-specific)

Platform does not matter. Domain does.

### Three Failure Modes This Policy Prevents

1. **Useful skill buried in an agent** → explicit promotion required when 2+ agents confirm use
2. **Domain-specific skill polluting shared/** → blocked by Question 2
3. **Duplicated logic across agents** → forbidden by promotion rule (promote instead of duplicate)

---

## Layer Definitions

| Layer | Path | Purpose |
|-------|------|---------|
| **shared/** | `skills/shared/` | Skills any agent in any workspace can invoke with zero domain knowledge. Generic mechanics only. |
| **core/** | `skills/core/` | Skills that define OpenClaw's identity and govern cross-agent behavior (audit, evolution, sync). Not domain tools — infrastructure. |
| **agent-specific** | `agents/[name]/skills/` | Skills requiring the voice, data model, or business logic of a specific agent. Cannot be used as-is by another agent. |

---

## Current Skills Inventory

### shared/ — Generic mechanics, usable by any agent

| Skill | Why shared/ |
|-------|-------------|
| `weather` | Pure external API lookup — zero domain context required |
| `slack` | Generic channel mechanic — post to any Slack workspace |
| `notion` | Generic Notion read/write — no domain schema baked in |
| `whatsapp` (group: utils, styling-guide, chats, openclaw-whatsapp) | Transport + formatting mechanics — not tied to any agent's domain |
| `biz-reporter` | Generic business report formatter — no single-agent domain logic |
| `academic-research-hub` | General research pipeline — usable across any knowledge domain |
| `youtube-publisher` | Generic video upload mechanic — no content domain required |
| `docling` | Document parsing utility — format conversion, domain-agnostic |
| `superpowers` | OpenClaw meta-tooling (token analysis, brainstorm server) — cross-agent dev utility |
| `agent-context-system` | Generic context sync scaffolding — not bound to one agent's schema |
| `agent-task-tracker` | Generic task state tracker — any agent can track tasks |
| `arc-trust-verifier` | Source trust verification — generic quality gate for any agent |
| `afrexai-supply-chain` | Supply chain data connector for AfrexAI — reusable across finance/ops agents |
| `afrexai-inventory-supply-chain` | Inventory layer on top of above — same cross-agent applicability |
| `aeo-analytics-free` | Analytics fetch utility — generic data retrieval, no domain config |
| `active-maintenance` | Keepalive / maintenance heartbeat — infrastructure utility |

### core/ — OpenClaw identity and cross-agent infrastructure

| Skill | Why core/ |
|-------|-----------|
| `agent-audit-trail` | Defines immutable audit logging for ALL agents — platform identity layer |
| `agent-daily-planner` | Cross-agent daily scheduling framework — orchestration, not domain |
| `capability-evolver` | GEP-based evolution engine — defines how OpenClaw grows its own capabilities |
| `capability-evolver-src` | Source/assets for the evolver (capsules, genes, evolution state) |
| `check-analytics` | Cross-agent analytics check — platform observability layer |

### agents/mensura/skills/ — Mensura domain knowledge required

| Skill | Why agent-specific |
|-------|-------------------|
| `mensura-autopilot` | Encodes MENSURA's obra monitoring logic, monitored-projects registry, LPS+EVM methodology |
| `mensura-relatorio-semanal` | Encodes MENSURA's weekly report format, voice, and client communication standards |
| `orcamentista` | Encodes MENSURA's cost decomposition process (MAT/MO/EQ), SINAPI/TCPO references, BDI rules |

### agents/finance/skills/ — Finance domain knowledge required

| Skill | Why agent-specific |
|-------|-------------------|
| `cs-financial-analyst` | Encodes DCF valuation logic, budget variance analysis, and forecast methodology for finance agent |
| `financial-analyst` | Finance agent's primary analyst persona — voice and process are finance-specific |

---

## Promotion Protocol

A skill may be promoted from `agents/[name]/skills/` to `shared/` only when:

1. At least **2 distinct agents** have confirmed they use it without modification
2. All domain-specific parameters are extracted to config (no hardcoded domain logic)
3. A PR is opened with explicit notation of which agents triggered promotion

**No exceptions to the 2-agent rule.** Anticipatory promotion is prohibited.

---

## New Skill Placement Checklist

```
[ ] Does it require this agent's data model, voice, or domain rules?
    YES → agents/[name]/skills/
    NO  → continue

[ ] Does it define cross-agent OpenClaw behavior (audit, evolution, orchestration)?
    YES → core/
    NO  → shared/

[ ] Is placement still unclear?
    → agents/[name]/skills/ (tiebreaker: always conservative)
    → Open promotion review when a second agent adopts it
```
