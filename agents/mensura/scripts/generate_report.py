#!/usr/bin/env python3
"""
generate_report.py — Formata dados extraidos do .mpp em prompt para skill relatorio-preditivo-obras
e salva KPIs na memoria do OpenClaw para comparativo semanal.
Uso: python3 generate_report.py --json <extracted.json> --obra <nome> [--memoria]
"""

import json
import sys
import os
import argparse
from datetime import date

def calc_time_pct(start_str, baseline_finish_str):
    if not start_str or not baseline_finish_str:
        return None
    try:
        start = date.fromisoformat(start_str)
        finish = date.fromisoformat(baseline_finish_str)
        today = date.today()
        total_days = (finish - start).days
        elapsed = (today - start).days
        return round(elapsed / total_days * 100, 1) if total_days > 0 else None
    except:
        return None

def calc_spi(physical_pct, time_pct):
    if physical_pct is None or time_pct is None or time_pct == 0:
        return None
    return round(physical_pct / time_pct, 3)

def load_memory(obra_name):
    mem_path = f'/root/.openclaw/workspace/memory/obras/{obra_name.lower().replace(" ", "-")}-kpis.json'
    try:
        with open(mem_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def save_memory(obra_name, kpis):
    mem_dir = '/root/.openclaw/workspace/memory/obras'
    os.makedirs(mem_dir, exist_ok=True)
    mem_path = f'{mem_dir}/{obra_name.lower().replace(" ", "-")}-kpis.json'
    history = []
    try:
        with open(mem_path, 'r') as f:
            existing = json.load(f)
            history = existing.get('history', [])
    except:
        pass
    history.append(kpis)
    if len(history) > 12:
        history = history[-12:]
    data = {'current': kpis, 'previous': history[-2] if len(history) >= 2 else None, 'history': history}
    with open(mem_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'KPIs salvos em memoria: {mem_path}')

def generate_prompt(data, previous_kpis=None):
    s = data['summary']
    time_pct = calc_time_pct(data.get('project_start'), data.get('project_baseline_finish'))
    spi = calc_spi(s['physical_progress_pct'], time_pct)
    today = date.today().isoformat()
    report_type = 'Relatorio 001 (1a analise)' if previous_kpis is None else 'Relatorio comparativo semanal'

    pct_concl = round(s['completed'] / s['total_tasks'] * 100, 1) if s['total_tasks'] else 0

    prompt = f'''DADOS DO CRONOGRAMA — {data["obra"].upper()}
Data de extracao: {today}
Tipo: {report_type}

=== DADOS GERAIS ===
Inicio do projeto: {data.get("project_start", "N/D")}
Termino baseline: {data.get("project_baseline_finish", "N/D")}
Termino projetado (MS Project): {data.get("project_finish", "N/D")}

=== INDICADORES ===
Avanco fisico (ponderado por duracao): {s["physical_progress_pct"]}%
% Tempo consumido: {time_pct}%
SPI calculado: {spi}
BEI: {s["bei"]}

=== ATIVIDADES ===
Total de atividades: {s["total_tasks"]}
Concluidas: {s["completed"]} ({pct_concl}%)
Em andamento: {s["in_progress"]}
Nao iniciadas: {s["not_started"]}
Atividades no caminho critico: {s["critical_tasks"]}

=== DCMA FLAGS ===
Sem predecessoras: {data["dcma_flags"]["no_predecessors"]}
Folga negativa: {data["dcma_flags"]["negative_slack"]}
Atividades > 44 dias: {data["dcma_flags"]["long_tasks"]}
Folga > 44 dias: {data["dcma_flags"]["high_slack"]}
'''

    if previous_kpis:
        prompt += f'''
=== COMPARATIVO SEMANA ANTERIOR ===
Avanco fisico anterior: {previous_kpis.get("physical_progress_pct", "N/D")}%
SPI anterior: {previous_kpis.get("spi", "N/D")}
BEI anterior: {previous_kpis.get("bei", "N/D")}
Atividades criticas anterior: {previous_kpis.get("critical_tasks", "N/D")}
'''

    critical_late = [
        t for t in data['tasks']
        if t['critical'] and not t['summary'] and t['percent_complete'] < 100
        and t['baseline_finish'] and t['baseline_finish'] <= today
    ][:10]

    if critical_late:
        prompt += '\n=== ATIVIDADES CRITICAS ATRASADAS (TOP 10) ===\n'
        for t in critical_late:
            prompt += f'- [{t["wbs"]}] {t["name"]} | Baseline: {t["baseline_finish"]} | Progresso: {t["percent_complete"]}% | Folga: {t.get("total_slack_days", "N/D")} dias\n'

    tipo_relatorio = 'Secao A (Relatorio Completo)' if previous_kpis is None else 'Secao B (Relatorio Comparativo Semanal)'
    prompt += f'''
=== INSTRUCAO ===
Com base nos dados acima, gere o relatorio conforme o protocolo MENSURA v3.0.
Tipo solicitado: {tipo_relatorio}
Obra: {data["obra"]}
'''
    return prompt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', required=True, help='JSON extraido pelo extract_schedule.py')
    parser.add_argument('--obra', required=True, help='Nome da obra')
    parser.add_argument('--memoria', action='store_true', help='Salvar KPIs na memoria OpenClaw')
    parser.add_argument('--out', default=None, help='Arquivo de saida do prompt')
    args = parser.parse_args()

    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['obra'] = args.obra

    mem_data = load_memory(args.obra)
    previous_kpis = mem_data['current'] if mem_data else None
    prompt = generate_prompt(data, previous_kpis)

    if args.memoria:
        s = data['summary']
        time_pct = calc_time_pct(data.get('project_start'), data.get('project_baseline_finish'))
        spi = calc_spi(s['physical_progress_pct'], time_pct)
        kpis = {
            'date': date.today().isoformat(),
            'physical_progress_pct': s['physical_progress_pct'],
            'spi': spi,
            'bei': s['bei'],
            'critical_tasks': s['critical_tasks'],
            'time_pct': time_pct,
            'baseline_finish': data.get('project_baseline_finish'),
            'projected_finish': data.get('project_finish'),
        }
        save_memory(args.obra, kpis)

    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f'Prompt salvo em {args.out}')
    else:
        print(prompt)
