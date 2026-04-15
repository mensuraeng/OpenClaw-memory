#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, UTC
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
INBOX = MEMORY / "inbox"
CONSOLIDATION = MEMORY / "consolidation"
AGENTS = ["main", "mensura", "mia", "pcs", "finance"]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_text(path: Path, text: str) -> None:
    ensure_parent(path)
    with path.open("a", encoding="utf-8") as f:
        if path.exists() and path.stat().st_size > 0:
            f.write("\n")
        f.write(text.rstrip() + "\n")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def count_events(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            total += 1
    return total


def consolidate_for_day(day: str) -> int:
    day_dir = INBOX / day
    if not day_dir.exists():
        print(f"No inbox for {day}")
        return 0

    out_dir = CONSOLIDATION / day
    out_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    promoted = 0
    rows = []

    for agent in AGENTS:
        notes_path = day_dir / agent / "notes.md"
        events_path = day_dir / agent / "events.jsonl"
        notes = read_text(notes_path)
        events_count = count_events(events_path)
        summary_path = out_dir / f"{agent}-summary.md"

        body = [f"# {agent} — consolidação {day}", "", f"Gerado em {generated_at}.", ""]
        body.append(f"- eventos capturados: {events_count}")
        body.append(f"- notas presentes: {'sim' if notes else 'não'}")
        body.append("")
        body.append("## Material bruto")
        body.append("")
        body.append(notes if notes else "Sem notas relevantes registradas no inbox.")
        summary_path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")

        if notes or events_count:
            promoted += 1
        rows.append(f"- {agent}: eventos={events_count}, notas={'sim' if notes else 'não'}, resumo={summary_path.name}")

    master_summary = out_dir / "summary.md"
    payload = [
        f"# Consolidação noturna — {day}",
        "",
        f"Gerado em {generated_at}.",
        "",
        "## Agentes processados",
        "",
        *rows,
        "",
        "## Próximo passo",
        "",
        "Revisar os resumos por agente e promover decisões, lições, pendências e contexto de projeto para a memória institucional compartilhada.",
    ]
    master_summary.write_text("\n".join(payload).rstrip() + "\n", encoding="utf-8")
    print(json.dumps({"day": day, "processed_agents": len(AGENTS), "agents_with_material": promoted, "summary": str(master_summary)}))
    return 0


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    raise SystemExit(consolidate_for_day(day))
