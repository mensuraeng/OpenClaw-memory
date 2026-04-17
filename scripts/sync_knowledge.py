#!/usr/bin/env python3
"""
sync_knowledge.py — sincroniza ~/.openclaw/workspace/knowledge/openclaw-context/
                    e injeta arquivos novos/modificados na memória da Flávia.

Fluxo:
1. git pull no clone local
2. Detecta arquivos novos ou modificados desde o último sync
   (compara com ~/.openclaw/workspace/logs/knowledge-sync.json)
3. Para cada arquivo novo/modificado:
   - Lê conteúdo (.md, .txt, .pdf via pdftotext)
   - Gera payload estruturado
   - Entrega à Flávia via send_to_flavia(payload)
4. Atualiza knowledge-sync.json
5. Tudo para stderr (cron captura no log)

Flags:
  --dry-run   não envia à Flávia, mostra o que processaria
  --force     reprocessa todos os arquivos mesmo já indexados
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

REPO_DIR   = os.path.expanduser("~/.openclaw/workspace/knowledge/openclaw-context")
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/logs/knowledge-sync.json")

SUPPORTED_EXTS = {".md", ".txt", ".pdf"}
SKIP_FILES = {"README.md", ".gitkeep"}
PREVIEW_CHARS = 500


def log(msg: str) -> None:
    sys.stderr.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {"last_sync_at": None, "files": {}}
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log(f"WARN: state file corrompido ({e}); começando do zero")
        return {"last_sync_at": None, "files": {}}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def git_pull() -> int:
    log("git pull no openclaw-context...")
    r = subprocess.run(
        ["git", "-C", REPO_DIR, "pull", "--ff-only"],
        capture_output=True, text=True, timeout=60,
    )
    if r.stdout.strip():
        log(f"git stdout: {r.stdout.strip()}")
    if r.returncode != 0:
        log(f"ERRO git pull (rc={r.returncode}): {r.stderr.strip()}")
    return r.returncode


def list_files() -> list:
    """Lista arquivos suportados, ignorando .git/, .gitkeep e README.md."""
    out = []
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            if name in SKIP_FILES:
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in SUPPORTED_EXTS:
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, REPO_DIR)
            out.append(rel)
    return sorted(out)


def file_hash(full_path: str) -> str:
    h = hashlib.sha256()
    with open(full_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_content(full_path: str) -> str:
    ext = os.path.splitext(full_path)[1].lower()
    if ext == ".pdf":
        try:
            r = subprocess.run(
                ["pdftotext", "-layout", full_path, "-"],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode != 0:
                return f"[ERRO pdftotext: {r.stderr.strip()[:200]}]"
            return r.stdout
        except FileNotFoundError:
            return "[pdftotext não instalado — instale poppler-utils]"
        except subprocess.TimeoutExpired:
            return "[timeout extraindo PDF]"
    try:
        with open(full_path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return "[arquivo não-UTF8 — pulando]"


def category_of(rel_path: str) -> str:
    parts = rel_path.split(os.sep)
    return parts[0] if parts else "raiz"


def build_payload(rel_path: str, content: str) -> dict:
    preview = content.strip()[:PREVIEW_CHARS]
    if len(content.strip()) > PREVIEW_CHARS:
        preview += " […]"
    name = os.path.basename(rel_path)
    cat = category_of(rel_path)
    return {
        "source": "sync_knowledge.py",
        "kind": "knowledge_update",
        "file": rel_path,
        "category": cat,
        "content_preview": preview,
        "scheduled_at": datetime.now().isoformat(),
        "body": (
            f"Novo arquivo disponível: {name}. "
            f"Categoria: {cat}. "
            f"Preview: {preview}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Não envia à Flávia; só mostra o que processaria")
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa todos os arquivos mesmo que já indexados")
    parser.add_argument("--no-pull", action="store_true",
                        help="Pula o git pull (útil em teste local)")
    args = parser.parse_args()

    if not os.path.isdir(os.path.join(REPO_DIR, ".git")):
        log(f"ERRO: {REPO_DIR} não é um repo git válido")
        return 1

    if not args.no_pull:
        if git_pull() != 0:
            log("ABORTANDO: git pull falhou")
            return 1

    state = load_state()
    if args.force:
        log("--force: ignorando estado anterior")
        state = {"last_sync_at": None, "files": {}}

    known = state.get("files", {})
    files_now = list_files()
    log(f"arquivos suportados encontrados: {len(files_now)}")

    novos = []
    modificados = []
    inalterados = []
    for rel in files_now:
        full = os.path.join(REPO_DIR, rel)
        h = file_hash(full)
        prev = known.get(rel)
        if prev is None:
            novos.append((rel, h))
        elif prev.get("hash") != h:
            modificados.append((rel, h))
        else:
            inalterados.append(rel)

    log(f"novos: {len(novos)} · modificados: {len(modificados)} · inalterados: {len(inalterados)}")

    a_processar = novos + modificados
    if not a_processar:
        log("nada para processar")
        if not args.dry_run:
            state["last_sync_at"] = datetime.now().isoformat()
            save_state(state)
        return 0

    rc_max = 0
    processed = []
    for rel, h in a_processar:
        full = os.path.join(REPO_DIR, rel)
        content = read_content(full)
        payload = build_payload(rel, content)
        status = "novo" if (rel, h) in novos else "modificado"

        if args.dry_run:
            log(f"[DRY-RUN] {status}: {rel} ({len(content)} chars; categoria={payload['category']})")
            log(f"          preview: {payload['content_preview'][:120]!r}")
            continue

        log(f"[{status}] entregando à Flávia: {rel}")
        rc = send_to_flavia(payload)
        log(f"  → exit={rc}")
        if rc != 0:
            rc_max = max(rc_max, rc)
            log(f"  → FALHA, não marcando como sincronizado")
            continue
        processed.append(rel)
        known[rel] = {"hash": h, "synced_at": datetime.now().isoformat()}

    if not args.dry_run:
        state["files"] = known
        state["last_sync_at"] = datetime.now().isoformat()
        save_state(state)
        log(f"state atualizado: {len(processed)} processados")
    else:
        log(f"[DRY-RUN] terminado — state NÃO atualizado")

    return rc_max


if __name__ == "__main__":
    sys.exit(main())
