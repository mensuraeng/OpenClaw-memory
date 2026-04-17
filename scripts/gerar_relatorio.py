#!/usr/bin/env python3
"""
gerar_relatorio.py — orquestra a geração e publicação de relatório
                     semanal de obra (template React → build → upload).

Fluxo:
1. Localiza o repo do template da obra (mapping em OBRAS).
2. Roda npm run build no template (consome src/data/relatorio.json).
3. Copia dist/ para openclaw-context/relatorios/<dominio>/<obra>/
   <YYYY-MM-DD_semana-NNN_<obra>>/
4. git add + commit + push no repo openclaw-context.
5. Verifica se GitHub Pages está respondendo (HEAD na URL).
6. Notifica a Flávia via send_to_flavia com payload incluindo
   github_url + github_pages_url.

Flags:
  --obra <nome>      obrigatório (ex.: pg-louveira)
  --dry-run          não faz build, push nem notificação. Só valida e mostra plano.
  --skip-upload      faz build mas não copia/sobe para openclaw-context.
  --skip-flavia      pula notificação à Flávia.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
KNOWLEDGE = os.path.join(WORKSPACE, "knowledge")
CONTEXT_REPO = os.path.join(KNOWLEDGE, "openclaw-context")
LOG_DIR = os.path.join(WORKSPACE, "logs", "cron")
LOG_FILE = os.path.join(LOG_DIR, "upload-relatorios.log")

OBRAS = {
    "pg-louveira": {
        "dominio": "mensura",
        "repo_dir": os.path.join(KNOWLEDGE, "P-G---Louveira"),
        "data_file": "src/data/relatorio.json",
        "pages_url": "https://mensuraeng.github.io/P-G---Louveira/",
        "github_repo": "mensuraeng/P-G---Louveira",
    },
}


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    sys.stderr.write(line + "\n")
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def load_relatorio_meta(repo_dir: str, data_rel: str) -> dict:
    full = os.path.join(repo_dir, data_rel)
    if not os.path.exists(full):
        raise FileNotFoundError(f"data file não encontrado: {full}")
    with open(full, encoding="utf-8") as f:
        data = json.load(f)
    meta = data.get("meta") or {}
    if not meta.get("data") or not meta.get("semana"):
        raise ValueError(f"data file sem meta.data ou meta.semana: {full}")
    return meta


def normalize_semana(semana_raw) -> str:
    """'002' / '2' / 2 → '002' (zero-pad 3 dígitos)."""
    s = str(semana_raw).strip().lstrip("S").lstrip("s")
    s = "".join(ch for ch in s if ch.isdigit())
    if not s:
        s = "0"
    return s.zfill(3)


def build_template(repo_dir: str, dry_run: bool) -> int:
    if dry_run:
        log(f"[dry-run] pularia 'npm run build' em {repo_dir}")
        return 0
    log(f"npm run build em {repo_dir} ...")
    try:
        r = subprocess.run(
            ["npm", "run", "build"],
            cwd=repo_dir, capture_output=True, text=True, timeout=300,
        )
    except FileNotFoundError:
        log("ERRO: npm não encontrado no PATH")
        return 1
    except subprocess.TimeoutExpired:
        log("ERRO: timeout no npm run build")
        return 1
    if r.stdout:
        for line in r.stdout.strip().splitlines()[-12:]:
            log(f"  npm: {line}")
    if r.returncode != 0:
        log(f"ERRO npm build (rc={r.returncode}): {r.stderr.strip()[:500]}")
        return r.returncode
    return 0


def copy_dist(repo_dir: str, dest_dir: str, dry_run: bool) -> int:
    src = os.path.join(repo_dir, "dist")
    if dry_run:
        log(f"[dry-run] copiaria {src} → {dest_dir}")
        return 0
    if not os.path.isdir(src):
        log(f"ERRO: {src} não existe (build falhou?)")
        return 1
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src, dest_dir)
    n_files = sum(len(files) for _, _, files in os.walk(dest_dir))
    log(f"copiado {src} → {dest_dir} ({n_files} arquivo(s))")
    return 0


def git_publish(commit_msg: str, dry_run: bool) -> int:
    if dry_run:
        log(f"[dry-run] git add + commit + push em {CONTEXT_REPO}")
        log(f"[dry-run]   mensagem: {commit_msg}")
        return 0
    try:
        subprocess.run(["git", "-C", CONTEXT_REPO, "add", "."],
                       check=True, capture_output=True, text=True, timeout=30)
        r = subprocess.run(["git", "-C", CONTEXT_REPO, "commit", "-m", commit_msg],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            if "nothing to commit" in r.stdout.lower() or "nothing to commit" in r.stderr.lower():
                log("nada novo para commitar (idempotente)")
                return 0
            log(f"ERRO git commit (rc={r.returncode}): {r.stderr.strip()[:300]}")
            return r.returncode
        log(f"commit ok: {r.stdout.strip().splitlines()[0] if r.stdout.strip() else commit_msg}")
        rp = subprocess.run(["git", "-C", CONTEXT_REPO, "push"],
                            capture_output=True, text=True, timeout=60)
        if rp.returncode != 0:
            log(f"ERRO git push (rc={rp.returncode}): {rp.stderr.strip()[:300]}")
            return rp.returncode
        log("push ok")
        return 0
    except subprocess.CalledProcessError as e:
        log(f"ERRO subprocess git: {e}")
        return 1


def check_pages(url: str, dry_run: bool) -> str:
    """Retorna 'ativo' | 'inativo' | 'desconhecido'."""
    if dry_run:
        log(f"[dry-run] HEAD em {url} (pulado)")
        return "desconhecido"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if 200 <= resp.status < 400:
                log(f"GitHub Pages ativo: {url} (status {resp.status})")
                return "ativo"
            log(f"GitHub Pages respondeu {resp.status} em {url}")
            return "inativo"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            log(f"GitHub Pages 404 em {url} — provavelmente não está ativo")
            return "inativo"
        log(f"GitHub Pages HTTP {e.code} em {url}")
        return "inativo"
    except (urllib.error.URLError, OSError) as e:
        log(f"GitHub Pages inacessível em {url}: {e}")
        return "desconhecido"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--obra", required=True, help=f"Obra alvo. Disponíveis: {sorted(OBRAS)}")
    parser.add_argument("--dry-run", action="store_true",
                        help="Não faz build/push/notificação; apenas valida e mostra plano")
    parser.add_argument("--skip-upload", action="store_true",
                        help="Faz build mas não copia/sobe para openclaw-context")
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Pula notificação à Flávia")
    args = parser.parse_args()

    if args.obra not in OBRAS:
        log(f"ERRO: obra '{args.obra}' não mapeada. Disponíveis: {sorted(OBRAS)}")
        return 1
    cfg = OBRAS[args.obra]
    repo_dir = cfg["repo_dir"]
    dominio = cfg["dominio"]
    pages_url = cfg["pages_url"]
    github_repo = cfg["github_repo"]

    log(f"=== gerar_relatorio.py iniciado para obra={args.obra} dominio={dominio} ===")

    if not os.path.isdir(repo_dir):
        log(f"ERRO: repo_dir não existe: {repo_dir}")
        return 1

    try:
        meta = load_relatorio_meta(repo_dir, cfg["data_file"])
    except (FileNotFoundError, ValueError) as e:
        log(f"ERRO: {e}")
        return 1

    semana = normalize_semana(meta["semana"])
    data_iso = str(meta["data"])
    log(f"meta.semana={semana} meta.data={data_iso} meta.numero={meta.get('numero','?')}")

    folder_name = f"{data_iso}_semana-{semana}_{args.obra}"
    dest_dir = os.path.join(CONTEXT_REPO, "relatorios", dominio, args.obra, folder_name)
    log(f"destino: {dest_dir}")

    rc = build_template(repo_dir, args.dry_run)
    if rc != 0:
        return rc

    if args.skip_upload:
        log("--skip-upload: parando após build")
        return 0

    rc = copy_dist(repo_dir, dest_dir, args.dry_run)
    if rc != 0:
        return rc

    commit_msg = (
        f"relatorio: {dominio}/{args.obra} semana {semana} ({data_iso})"
    )

    rc = git_publish(commit_msg, args.dry_run)
    if rc != 0:
        return rc

    pages_status = check_pages(pages_url, args.dry_run)

    rel_path = f"relatorios/{dominio}/{args.obra}/{folder_name}"
    github_url = f"https://github.com/{github_repo}/tree/main"
    github_context_url = f"https://github.com/mensuraeng/openclaw-context/tree/main/{rel_path}"

    if args.skip_flavia:
        log("--skip-flavia: pulando notificação")
        log(f"=== concluído (sem notificação): {rel_path} ===")
        return 0

    payload = {
        "source": "gerar_relatorio.py",
        "kind": "relatorio_publicado",
        "obra": args.obra,
        "dominio": dominio,
        "semana": semana,
        "data": data_iso,
        "github_path": rel_path,
        "github_url": github_context_url,
        "github_pages_url": pages_url,
        "github_pages_status": pages_status,
        "scheduled_at": datetime.now().isoformat(),
        "body": (
            f"Relatório semana {semana} de {args.obra} ({dominio}) publicado no GitHub.\n"
            f"Snapshot versionado: {github_context_url}\n"
            f"Visualização interativa (GitHub Pages, status={pages_status}): {pages_url}"
        ),
    }

    if args.dry_run:
        log("[dry-run] payload que seria enviado à Flávia:")
        log(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    rc = send_to_flavia(payload)
    log(f"send_to_flavia exit={rc}")
    log(f"=== concluído: {rel_path} ===")
    return rc


if __name__ == "__main__":
    sys.exit(main())
