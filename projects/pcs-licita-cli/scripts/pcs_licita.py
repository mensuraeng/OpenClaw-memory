#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
MONITOR=WORKSPACE/'scripts/monitor_licitacoes.py'
EMAIL=WORKSPACE/'scripts/licitacoes_email.py'
CONFIRM='AUTORIZO PCS LICITA'
BLOCKED_TOP={'delete','remove','telegram'}

def run(cmd,timeout=300):
 try:
  cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
  return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
 except Exception as e: return {'ok':False,'error':str(e),'cmd':cmd}

def emit(payload,args):
 print(json.dumps(payload,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else (payload.get('stdout') if isinstance(payload,dict) and 'stdout' in payload else json.dumps(payload,ensure_ascii=False,indent=2,default=str)))

def status(args): emit({'mode':'controlled_v0.2','time':datetime.now().isoformat(timespec='seconds'),'monitor_exists':MONITOR.exists(),'email_script_exists':EMAIL.exists(),'guardrails':'search read-only; weekly email only with explicit Alexandre authorization','confirm_phrase':CONFIRM},args)

def search(args):
 cmd=['python3',str(MONITOR),'--dias',str(args.dias)]
 if args.uf: cmd+=['--uf',args.uf]
 if args.valores: cmd+=['--valores']
 res=run(cmd,args.timeout)
 if args.json: emit({'mode':'read_only','ok':res['ok'],'code':res.get('code'),'stdout':res.get('stdout'),'stderr':res.get('stderr')},args)
 else:
  if not res['ok']:
   print(res.get('stderr') or res.get('stdout') or res.get('error')); raise SystemExit(res.get('code') or 1)
  print(res['stdout'])

def weekly(args):
 execute=bool(args.execute)
 if execute:
  missing=[]
  if (args.approved_by or '').strip().lower() not in {'alexandre','alê','ale','alexandre aguiar'}: missing.append('--approved-by Alexandre')
  if (args.confirm or '').strip()!=CONFIRM: missing.append(f'--confirm "{CONFIRM}"')
  if not args.approval_note or len(args.approval_note.strip())<12: missing.append('--approval-note')
  if missing:
   emit({'mode':'blocked_missing_authorization','missing':missing,'rule':'Email PCS licita só sob ordem explícita do Alê/Alexandre.'},args); raise SystemExit(2)
 cmd=['python3',str(EMAIL),'--force']
 if not execute: cmd.append('--dry-run')
 if args.to: cmd+=['--to',args.to]
 res=run(cmd,args.timeout)
 emit({'mode':'authorized_execute_result' if execute else 'dry_run_result','execute':execute,'ok':res['ok'],'code':res.get('code'),'cmd':cmd,'stdout':res.get('stdout','')[-6000:],'stderr':res.get('stderr','')[-6000:]},args)
 if not res['ok']: raise SystemExit(res.get('code') or 1)

def guardrails(args): emit({'mode':'controlled_v0.2','confirm_phrase':CONFIRM,'rules':['PNCP search is read-only.','Weekly email can run only with --execute + approved-by + exact confirm + approval note.','No Telegram direct command.','No delete/remove.']},args)

def parser():
 p=argparse.ArgumentParser(prog='pcs-licita',description='CLI PCS licitações controlled')
 sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('search'); s.add_argument('--uf'); s.add_argument('--dias',type=int,default=14); s.add_argument('--valores',action='store_true'); s.add_argument('--timeout',type=int,default=300); s.add_argument('--json',action='store_true'); s.set_defaults(func=search)
 s=sub.add_parser('weekly'); ss=s.add_subparsers(dest='subcmd',required=True); r=ss.add_parser('send-authorized'); r.add_argument('--execute',action='store_true'); r.add_argument('--approved-by'); r.add_argument('--confirm'); r.add_argument('--approval-note'); r.add_argument('--to'); r.add_argument('--timeout',type=int,default=360); r.add_argument('--json',action='store_true'); r.set_defaults(func=weekly)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p

def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED_TOP: raise SystemExit('Blocked: pcs-licita v0.2 only allows controlled weekly send subcommand.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
