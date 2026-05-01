#!/usr/bin/env python3
"""
linkedin_post.py — Post a personal update to LinkedIn via OpenClaw - Mensura app
Usage: python3 linkedin_post.py "Texto do post"
       python3 linkedin_post.py --dry-run "Texto do post"
"""
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

CONFIG_PATH = "/root/.openclaw/workspace/config/linkedin-mensura.json"
WORKSPACE = Path("/root/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / "scripts"))
from secret_config import load_json_config, resolve_secret_ref  # noqa: E402

def load_config():
    return load_json_config(CONFIG_PATH, resolve=False)


def get_token(config):
    token_ref = config.get("accessToken")
    if token_ref:
        return resolve_secret_ref(token_ref, name="linkedin-mensura.accessToken")
    raise RuntimeError(
        "Token do LinkedIn ausente. Configure accessToken com referência env/KeeSpace no arquivo de config."
    )

def get_profile(token):
    req = urllib.request.Request(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def post_update(token, author_urn, text):
    payload = json.dumps({
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }).encode()
    req = urllib.request.Request(
        "https://api.linkedin.com/v2/ugcPosts",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    )
    with urllib.request.urlopen(req) as r:
        body = r.read()
        return json.loads(body) if body else {"status": "posted", "http_status": r.status}

if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    text_args = [a for a in args if a != "--dry-run"]
    if not text_args:
        print("Uso: python3 linkedin_post.py [--dry-run] 'Texto do post'")
        sys.exit(1)
    text = text_args[0]

    config = load_config()
    token = get_token(config)

    profile = get_profile(token)
    person_urn = f"urn:li:person:{profile['sub']}"
    print(f"Autenticado como: {profile.get('name', 'N/A')} ({profile.get('email', 'N/A')})")
    print(f"Author URN: {person_urn}")
    print(f"Texto: {text[:100]}...")

    if dry_run:
        print("[DRY-RUN] Post nao enviado.")
    else:
        result = post_update(token, person_urn, text)
        print(f"Publicado! Resultado: {result}")

