#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={
 'status_guard': WORKSPACE/'scripts/ccsp_status_guard.py',
 'weekly': WORKSPACE/'scripts/ccsp_relatorio_semanal.py',
 'manha_victor': WORKSPACE/'scripts/ccsp_manha_victor.py',
 'rdo': WORKSPACE/'scripts/ccsp_rdo_cobranca.py',
}
BLOCKED={'send','email','telegram','enviar','force','delete','remove'}

def emit(x,args):
 if getattr(args,'json',False): print(json.dumps(x,ensure_ascii=False,indent=2,default=str))
 else: print('\n'.join(x['lines']) if isinstance(x,dict) and 'lines' in x else json.dumps(x,ensure_ascii=False,indent=2,default=str))

def run(cmd,timeout=120):
 cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
 return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}

def status(args): emit({'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()},'guardrails':'no email/Telegram/send'},args)

def classify(args):
 sys.path.insert(0,str(WORKSPACE/'scripts'))
 import ccsp_status_guard as g
 text=Path(args.file).read_text(encoding='utf-8') if args.file else args.text
 if text is None: raise SystemExit('Informe --text ou --file')
 try:
  g.assert_not_legacy_status_text(text)
  kind=g.classify_ccsp_message(text)
  emit({'ok':True,'classification':kind,'mode':'read_only'},args)
 except Exception as e:
  emit({'ok':False,'blocked':True,'error':str(e),'mode':'read_only'},args); raise SystemExit(2)

def weekly(args):
 payload={'mode':'preview_only_blocked','script':str(SCRIPTS['weekly']),'reason':'Script entrega payload à Flávia; CLI v0.1 não dispara fluxo externo/sessão. Use apenas como referência até separar geração pura do envio.'}
 emit(payload,args)

def dry_script(args, key):
 script=SCRIPTS[key]
 cmd=['python3',str(script),'--dry-run','--no-pull'] if key=='rdo' else ['python3',str(script),'--dry-run']
 res=run(cmd,args.timeout)
 emit({'mode':'dry_run','ok':res['ok'],'code':res['code'],'stdout':res['stdout'][-4000:],'stderr':res['stderr'][-4000:]},args)
 if not res['ok']: raise SystemExit(res['code'])

def manha(args): dry_script(args,'manha_victor')
def rdo(args): dry_script(args,'rdo')
def guardrails(args): emit({'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No external email/Telegram send from CLI.','CCSP status guard can classify/block text.','Morning/RDO only via --dry-run wrappers.','Weekly report dispatch remains blocked until pure generator exists.']},args)

def parser():
 p=argparse.ArgumentParser(prog='mia-obra',description='CLI MIA obra/CCSP read-only')
 sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('ccsp'); ss=s.add_subparsers(dest='subcmd',required=True)
 c=ss.add_parser('classify'); c.add_argument('--text'); c.add_argument('--file'); c.add_argument('--json',action='store_true'); c.set_defaults(func=classify)
 w=ss.add_parser('weekly-preview'); w.add_argument('--json',action='store_true'); w.set_defaults(func=weekly)
 m=ss.add_parser('manha-dry-run'); m.add_argument('--json',action='store_true'); m.add_argument('--timeout',type=int,default=120); m.set_defaults(func=manha)
 r=ss.add_parser('rdo-dry-run'); r.add_argument('--json',action='store_true'); r.add_argument('--timeout',type=int,default=120); r.set_defaults(func=rdo)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p

def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if any(a.lower() in BLOCKED for a in argv): raise SystemExit('Blocked: mia-obra v0.1 is read-only/dry-run only. No external send.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
