#!/usr/bin/env python3
"""
consultar_claude_code.py — consulta a CLI do Claude Code local na VPS
                            via wrapper /usr/local/bin/claude_worker.sh.

Fluxo:
1. Recebe --prompt (texto da consulta) e opcional --timeout (default 120s).
2. Em modo --dry-run: só imprime o prompt + parâmetros, não executa.
3. Caso contrário: chama claude_worker.sh, captura stdout (JSON do CC),
   e notifica a Flávia via send_to_flavia com o resultado embalado.
4. Log em ~/.openclaw/workspace/logs/cron/claude-code-consultas.log.

Uso típico (interno, via Flávia):
    python3 scripts/consultar_claude_code.py \\
        --prompt "Liste os arquivos em ~/.openclaw/workspace/scripts/" \\
        --timeout 90
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

WRAPPER = "/usr/local/bin/claude_worker.sh"
LOG_DIR = os.path.expanduser("~/.openclaw/workspace/logs/cron")
LOG_FILE = os.path.join(LOG_DIR, "claude-code-consultas.log")
PREVIEW_CHARS = 100


def log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    sys.stderr.write(line + "\n")
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def run_claude(prompt: str, timeout: int) -> tuple[int, str, str]:
    """Chama o wrapper e retorna (returncode, stdout, stderr)."""
    if not os.path.exists(WRAPPER):
        return 127, "", f"wrapper não encontrado: {WRAPPER}"
    if not os.access(WRAPPER, os.X_OK):
        return 126, "", f"wrapper não executável: {WRAPPER}"
    try:
        # buffer extra de 30s para o wrapper finalizar limpo após timeout interno
        proc = subprocess.run(
            [WRAPPER, prompt, str(timeout)],
            capture_output=True, text=True, timeout=timeout + 30,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "subprocess timeout (acima do limite do wrapper)"
    except OSError as e:
        return 1, "", f"erro de OS executando wrapper: {e}"


def parse_claude_output(stdout: str) -> tuple[str, dict]:
    """Extrai a resposta limpa + metadados úteis do output do Claude Code.

    O Claude Code com --output-format json devolve algo como:
      {"type":"result","subtype":"success","result":"<texto>",
       "duration_ms":...,"total_cost_usd":...,"usage":{...},...}

    Esta função:
      - extrai data["result"] (a resposta crua do modelo)
      - extrai duration_ms, total_cost_usd, stop_reason, is_error
        como metadados separados
      - se o stdout não for JSON parseável, devolve o texto inteiro
      - se for o erro de timeout do wrapper ({"error":"timeout"...}),
        formata como string amigável

    Retorna (resultado_limpo, metadata_dict).
    """
    if not stdout.strip():
        return "", {}
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        # Não é JSON; devolve o texto cru para a Flávia interpretar
        return stdout, {}

    # Erro do wrapper (timeout etc.)
    if data.get("error"):
        msg = data.get("message", "")
        return f"[{data['error']}] {msg}", {"erro": data["error"]}

    resultado = data.get("result")
    if resultado is None:
        # JSON sem "result" (formato inesperado) — devolve cru
        return stdout, {"aviso": "campo 'result' ausente no JSON do Claude Code"}

    metadata = {
        "duration_ms": data.get("duration_ms"),
        "cost_usd": data.get("total_cost_usd"),
        "stop_reason": data.get("stop_reason"),
        "is_error": data.get("is_error"),
        "num_turns": data.get("num_turns"),
    }
    # remove chaves None
    metadata = {k: v for k, v in metadata.items() if v is not None}
    return resultado, metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True,
                        help="Texto da consulta enviada ao Claude Code")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout em segundos (default 120)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Não executa o Claude Code; mostra prompt + parâmetros")
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Não notifica a Flávia; só imprime o resultado")
    args = parser.parse_args()

    prompt_resumo = args.prompt[:PREVIEW_CHARS]
    if len(args.prompt) > PREVIEW_CHARS:
        prompt_resumo += " […]"

    if args.dry_run:
        log(f"[DRY-RUN] prompt ({len(args.prompt)} chars), timeout={args.timeout}s")
        print("=== DRY-RUN ===")
        print(f"WRAPPER:  {WRAPPER}")
        print(f"TIMEOUT:  {args.timeout}s")
        print(f"PROMPT:   {args.prompt}")
        print(f"RESUMO:   {prompt_resumo}")
        return 0

    log(f"executando Claude Code: prompt resumo={prompt_resumo!r} timeout={args.timeout}s")
    rc, stdout, stderr = run_claude(args.prompt, args.timeout)
    log(f"Claude Code rc={rc} stdout={len(stdout)}B stderr={len(stderr)}B")

    if rc != 0 and not stdout:
        # falha total — sem JSON pra processar
        log(f"FALHA: {stderr.strip()[:300]}")
        if not args.skip_flavia:
            payload_falha = {
                "source": "consultar_claude_code.py",
                "kind": "analise_tecnica_falha",
                "prompt_resumo": prompt_resumo,
                "exit_code": rc,
                "erro": stderr.strip()[:1000],
                "scheduled_at": datetime.now().isoformat(),
                "body": (
                    f"Consulta ao Claude Code falhou (rc={rc}). "
                    f"Prompt: {prompt_resumo!r}. Erro: {stderr.strip()[:300]}"
                ),
            }
            send_to_flavia(payload_falha)
        return rc

    resultado_limpo, cc_meta = parse_claude_output(stdout)
    log(
        f"parse_claude_output: resultado={len(resultado_limpo)}B "
        f"meta_keys={list(cc_meta.keys())}"
    )

    if args.skip_flavia:
        print(resultado_limpo)
        return 0

    payload = {
        "source": "consultar_claude_code.py",
        "kind": "analise_tecnica",
        "prompt_resumo": prompt_resumo,
        "resultado": resultado_limpo,
        "claude_code_meta": cc_meta,
        "scheduled_at": datetime.now().isoformat(),
        "body": "Análise técnica concluída via Claude Code.",
    }
    rc_flavia = send_to_flavia(payload)
    log(f"send_to_flavia exit={rc_flavia}")
    return rc_flavia


if __name__ == "__main__":
    sys.exit(main())
