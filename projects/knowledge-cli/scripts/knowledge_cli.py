#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={k:WORKSPACE/'scripts'/v for k,v in {'docling_convert':'docling_converter.py','docling_ingest':'docling_ingest.py','rag_query':'rag_query.py','notion_sync':'notion_sync.py','nblm_sync':'nblm_sync.py','sync_knowledge':'sync_knowledge.py'}.items()}
CONFIRM='AUTORIZO KNOWLEDGE'
BLOCKED_TOP={'delete','send','upload'}

def emit(x,args): print(json.dumps(x,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else ('\n'.join(x['lines']) if isinstance(x,dict) and 'lines' in x else json.dumps(x,ensure_ascii=False,indent=2,default=str)))
def run(cmd,timeout=600):
 cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
 return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
def status(args): emit({'mode':'controlled_v0.2','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()},'guardrails':'inventory/read-only default; sync only with explicit Alexandre authorization','confirm_phrase':CONFIRM},args)
def inventory(args):
 roots=[WORKSPACE/'docs',WORKSPACE/'memory',Path('/root/2nd-brain')]; files=[]
 for r in roots:
  if r.exists():
   for p in r.rglob('*'):
    if p.is_file() and '.git' not in p.parts and p.suffix.lower() in {'.md','.json','.txt','.pdf','.docx','.xlsx'}: files.append({'path':str(p),'suffix':p.suffix.lower(),'size':p.stat().st_size})
 emit({'mode':'read_only','count':len(files),'files':files[:args.limit]},args)
def _auth(args):
 missing=[]
 if (args.approved_by or '').strip().lower() not in {'alexandre','alê','ale','alexandre aguiar'}: missing.append('--approved-by Alexandre')
 if (args.confirm or '').strip()!=CONFIRM: missing.append(f'--confirm "{CONFIRM}"')
 if not args.approval_note or len(args.approval_note.strip())<12: missing.append('--approval-note')
 if missing: emit({'mode':'blocked_missing_authorization','missing':missing,'rule':'Knowledge sync/ingest só sob ordem explícita do Alê/Alexandre.'},args); raise SystemExit(2)
def sync_authorized(args,script_key):
 execute=bool(args.execute)
 if execute: _auth(args)
 script=SCRIPTS[script_key]
 cmd=['python3',str(script)]
 if not execute:
  emit({'mode':'preview_only','execute':False,'script':str(script),'note':'Sem --execute, não roda sync/ingest real.'},args); return
 res=run(cmd,args.timeout)
 emit({'mode':'authorized_execute_result','execute':True,'script':str(script),'ok':res['ok'],'code':res['code'],'stdout':res['stdout'][-8000:],'stderr':res['stderr'][-8000:]},args)
 if not res['ok']: raise SystemExit(res['code'])
def notion(args): sync_authorized(args,'notion_sync')
def notebook_run(args): sync_authorized(args,'nblm_sync')
def knowledge_sync(args): sync_authorized(args,'sync_knowledge')
def notebook_status(args): emit({'mode':'status_only','script':str(SCRIPTS['nblm_sync']),'exists':SCRIPTS['nblm_sync'].exists(),'note':'Use notebooklm sync-authorized para execução real.'},args)
def rag(args):
 if not args.query: raise SystemExit('Informe query')
 emit({'mode':'preview_only','query':args.query,'note':'rag_query real pode depender de embeddings; execução real não habilitada neste subcomando.'},args)
def guardrails(args): emit({'mode':'controlled_v0.2','confirm_phrase':CONFIRM,'rules':['Inventory/read-only por padrão.','Notion/NotebookLM/sync_knowledge podem rodar com --execute + approved-by + confirm + approval-note.','Sem delete/upload/send.','Não versionar segredos.']},args)
def add_auth(x):
 x.add_argument('--execute',action='store_true'); x.add_argument('--approved-by'); x.add_argument('--confirm'); x.add_argument('--approval-note'); x.add_argument('--timeout',type=int,default=600); x.add_argument('--json',action='store_true')
def parser():
 p=argparse.ArgumentParser(prog='knowledge'); sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('inventory'); s.add_argument('--limit',type=int,default=80); s.add_argument('--json',action='store_true'); s.set_defaults(func=inventory)
 s=sub.add_parser('notion'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('sync-authorized'); add_auth(x); x.set_defaults(func=notion)
 s=sub.add_parser('notebooklm'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('status'); x.add_argument('--json',action='store_true'); x.set_defaults(func=notebook_status); y=ss.add_parser('sync-authorized'); add_auth(y); y.set_defaults(func=notebook_run)
 s=sub.add_parser('sync-authorized'); add_auth(s); s.set_defaults(func=knowledge_sync)
 s=sub.add_parser('rag'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('query-preview'); x.add_argument('query'); x.add_argument('--json',action='store_true'); x.set_defaults(func=rag)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p
def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED_TOP: raise SystemExit('Blocked: knowledge v0.2 only allows controlled sync subcommands.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
