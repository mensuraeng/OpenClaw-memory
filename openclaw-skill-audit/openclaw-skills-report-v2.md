# OpenClaw Skill Audit Report

> Source: `/usr/lib/node_modules/openclaw/skills`
> Total skills: **53**
> Average score: **77.5/100**

## Skill types

- **procedural**: 42
- **reference-heavy**: 6
- **script-backed**: 5

## Most common findings

- `examples_thin`: 52
- `edge_cases_thin`: 42
- `scope_ambiguity`: 40
- `hidden_dependencies`: 35
- `weak_trigger_cues`: 24
- `evals_recommended`: 23
- `unclear_output`: 21
- `missing_progressive_disclosure`: 7
- `missing_actionability`: 6
- `skill_too_long`: 4

## Ranking

| Skill | Type | Score | Rating |
|---|---|---:|---|
| canvas | script-backed | 52 | weak |
| blucli | procedural | 57 | borderline |
| eightctl | procedural | 57 | borderline |
| video-frames | procedural | 57 | borderline |
| gemini | procedural | 64 | borderline |
| nano-pdf | procedural | 64 | borderline |
| openai-whisper | procedural | 64 | borderline |
| gh-issues | procedural | 69 | borderline |
| voice-call | procedural | 69 | borderline |
| discord | procedural | 70 | good |
| coding-agent | procedural | 72 | good |
| notion | procedural | 73 | good |
| trello | procedural | 73 | good |
| gog | procedural | 74 | good |
| obsidian | procedural | 74 | good |
| sag | procedural | 74 | good |
| node-connect | procedural | 75 | good |
| openhue | procedural | 75 | good |
| sherpa-onnx-tts | procedural | 75 | good |
| slack | procedural | 75 | good |
| sonoscli | procedural | 75 | good |
| taskflow-inbox-triage | procedural | 75 | good |
| things-mac | procedural | 75 | good |
| goplaces | procedural | 76 | good |
| openai-whisper-api | procedural | 76 | good |
| ordercli | procedural | 76 | good |
| songsee | procedural | 76 | good |
| camsnap | procedural | 77 | good |
| clawhub | procedural | 77 | good |
| spotify-player | procedural | 77 | good |
| xurl | script-backed | 79 | good |
| bear-notes | procedural | 80 | good |
| oracle | procedural | 80 | good |
| peekaboo | procedural | 80 | good |
| taskflow | procedural | 82 | good |
| tmux | procedural | 82 | good |
| apple-notes | procedural | 84 | good |
| blogwatcher | procedural | 84 | good |
| bluebubbles | reference-heavy | 84 | good |
| gifgrep | procedural | 84 | good |
| session-logs | reference-heavy | 84 | good |
| summarize | procedural | 84 | good |
| wacli | procedural | 84 | good |
| skill-creator | reference-heavy | 88 | excellent |
| 1password | script-backed | 90 | excellent |
| apple-reminders | procedural | 90 | excellent |
| github | procedural | 90 | excellent |
| imsg | script-backed | 90 | excellent |
| weather | procedural | 90 | excellent |
| mcporter | reference-heavy | 91 | excellent |
| healthcheck | script-backed | 93 | excellent |
| himalaya | reference-heavy | 97 | excellent |
| model-usage | reference-heavy | 97 | excellent |

## Details

### canvas — 52/100 — script-backed
- Path: `canvas/SKILL.md`
- Rating: **weak**
- Subscores: Trigger 1/35, Execution 20/30, Context 16/20, Reliability 15/15
- Findings:
  - **critical** `missing_description`: Missing description in frontmatter.
  - **critical** `missing_frontmatter`: Missing YAML frontmatter.
  - **critical** `missing_name`: Missing skill name in frontmatter.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `examples_thin`: Script-backed skill should show at least one invocation example.

