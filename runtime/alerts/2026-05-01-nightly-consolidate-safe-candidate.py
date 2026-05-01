#!/usr/bin/env python3
"""
nightly_consolidate.py — consolida journal nightly sem sobrescrever 2nd-brain/02-context.

Rotina oficial: root cron às 01:00 BRT.
Esta rotina nunca deve fazer git add -A no workspace principal.

Regra crítica: /root/2nd-brain é fonte oficial. workspace/memory/context é legado/local.
Portanto, esta rotina não copia pending.md, decisions.md ou lessons.md do workspace
para /root/2nd-brain/02-context.
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


# 1. Verificar contexto legado apenas para diagnóstico, sem promoção automática.
for fname in ["pending.md", "decisions.md", "lessons.md", "mapa-frentes-criticas.md", "urgent_notifications.md"]:
    fpath = f"{CTX}/{fname}"
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        print(f"   legado {fname}: {size} bytes (sem sync automatico)")
    else:
        print(f"   legado {fname}: AUSENTE")

# 2. Nunca sobrescrever 2nd-brain/02-context a partir do workspace legado.
print("  contexto canonico preservado: 2nd-brain/02-context nao foi sobrescrito")

# 3. Verificar journal de hoje.
journal_dir = f"{BRAIN}/05-journal/2026"
os.makedirs(journal_dir, exist_ok=True)
journal_file = f"{journal_dir}/{TODAY}.md"
if not os.path.exists(journal_file):
    with open(journal_file, "w") as f:
        f.write(f"# Journal {TODAY}\n\n## Resumo do dia\n\n## Decisoes\n\n## Pendencias para amanha\n")
    print(f"  journal {TODAY}.md criado")

# 4. Commit e push apenas do journal esperado no 2nd-brain.
tracked_paths = [f"05-journal/2026/{TODAY}.md"]
if changed(tracked_paths):
    add_result = run(["git", "-C", BRAIN, "add", "--", *tracked_paths])
    if add_result.returncode != 0:
        print(f"  2nd-brain: git add falhou: {add_result.stderr.strip()}")
    else:
        commit_result = run(["git", "-C", BRAIN, "commit", "-m", f"nightly: journal {TODAY}"])
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

print(f"[{TS}] Nightly consolidate concluido.")
