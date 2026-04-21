#!/usr/bin/env python3
"""OpenClaw MCP server — read-only bridge for Google Antigravity.

Exposes a curated, read-only view of the OpenClaw workspace so that
Antigravity (running on the user's Windows box, over Tailscale) can
pull project memory, notes, cron state, and the NotebookLM inventory
while drafting reports and day-to-day work.

Transport: streamable HTTP (FastMCP default for networked setups).
Bind:      the tailnet IP only — never the public IPv4.
Auth:      none at v1 (tailnet is private). Bearer token TBD.

See docs/openclaw-mcp-runbook.md for how Antigravity connects.
"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from fastmcp import FastMCP

# ---------- config ---------------------------------------------------------

WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_ROOT = WORKSPACE / "memory"
PROJECTS_ROOT = MEMORY_ROOT / "projects"
CRON_JOBS = Path("/root/.openclaw/cron/jobs.json")
NBLM_INVENTORY = MEMORY_ROOT / "integrations" / "notebooklm" / "_state" / "inventory.json"
NBLM_NOTES_ROOT = MEMORY_ROOT / "integrations" / "notebooklm" / "notes"
NBLM_CHANGES_ROOT = MEMORY_ROOT / "integrations" / "notebooklm" / "changes"

BIND_HOST = os.environ.get("OPENCLAW_MCP_HOST", "100.124.198.120")
BIND_PORT = int(os.environ.get("OPENCLAW_MCP_PORT", "5800"))

MAX_READ_BYTES = 500_000  # cap per read_memory call


mcp = FastMCP(
    name="openclaw",
    instructions=(
        "OpenClaw é a memória operacional do Alê (Mensura/MIA Engenharia). "
        "Use estas ferramentas para ler projetos, memória diária, crons, "
        "e o índice NotebookLM. Todas são read-only. Para relatórios, "
        "comece por list_projects + read_project."
    ),
)


# ---------- helpers --------------------------------------------------------


def _safe_under(root: Path, requested: str) -> Path:
    """Resolve `requested` against `root` and refuse anything escaping it."""
    root = root.resolve()
    # Treat absolute paths that are already inside root as valid; reject others.
    p = Path(requested)
    if p.is_absolute():
        candidate = p.resolve()
    else:
        candidate = (root / p).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError(
            f"path '{requested}' escapes allowed root '{root}'"
        )
    return candidate


def _truncate(text: str, limit: int = MAX_READ_BYTES) -> tuple[str, bool]:
    if len(text.encode("utf-8")) <= limit:
        return text, False
    encoded = text.encode("utf-8")[:limit]
    # Trim to valid UTF-8 boundary
    while encoded and (encoded[-1] & 0xC0) == 0x80:
        encoded = encoded[:-1]
    return encoded.decode("utf-8", errors="replace"), True


# ---------- tools ----------------------------------------------------------


@mcp.tool(
    description=(
        "Lista todos os projetos rastreados em memory/projects/. Use primeiro "
        "para descobrir o nome exato antes de chamar read_project."
    )
)
def list_projects() -> list[dict]:
    if not PROJECTS_ROOT.exists():
        return []
    projects = []
    for entry in sorted(PROJECTS_ROOT.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            projects.append({
                "name": entry.name,
                "kind": "folder",
                "files": sorted(f.name for f in entry.iterdir() if f.is_file()),
            })
        elif entry.is_file() and entry.suffix == ".md":
            projects.append({
                "name": entry.stem,
                "kind": "file",
                "files": [entry.name],
            })
    return projects


@mcp.tool(
    description=(
        "Lê a memória de um projeto específico. `name` é o que list_projects "
        "retornou. Se o projeto for um diretório, concatena os .md na ordem "
        "alfabética. Retorna texto markdown."
    )
)
def read_project(name: str) -> str:
    # Try dir first, then single file
    dir_path = PROJECTS_ROOT / name
    file_path = PROJECTS_ROOT / f"{name}.md"
    parts: list[str] = []
    if dir_path.is_dir():
        dir_path = _safe_under(PROJECTS_ROOT, str(dir_path))
        for md in sorted(dir_path.rglob("*.md")):
            rel = md.relative_to(PROJECTS_ROOT)
            parts.append(f"\n\n<!-- {rel} -->\n\n{md.read_text(errors='replace')}")
    elif file_path.is_file():
        file_path = _safe_under(PROJECTS_ROOT, str(file_path))
        parts.append(file_path.read_text(errors="replace"))
    else:
        raise FileNotFoundError(
            f"no project '{name}' (not a dir or .md in {PROJECTS_ROOT})"
        )
    text, truncated = _truncate("".join(parts))
    if truncated:
        text += "\n\n[truncated at 500 KB]"
    return text


@mcp.tool(
    description=(
        "Lê um arquivo arbitrário da memória do workspace. `path` é relativo "
        "a memory/ (ex.: '2026-04-21.md', 'context/decisions.md'). Restrito "
        "ao diretório memory/. Retorna texto, truncado a 500 KB."
    )
)
def read_memory(path: str) -> str:
    resolved = _safe_under(MEMORY_ROOT, path)
    if not resolved.is_file():
        raise FileNotFoundError(f"not a file: memory/{path}")
    text = resolved.read_text(errors="replace")
    text, truncated = _truncate(text)
    if truncated:
        text += "\n\n[truncated at 500 KB]"
    return text


@mcp.tool(
    description=(
        "Lista arquivos numa pasta da memória. `path` relativo a memory/ "
        "(vazio = raiz da memória). Retorna lista de nomes."
    )
)
def list_memory(path: str = "") -> list[str]:
    resolved = _safe_under(MEMORY_ROOT, path) if path else MEMORY_ROOT
    if not resolved.is_dir():
        raise NotADirectoryError(f"not a directory: memory/{path}")
    return sorted(entry.name for entry in resolved.iterdir() if not entry.name.startswith("."))


@mcp.tool(
    description=(
        "Busca textual (ripgrep) em todo o workspace do OpenClaw. Retorna até "
        "`limit` matches, cada um como {path, line_number, line}. Ótima "
        "primeira ferramenta quando o Alê pede 'acha onde falamos sobre X'."
    )
)
def search_knowledge(query: str, limit: int = 30) -> list[dict]:
    if not query or len(query) > 200:
        raise ValueError("query must be 1..200 chars")
    if not 1 <= limit <= 200:
        raise ValueError("limit must be 1..200")
    try:
        result = subprocess.run(
            [
                "rg", "--no-messages", "--no-heading", "--with-filename",
                "--line-number", "--max-count", "3",
                "--glob", "!.git",
                "--glob", "!node_modules",
                "--glob", "!*.lock",
                "--ignore-case",
                query,
                str(WORKSPACE),
            ],
            capture_output=True, text=True, timeout=15,
        )
    except FileNotFoundError:
        raise RuntimeError("ripgrep (rg) não instalado no servidor")

    matches: list[dict] = []
    for line in result.stdout.splitlines():
        # format: path:lineno:content
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        try:
            lineno = int(parts[1])
        except ValueError:
            continue
        path = Path(parts[0])
        try:
            rel = path.relative_to(WORKSPACE)
        except ValueError:
            rel = path
        matches.append({
            "path": str(rel),
            "line_number": lineno,
            "line": parts[2][:300],
        })
        if len(matches) >= limit:
            break
    return matches


@mcp.tool(
    description=(
        "Lista os cron jobs agendados no OpenClaw com seus nomes, schedule "
        "(cron expression + timezone), status, e última execução. Útil "
        "pra saber o que a infra está fazendo."
    )
)
def list_crons() -> list[dict]:
    if not CRON_JOBS.exists():
        return []
    data = json.loads(CRON_JOBS.read_text())
    out = []
    for job in data.get("jobs", []):
        sched = job.get("schedule", {})
        state = job.get("state", {})
        out.append({
            "name": job.get("name", "(sem nome)"),
            "enabled": job.get("enabled", False),
            "schedule": f'{sched.get("expr","?")} @ {sched.get("tz","?")}',
            "last_status": state.get("lastStatus", "n/a"),
            "last_duration_ms": state.get("lastDurationMs"),
            "consecutive_errors": state.get("consecutiveErrors", 0),
            "id": job.get("id", ""),
        })
    return out


@mcp.tool(
    description=(
        "Lê o inventário do NotebookLM daily sync: lista de notebooks e "
        "quantas notas cada um tem, com títulos das notas. Use antes de "
        "mergulhar em uma nota específica via read_memory."
    )
)
def notebooklm_inventory() -> list[dict]:
    if not NBLM_INVENTORY.exists():
        return []
    inv = json.loads(NBLM_INVENTORY.read_text())
    out = []
    for nb_id, notes in inv.items():
        title = None
        note_list = []
        for note_id, rec in notes.items():
            if title is None:
                title = rec.get("notebook_title")
            note_list.append({
                "note_id": note_id,
                "title": rec.get("title"),
                "content_hash": rec.get("content_hash", "")[:16],
            })
        out.append({
            "notebook_id": nb_id,
            "notebook_title": title,
            "note_count": len(note_list),
            "notes": note_list,
        })
    return sorted(out, key=lambda x: (-x["note_count"], x["notebook_title"] or ""))


@mcp.tool(
    description=(
        "Lê uma nota específica do NotebookLM sync (pelo note_id completo). "
        "Use notebooklm_inventory primeiro para descobrir o ID."
    )
)
def notebooklm_read_note(notebook_id: str, note_id: str) -> str:
    # path: notes/<notebook_id>/<note_id>.md — both components come from inventory
    rel = f"integrations/notebooklm/notes/{notebook_id}/{note_id}.md"
    return read_memory.fn(rel)  # reuse guarded reader


# ---------- entry ----------------------------------------------------------


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=BIND_HOST,
        port=BIND_PORT,
        path="/mcp",
        stateless_http=True,
        json_response=True,
    )