### blucli — 57/100 — procedural
- Path: `blucli/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 3/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### eightctl — 57/100 — procedural
- Path: `eightctl/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 3/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### video-frames — 57/100 — procedural
- Path: `video-frames/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 3/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### gemini — 64/100 — procedural
- Path: `gemini/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 10/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### nano-pdf — 64/100 — procedural
- Path: `nano-pdf/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 10/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### openai-whisper — 64/100 — procedural
- Path: `openai-whisper/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 10/30, Context 20/20, Reliability 9/15
- Findings:
  - **critical** `missing_actionability`: Procedural skill lacks enough actionable guidance.
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### gh-issues — 69/100 — procedural
- Path: `gh-issues/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 35/35, Execution 22/30, Context 5/20, Reliability 7/15
- Findings:
  - **major** `skill_too_long`: SKILL.md is very long and likely needs progressive disclosure.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `reference_material_embedded`: Detailed reference material may belong in references/.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### voice-call — 69/100 — procedural
- Path: `voice-call/SKILL.md`
- Rating: **borderline**
- Subscores: Trigger 25/35, Execution 15/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### discord — 70/100 — procedural
- Path: `discord/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 16/20, Reliability 7/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### coding-agent — 72/100 — procedural
- Path: `coding-agent/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 10/20, Reliability 7/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `reference_material_embedded`: Detailed reference material may belong in references/.
  - **minor** `skill_too_long`: SKILL.md is getting long. Consider moving detail into references/.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### notion — 73/100 — procedural
- Path: `notion/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 15/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### trello — 73/100 — procedural
- Path: `trello/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 15/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### gog — 74/100 — procedural
- Path: `gog/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### obsidian — 74/100 — procedural
- Path: `obsidian/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### sag — 74/100 — procedural
- Path: `sag/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### node-connect — 75/100 — procedural
- Path: `node-connect/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### openhue — 75/100 — procedural
- Path: `openhue/SKILL.md`
- Rating: **good**
- Subscores: Trigger 27/35, Execution 15/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### sherpa-onnx-tts — 75/100 — procedural
- Path: `sherpa-onnx-tts/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 15/30, Context 20/20, Reliability 15/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### slack — 75/100 — procedural
- Path: `slack/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### sonoscli — 75/100 — procedural
- Path: `sonoscli/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### taskflow-inbox-triage — 75/100 — procedural
- Path: `taskflow-inbox-triage/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### things-mac — 75/100 — procedural
- Path: `things-mac/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### goplaces — 76/100 — procedural
- Path: `goplaces/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### openai-whisper-api — 76/100 — procedural
- Path: `openai-whisper-api/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### ordercli — 76/100 — procedural
- Path: `ordercli/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### songsee — 76/100 — procedural
- Path: `songsee/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### camsnap — 77/100 — procedural
- Path: `camsnap/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### clawhub — 77/100 — procedural
- Path: `clawhub/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### spotify-player — 77/100 — procedural
- Path: `spotify-player/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 15/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### xurl — 79/100 — script-backed
- Path: `xurl/SKILL.md`
- Rating: **good**
- Subscores: Trigger 27/35, Execution 27/30, Context 10/20, Reliability 15/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `examples_thin`: Script-backed skill should show at least one invocation example.
  - **minor** `reference_material_embedded`: Detailed reference material may belong in references/.
  - **minor** `skill_too_long`: SKILL.md is getting long. Consider moving detail into references/.

### bear-notes — 80/100 — procedural
- Path: `bear-notes/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### oracle — 80/100 — procedural
- Path: `oracle/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### peekaboo — 80/100 — procedural
- Path: `peekaboo/SKILL.md`
- Rating: **good**
- Subscores: Trigger 25/35, Execution 26/30, Context 16/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### taskflow — 82/100 — procedural
- Path: `taskflow/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### tmux — 82/100 — procedural
- Path: `tmux/SKILL.md`
- Rating: **good**
- Subscores: Trigger 27/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **major** `weak_trigger_cues`: Description lacks clear activation cues.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### apple-notes — 84/100 — procedural
- Path: `apple-notes/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### blogwatcher — 84/100 — procedural
- Path: `blogwatcher/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### bluebubbles — 84/100 — reference-heavy
- Path: `bluebubbles/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.

### gifgrep — 84/100 — procedural
- Path: `gifgrep/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### session-logs — 84/100 — reference-heavy
- Path: `session-logs/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.

### summarize — 84/100 — procedural
- Path: `summarize/SKILL.md`
- Rating: **good**
- Subscores: Trigger 33/35, Execution 22/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.

### wacli — 84/100 — procedural
- Path: `wacli/SKILL.md`
- Rating: **good**
- Subscores: Trigger 35/35, Execution 22/30, Context 20/20, Reliability 7/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### skill-creator — 88/100 — reference-heavy
- Path: `skill-creator/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 27/30, Context 17/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `skill_too_long`: SKILL.md is getting long. Consider moving detail into references/.
  - **minor** `workflow_too_vague`: Body contains vague wording.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.

### 1password — 90/100 — script-backed
- Path: `1password/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 20/30, Context 20/20, Reliability 15/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `examples_thin`: Script-backed skill should show at least one invocation example.

### apple-reminders — 90/100 — procedural
- Path: `apple-reminders/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### github — 90/100 — procedural
- Path: `github/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### imsg — 90/100 — script-backed
- Path: `imsg/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 20/30, Context 20/20, Reliability 15/15
- Findings:
  - **major** `unclear_output`: Skill does not make the expected output clear.
  - **minor** `examples_thin`: Script-backed skill should show at least one invocation example.

### weather — 90/100 — procedural
- Path: `weather/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 22/30, Context 20/20, Reliability 13/15
- Findings:
  - **minor** `edge_cases_thin`: Procedural skill should mention likely edge cases.
  - **minor** `examples_thin`: Procedural skill should include at least one concrete example.
  - **minor** `evals_recommended`: High-risk or reusable skill would benefit from evals.

### mcporter — 91/100 — reference-heavy
- Path: `mcporter/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 33/35, Execution 29/30, Context 20/20, Reliability 9/15
- Findings:
  - **major** `hidden_dependencies`: Skill mentions external dependencies but does not surface them clearly.
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.

### healthcheck — 93/100 — script-backed
- Path: `healthcheck/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 35/35, Execution 27/30, Context 16/20, Reliability 15/15
- Findings:
  - **minor** `missing_progressive_disclosure`: Large skill does not use references/ or scripts/.
  - **minor** `examples_thin`: Script-backed skill should show at least one invocation example.

### himalaya — 97/100 — reference-heavy
- Path: `himalaya/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 33/35, Execution 29/30, Context 20/20, Reliability 15/15
- Findings:
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.

### model-usage — 97/100 — reference-heavy
- Path: `model-usage/SKILL.md`
- Rating: **excellent**
- Subscores: Trigger 33/35, Execution 29/30, Context 20/20, Reliability 15/15
- Findings:
  - **minor** `scope_ambiguity`: Skill boundaries are not explicit.
  - **info** `examples_thin`: A reference-heavy skill would benefit from one concrete usage example.
