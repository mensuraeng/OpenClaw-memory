#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={'upload_teatro':WORKSPACE/'scripts/sienge_upload_orcamento_teatro_suzano.py','monitor_lock':WORKSPACE/'scripts/sienge_monitor_lock_teatro.py','pcs_upload':WORKSPACE/'projects/pcs-sienge-integration/scripts/upload_budget.py','pcs_upload_teatro':WORKSPACE/'projects/pcs-sienge-integration/scripts/upload_budget_teatro.py'}
BLOCKED={'upload','send','delete','post','commit','execute'}
def emit(x,args): print(json.dumps(x,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else json.dumps(x,ensure_ascii=False,indent=2,default=str))
def status(args): emit({'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()},'guardrails':'upload real blocked'},args)
def budget_validate(args):
 p=Path(args.file).expanduser().resolve()
 emit({'mode':'read_only','file':str(p),'exists':p.exists(),'suffix':p.suffix.lower(),'size':p.stat().st_size if p.exists() else None,'note':'Validação estrutural profunda pendente; upload bloqueado.'},args)
def upload_dry(args): emit({'mode':'dry_run_blocked','reason':'Upload Sienge é crítico e permanece bloqueado; precisa backup, diff e autorização explícita.','file':args.file},args)
def guardrails(args): emit({'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No real Sienge upload.','No budget mutation.','Require backup/diff/explicit approval before future execution.']},args)
def parser():
 p=argparse.ArgumentParser(prog='sienge'); sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('budget'); ss=s.add_subparsers(dest='subcmd',required=True); v=ss.add_parser('validate'); v.add_argument('file'); v.add_argument('--json',action='store_true'); v.set_defaults(func=budget_validate); u=ss.add_parser('upload-dry-run'); u.add_argument('file'); u.add_argument('--json',action='store_true'); u.set_defaults(func=upload_dry)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p
def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED: raise SystemExit('Blocked: sienge v0.1 is read-only/dry-run only. No upload.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
