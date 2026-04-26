#!/usr/bin/env python3
"""msgraph — CLI agent-native read-only para Microsoft Graph.

Encapsula os scripts locais existentes com guardrails: sem envio, sem mover email,
sem criar/deletar evento no v0.1.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Any

WORKSPACE=Path('/root/.openclaw/workspace')
EMAIL=WORKSPACE/'scripts/msgraph_email.py'
CAL=WORKSPACE/'scripts/msgraph_calendar.py'
HEALTH=WORKSPACE/'scripts/msgraph_healthcheck.py'
CONFIGS={
 'mensura': WORKSPACE/'config/ms-graph.json',
 'mia': WORKSPACE/'config/ms-graph-mia.json',
 'pcs': WORKSPACE/'config/ms-graph-pcs.json',
}
BLOCKED={'send','enviar','move','mover','create','criar','delete','deletar','remove','remover','calendar-create','calendar-delete','email-send','email-move'}


def run(cmd:list[str], timeout:int=60)->dict[str,Any]:
    try:
        cp=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
        return {'ok':cp.returncode==0,'code':cp.returncode,'cmd':cmd,'stdout':cp.stdout,'stderr':cp.stderr}
    except subprocess.TimeoutExpired as e:
        return {'ok':False,'cmd':cmd,'error':f'timeout after {timeout}s','stdout':e.stdout or '','stderr':e.stderr or ''}
    except Exception as e:
        return {'ok':False,'cmd':cmd,'error':str(e)}


def safe_cmd_repr(cmd:list[str])->list[str]:
    return [str(x) for x in cmd]


def output_result(res:dict[str,Any], args, title:str):
    payload={k:v for k,v in res.items() if k!='cmd'}
    payload['title']=title
    payload['cmd']=safe_cmd_repr(res.get('cmd',[]))
    if getattr(args,'json',False):
        print(json.dumps(payload,ensure_ascii=False,indent=2))
    else:
        if not res.get('ok'):
            print(f"FAIL {title}")
            if res.get('error'): print(res['error'])
            if res.get('stderr'): print(res['stderr'].strip()[-4000:])
            if res.get('stdout'): print(res['stdout'].strip()[-4000:])
            raise SystemExit(res.get('code') or 1)
        print(res.get('stdout','').strip() or f'OK {title}')


def cmd_status(args):
    cfg=[]
    for name,path in CONFIGS.items():
        exists=path.exists()
        default_user=None
        if exists:
            try:
                data=json.loads(path.read_text())
                default_user=data.get('defaultUser')
            except Exception:
                default_user='[config unreadable]'
        cfg.append({'account':name,'config_exists':exists,'default_user':default_user,'path':str(path)})
    payload={'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'scripts':{'email':str(EMAIL),'calendar':str(CAL),'health':str(HEALTH)},'configs':cfg,'guardrails':'send/move/create/delete blocked'}
    if args.json: print(json.dumps(payload,ensure_ascii=False,indent=2))
    else:
        print('msgraph status')
        print('- modo: read-only')
        for c in cfg: print(f"- {c['account']}: config={c['config_exists']} default_user={c['default_user']}")


def cmd_health(args):
    res=run(['python3',str(HEALTH)],timeout=args.timeout)
    output_result(res,args,'msgraph health')


def cmd_inbox_list(args):
    cmd=['python3',str(EMAIL),'list','--account',args.account,'--folder',args.folder,'--limit',str(args.limit)]
    if args.user: cmd += ['--user',args.user]
    res=run(cmd,timeout=args.timeout)
    output_result(res,args,'inbox list')


def cmd_inbox_read(args):
    cmd=['python3',str(EMAIL),'read','--account',args.account,'--id',args.id]
    if args.user: cmd += ['--user',args.user]
    res=run(cmd,timeout=args.timeout)
    output_result(res,args,'inbox read')


def cmd_inbox_folders(args):
    cmd=['python3',str(EMAIL),'folders','--account',args.account]
    if args.user: cmd += ['--user',args.user]
    res=run(cmd,timeout=args.timeout)
    output_result(res,args,'inbox folders')


def cmd_calendar_list(args):
    cmd=['python3',str(CAL),'list','--account',args.account,'--days',str(args.days)]
    if args.user: cmd += ['--user',args.user]
    res=run(cmd,timeout=args.timeout)
    output_result(res,args,'calendar list')


def cmd_guardrails(args):
    payload={'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'allowed':['status','health','inbox list','inbox read','inbox folders','calendar list','guardrails'],'rules':['No email send.','No email move/archive/delete.','No calendar create/delete/update.','No attachment download in v0.1 until destination policy is defined.','No secrets printed.']}
    if args.json: print(json.dumps(payload,ensure_ascii=False,indent=2))
    else:
        print('msgraph guardrails')
        for r in payload['rules']: print(f'- {r}')


def parser():
    p=argparse.ArgumentParser(prog='msgraph',description='CLI Microsoft Graph read-only v0.1')
    sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_status)
    s=sub.add_parser('health'); s.add_argument('--json',action='store_true'); s.add_argument('--timeout',type=int,default=90); s.set_defaults(func=cmd_health)
    s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_guardrails)
    s=sub.add_parser('inbox'); ss=s.add_subparsers(dest='subcmd',required=True)
    for name,func in [('list',cmd_inbox_list),('read',cmd_inbox_read),('folders',cmd_inbox_folders)]:
        x=ss.add_parser(name); x.add_argument('--account',choices=['mensura','mia','pcs'],default='mensura'); x.add_argument('--user'); x.add_argument('--timeout',type=int,default=90); x.add_argument('--json',action='store_true'); x.set_defaults(func=func)
        if name=='list': x.add_argument('--folder',default='inbox'); x.add_argument('--limit',type=int,default=10)
        if name=='read': x.add_argument('--id',required=True)
    s=sub.add_parser('calendar'); ss=s.add_subparsers(dest='subcmd',required=True)
    x=ss.add_parser('list'); x.add_argument('--account',choices=['mensura','mia','pcs'],default='mensura'); x.add_argument('--user'); x.add_argument('--days',type=int,default=7); x.add_argument('--timeout',type=int,default=90); x.add_argument('--json',action='store_true'); x.set_defaults(func=cmd_calendar_list)
    return p


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() in BLOCKED:
        raise SystemExit('Blocked: msgraph v0.1 is read-only. No send/move/create/delete.')
    if any(a.lower() in BLOCKED for a in argv[:3]):
        raise SystemExit('Blocked: msgraph v0.1 is read-only. No send/move/create/delete.')
    args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
