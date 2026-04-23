# OpenClaw Skill Audit v1

## Objective

Audit OpenClaw-compatible skills for trigger quality, execution clarity, context efficiency, and operational reliability without forcing unnecessary verbosity or a rigid one-size-fits-all template.

This spec adapts the useful parts of `okjpg/skill-audit` to the OpenClaw skill model and the `skill-creator` guidance.

## Design Principles

1. Favor clear triggering over long descriptions.
2. Favor concise operational guidance over documentation bloat.
3. Reward progressive disclosure using `references/`, `scripts/`, and `assets/`.
4. Distinguish between required quality bars and recommended excellence patterns.
5. Evaluate skills according to their type, not by a single rigid document shape.

## Compatibility Assumptions

This spec assumes the OpenClaw skill model where:
- trigger metadata primarily comes from YAML frontmatter
- the essential frontmatter fields are `name` and `description`
- SKILL.md should stay lean
- large or variant-specific material should move into `references/`
- deterministic or repetitive procedures should move into `scripts/`

## Skill Types

Before scoring, classify the skill into one of these types:

### 1. Procedural skill
A multi-step operational workflow where the model must execute a sequence reliably.

Examples:
- deployment skill
- invoice processing skill
- inbox triage skill

### 2. Reference-heavy skill
A skill that mainly routes the model to domain knowledge, schemas, policies, or supporting material.

Examples:
- finance schema skill
- API contract skill
- company policy skill

### 3. Script-backed skill
A skill where the most important action is running one or more bundled scripts or deterministic commands.

Examples:
- PDF rotation skill
- media transcoding skill
- batch renaming skill

If a skill spans multiple types, score it against the dominant type and note the hybrid behavior.

## Scoring Model

Score each skill on a 100-point scale.

### Category weights
- Trigger Quality: 35
- Execution Clarity: 30
- Context Efficiency: 20
- Reliability and Safety: 15

### Passing guidance
- 85-100: Excellent, portable, OpenClaw-aligned
- 70-84: Good, production-usable
- 55-69: Borderline, needs revision before broad reuse
- 0-54: Weak, likely brittle or poorly triggered

## Category 1: Trigger Quality (35)

### Required checks

#### T1. Valid identity
- `name` exists
- `name` is kebab-case
- skill folder name matches `name`

Penalty guidance:
- major failure if name is missing or malformed
- medium failure if folder mismatch creates ambiguity

#### T2. Useful description
The `description` must help the runtime decide when to activate the skill.

A good description:
- states what the skill does
- states when to use it
- contains concrete trigger cues or user phrasings when useful
- is specific enough to distinguish this skill from similar ones

Do not require:
- fixed minimum word counts
- third-person grammar
- an arbitrary number of quoted trigger phrases

Penalty guidance:
- major failure if description is generic enough to fit many unrelated skills
- medium failure if it explains capability but not activation context
- minor failure if it is correct but underspecified

#### T3. Scope clarity
The skill should make its boundaries clear when ambiguity is likely.

Accept any of these forms:
- `## When NOT to Use`
- negative boundaries embedded in description
- explicit confusable-case notes in instructions

Do not require negative boundaries for trivial or low-confusion skills.

Penalty guidance:
- apply only when trigger confusion risk is real

### Bonus indicators
- multiple realistic trigger phrasings
- confusable alternatives are called out cleanly
- automatic routing cues are included without bloating text

## Category 2: Execution Clarity (30)

### Required checks

#### E1. Actionability
The skill must contain enough operational guidance for the model to act.

Acceptable forms:
- explicit workflow
- concise procedural instructions
- script-first guidance with clear invocation
- reference-routing instructions with clear selection rules

Do not require a formal `## Workflow` heading for every skill.

Penalty guidance:
- major failure if the skill explains purpose but not how to proceed
- major failure if execution depends on hidden author context

#### E2. Non-vague instructions
Avoid vague phrases that delegate important judgment without criteria.

Examples of weak phrasing:
- handle appropriately
- as needed
- format nicely
- when relevant
- if it makes sense

Use this as a semantic warning, not a blind regex-only conviction.

Penalty guidance:
- major if core steps are vague
- minor if only auxiliary notes contain vague language

#### E3. Output clarity
The skill should make the expected result clear.

Acceptable forms:
- `## Outputs`
- output expectations in workflow
- output examples
- clear delivery notes in body text

Do not require a dedicated section if outcome is otherwise unambiguous.

#### E4. Examples proportional to complexity
Examples are strongly recommended and should be expected for medium or high complexity skills.

Guidance:
- simple skill: examples optional
- medium skill: at least 1 concrete example recommended
- complex skill: 2 or more examples strongly preferred

#### E5. Edge handling proportional to complexity
Edge cases should be documented when failure modes are likely.

Guidance:
- trivial skill: optional
- procedural or external-dependency skill: expected
- automation/cron-facing skill: strongly expected

## Category 3: Context Efficiency (20)

### Required checks

#### C1. Lean SKILL.md
SKILL.md should contain the minimum instructions required to operate effectively.

