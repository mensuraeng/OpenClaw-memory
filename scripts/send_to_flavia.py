#!/usr/bin/env python3
"""
Helper canônico de entrega: scripts geram payload → Flávia consolida.

Uso:
    cat payload.json | send_to_flavia.py
    echo '{"source":"foo","body":"..."}' | send_to_flavia.py

O payload (dict JSON) é serializado e entregue ao agent main via:
    openclaw agent --agent main --message <json-string>

Exit code:
    0 = entregue (Flávia respondeu)
    1 = falha (stderr explica)

Convenção sugerida de payload (não obrigatória, mas ajuda a Flávia):
    {
      "source":   "nome_do_script.py",
      "kind":     "alerta_semanal" | "relatorio" | "evento" | ...,
      "project":  "CCSP Casa 7" | null,
      "company":  "MIA" | "MENSURA" | "PCS" | "FINANCE" | null,
      "urgency":  "low" | "normal" | "high" | "critical",
      "body":     "<conteúdo principal>"
    }
"""

import json
import subprocess
import sys


def send_to_flavia(payload, timeout=180):
    message = json.dumps(payload, ensure_ascii=False)
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--agent", "main", "--message", message],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        return 0
    except subprocess.TimeoutExpired:
        print(f"Timeout após {timeout}s aguardando a Flávia", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(
            f"Falha entregando à Flávia (exit={e.returncode}): "
            f"{(e.stderr or '').strip()[:500]}",
            file=sys.stderr,
        )
        return 1
    except FileNotFoundError:
        print("openclaw CLI não encontrado no PATH", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Stdin não é JSON válido: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(send_to_flavia(data))
