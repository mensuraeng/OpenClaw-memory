#!/usr/bin/env python3
"""commercial — CLI automática/controlada para marketing/comercial Mensura/MIA."""
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
BLOCKED_TOP={'delete','remove','upload'}
DEFAULT_PERSON_ID='JYAsCudAAE'


def run(cmd:list[str], cwd:Path|None=None, timeout:int=60)->dict[str,Any]:
    try:
        cp=subprocess.run(cmd,cwd=str(cwd) if cwd else None,text=True,capture_output=True,timeout=timeout)
        return {'ok':cp.returncode==0,'code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'cmd':cmd}
    except Exception as e:
        return {'ok':False,'code':1,'error':str(e),'cmd':cmd}


def output(payload,args):
    if getattr(args,'json',False): print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))
    else:
        if isinstance(payload,dict) and 'lines' in payload:
            print('\n'.join(payload['lines']))
        else: print(json.dumps(payload,ensure_ascii=False,indent=2,default=str))


def cmd_status(args):
    payload={'mode':'automatic_v0.3','time':datetime.now().isoformat(timespec='seconds'),'configs':{k:v.exists() for k,v in CONFIGS.items()},'scripts':{k:str(v) for k,v in SCRIPTS.items()},'guardrails':'automatic commercial/LinkedIn routines allowed; destructive actions blocked'}
    if args.json: output(payload,args)
    else:
        lines=['commercial status','- modo: automatic_v0.3']+[f"- {k}: {exists}" for k,exists in payload['configs'].items()]
        output({'lines':lines},args)


def cmd_pipeline(args):
    if not args.execute:
        payload={'mode':'preview_only','execute':False,'script':str(SCRIPTS['monitoramento_comercial']),'note':'Use --execute para enviar o relatório comercial automático no Telegram Mensura.'}
        output(payload,args); return
    res=run(['python3',str(SCRIPTS['monitoramento_comercial'])],timeout=args.timeout)
    payload={'mode':'automatic_execute_result','kind':'pipeline_report','ok':res.get('ok'),'code':res.get('code'),'cmd':res.get('cmd'),'stdout':res.get('stdout','')[-8000:],'stderr':res.get('stderr','')[-8000:],'error':res.get('error')}
    output(payload,args)
    if not res.get('ok'): raise SystemExit(res.get('code') or 1)


def cmd_marketing_daily(args):
    if not args.execute:
        payload={'mode':'preview_only','execute':False,'script':str(SCRIPTS['operacional_marketing']),'note':'Use --execute para enviar o prompt operacional automático ao Marketing.'}
        output(payload,args); return
    res=run(['python3',str(SCRIPTS['operacional_marketing'])],timeout=args.timeout)
    payload={'mode':'automatic_execute_result','kind':'marketing_daily','ok':res.get('ok'),'code':res.get('code'),'cmd':res.get('cmd'),'stdout':res.get('stdout','')[-8000:],'stderr':res.get('stderr','')[-8000:],'error':res.get('error')}
    output(payload,args)
    if not res.get('ok'): raise SystemExit(res.get('code') or 1)


def cmd_linkedin_check(args):
    res=run(['node','scripts/check_config.js'],cwd=LINKEDIN,timeout=args.timeout)
    payload={'ok':res.get('ok'), 'code':res.get('code'), 'stdout':res.get('stdout','').strip(), 'stderr':res.get('stderr','').strip(), 'mode':'read_only'}
    output(payload,args)
    if not res.get('ok'): raise SystemExit(res.get('code') or 1)


def _read_post_text(args)->str:
    text=Path(args.file).read_text(encoding='utf-8') if args.file else args.text
    if not text: raise SystemExit('Informe --text ou --file')
    text='\n'.join(line.rstrip() for line in text.replace('\r\n','\n').replace('\r','\n').split('\n')).strip()
    if len(text) < 80: raise SystemExit('Post muito curto; bloqueado para evitar publicação acidental.')
    return text


def cmd_linkedin_preview(args):
    text=_read_post_text(args)
    res=run(['node','scripts/render_linkedin_preview.js',text],cwd=LINKEDIN,timeout=args.timeout)
    payload={'mode':'preview_only','chars':len(text),'ok':res.get('ok'),'preview_stdout':res.get('stdout','')[-8000:],'stderr':res.get('stderr','')[-4000:]}
    output(payload,args)
    if not res.get('ok'): raise SystemExit(res.get('code') or 1)


