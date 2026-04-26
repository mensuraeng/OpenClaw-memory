#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from datetime import datetime
from pathlib import Path
WORKSPACE=Path('/root/.openclaw/workspace')
SCRIPTS={k:WORKSPACE/'scripts'/v for k,v in {'docling_convert':'docling_converter.py','docling_ingest':'docling_ingest.py','rag_query':'rag_query.py','notion_sync':'notion_sync.py','nblm_sync':'nblm_sync.py','sync_knowledge':'sync_knowledge.py'}.items()}
BLOCKED={'sync','ingest','write','delete','promote','send','upload'}
def emit(x,args): print(json.dumps(x,ensure_ascii=False,indent=2,default=str) if getattr(args,'json',False) else ('\n'.join(x['lines']) if isinstance(x,dict) and 'lines' in x else json.dumps(x,ensure_ascii=False,indent=2,default=str)))
def status(args): emit({'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'scripts':{k:{'path':str(v),'exists':v.exists()} for k,v in SCRIPTS.items()},'guardrails':'mutating sync/ingest blocked'},args)
def inventory(args):
 roots=[WORKSPACE/'docs',WORKSPACE/'memory',Path('/root/2nd-brain')]
 files=[]
 for r in roots:
  if r.exists():
   for p in r.rglob('*'):
    if p.is_file() and '.git' not in p.parts and p.suffix.lower() in {'.md','.json','.txt','.pdf','.docx','.xlsx'}:
     files.append({'path':str(p),'suffix':p.suffix.lower(),'size':p.stat().st_size})
 emit({'mode':'read_only','count':len(files),'files':files[:args.limit]},args)
def notion(args): emit({'mode':'dry_run_blocked','script':str(SCRIPTS['notion_sync']),'reason':'notion_sync altera 2nd-brain/local reports; CLI v0.1 não executa. Refatorar preview/diff antes.'},args)
def notebook(args): emit({'mode':'status_only','script':str(SCRIPTS['nblm_sync']),'exists':SCRIPTS['nblm_sync'].exists(),'note':'sync real bloqueado no v0.1.'},args)
def rag(args):
 if not args.query: raise SystemExit('Informe query')
 emit({'mode':'preview_only','query':args.query,'note':'rag_query real pode depender de embeddings atualmente bloqueados; v0.1 não executa.'},args)
def guardrails(args): emit({'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No Notion/NotebookLM sync real.','No memory promotion.','No ingest/write mutation.','Inventory and previews only.']},args)
def parser():
 p=argparse.ArgumentParser(prog='knowledge'); sub=p.add_subparsers(dest='cmd',required=True)
 s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=status)
 s=sub.add_parser('inventory'); s.add_argument('--limit',type=int,default=80); s.add_argument('--json',action='store_true'); s.set_defaults(func=inventory)
 s=sub.add_parser('notion'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('sync-preview'); x.add_argument('--json',action='store_true'); x.set_defaults(func=notion)
 s=sub.add_parser('notebooklm'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('status'); x.add_argument('--json',action='store_true'); x.set_defaults(func=notebook)
 s=sub.add_parser('rag'); ss=s.add_subparsers(dest='subcmd',required=True); x=ss.add_parser('query-preview'); x.add_argument('query'); x.add_argument('--json',action='store_true'); x.set_defaults(func=rag)
 s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=guardrails)
 return p
def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0].lower() in BLOCKED: raise SystemExit('Blocked: knowledge v0.1 is read-only/preview only.')
 args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
