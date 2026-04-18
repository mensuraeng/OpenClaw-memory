#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTITUTIONAL = ROOT / "memory" / "institutional"


def tail_blocks(path: Path, limit: int = 5) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []
    blocks = [block.strip() for block in text.split("\n\n") if block.strip() and not block.startswith("#") and not block.startswith("_")]
    return blocks[-limit:]


def main() -> int:
    decisions = tail_blocks(INSTITUTIONAL / "decisions.md", 3)
    pending = tail_blocks(INSTITUTIONAL / "pending.md", 5)
    lessons = tail_blocks(INSTITUTIONAL / "lessons.md", 3)
    projects = tail_blocks(INSTITUTIONAL / "projects.md", 5)

    lines = ["MEMÓRIA EXECUTIVA", ""]
    lines.append("DECISÕES RECENTES")
    lines.extend(decisions or ["- sem decisões registradas"]) 
    lines.append("")
    lines.append("PENDÊNCIAS RELEVANTES")
    lines.extend(pending or ["- sem pendências registradas"]) 
    lines.append("")
    lines.append("LIÇÕES")
    lines.extend(lessons or ["- sem lições registradas"]) 
    lines.append("")
    lines.append("MOVIMENTOS / PROJETOS")
    lines.extend(projects or ["- sem movimentos registrados"]) 

    print("\n".join(lines).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
