#!/usr/bin/env python3
"""
update_memory_panel.py
Atualiza a secao "Estado Atual" do MEMORY.md com dados derivados automaticamente.
Chamado pelo nightly_consolidate.py no final do ciclo noturno.
"""
import re, os, glob
from datetime import date

WORKSPACE = '/root/.openclaw/workspace'
MEMORY_MD = os.path.join(WORKSPACE, 'MEMORY.md')
PENDING   = os.path.join(WORKSPACE, 'memory/context/pending.md')
DECISIONS = os.path.join(WORKSPACE, 'memory/context/decisions.md')
TODAY_STR = date.today().strftime('%Y-%m-%d')
DAILY     = os.path.join(WORKSPACE, f'memory/{TODAY_STR}.md')

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''

def extract_pending_open(content):
    lines = content.split('\n')
    open_items = []
    for line in lines:
        s = line.strip()
        if re.match(r'^- \[ \]', s):
            open_items.append(s)
        elif re.search(r'CRITICO|BLOQUEADO|\U0001F534', s) and s.startswith('-'):
            open_items.append(s)
    return open_items[:10]

def extract_last_decisions(content, n=5):
    decisions = []
    current = None
    for line in content.split('\n'):
        if re.match(r'^### ', line):
            current = line.replace('### ', '').strip()
        elif '[ATIVA]' in line and current:
            decisions.append(current)
            current = None
    return decisions[-n:]

def extract_daily_highlights(content):
    highlights = []
    for line in content.split('\n'):
        s = line.strip()
        if re.search(r'entrega|alerta|concluido|urgente|\u2705|\u26a0', s, re.IGNORECASE):
            if s and len(s) > 10:
                highlights.append(s[:120])
    return highlights[:5]

def build_estado_atual():
    p_content = read_file(PENDING)
    d_content = read_file(DECISIONS)
    daily_c   = read_file(DAILY)
    
    open_items  = extract_pending_open(p_content)
    active_decs = extract_last_decisions(d_content)
    highlights  = extract_daily_highlights(daily_c)
    
    block = f'## Estado Atual\n_Atualizado automaticamente em {TODAY_STR} pelo update_memory_panel.py_\n\n'
    block += f'### Pendencias Abertas ({len(open_items)} itens)\n'
    block += ('\n'.join(open_items) if open_items else '_Nenhuma pendencia aberta_') + '\n'
    block += f'\n### Ultimas Decisoes Ativas\n'
    block += ('\n'.join(f'- {d}' for d in active_decs) if active_decs else '_Sem decisoes ativas recentes_') + '\n'
    block += f'\n### Destaques de Hoje ({TODAY_STR})\n'
    block += ('\n'.join(f'- {h}' for h in highlights) if highlights else '_Sem destaques registrados hoje_') + '\n'
    
    return block, len(open_items), len(active_decs)

def update_memory_md():
    content = read_file(MEMORY_MD)
    if not content:
        print(f'ERRO: {MEMORY_MD} nao encontrado')
        return
    
    new_block, n_pending, n_decisions = build_estado_atual()
    
    if '## Estado Atual' in content:
        pattern = r'## Estado Atual.*?(?=\n## |\Z)'
        new_content = re.sub(pattern, new_block.rstrip(), content, flags=re.DOTALL)
    else:
        new_content = content.rstrip() + '\n\n' + new_block
    
    with open(MEMORY_MD, 'w') as f:
        f.write(new_content)
    
    print(f'MEMORY.md atualizado: {n_pending} pendencias, {n_decisions} decisoes ativas')

if __name__ == '__main__':
    update_memory_md()
