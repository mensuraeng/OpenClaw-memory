#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
MONITOR=WORKSPACE/'scripts/monitor_licitacoes.py'
EMAIL=WORKSPACE/'scripts/licitacoes_email.py'
BLOCKED={'send','email','enviar','telegram','force','--telegram','delete','remove'}

def run(cmd,timeout=300):
 try:
  cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
  return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
 except Exception as e: return {'ok':False,'error':str(e),'cmd':cmd}

def emit(payload,args):
 if getattr(args,'json',False): print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
 elif isinstance(payload,dict) and 'stdout' in payload: print(payload.get('stdout') or payload.get('stderr') or payload.get('error') or '')
 else: print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))

def status(args):
 emit({'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'monitor_exists':MONITOR.exists(),'email_script_exists':EMAIL.exists(),'guardrails':'no email/telegram send'},args)

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
 payload={'mode':'dry_run_preview_only','script':str(EMAIL),'reason':'Script semanal pode enviar email e payload externo; CLI v0.1 não executa. Use fluxo aprovado separado ou refatore geração do relatório sem envio.','safe_source':str(MONITOR)}
 emit(payload,args)

def guardrails(args):
 emit({'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No email send.','No Telegram send.','No force weekly delivery.','PNCP search is read-only.']},args)

def parser():
 p=argparse.ArgumentParser(prog='pcs-licita',description='CLI PCS licitações read-only')
 sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('search'); s.add_argument('--uf'); s.add_argument('--dias',type=int,default=14); s.add_argument('--valores',action='store_true'); s.add_argument('--timeout',type=int,default=300); s.add_argument('--json',action='store_true'); s.set_defaults(func=search)
 s=sub.add_parser('weekly'); ss=s.add_subparsers(dest='subcmd',required=True); r=ss.add_parser('preview'); r.add_argument('--json',action='store_true'); r.set_defaults(func=weekly)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p

def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if any(a.lower() in BLOCKED for a in argv): raise SystemExit('Blocked: pcs-licita v0.1 is read-only. No email/Telegram/send.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
