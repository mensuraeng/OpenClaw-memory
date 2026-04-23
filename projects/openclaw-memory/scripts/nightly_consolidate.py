#!/usr/bin/env python3
import os, datetime
WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR=os.path.join(WORKSPACE,"memory","context")
PANEL=os.path.join(WORKSPACE,"projects","openclaw-memory","MEMORY.md")
now=datetime.datetime.now(); now_str=now.strftime("%Y-%m-%d %H:%M"); today=now.strftime("%Y-%m-%d")
files=["pending.md","decisions.md","lessons.md","people.md","business-context.md"]
lines=[]
for f in files:
    p=os.path.join(MEMORY_DIR,f)
    if os.path.exists(p):
        sz=os.path.getsize(p); lc=open(p).read().count('\n')
        flag="" if sz<50000 else " GRANDE"
        lines.append(f"- `{f}`: {lc} linhas / {sz//1024}KB {flag}")
    else: lines.append(f"- `{f}`:  ausente")
daily=os.path.join(WORKSPACE,"memory","daily",f"{today}.md")
ds="" if os.path.exists(daily) else ""
content=f"# MEMORY.md\n> Atualizado: {now_str}\n\n## Contexto\n"+"\n".join(lines)+f"\n\n## Dirio hoje ({today}): {ds}\n"
os.makedirs(os.path.dirname(PANEL),exist_ok=True)
open(PANEL,"w").write(content)
print(f"[{now_str}] MEMORY.md atualizado OK")
