#!/usr/bin/env python3
"""NotebookLM → OpenClaw daily note-delta sync.

Runs once per day (via systemd timer). Compares the current set of notes
across all NotebookLM notebooks with the inventory from the previous run,
then writes:

  - notes/<notebook_id>/<note_id>.md           current content per note
  - changes/YYYY-MM-DD.md                      daily delta (only if non-empty)
  - _state/inventory.json                      persisted inventory (id → hash)
  - _state/errors.log                          append-only failure log

First run is a silent seed (no changes file).

See docs/notebooklm-sync-v2-design.md for the full design.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import traceback
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from notebooklm import NotebookLMClient
from notebooklm.exceptions import AuthError

CONFIG_PATH = Path("/root/.openclaw/bin/nblm_sync.config.json")


# ---------- configuration ---------------------------------------------------


@dataclass
class Config:
    storage_path: Path
    memory_root: Path
    timezone: str
    telegram_bot_token_env: str
    telegram_chat_id: str

    @classmethod
    def load(cls, path: Path) -> "Config":
        data = json.loads(path.read_text())
        return cls(
            storage_path=Path(data["storage_path"]),
            memory_root=Path(data["memory_root"]),
            timezone=data.get("timezone", "America/Sao_Paulo"),
            telegram_bot_token_env=data.get("telegram_bot_token_env", "TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=str(data["telegram_chat_id"]),
        )


# ---------- inventory -------------------------------------------------------


@dataclass
class NoteRecord:
    title: str
    content_hash: str
    notebook_title: str
    last_seen: str  # ISO 8601 in config timezone


def load_inventory(path: Path) -> dict[str, dict[str, NoteRecord]]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return {
        nb_id: {n_id: NoteRecord(**rec) for n_id, rec in notes.items()}
        for nb_id, notes in raw.items()
    }


def save_inventory(path: Path, inv: dict[str, dict[str, NoteRecord]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialisable = {
        nb_id: {n_id: rec.__dict__ for n_id, rec in notes.items()}
        for nb_id, notes in inv.items()
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(serialisable, indent=2, ensure_ascii=False, sort_keys=True))
    os.replace(tmp, path)


# ---------- fetch -----------------------------------------------------------


@dataclass
class NoteSnapshot:
    note_id: str
    notebook_id: str
    notebook_title: str
    title: str
    content: str
    content_hash: str


async def fetch_current_state(client: NotebookLMClient) -> dict[str, dict[str, NoteSnapshot]]:
    """Return {notebook_id → {note_id → NoteSnapshot}} for every note today."""
    out: dict[str, dict[str, NoteSnapshot]] = {}
    notebooks = await client.notebooks.list()
    for nb in notebooks:
        notes = await client.notes.list(nb.id)
        by_id: dict[str, NoteSnapshot] = {}
        for note in notes:
            content = note.content or ""
            by_id[note.id] = NoteSnapshot(
                note_id=note.id,
                notebook_id=nb.id,
                notebook_title=nb.title or "(sem título)",
                title=note.title or "(sem título)",
                content=content,
                content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            )
        out[nb.id] = by_id
    return out


# ---------- diff ------------------------------------------------------------


@dataclass
class DiffEntry:
    notebook_id: str
    notebook_title: str
    note_id: str
    title: str
    old_title: str | None = None  # populated only for renames


@dataclass
class Diff:
    added: list[DiffEntry] = field(default_factory=list)
    edited: list[DiffEntry] = field(default_factory=list)
    removed: list[DiffEntry] = field(default_factory=list)
    renamed: list[DiffEntry] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.added or self.edited or self.removed or self.renamed)


def compute_diff(
    prev: dict[str, dict[str, NoteRecord]],
    curr: dict[str, dict[str, NoteSnapshot]],
) -> Diff:
    diff = Diff()

    # Added / edited / renamed — iterate current state
    for nb_id, notes in curr.items():
        prev_notes = prev.get(nb_id, {})
        for note_id, snap in notes.items():
            prev_rec = prev_notes.get(note_id)
            entry = DiffEntry(
                notebook_id=nb_id,
                notebook_title=snap.notebook_title,
                note_id=note_id,
                title=snap.title,
            )
            if prev_rec is None:
                diff.added.append(entry)
            elif prev_rec.content_hash != snap.content_hash:
                diff.edited.append(entry)
            elif prev_rec.title != snap.title:
                entry.old_title = prev_rec.title
                diff.renamed.append(entry)

    # Removed — in prev but not in curr
    for nb_id, prev_notes in prev.items():
        curr_notes = curr.get(nb_id, {})
        for note_id, prev_rec in prev_notes.items():
            if note_id not in curr_notes:
                diff.removed.append(
                    DiffEntry(
                        notebook_id=nb_id,
                        notebook_title=prev_rec.notebook_title,
                        note_id=note_id,
                        title=prev_rec.title,
                    )
                )

    return diff


# ---------- writes ----------------------------------------------------------


def note_path(memory_root: Path, notebook_id: str, note_id: str) -> Path:
    return memory_root / "notes" / notebook_id / f"{note_id}.md"


def write_note_file(memory_root: Path, snap: NoteSnapshot, now_iso: str) -> None:
    path = note_path(memory_root, snap.notebook_id, snap.note_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = (
        "---\n"
        f"notebook_id: {snap.notebook_id}\n"
        f"notebook_title: {json.dumps(snap.notebook_title, ensure_ascii=False)}\n"
        f"note_id: {snap.note_id}\n"
        f"title: {json.dumps(snap.title, ensure_ascii=False)}\n"
        f"content_hash: {snap.content_hash}\n"
        f"updated_at_sync: {now_iso}\n"
        "---\n\n"
    )
    path.write_text(frontmatter + (snap.content or ""))


def remove_note_file(memory_root: Path, notebook_id: str, note_id: str) -> None:
    path = note_path(memory_root, notebook_id, note_id)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _fmt_entry(e: DiffEntry) -> str:
    nb_short = e.notebook_id[:8]
    n_short = e.note_id[:8]
    rel = f"../notes/{e.notebook_id}/{e.note_id}.md"
    if e.old_title and e.old_title != e.title:
        return f'- `{nb_short}/{n_short}` — "{e.old_title}" → "{e.title}" (notebook: "{e.notebook_title}") — [[{rel}]]'
    return f'- `{nb_short}/{n_short}` — "{e.title}" (notebook: "{e.notebook_title}") — [[{rel}]]'


def write_changes_file(memory_root: Path, day_label: str, diff: Diff) -> Path:
    path = memory_root / "changes" / f"{day_label}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# NotebookLM deltas — {day_label}", ""]
    if diff.added:
        lines += ["## Novas", *[_fmt_entry(e) for e in diff.added], ""]
    if diff.edited:
        lines += ["## Editadas", *[_fmt_entry(e) for e in diff.edited], ""]
    if diff.removed:
        lines += ["## Removidas", *[_fmt_entry(e) for e in diff.removed], ""]
    if diff.renamed:
        lines += ["## Renomeadas", *[_fmt_entry(e) for e in diff.renamed], ""]
    path.write_text("\n".join(lines))
    return path


# ---------- notifications ---------------------------------------------------


def notify_telegram(cfg: Config, message: str) -> None:
    """Best-effort Telegram notification. Never raises."""
    token = os.environ.get(cfg.telegram_bot_token_env, "").strip()
    if not token:
        return
    try:
        data = urllib.parse.urlencode(
            {"chat_id": cfg.telegram_chat_id, "text": message, "disable_web_page_preview": "true"}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except Exception:
        pass  # swallow — never mask the root cause


def append_error_log(memory_root: Path, message: str) -> None:
    path = memory_root / "_state" / "errors.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now(ZoneInfo('UTC')).isoformat()}Z] {message}\n")


# ---------- orchestration ---------------------------------------------------


def records_from_snapshots(
    curr: dict[str, dict[str, NoteSnapshot]], now_iso: str
) -> dict[str, dict[str, NoteRecord]]:
    return {
        nb_id: {
            note_id: NoteRecord(
                title=snap.title,
                content_hash=snap.content_hash,
                notebook_title=snap.notebook_title,
                last_seen=now_iso,
            )
            for note_id, snap in notes.items()
        }
        for nb_id, notes in curr.items()
    }


async def run(cfg: Config, dry_run: bool = False) -> int:
    tz = ZoneInfo(cfg.timezone)
    now = datetime.now(tz)
    now_iso = now.isoformat()
    day_label = now.date().isoformat()

    inventory_path = cfg.memory_root / "_state" / "inventory.json"
    cfg.memory_root.mkdir(parents=True, exist_ok=True)

    prev = load_inventory(inventory_path)
    is_first_run = not prev

    try:
        async with await NotebookLMClient.from_storage(str(cfg.storage_path)) as client:
            curr = await fetch_current_state(client)
    except AuthError as e:
        msg = f"NotebookLM sync: sessão expirada, rodar login. ({e})"
        append_error_log(cfg.memory_root, msg)
        notify_telegram(cfg, msg)
        return 1

    diff = compute_diff(prev, curr)

    total_notes = sum(len(n) for n in curr.values())
    print(
        f"[*] notebooks={len(curr)} notes_total={total_notes} "
        f"added={len(diff.added)} edited={len(diff.edited)} "
        f"removed={len(diff.removed)} renamed={len(diff.renamed)} "
        f"first_run={is_first_run} dry_run={dry_run}"
    )

    if dry_run:
        return 0

    # Writes — order matters: notes first, then changes file, then inventory
    if is_first_run:
        for nb_id, notes in curr.items():
            for snap in notes.values():
                write_note_file(cfg.memory_root, snap, now_iso)
    else:
        touched_ids = {(e.notebook_id, e.note_id) for e in (diff.added + diff.edited + diff.renamed)}
        for nb_id, note_id in touched_ids:
            snap = curr[nb_id][note_id]
            write_note_file(cfg.memory_root, snap, now_iso)
        for e in diff.removed:
            remove_note_file(cfg.memory_root, e.notebook_id, e.note_id)
        if not diff.is_empty():
            written = write_changes_file(cfg.memory_root, day_label, diff)
            print(f"[+] wrote {written}")

    save_inventory(inventory_path, records_from_snapshots(curr, now_iso))
    return 0


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    try:
        cfg = Config.load(CONFIG_PATH)
    except Exception as e:
        sys.stderr.write(f"config load failed: {e}\n")
        return 3

    try:
        return asyncio.run(run(cfg, dry_run=dry_run))
    except Exception:
        tb = traceback.format_exc()
        append_error_log(cfg.memory_root, f"unhandled exception:\n{tb}")
        first_line = tb.strip().splitlines()[-1] if tb.strip() else "unknown"
        notify_telegram(cfg, f"NotebookLM sync falhou: {first_line}")
        sys.stderr.write(tb)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