Warning conditions:
- excessive exposition
- repeated explanations
- user-facing documentation that does not help the runtime
- large embedded reference material that should live elsewhere

#### C2. Progressive disclosure
Reward use of:
- `references/` for detailed docs or domain material
- `scripts/` for deterministic repetitive logic
- `assets/` for non-context resources

Penalty guidance:
- medium penalty when large detail blocks stay in SKILL.md with no reason
- bonus when the skill cleanly points to the right supporting files

#### C3. Low duplication
Avoid duplicating the same instructions in description, overview, examples, and references.

Penalty guidance:
- minor to medium depending on wasted context cost

## Category 4: Reliability and Safety (15)

### Required checks

#### R1. No secrets
No hardcoded API keys, tokens, or credentials in any skill files.

#### R2. Reference integrity
Internal links and referenced files should resolve correctly.

#### R3. Dependency clarity
If the skill requires external files, tools, APIs, env vars, or scripts, that should be discoverable from the skill.

This does not require a formal `## Dependencies` section, but dependencies must not be hidden.

#### R4. Evals for high-risk skills
`evals/` are recommended, and strongly recommended for:
- shared/public skills
- cron or automation skills
- high-branching workflows
- critical business tasks

Do not fail a small local skill solely for missing evals.

## Severity Model

Classify findings as:
- Critical: likely to break triggering, safety, or basic execution
- Major: materially harms usability or portability
- Minor: useful cleanup with moderate impact
- Info: suggestion or excellence opportunity

## Suggested Finding Codes

### Trigger
- `missing_frontmatter`
- `missing_name`
- `invalid_name`
- `name_folder_mismatch`
- `missing_description`
- `generic_description`
- `weak_trigger_cues`
- `scope_ambiguity`

### Execution
- `missing_actionability`
- `workflow_too_vague`
- `unclear_output`
- `examples_thin`
- `edge_cases_thin`
- `hidden_author_context`

### Context efficiency
- `skill_too_long`
- `missing_progressive_disclosure`
- `duplicated_guidance`
- `reference_material_embedded`

### Reliability and safety
- `hardcoded_secret`
- `broken_refs`
- `hidden_dependencies`
- `evals_recommended`

## Type-Aware Interpretation

### Procedural skill
Score more heavily on:
- actionability
- explicit conditions
- outputs
- edge cases
- dependency clarity

### Reference-heavy skill
Score more heavily on:
- trigger specificity
- reference organization
- lean overview
- clear routing to supporting files

Do not over-penalize lack of formal workflow if the skill is primarily navigational.

### Script-backed skill
Score more heavily on:
- invocation clarity
- script discoverability
- input/output contract
- failure handling

Do not over-penalize short body text if the script is the core logic and is clearly described.

## Auditor Behavior Recommendations

### Prefer weighted scoring over binary gates
Do not model the entire audit as 10 pass/fail checks. Use weighted scoring with severity.

### Prefer warnings over rigid failure for stylistic issues
Do not fail a skill solely because it lacks:
- 50+ words
- third-person writing
- 5 quoted trigger phrases
- a specific H2 order
- an `evals/` folder for a trivial local skill

### Fail hard on truly important problems
Use hard failures or strong penalties for:
- malformed or missing identity
- generic or missing description
- no actionable guidance
- secrets in repo
- broken internal references
- hidden critical dependencies

## Minimal Good Skill Standard

A skill should be considered good in OpenClaw if it:
- has valid `name` and `description`
- can be triggered for the right reasons
- gives enough guidance to act
- does not waste context unnecessarily
- does not hide critical dependencies
- does not contain secrets

## Excellent Skill Standard

A skill should be considered excellent if it also:
- uses progressive disclosure well
- includes concrete examples for realistic use
- documents important failure modes
- has clear scope boundaries where ambiguity exists
- is portable across models without becoming bloated

## Migration Guidance from V3-style Audits

When adapting a skill from rigid V3 audit standards to OpenClaw:
- keep strong trigger cues
- keep clear workflows where they matter
- keep examples and edge cases when complexity warrants them
- remove unnecessary frontmatter fields
- move large detailed content into `references/`
- move deterministic logic into `scripts/`
- shorten boilerplate sections that do not improve execution

## Implementation Guidance for an OpenClaw Auditor

An OpenClaw implementation should:
1. parse `name` and `description`
2. classify skill type
3. score by weighted categories
4. emit severity-ranked findings
5. distinguish required failures from recommended improvements
6. report both score and rationale

## Recommended Output Format

For each skill, report:
- overall score
- skill type
- top critical or major findings
- category subscores
- concise remediation suggestions

Example summary:

```text
invoice-parser — 78/100 — procedural
Trigger Quality: 28/35
Execution Clarity: 24/30
Context Efficiency: 12/20
Reliability and Safety: 14/15

Major findings:
- weak_trigger_cues
- edge_cases_thin

Minor findings:
- duplicated_guidance
- evals_recommended
```

## Final Position

This spec treats `skill-audit` as a valuable source of structural heuristics, but not as a rigid canonical standard. OpenClaw should optimize for portable triggering, actionable guidance, and context efficiency rather than document maximalism.
