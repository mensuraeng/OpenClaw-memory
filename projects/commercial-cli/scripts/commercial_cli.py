#!/usr/bin/env python3
"""commercial — CLI read-only para marketing/comercial Mensura/MIA."""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import Any

WORKSPACE=Path('/root/.openclaw/workspace')
LINKEDIN=WORKSPACE/'projects/openclaw-linkedin'
GA4=WORKSPACE/'projects/ga4-reports/ga4_client.py'
SCRIPTS={
 'monitoramento_comercial': WORKSPACE/'scripts/monitoramento_comercial_mensura.py',
 'operacional_marketing': WORKSPACE/'scripts/operacional_marketing_mensura.py',
 'revisao_tecnica': WORKSPACE/'scripts/revisao_tecnica_mensura.py',
}
CONFIGS={
 'hubspot': WORKSPACE/'config/hubspot-mensura.json',
 'phantombuster': WORKSPACE/'config/phantombuster-mensura.json',
 'linkedin_pages_example': LINKEDIN/'config/pages.example.json',
 'ga4_service_account': WORKSPACE/'credentials/ga4-service-account.json',
}
BLOCKED={'publish','post','send','enviar','telegram','email','live','upload','delete','remove'}


def run(cmd:list[str], cwd:Path|None=None, timeout:int=60)->dict[str,Any]:
    try:
        cp=subprocess.run(cmd,cwd=str(cwd) if cwd else None,text=True,capture_output=True,timeout=timeout)
        return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
    except Exception as e:
        return {'ok':False,'error':str(e),'cmd':cmd}


def output(payload,args):
    if getattr(args,'json',False): print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
    else:
        if isinstance(payload,dict) and 'lines' in payload:
            print('\n'.join(payload['lines']))
        else: print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))


def cmd_status(args):
    payload={'mode':'read_only_v0.1','time':datetime.now().isoformat(timespec='seconds'),'configs':{k:v.exists() for k,v in CONFIGS.items()},'scripts':{k:str(v) for k,v in SCRIPTS.items()},'guardrails':'no publish/send/live external action'}
    if args.json: output(payload,args)
    else:
        lines=['commercial status','- modo: read-only']+[f"- {k}: {exists}" for k,exists in payload['configs'].items()]
        output({'lines':lines},args)


def cmd_pipeline(args):
    payload={'mode':'dry_run_blocked','reason':'Scripts comerciais atuais coletam dados e enviam Telegram; v0.1 não executa side effects.','scripts':{k:str(v) for k,v in SCRIPTS.items()},'next_step':'Refatorar coleta HubSpot/Phantombuster para função read-only antes de habilitar report real.'}
    output(payload,args)


def cmd_linkedin_check(args):
    res=run(['node','scripts/check_config.js'],cwd=LINKEDIN,timeout=args.timeout)
    payload={'ok':res.get('ok'), 'code':res.get('code'), 'stdout':res.get('stdout','').strip(), 'stderr':res.get('stderr','').strip(), 'mode':'read_only'}
    output(payload,args)
    if not res.get('ok'): raise SystemExit(res.get('code') or 1)


def cmd_linkedin_preview(args):
    text=Path(args.file).read_text(encoding='utf-8') if args.file else args.text
    if not text:
        raise SystemExit('Informe --text ou --file')
    payload={'mode':'preview_only','chars':len(text),'preview':text[:args.limit],'note':'Preview local apenas; não publica.'}
    output(payload,args)


def cmd_ga4_status(args):
    payload={'mode':'read_only','client_exists':GA4.exists(),'service_account_exists':CONFIGS['ga4_service_account'].exists(),'note':'summary real será habilitado com wrapper JSON dedicado; v0.1 não imprime credenciais.'}
    output(payload,args)


def cmd_guardrails(args):
    payload={'mode':'read_only_v0.1','blocked':sorted(BLOCKED),'rules':['No LinkedIn/Instagram/Telegram/email publishing.','No live post scripts.','Pipeline scripts with Telegram side effects are blocked until refactored.','Only previews, config checks and read-only status.']}
    output(payload,args)


def parser():
    p=argparse.ArgumentParser(prog='commercial',description='CLI comercial/marketing read-only')
    sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_status)
    s=sub.add_parser('pipeline'); ss=s.add_subparsers(dest='subcmd',required=True); r=ss.add_parser('report'); r.add_argument('--json',action='store_true'); r.set_defaults(func=cmd_pipeline)
    s=sub.add_parser('linkedin'); ss=s.add_subparsers(dest='subcmd',required=True)
    c=ss.add_parser('check-config'); c.add_argument('--json',action='store_true'); c.add_argument('--timeout',type=int,default=60); c.set_defaults(func=cmd_linkedin_check)
    pvw=ss.add_parser('preview'); pvw.add_argument('--text'); pvw.add_argument('--file'); pvw.add_argument('--limit',type=int,default=2000); pvw.add_argument('--json',action='store_true'); pvw.set_defaults(func=cmd_linkedin_preview)
    s=sub.add_parser('ga4'); ss=s.add_subparsers(dest='subcmd',required=True); g=ss.add_parser('status'); g.add_argument('--json',action='store_true'); g.set_defaults(func=cmd_ga4_status)
    s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_guardrails)
    return p


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if any(a.lower() in BLOCKED for a in argv[:4]):
        raise SystemExit('Blocked: commercial v0.1 is preview/read-only. No publish/send/live action.')
    args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
