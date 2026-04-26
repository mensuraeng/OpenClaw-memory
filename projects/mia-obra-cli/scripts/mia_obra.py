#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={'status_guard':WORKSPACE/'scripts/ccsp_status_guard.py','weekly':WORKSPACE/'scripts/ccsp_relatorio_semanal.py','manha_victor':WORKSPACE/'scripts/ccsp_manha_victor.py','rdo':WORKSPACE/'scripts/ccsp_rdo_cobranca.py'}
CONFIRM='AUTORIZO MIA OBRA'
BLOCKED_TOP={'delete','remove','telegram'}

def emit(x,args): print(json.dumps(x,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else json.dumps(x,ensure_ascii=False,indent=2,default=str))
def run(cmd,timeout=120):
 cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
 return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
def status(args): emit({'mode':'controlled_v0.2','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()},'guardrails':'dry-run default; internal email only with explicit Alexandre authorization','confirm_phrase':CONFIRM},args)
def classify(args):
 sys.path.insert(0,str(WORKSPACE/'scripts')); import ccsp_status_guard as g
 text=Path(args.file).read_text(encoding='utf-8') if args.file else args.text
 if text is None: raise SystemExit('Informe --text ou --file')
 try: g.assert_not_legacy_status_text(text); emit({'ok':True,'classification':g.classify_ccsp_message(text),'mode':'read_only'},args)
 except Exception as e: emit({'ok':False,'blocked':True,'error':str(e),'mode':'read_only'},args); raise SystemExit(2)
def _auth(args):
 missing=[]
 if (args.approved_by or '').strip().lower() not in {'alexandre','alê','ale','alexandre aguiar'}: missing.append('--approved-by Alexandre')
 if (args.confirm or '').strip()!=CONFIRM: missing.append(f'--confirm "{CONFIRM}"')
 if not args.approval_note or len(args.approval_note.strip())<12: missing.append('--approval-note')
 if missing: emit({'mode':'blocked_missing_authorization','missing':missing,'rule':'Email MIA Obra só sob ordem explícita do Alê/Alexandre.'},args); raise SystemExit(2)
def _script_cmd(kind, execute):
 if kind=='rdo':
  cmd=['python3',str(SCRIPTS['rdo']),'--no-pull']
 else:
  cmd=['python3',str(SCRIPTS[kind])]
 if not execute: cmd.append('--dry-run')
 return cmd
def controlled_script(args,kind):
 execute=bool(args.execute)
 if execute: _auth(args)
 cmd=_script_cmd(kind,execute)
 res=run(cmd,args.timeout)
 emit({'mode':'authorized_execute_result' if execute else 'dry_run_result','execute':execute,'kind':kind,'ok':res['ok'],'code':res['code'],'cmd':cmd,'stdout':res['stdout'][-6000:],'stderr':res['stderr'][-6000:]},args)
 if not res['ok']: raise SystemExit(res['code'])
def manha(args): controlled_script(args,'manha_victor')
def rdo(args): controlled_script(args,'rdo')
def weekly(args):
 execute=bool(args.execute)
 if execute: _auth(args)
 cmd=['python3',str(SCRIPTS['weekly'])]
 res=run(cmd,args.timeout) if execute else {'ok':True,'code':0,'stdout':'weekly real dispatch blocked in dry-run; script has no --dry-run pure generator yet.','stderr':'','cmd':cmd}
 emit({'mode':'authorized_execute_result' if execute else 'preview_only','execute':execute,'kind':'weekly','ok':res['ok'],'code':res['code'],'cmd':cmd,'stdout':res['stdout'][-6000:],'stderr':res['stderr'][-6000:]},args)
 if not res['ok']: raise SystemExit(res['code'])
def guardrails(args): emit({'mode':'controlled_v0.2','confirm_phrase':CONFIRM,'rules':['Dry-run é padrão.','Emails internos CCSP podem rodar com --execute + approved-by + confirm + approval-note.','Sem Telegram direto.','Guardrail CCSP continua bloqueando status legado.']},args)
def add_auth(x):
 x.add_argument('--execute',action='store_true'); x.add_argument('--approved-by'); x.add_argument('--confirm'); x.add_argument('--approval-note'); x.add_argument('--timeout',type=int,default=180); x.add_argument('--json',action='store_true')
def parser():
 p=argparse.ArgumentParser(prog='mia-obra',description='CLI MIA obra/CCSP controlled')
 sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('ccsp'); ss=s.add_subparsers(dest='subcmd',required=True)
 c=ss.add_parser('classify'); c.add_argument('--text'); c.add_argument('--file'); c.add_argument('--json',action='store_true'); c.set_defaults(func=classify)
 for name,func in [('weekly-send-authorized',weekly),('manha-send-authorized',manha),('rdo-send-authorized',rdo)]:
  x=ss.add_parser(name); add_auth(x); x.set_defaults(func=func)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p
def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED_TOP: raise SystemExit('Blocked: mia-obra v0.2 only allows controlled CCSP subcommands.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