def cmd_linkedin_publish(args):
    text=_read_post_text(args)
    preview=run(['node','scripts/render_linkedin_preview.js',text],cwd=LINKEDIN,timeout=args.timeout)
    if not preview.get('ok'):
        output({'mode':'blocked_preview_failed','ok':False,'stderr':preview.get('stderr',''),'stdout':preview.get('stdout','')},args)
        raise SystemExit(preview.get('code') or 1)
    if not args.execute:
        dry=run(['node','scripts/test_personal_post_dryrun.js',text,args.person_id],cwd=LINKEDIN,timeout=args.timeout)
        output({'mode':'dry_run_result','execute':False,'chars':len(text),'ok':dry.get('ok'),'code':dry.get('code'),'stdout':dry.get('stdout','')[-8000:],'stderr':dry.get('stderr','')[-4000:]},args)
        if not dry.get('ok'): raise SystemExit(dry.get('code') or 1)
        return
    live=run(['node','scripts/test_personal_post_live.js',text,args.person_id],cwd=LINKEDIN,timeout=args.timeout)
    payload={'mode':'automatic_publish_result','execute':True,'chars':len(text),'ok':live.get('ok'),'code':live.get('code'),'stdout':live.get('stdout','')[-12000:],'stderr':live.get('stderr','')[-8000:]}
    output(payload,args)
    if not live.get('ok'): raise SystemExit(live.get('code') or 1)


def cmd_ga4_status(args):
    payload={'mode':'read_only','client_exists':GA4.exists(),'service_account_exists':CONFIGS['ga4_service_account'].exists(),'note':'status não imprime credenciais'}
    output(payload,args)


def cmd_guardrails(args):
    payload={'mode':'automatic_v0.3','blocked':sorted(BLOCKED_TOP),'rules':['LinkedIn pessoal e rotinas comerciais podem publicar/enviar automaticamente quando chamadas pelos subcomandos dedicados.','Sem delete/remove/upload.','LinkedIn publish-auto exige texto mínimo e faz preview antes do live post.','Páginas institucionais continuam pendentes de organization URN/admin antes de publicação por página.']}
    output(payload,args)


def parser():
    p=argparse.ArgumentParser(prog='commercial',description='CLI comercial/marketing automatic_v0.3')
    sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('status'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_status)
    s=sub.add_parser('pipeline'); ss=s.add_subparsers(dest='subcmd',required=True); r=ss.add_parser('report'); r.add_argument('--execute',action='store_true'); r.add_argument('--timeout',type=int,default=180); r.add_argument('--json',action='store_true'); r.set_defaults(func=cmd_pipeline)
    s=sub.add_parser('marketing'); ss=s.add_subparsers(dest='subcmd',required=True); d=ss.add_parser('daily'); d.add_argument('--execute',action='store_true'); d.add_argument('--timeout',type=int,default=180); d.add_argument('--json',action='store_true'); d.set_defaults(func=cmd_marketing_daily)
    s=sub.add_parser('linkedin'); ss=s.add_subparsers(dest='subcmd',required=True)
    c=ss.add_parser('check-config'); c.add_argument('--json',action='store_true'); c.add_argument('--timeout',type=int,default=60); c.set_defaults(func=cmd_linkedin_check)
    pvw=ss.add_parser('preview'); pvw.add_argument('--text'); pvw.add_argument('--file'); pvw.add_argument('--timeout',type=int,default=60); pvw.add_argument('--json',action='store_true'); pvw.set_defaults(func=cmd_linkedin_preview)
    pub=ss.add_parser('publish-auto'); pub.add_argument('--text'); pub.add_argument('--file'); pub.add_argument('--person-id',default=DEFAULT_PERSON_ID); pub.add_argument('--execute',action='store_true'); pub.add_argument('--timeout',type=int,default=90); pub.add_argument('--json',action='store_true'); pub.set_defaults(func=cmd_linkedin_publish)
    s=sub.add_parser('ga4'); ss=s.add_subparsers(dest='subcmd',required=True); g=ss.add_parser('status'); g.add_argument('--json',action='store_true'); g.set_defaults(func=cmd_ga4_status)
    s=sub.add_parser('guardrails'); s.add_argument('--json',action='store_true'); s.set_defaults(func=cmd_guardrails)
    return p


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0].lower() in BLOCKED_TOP:
        raise SystemExit('Blocked: destructive commercial action is not allowed.')
    args=parser().parse_args(argv); args.func(args)
if __name__=='__main__': main()
