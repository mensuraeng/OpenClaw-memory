#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={k:WORKSPACE/'scripts'/v for k,v in {'gerar':'gerar_relatorio.py','analytics':'relatorio_analytics.py','cursos':'relatorio_cursos.py','cursos_telegram':'relatorio_cursos_telegram.py','send_cursos':'send_relatorio_cursos.sh'}.items()}
BLOCKED={'send','deliver','telegram','email','delete','upload'}
def emit(x,args): print(json.dumps(x,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else json.dumps(x,ensure_ascii=False,indent=2,default=str))
def status(args): emit({'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()}},args)
def list_reports(args):
 roots=[WORKSPACE/'reports',WORKSPACE/'projects']
 files=[]
 for r in roots:
  if r.exists():
   for p in r.rglob('*'):
    if p.is_file() and '.git' not in p.parts and 'runtime' not in p.parts and p.suffix.lower() in {'.md','.html','.pdf','.json'}:
     files.append({'path':str(p),'suffix':p.suffix.lower(),'size':p.stat().st_size})
 emit({'mode':'read_only','count':len(files),'files':files[:args.limit]},args)
def build_preview(args): emit({'mode':'dry_run_blocked','kind':args.kind,'reason':'Build real pode gerar artefatos ou acionar scripts com side effects; v0.1 só mapeia. Refatorar builders puros.'},args)
def guardrails(args): emit({'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No Telegram/email delivery.','No report generation with side effects in v0.1.','List/preview only.']},args)
def parser():
 p=argparse.ArgumentParser(prog='reports'); sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('list'); s.add_argument('--limit',type=int,default=80); s.add_argument('--json',action='store_true'); s.set_defaults(func=list_reports)
 s=sub.add_parser('build-preview'); s.add_argument('kind'); s.add_argument('--json',action='store_true'); s.set_defaults(func=build_preview)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p
def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED: raise SystemExit('Blocked: reports v0.1 is read-only/preview only. No delivery.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
