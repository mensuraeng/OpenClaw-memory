#!/usr/bin/env python3
"""
extract_schedule.py — Extrai dados de cronograma .mpp via mpxj (org.mpxj 16.x)
Uso: python3 extract_schedule.py <caminho_do_arquivo.mpp> [--obra <nome>]
Output: JSON estruturado compativel com skill relatorio-preditivo-obras
"""

import sys
import json
import argparse
from datetime import date

def extract_mpp(file_path, obra_name=''):
    import mpxj
    import jpype
    import jpype.imports
    if not jpype.isJVMStarted():
        jpype.startJVM()

    from org.mpxj.reader import UniversalProjectReader
    reader = UniversalProjectReader()
    project = reader.read(file_path)

    tasks = []
    for task in project.getTasks():
        if task.getName() is None:
            continue
        dur = task.getDuration()
        dur_days = float(str(dur.getDuration())) if dur else 0.0
        slack = task.getTotalSlack()
        slack_days = None
        if slack is not None:
            try:
                slack_days = float(str(slack.getDuration()))
            except:
                slack_days = None
        bs = task.getBaselineStart()
        bf = task.getBaselineFinish()
        as_ = task.getActualStart()
        af = task.getActualFinish()
        pct = task.getPercentageComplete()
        pct_val = float(str(pct)) if pct is not None else 0.0

        preds = []
        for rel in (task.getPredecessors() or []):
            pred_task = rel.getTargetTask()
            if pred_task:
                preds.append(str(pred_task.getID()))

        tasks.append({
            'id': str(task.getID()),
            'wbs': str(task.getWBS()) if task.getWBS() else '',
            'name': str(task.getName()),
            'duration_days': dur_days,
            'baseline_start': str(bs)[:10] if bs else None,
            'baseline_finish': str(bf)[:10] if bf else None,
            'actual_start': str(as_)[:10] if as_ else None,
            'actual_finish': str(af)[:10] if af else None,
            'percent_complete': pct_val,
            'total_slack_days': slack_days,
            'critical': bool(task.getCritical()),
            'milestone': bool(task.getMilestone()),
            'predecessors': preds,
            'summary': bool(task.getSummary()),
        })

    today = date.today().isoformat()
    total = len([t for t in tasks if not t['summary']])
    completed = len([t for t in tasks if not t['summary'] and t['percent_complete'] >= 100])
    in_progress = len([t for t in tasks if not t['summary'] and 0 < t['percent_complete'] < 100])
    not_started = len([t for t in tasks if not t['summary'] and t['percent_complete'] == 0])

    should_done = [t for t in tasks if not t['summary'] and t['baseline_finish'] and t['baseline_finish'] <= today]
    done_on_time = [t for t in should_done if t['percent_complete'] >= 100]
    bei = round(len(done_on_time) / len(should_done), 3) if should_done else None

    leaf_tasks = [t for t in tasks if not t['summary'] and t['duration_days'] > 0]
    total_dur = sum(t['duration_days'] for t in leaf_tasks)
    weighted_progress = (
        sum(t['percent_complete'] * t['duration_days'] for t in leaf_tasks) / total_dur
        if total_dur > 0 else 0
    )

    props = project.getProjectProperties()
    def fmt_date(d):
        return str(d)[:10] if d else None

    return {
        'obra': obra_name,
        'extraction_date': today,
        'project_start': fmt_date(props.getStartDate()),
        'project_finish': fmt_date(props.getFinishDate()),
        'project_baseline_finish': fmt_date(props.getBaselineFinishDate()),
        'summary': {
            'total_tasks': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'physical_progress_pct': round(weighted_progress, 2),
            'bei': bei,
            'critical_tasks': len([t for t in tasks if t['critical'] and not t['summary']]),
        },
        'tasks': tasks,
        'dcma_flags': {
            'no_predecessors': len([t for t in tasks if not t['summary'] and not t['predecessors'] and not t['milestone']]),
            'negative_slack': len([t for t in tasks if not t['summary'] and t['total_slack_days'] is not None and t['total_slack_days'] < 0]),
            'long_tasks': len([t for t in tasks if not t['summary'] and t['duration_days'] > 44]),
            'high_slack': len([t for t in tasks if not t['summary'] and t['total_slack_days'] is not None and t['total_slack_days'] > 44]),
        }
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extrai cronograma .mpp para JSON')
    parser.add_argument('file', nargs='?', help='Caminho para o arquivo .mpp')
    parser.add_argument('--obra', default='', help='Nome da obra')
    parser.add_argument('--out', default=None, help='Arquivo JSON de saida (opcional)')
    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        sys.exit(0)

    data = extract_mpp(args.file, args.obra)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'Salvo em {args.out}')
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
