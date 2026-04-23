#!/usr/bin/env python3
"""
OpenClaw Skill Audit v1

Weighted audit for OpenClaw-compatible skills.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

VAGUE_PATTERNS = [
    r"\bhandle appropriately\b",
    r"\bformat nicely\b",
    r"\bas needed\b",
    r"\bwhen relevant\b",
    r"\bif it makes sense\b",
    r"\bquando relevante\b",
    r"\bse fizer sentido\b",
    r"\bapropriadamente\b",
    r"\badequadamente\b",
    r"\bde forma apropriada\b",
    r"\bconforme necess[aá]rio\b",
]

SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"ghp_[a-zA-Z0-9]{20,}",
    r"gho_[a-zA-Z0-9]{20,}",
    r"xoxb-[a-zA-Z0-9-]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z_-]{35}",
    r"(?:anthropic|openai)[_-]?api[_-]?key\s*[=:]\s*['\"][a-zA-Z0-9-]{20,}['\"]",
]

GENERIC_DESCRIPTION_PATTERNS = [
    r"\bhelps? with many tasks\b",
    r"\bhandles? various tasks\b",
    r"\bdoes many things\b",
    r"\bgeneral purpose\b",
    r"\bassist(?:s)? with.*various\b",
]

TRIGGER_HINT_PATTERNS = [
    r'"[^"]{3,80}"',
    r"'[^']{3,80}'",
    r"/[a-z][a-z0-9-]{2,}",
    r"\buse when\b",
    r"\bwhen the user\b",
    r"\bativa quando\b",
    r"\buse quando\b",
]


def word_count(text):
    return len(re.findall(r"\b\w+\b", text or ""))


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None, text
    fm_raw = m.group(1)
    body = text[m.end():]
    fm = {}
    current_key = None
    current_val = []
    multiline = False
    for line in fm_raw.split("\n"):
        if multiline:
            if line.startswith("  ") or line.strip() == "":
                current_val.append(line.strip())
                continue
            fm[current_key] = " ".join(current_val).strip()
            multiline = False
            current_val = []
        m2 = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", line)
        if m2:
            key, val = m2.group(1), m2.group(2).strip()
            if val in {">", "|"}:
                current_key = key
                multiline = True
                current_val = []
            else:
                fm[key] = val.strip("\"'")
    if multiline and current_val:
        fm[current_key] = " ".join(current_val).strip()
    return fm, body


def extract_sections(body):
    sections = {}
    current = "_pre"
    current_lines = []
    in_fence = False
    fence_re = re.compile(r"^(?:```|~~~)")
    h2_re = re.compile(r"^##\s+(.+?)\s*$")
    for line in body.split("\n"):
        if fence_re.match(line):
            in_fence = not in_fence
            current_lines.append(line)
            continue
        if not in_fence:
            m = h2_re.match(line)
            if m:
                sections[current] = "\n".join(current_lines)
                current = m.group(1).strip().lower()
                current_lines = []
                continue
        current_lines.append(line)
    sections[current] = "\n".join(current_lines)
    return sections


def find_section(sections, *names):
    for name in names:
        needle = name.lower()
        for k, v in sections.items():
            if needle in k:
                return v
    return None


def count_examples(sections):
    sec = find_section(sections, "examples", "exemplos")
    if not sec:
        return 0
    return len(re.findall(r"^###\s+", sec, re.MULTILINE))


def count_edge_cases(sections):
    total = 0
    for name in ["edge cases", "edge case", "errors & recovery", "errors", "fallback"]:
        sec = find_section(sections, name)
        if not sec:
            continue
        total += len(re.findall(r"^\s*[-*]\s+\S", sec, re.MULTILINE))
        table_rows = 0
        in_table = False
        for line in sec.split("\n"):
            if re.match(r"^\s*\|.+\|\s*$", line):
                if re.match(r"^\s*\|[\s:|-]+\|\s*$", line):
                    in_table = True
                    continue
                if in_table:
                    table_rows += 1
            else:
                in_table = False
        total += table_rows
    return total


def detect_type(text, sections, skill_dir):
    lower = text.lower()
    has_workflow = bool(find_section(sections, "workflow", "passos"))
    has_many_commands = len(re.findall(r"^```(?:bash|sh|python)?", text, re.MULTILINE)) >= 2
    if (skill_dir / "scripts").exists() or (has_workflow and ("script" in lower or "comando" in lower or "command" in lower)):
        return "script-backed"
    if (skill_dir / "references").exists() or (("reference" in lower or "schema" in lower or "policy" in lower) and not has_workflow):
        return "reference-heavy"
    if has_many_commands and not has_workflow:
        return "script-backed"
    return "procedural"


def resolve_internal_refs(skill_path, body):
    placeholder_refs = {"link", "url", "path", "nome", "file", "href", "target", "dir", "folder"}
    body_no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body_no_code = re.sub(r"`[^`\n]+`", "", body_no_code)
    broken = []
    for m in re.finditer(r"\]\(([^)]+)\)", body_no_code):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if target.lower() in placeholder_refs:
            continue
        target_clean = target.split("#")[0]
        if not target_clean:
            continue
        p = Path(target_clean) if target_clean.startswith("/") else (skill_path.parent / target_clean).resolve()
        if not p.exists():
            broken.append(target)
    return broken


def has_trigger_hints(desc):
    hits = 0
    for p in TRIGGER_HINT_PATTERNS:
        if re.search(p, desc, re.IGNORECASE):
            hits += 1
    return hits


def is_generic_description(desc):
    if word_count(desc) < 8:
        return True
    return any(re.search(p, desc, re.IGNORECASE) for p in GENERIC_DESCRIPTION_PATTERNS)


def has_hidden_dependencies(text, sections):
    lower = text.lower()
    mentions_external = any(x in lower for x in ["api", "env var", "environment variable", "token", "credential", "credentials", "mcp", "requires", "prerequisite", "prerequisites", "install"])
    surfaced_sections = [
        find_section(sections, "dependencies", "dependências"),
        find_section(sections, "prerequisites", "prerequisite", "requirements", "setup", "configuration", "configuração"),
        find_section(sections, "references", "reference"),
        find_section(sections, "commands", "command", "usage"),
    ]
    surfaced = any(sec and word_count(sec) >= 8 for sec in surfaced_sections)
    if mentions_external and not surfaced:
        return True
    return False


def analyze_skill(skill_path, root=None):
    rel = str(skill_path.relative_to(root)) if root else str(skill_path)
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    sections = extract_sections(body)
    skill_dir = skill_path.parent
    skill_type = detect_type(text, sections, skill_dir)
    lines = len(text.splitlines())

    findings = []
    scores = {
        "trigger": 35,
        "execution": 30,
        "context": 20,
        "reliability": 15,
    }

    def add(code, severity, message, category, penalty):
        findings.append({
            "code": code,
            "severity": severity,
            "message": message,
            "category": category,
            "penalty": penalty,
        })
        scores[category] = max(0, scores[category] - penalty)

    name = (fm or {}).get("name", "").strip()
    desc = (fm or {}).get("description", "").strip()

    if not fm:
        add("missing_frontmatter", "critical", "Missing YAML frontmatter.", "trigger", 12)
    if not name:
        add("missing_name", "critical", "Missing skill name in frontmatter.", "trigger", 10)
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        add("invalid_name", "major", "Skill name should use kebab-case.", "trigger", 7)
    elif name != skill_dir.name:
        add("name_folder_mismatch", "minor", "Skill name does not match folder name.", "trigger", 3)

    if not desc:
        add("missing_description", "critical", "Missing description in frontmatter.", "trigger", 12)
    else:
        if is_generic_description(desc):
            add("generic_description", "major", "Description is too generic to trigger reliably.", "trigger", 10)
        trigger_hints = has_trigger_hints(desc)
        if trigger_hints == 0:
            add("weak_trigger_cues", "major", "Description lacks clear activation cues.", "trigger", 8)
        ambiguity_risk = skill_type == "procedural" and (bool(find_section(sections, "when to use")) or word_count(body) > 120)
        if ambiguity_risk and not re.search(r"not use|n[aã]o use|when not|confus|don't use|do not use", (desc + "\n" + body), re.IGNORECASE):
            add("scope_ambiguity", "minor", "Skill boundaries are not explicit.", "trigger", 2)

    workflow = find_section(sections, "workflow", "passos", "step-by-step")
    examples = count_examples(sections)
    edge_cases = count_edge_cases(sections)

    if skill_type == "procedural":
        if not workflow and word_count(body) < 80:
            add("missing_actionability", "critical", "Procedural skill lacks enough actionable guidance.", "execution", 12)
    elif skill_type == "script-backed":
        if not re.search(r"```|python|bash|script", text, re.IGNORECASE) and not (skill_dir / "scripts").exists():
            add("missing_actionability", "major", "Script-backed skill does not clearly expose invocation.", "execution", 9)
    elif skill_type == "reference-heavy":
        if word_count(body) < 40 and not (skill_dir / "references").exists():
            add("missing_actionability", "major", "Reference-heavy skill does not route to supporting material.", "execution", 8)

    vague_hits_workflow = sum(1 for p in VAGUE_PATTERNS if re.search(p, workflow or "", re.IGNORECASE))
    vague_hits_body = sum(1 for p in VAGUE_PATTERNS if re.search(p, body or "", re.IGNORECASE))
    if vague_hits_workflow:
        add("workflow_too_vague", "major", "Workflow contains vague instructions.", "execution", min(10, 3 * vague_hits_workflow))
    elif vague_hits_body:
        add("workflow_too_vague", "minor", "Body contains vague wording.", "execution", 2)

    outputs = find_section(sections, "outputs", "output")
    has_output_clarity = bool(outputs) or bool(re.search(r"output|deliver|retorn|salvar|arquivo|markdown", body, re.IGNORECASE))
    if not has_output_clarity:
        add("unclear_output", "major", "Skill does not make the expected output clear.", "execution", 7)

    body_words = word_count(body)
    if skill_type == "procedural":
        if body_words > 180 and examples == 0:
            add("examples_thin", "minor", "Procedural skill would benefit from at least one concrete example.", "execution", 3)
        if body_words > 220 and edge_cases == 0:
            add("edge_cases_thin", "minor", "Procedural skill should mention likely edge cases when complexity rises.", "execution", 3)
    elif skill_type == "script-backed":
        if body_words > 140 and examples == 0:
            add("examples_thin", "minor", "Script-backed skill should show at least one invocation example.", "execution", 2)
    else:
        if examples == 0 and body_words > 180:
            add("examples_thin", "info", "A reference-heavy skill would benefit from one concrete usage example.", "execution", 1)

    if re.search(r"same as above|as discussed|the usual process|known setup", body, re.IGNORECASE):
        add("hidden_author_context", "major", "Skill appears to depend on unstated author context.", "execution", 8)

    if lines > 500:
        add("skill_too_long", "major", "SKILL.md is very long and likely needs progressive disclosure.", "context", 8)
    elif lines > 300:
        add("skill_too_long", "minor", "SKILL.md is getting long. Consider moving detail into references/.", "context", 3)

    has_references = (skill_dir / "references").exists()
    has_scripts = (skill_dir / "scripts").exists()
    if lines > 180 and not (has_references or has_scripts):
        add("missing_progressive_disclosure", "minor", "Large skill does not use references/ or scripts/.", "context", 4)

    overview = body[:1000].lower()
    if desc and desc.lower()[:120] in overview:
        add("duplicated_guidance", "info", "Description appears to be duplicated in the body.", "context", 1)

    if lines > 250 and re.search(r"\|.+\|", body) and not has_references:
        add("reference_material_embedded", "minor", "Detailed reference material may belong in references/.", "context", 3)

    secret_hits = sum(1 for p in SECRET_PATTERNS if re.search(p, text))
    if secret_hits:
        add("hardcoded_secret", "critical", "Hardcoded credentials or tokens detected.", "reliability", 15)

    broken_refs = resolve_internal_refs(skill_path, body)
    if broken_refs:
        add("broken_refs", "major", f"Broken internal references detected: {len(broken_refs)}.", "reliability", min(10, 3 + len(broken_refs)))

    if has_hidden_dependencies(text, sections):
        add("hidden_dependencies", "major", "Skill mentions external dependencies but does not surface them clearly.", "reliability", 6)

    evals_json = skill_dir / "evals" / "evals.json"
    high_risk = skill_type == "procedural" and ("cron" in text.lower() or edge_cases >= 2 or word_count(body) > 220)
    if high_risk and not evals_json.exists():
        add("evals_recommended", "minor", "High-risk or reusable skill would benefit from evals.", "reliability", 2)

    total = sum(scores.values())
    rating = (
        "excellent" if total >= 85 else
        "good" if total >= 70 else
        "borderline" if total >= 55 else
        "weak"
    )

    findings.sort(key=lambda f: ({"critical":0,"major":1,"minor":2,"info":3}[f["severity"]], -f["penalty"], f["code"]))

    return {
        "path": rel,
        "name": name or skill_dir.name,
        "type": skill_type,
        "score": total,
        "rating": rating,
        "lines": lines,
        "subscores": scores,
        "findings": findings,
        "broken_refs": broken_refs,
        "metrics": {
            "examples": examples,
            "edge_cases": edge_cases,
            "description_words": word_count(desc),
        },
    }


def generate_markdown(results, source_path):
    total = len(results)
    avg = sum(r["score"] for r in results) / total if total else 0
    type_counter = Counter(r["type"] for r in results)
    finding_counter = Counter(f["code"] for r in results for f in r["findings"])

    lines = []
    lines.append("# OpenClaw Skill Audit Report")
    lines.append("")
    lines.append(f"> Source: `{source_path}`")
    lines.append(f"> Total skills: **{total}**")
    lines.append(f"> Average score: **{avg:.1f}/100**")
    lines.append("")
    lines.append("## Skill types")
    lines.append("")
    for skill_type, count in sorted(type_counter.items()):
        lines.append(f"- **{skill_type}**: {count}")
    lines.append("")
    lines.append("## Most common findings")
    lines.append("")
    for code, count in finding_counter.most_common(10):
        lines.append(f"- `{code}`: {count}")
    lines.append("")
    lines.append("## Ranking")
    lines.append("")
    lines.append("| Skill | Type | Score | Rating |")
    lines.append("|---|---|---:|---|")
    for r in sorted(results, key=lambda x: x["score"]):
        lines.append(f"| {r['name']} | {r['type']} | {r['score']} | {r['rating']} |")
    lines.append("")
    lines.append("## Details")
    lines.append("")
    for r in sorted(results, key=lambda x: x["score"]):
        lines.append(f"### {r['name']} — {r['score']}/100 — {r['type']}")
        lines.append(f"- Path: `{r['path']}`")
        lines.append(f"- Rating: **{r['rating']}**")
        lines.append(f"- Subscores: Trigger {r['subscores']['trigger']}/35, Execution {r['subscores']['execution']}/30, Context {r['subscores']['context']}/20, Reliability {r['subscores']['reliability']}/15")
        if r["findings"]:
            lines.append("- Findings:")
            for f in r["findings"][:8]:
                lines.append(f"  - **{f['severity']}** `{f['code']}`: {f['message']}")
        else:
            lines.append("- Findings: none")
        lines.append("")
    return "\n".join(lines)


def collect_skill_files(target):
    if target.is_file():
        return [target] if target.name == "SKILL.md" else []
    return sorted(target.rglob("SKILL.md"))


def main():
    ap = argparse.ArgumentParser(description="Audit OpenClaw-compatible skills with weighted scoring.")
    ap.add_argument("path", help="SKILL.md file or directory")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    ap.add_argument("-o", "--output", default="openclaw-audit-results.md", help="Output file path")
    args = ap.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"ERROR: path not found: {target}", file=sys.stderr)
        sys.exit(1)

    skill_files = collect_skill_files(target)
    if not skill_files:
        print(f"No SKILL.md files found in {target}")
        sys.exit(0)

    root = target if target.is_dir() else target.parent
    results = [analyze_skill(path, root=root) for path in skill_files]

    out = Path(args.output)
    if args.json:
        if out.suffix.lower() != ".json":
            out = out.with_suffix(".json")
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        out.write_text(generate_markdown(results, str(target)), encoding="utf-8")

    avg = sum(r["score"] for r in results) / len(results)
    print(f"openclaw-skill-audit: {len(results)} skill(s) analyzed")
    print(f"  Average score: {avg:.1f}/100")
    print(f"  Output: {out}")


if __name__ == "__main__":
    main()
