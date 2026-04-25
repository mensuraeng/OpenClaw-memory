#!/usr/bin/env python3
"""
notion_sync.py — Notion → 2nd-brain sync

Usage:
  python notion_sync.py                         # delta (default)
  python notion_sync.py --full                  # full sync (metadata only, no block content)
  python notion_sync.py --full --content        # full sync with block content (slow)
  python notion_sync.py --workspace pcs         # single workspace
  python notion_sync.py --dry-run               # simulate without writing
  python notion_sync.py --max-pages 100         # limit pages per workspace per run

Strategy:
  - Delta (default):  only pages edited since last sync, fetches full block content
  - Full (--full):    all pages, metadata only — builds the index fast
  - Full + --content: all pages with content — slow, for first-time rich sync
  - State saved per workspace, so a crash doesn't restart everything
  - git commit+push per workspace (not monolithic at the end)
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from slugify import slugify

# --- Paths ---
WORKSPACE_DIR = Path("/root/.openclaw/workspace")
SECOND_BRAIN = Path("/root/2nd-brain")
CREDENTIALS = WORKSPACE_DIR / "memory/context/credentials.md"
STATE_FILE = SECOND_BRAIN / "03-knowledge/notion/_state/last_sync.json"
LOG_DIR = WORKSPACE_DIR / "logs/cron"
REPORT_FILE = WORKSPACE_DIR / "logs/notion-sync-report.md"

# --- Notion API ---
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

TOKENS = {
    "mensura": "NOTION_TOKEN_REDACTED",
    "mia":     "NOTION_TOKEN_REDACTED",
    "pcs":     "NOTION_TOKEN_REDACTED",
}

# --- Limits ---
MAX_PAGES_PER_RUN = 200   # per workspace — prevents runaway full syncs
REQUEST_TIMEOUT = 10       # seconds per API call
RATE_LIMIT_SLEEP = 0.35   # seconds between API calls (≈170 req/min, well below 3/s limit)
MAX_BLOCK_DEPTH = 3        # max recursion depth for block children

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger("notion_sync")


# ── API helpers ─────────────────────────────────────────────────────────────

def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _get(url: str, token: str) -> dict:
    time.sleep(RATE_LIMIT_SLEEP)
    r = requests.get(url, headers=_headers(token), timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _post(url: str, token: str, body: dict, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        time.sleep(RATE_LIMIT_SLEEP)
        r = requests.post(url, headers=_headers(token), json=body, timeout=REQUEST_TIMEOUT)
        if r.status_code == 429 and attempt < max_retries - 1:
            wait = 2 ** (attempt + 1)
            log.warning(f"Rate limited, retrying in {wait}s…")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Max retries exceeded after 429s")


# ── State ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            log.warning("Corrupt state file — resetting")
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# ── Helpers ──────────────────────────────────────────────────────────────────

def _slug(title: str, notion_id: str) -> str:
    # Use full UUID (36 chars) to guarantee uniqueness across all database rows
    s = slugify(title, max_length=50, separator="-") if title else ""
    return f"{notion_id}-{s}" if s else notion_id


def _plain(rich_text: list) -> str:
    return "".join(rt.get("plain_text", "") for rt in (rich_text or []))


def _page_title(page: dict) -> str:
    props = page.get("properties", {})
    for key in ("title", "Title", "Name", "name"):
        if key in props:
            rt = props[key].get("title", [])
            t = _plain(rt)
            if t:
                return t
    for prop in props.values():
        if prop.get("type") == "title":
            t = _plain(prop.get("title", []))
            if t:
                return t
    return ""


# ── Block → Markdown ─────────────────────────────────────────────────────────

def _block_text(block: dict) -> str:
    btype = block.get("type", "")
    data = block.get(btype, {})
    return _plain(data.get("rich_text", []))


def blocks_to_md(blocks: list, depth: int = 0) -> str:
    lines = []
    ind = "  " * depth

    for b in blocks:
        btype = b.get("type", "")
        data = b.get(btype, {})
        text = _plain(data.get("rich_text", []))
        children_md = blocks_to_md(b.get("_children", []), depth + 1) if b.get("_children") else ""

        if btype == "paragraph":
            lines.append(f"{ind}{text}" if text else "")
        elif btype == "heading_1":
            lines.append(f"\n{ind}# {text}")
        elif btype == "heading_2":
            lines.append(f"\n{ind}## {text}")
        elif btype == "heading_3":
            lines.append(f"\n{ind}### {text}")
        elif btype == "bulleted_list_item":
            lines.append(f"{ind}- {text}")
        elif btype == "numbered_list_item":
            lines.append(f"{ind}1. {text}")
        elif btype == "to_do":
            check = "x" if data.get("checked") else " "
            lines.append(f"{ind}- [{check}] {text}")
        elif btype == "toggle":
            lines.append(f"{ind}<details><summary>{text}</summary>")
            if children_md:
                lines.append(children_md)
            lines.append(f"{ind}</details>")
            children_md = ""
        elif btype == "code":
            lang = data.get("language", "")
            lines.append(f"{ind}```{lang}\n{text}\n{ind}```")
        elif btype == "quote":
            lines.append(f"{ind}> {text}")
        elif btype == "callout":
            icon = (data.get("icon") or {}).get("emoji", "")
            lines.append(f"{ind}> {icon} {text}")
        elif btype == "divider":
            lines.append(f"{ind}---")
        elif btype == "image":
            src = (data.get("file") or data.get("external") or {}).get("url", "")
            cap = _plain(data.get("caption", []))
            lines.append(f"{ind}![{cap}]({src})")
        elif btype in ("child_page", "child_database"):
            lines.append(f"{ind}→ {data.get('title', '[subpage]')}")
        elif btype == "table_of_contents":
            lines.append(f"{ind}[TOC]")
        elif btype == "column_list":
            pass  # children handled below
        elif btype == "column":
            pass  # children handled below
        # unknown/unsupported: skip

        if children_md and btype != "toggle":
            lines.append(children_md)

    return "\n".join(lines)


def fetch_blocks(block_id: str, token: str, depth: int = 0) -> list:
    """Recursively fetch block children (capped at MAX_BLOCK_DEPTH)."""
    if depth >= MAX_BLOCK_DEPTH:
        return []
    try:
        data = _get(f"{NOTION_API}/blocks/{block_id}/children?page_size=100", token)
        blocks = data.get("results", [])
        for b in blocks:
            if b.get("has_children"):
                b["_children"] = fetch_blocks(b["id"], token, depth + 1)
        return blocks
    except Exception as e:
        log.warning(f"  blocks {block_id[:8]}: {e}")
        return []


# ── Converters ───────────────────────────────────────────────────────────────

def page_to_md(page: dict, token: str, workspace: str, fetch_content: bool) -> str:
    notion_id = page["id"]
    title = _page_title(page)
    last_edited = page.get("last_edited_time", "")
    url = page.get("url", "")

    content = ""
    if fetch_content:
        blocks = fetch_blocks(notion_id, token)
        content = blocks_to_md(blocks)

    return "\n".join(filter(None, [
        "---",
        f"notion_id: {notion_id}",
        f"title: {title or 'Untitled'}",
        "type: page",
        f"workspace: {workspace}",
        f"last_edited: {last_edited}",
        f"url: {url}",
        "---",
        "",
        f"# {title or 'Untitled'}",
        "",
        content if content else "_[conteúdo pendente — rodar com --content para sincronizar]_",
    ]))


def _prop_val(prop: dict) -> str:
    """Extract a display string from a Notion property."""
    ptype = prop.get("type", "")
    if ptype == "title":
        return _plain(prop.get("title", []))
    elif ptype == "rich_text":
        return _plain(prop.get("rich_text", []))
    elif ptype == "number":
        v = prop.get("number")
        return str(v) if v is not None else ""
    elif ptype == "select":
        s = prop.get("select") or {}
        return s.get("name", "")
    elif ptype == "multi_select":
        return ", ".join(s.get("name", "") for s in prop.get("multi_select", []))
    elif ptype == "status":
        s = prop.get("status") or {}
        return s.get("name", "")
    elif ptype == "checkbox":
        return "✓" if prop.get("checkbox") else ""
    elif ptype == "date":
        d = prop.get("date") or {}
        return d.get("start", "")
    elif ptype in ("created_time", "last_edited_time"):
        return (prop.get(ptype) or "")[:10]
    elif ptype == "people":
        return ", ".join(p.get("name", "") for p in prop.get("people", []))
    elif ptype == "url":
        return prop.get("url", "") or ""
    elif ptype == "email":
        return prop.get("email", "") or ""
    elif ptype == "phone_number":
        return prop.get("phone_number", "") or ""
    elif ptype == "formula":
        f = prop.get("formula") or {}
        return str(f.get(f.get("type", ""), ""))
    elif ptype == "relation":
        return f"{len(prop.get('relation', []))} itens"
    elif ptype == "rollup":
        return "[rollup]"
    return ""


def database_to_md(db: dict, token: str, workspace: str) -> str:
    notion_id = db["id"]
    title = _plain(db.get("title", []))
    last_edited = db.get("last_edited_time", "")
    url = db.get("url", "")

    rows = []
    try:
        data = _post(
            f"{NOTION_API}/databases/{notion_id}/query",
            token,
            {"page_size": 100},
        )
        rows = data.get("results", [])
    except Exception as e:
        log.warning(f"  query db {notion_id[:8]}: {e}")

    props_schema = db.get("properties", {})
    # Put title column first, then max 7 others
    col_names = [k for k, v in props_schema.items() if v.get("type") == "title"]
    col_names += [k for k, v in props_schema.items() if v.get("type") != "title"]
    col_names = col_names[:8]

    if rows and col_names:
        header = "| " + " | ".join(col_names) + " |"
        sep = "|" + "|".join(["---"] * len(col_names)) + "|"
        table_rows = []
        for row in rows[:100]:
            rp = row.get("properties", {})
            cells = []
            for col in col_names:
                val = _prop_val(rp.get(col, {}))
                cells.append(val.replace("|", "\\|").replace("\n", " "))
            table_rows.append("| " + " | ".join(cells) + " |")
        table = "\n".join([header, sep] + table_rows)
    else:
        table = "_Sem dados_"

    return "\n".join([
        "---",
        f"notion_id: {notion_id}",
        f"title: {title or 'Untitled'}",
        "type: database",
        f"workspace: {workspace}",
        f"last_edited: {last_edited}",
        f"url: {url}",
        "---",
        "",
        f"# {title or 'Untitled'}",
        "",
        table,
    ])


# ── Search ───────────────────────────────────────────────────────────────────

def search_workspace(
    token: str, last_sync: str | None, max_pages: int
) -> tuple[list, list]:
    """
    Fetch pages/databases from Notion API.
    Filters by last_edited_time client-side (API doesn't support server-side date filter on search).
    Returns (pages, databases).
    """
    pages, databases = [], []
    fetched = 0
    cursor = None

    while fetched < max_pages:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor

        try:
            data = _post(f"{NOTION_API}/search", token, body)
        except requests.HTTPError as e:
            if e.response.status_code in (401, 403):
                raise
            log.error(f"Search HTTP error: {e}")
            break

        results = data.get("results", [])
        for item in results:
            if last_sync and item.get("last_edited_time", "") <= last_sync:
                continue  # skip unmodified items (delta filter)
            obj = item.get("object")
            if obj == "page":
                pages.append(item)
            elif obj == "database":
                databases.append(item)

        fetched += len(results)

        if not data.get("has_more") or not data.get("next_cursor"):
            break
        cursor = data["next_cursor"]

        if fetched >= max_pages:
            log.info(f"  Reached max_pages={max_pages}, stopping early (use --max-pages to increase)")

    return pages, databases


# ── Git ──────────────────────────────────────────────────────────────────────

def git_commit_push(workspace: str, stats: dict, dry_run: bool) -> bool:
    if dry_run or not any(stats[k] for k in ("added", "updated", "deleted")):
        return True

    def run(cmd: list, timeout: int) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd, cwd=SECOND_BRAIN, capture_output=True, text=True, timeout=timeout
        )

    try:
        r = run(["git", "add", "-A"], 30)
        if r.returncode != 0:
            log.error(f"git add failed: {r.stderr.strip()}")
            return False

        msg = (
            f"sync(notion/{workspace}): "
            f"+{stats['added']} ~{stats['updated']} -{stats['deleted']} "
            f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}Z]"
        )
        r = run(["git", "commit", "-m", msg], 30)
        if r.returncode != 0:
            if "nothing to commit" in r.stdout:
                return True
            log.error(f"git commit failed: {r.stderr.strip()}")
            return False

        r = run(["git", "push"], 60)
        if r.returncode != 0:
            log.warning(f"git push failed (files saved locally): {r.stderr.strip()}")
            return False

        return True

    except subprocess.TimeoutExpired as e:
        log.warning(f"git timed out for {workspace}: {e} — files saved locally")
        return False


# ── Sync workspace ────────────────────────────────────────────────────────────

def sync_workspace(
    workspace: str,
    token: str,
    state: dict,
    dry_run: bool,
    full: bool,
    fetch_content: bool,
    max_pages: int,
) -> dict:
    last_sync = None if full else state.get(workspace)
    mode = "full" if (full or not last_sync) else f"delta (since {last_sync[:10]})"
    log.info(f"[{workspace}] {mode} sync | content={'yes' if fetch_content else 'no'}")

    base = SECOND_BRAIN / f"03-knowledge/notion/{workspace}"
    pages_dir = base / "pages"
    dbs_dir = base / "databases"

    if not dry_run:
        pages_dir.mkdir(parents=True, exist_ok=True)
        dbs_dir.mkdir(parents=True, exist_ok=True)

    existing_pages = {f.stem: f for f in pages_dir.glob("*.md")} if pages_dir.exists() else {}
    existing_dbs = {f.stem: f for f in dbs_dir.glob("*.md")} if dbs_dir.exists() else {}

    pages, databases = search_workspace(token, last_sync, max_pages)
    log.info(f"[{workspace}] {len(pages)} pages, {len(databases)} databases to process")

    stats = {"added": 0, "updated": 0, "deleted": 0, "errors": 0}
    seen_pages: set[str] = set()
    seen_dbs: set[str] = set()

    for page in pages:
        title = _page_title(page)
        slug = _slug(title, page["id"])
        seen_pages.add(slug)
        is_new = slug not in existing_pages
        target = pages_dir / f"{slug}.md"

        if dry_run:
            log.info(f"  [dry] {'ADD' if is_new else 'UPD'} pages/{slug}.md")
            stats["added" if is_new else "updated"] += 1
            continue

        try:
            content = page_to_md(page, token, workspace, fetch_content=fetch_content)
            target.write_text(content, encoding="utf-8")
            stats["added" if is_new else "updated"] += 1
        except Exception as e:
            log.warning(f"  page {page['id'][:8]}: {e}")
            stats["errors"] += 1

    for db in databases:
        title = _plain(db.get("title", []))
        slug = _slug(title, db["id"])
        seen_dbs.add(slug)
        is_new = slug not in existing_dbs
        target = dbs_dir / f"{slug}.md"

        if dry_run:
            log.info(f"  [dry] {'ADD' if is_new else 'UPD'} databases/{slug}.md")
            stats["added" if is_new else "updated"] += 1
            continue

        try:
            content = database_to_md(db, token, workspace)
            target.write_text(content, encoding="utf-8")
            stats["added" if is_new else "updated"] += 1
        except Exception as e:
            log.warning(f"  db {db['id'][:8]}: {e}")
            stats["errors"] += 1

    # Deletions only on full sync (delta has no visibility into deletions)
    if full and not dry_run:
        for stem, path in existing_pages.items():
            if stem not in seen_pages:
                path.unlink()
                stats["deleted"] += 1
        for stem, path in existing_dbs.items():
            if stem not in seen_dbs:
                path.unlink()
                stats["deleted"] += 1

    log.info(
        f"[{workspace}] +{stats['added']} ~{stats['updated']} "
        f"-{stats['deleted']} err={stats['errors']}"
    )
    return stats


# ── Report ───────────────────────────────────────────────────────────────────

def write_report(results: dict, start_time: datetime) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    duration = int((now - start_time).total_seconds())
    parts = [f"Sync: {now.strftime('%Y-%m-%d %H:%M')}Z | {duration}s"]
    for ws, stats in results.items():
        parts.append(
            f"{ws}: +{stats['added']} ~{stats['updated']} -{stats['deleted']} err={stats['errors']}"
        )
    line = " | ".join(parts)
    REPORT_FILE.write_text(line + "\n", encoding="utf-8")
    log.info(line)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Notion → 2nd-brain sync")
    parser.add_argument("--full", action="store_true", help="Full sync (ignores last_sync state)")
    parser.add_argument("--content", action="store_true", help="Fetch block content (slow, for pages)")
    parser.add_argument("--workspace", choices=list(TOKENS), help="Sync only one workspace")
    parser.add_argument("--dry-run", action="store_true", help="Simulate, no writes")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_PER_RUN,
                        help=f"Max Notion pages per workspace per run (default {MAX_PAGES_PER_RUN})")
    args = parser.parse_args()

    # Delta sync always fetches content (few pages); full sync only with --content flag
    fetch_content = args.content or (not args.full)

    start_time = datetime.now(timezone.utc)
    state = load_state()
    workspaces = [args.workspace] if args.workspace else list(TOKENS)
    results: dict = {}

    for ws in workspaces:
        token = TOKENS[ws]
        try:
            stats = sync_workspace(
                workspace=ws,
                token=token,
                state=state,
                dry_run=args.dry_run,
                full=args.full,
                fetch_content=fetch_content,
                max_pages=args.max_pages,
            )
            results[ws] = stats

            # Checkpoint: save state + push after each workspace
            if not args.dry_run:
                state[ws] = datetime.now(timezone.utc).isoformat()
                save_state(state)
                git_commit_push(ws, stats, dry_run=False)

        except requests.HTTPError as e:
            log.error(f"[{ws}] HTTP {e.response.status_code} — skipping")
            results[ws] = {"added": 0, "updated": 0, "deleted": 0, "errors": 1}
        except Exception as e:
            log.error(f"[{ws}] Error: {e} — skipping")
            results[ws] = {"added": 0, "updated": 0, "deleted": 0, "errors": 1}

    if not args.dry_run:
        write_report(results, start_time)

    return 0 if all(r["errors"] == 0 for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
