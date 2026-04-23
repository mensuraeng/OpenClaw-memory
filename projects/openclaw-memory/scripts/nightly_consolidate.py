#!/usr/bin/env python3
"""
nightly_consolidate.py  Consolida memria nightly + sync 2nd-brain
Roda via cron: 0 22 * * * python3 /root/.openclaw/workspace/projects/openclaw-memory/scripts/nightly_consolidate.py
"""
import os, subprocess, datetime

WS = "/root/.openclaw/workspace"
BRAIN = "/root/2nd-brain"
CTX = f"{WS}/memory/context"
NOW = datetime.datetime.now()
TODAY = NOW.strftime("%Y-%m-%d")
TS = NOW.strftime("%Y-%m-%d %H:%M")

print(f"[{TS}] Nightly consolidate iniciando...")

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
        with open(src) as f: content = f.read()
        with open(dst, "w") as f: f.write(content)
        print(f"  sync: {fname}  2nd-brain/02-context/")

# 3. Verificar journal de hoje
journal_dir = f"{BRAIN}/05-journal/2026"
os.makedirs(journal_dir, exist_ok=True)
journal_file = f"{journal_dir}/{TODAY}.md"
if not os.path.exists(journal_file):
    with open(journal_file, "w") as f:
        f.write(f"# Journal {TODAY}\n\n## Resumo do dia\n\n## Decises\n\n## Pendncias para amanh\n")
    print(f"  journal {TODAY}.md criado")

# 4. Commit e push do workspace
result = subprocess.run(
    ["git", "-C", WS, "status", "--short"],
    capture_output=True, text=True
)
if result.stdout.strip():
    subprocess.run(["git", "-C", WS, "add", "-A"])
    subprocess.run(["git", "-C", WS, "commit", "-m", f"nightly: consolidate {TODAY}"])
    subprocess.run(["git", "-C", WS, "push"])
    print(f"  workspace: push OK")
else:
    print(f"  workspace: sem mudanas")

# 5. Commit e push do 2nd-brain
result2 = subprocess.run(
    ["git", "-C", BRAIN, "status", "--short"],
    capture_output=True, text=True
)
if result2.stdout.strip():
    subprocess.run(["git", "-C", BRAIN, "add", "-A"])
    subprocess.run(["git", "-C", BRAIN, "commit", "-m", f"nightly: sync {TODAY}"])
    subprocess.run(["git", "-C", BRAIN, "push"])
    print(f"  2nd-brain: push OK")
else:
    print(f"  2nd-brain: sem mudanas")

print(f"[{TS}] Nightly consolidate concludo.")
