#!/usr/bin/env python3
import json
import subprocess
import sys

def send_to_flavia(payload):
    """
    Envia dados estruturados para a Flávia (main agent)
    """
    try:
        message = json.dumps(payload, ensure_ascii=False)
        
        subprocess.run(
            ["openclaw", "run", "--agent", "main", message],
            check=True
        )
        
    except Exception as e:
        print(f"Erro ao enviar para Flávia: {e}", file=sys.stderr)

if __name__ == "__main__":
    data = json.load(sys.stdin)
    send_to_flavia(data)
