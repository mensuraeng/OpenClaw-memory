#!/usr/bin/env python3
"""
nightly_consolidate.py  Consolida memoria nightly + sync 2nd-brain.

Rotina oficial: root cron as 01:00 BRT.
Esta rotina nunca deve fazer git add -A no workspace principal.
"""
import datetime
import os
import subprocess

WS = "/root/.openclaw/workspace"
BRAIN = "/root/2nd-brain"
CTX = f"{WS}/memory/context"
NOW = datetime.datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
TS = NOW.strftime("%Y-%m-%d %H:%M")

print(f"[{TS}] Nightly consolidate iniciando...")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def changed(paths):
    result = run(["git", "-C", BRAIN, "status", "--short", "--", *paths])
    return result.stdout.strip()

# 1. Verificar contexto ativo
for fname in ["pending.md", "decisions.md", "lessons.md", "mapa-frentes-criticas.md", "urgent_notifications.md"]:
    fpath = f"{CTX}/{fname}"
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        print(f"   {fname}: {size} bytes")
    else:
        print(f"   {fname}: AUSENTE  criando vazio")
        open(fpath, "w").write(f"# {fname}\n\nCriado em {TS}\n")

# 2. Copiar contexto atualizado para 2nd-brain
os.makedirs(f"{BRAIN}/02-context", exist_ok=True)
for fname in ["pending.md", "decisions.md", "lessons.md"]:
    src = f"{CTX}/{fname}"
    dst = f"{BRAIN}/02-context/{fname}"
    if os.path.exists(src):
        with open(src) as f:
            content = f.read()
        with open(dst, "w") as f:
            f.write(content)
        print(f"  sync: {fname}  2nd-brain/02-context/")

# 3. Verificar journal de hoje
journal_dir = f"{BRAIN}/05-journal/2026"
os.makedirs(journal_dir, exist_ok=True)
journal_file = f"{journal_dir}/{TODAY}.md"
if not os.path.exists(journal_file):
    with open(journal_file, "w") as f:
        f.write(f"# Journal {TODAY}\n\n## Resumo do dia\n\n## Decisoes\n\n## Pendencias para amanha\n")
    print(f"  journal {TODAY}.md criado")

# 4. Commit e push apenas dos caminhos esperados no 2nd-brain.
tracked_paths = ["02-context/pending.md", "02-context/decisions.md", "02-context/lessons.md", f"05-journal/2026/{TODAY}.md"]
if changed(tracked_paths):
    add_result = run(["git", "-C", BRAIN, "add", "--", *tracked_paths])
    if add_result.returncode != 0:
        print(f"  2nd-brain: git add falhou: {add_result.stderr.strip()}")
    else:
        commit_result = run(["git", "-C", BRAIN, "commit", "-m", f"nightly: sync {TODAY}"])
        if commit_result.returncode != 0:
            print(f"  2nd-brain: commit ignorado: {commit_result.stderr.strip() or commit_result.stdout.strip()}")
        else:
            push_result = run(["git", "-C", BRAIN, "push"])
            if push_result.returncode == 0:
                print("  2nd-brain: push OK")
            else:
                print(f"  2nd-brain: push falhou: {push_result.stderr.strip()}")
else:
    print("  2nd-brain: sem mudancas nos caminhos oficiais")

print(f"[{TS}] Nightly consolidate concludo.")
