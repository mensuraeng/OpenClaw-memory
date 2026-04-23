#!/usr/bin/env python3
"""
linkedin_post.py — Post a personal update to LinkedIn via OpenClaw - Mensura app
Usage: python3 linkedin_post.py "Texto do post"
       python3 linkedin_post.py --dry-run "Texto do post"
"""
import os
import sys
import json
import urllib.request
import urllib.error

CONFIG_PATH = "/root/.openclaw/workspace/config/linkedin-mensura.json"
ENV_TOKEN = "LINKEDIN_MENSURA_ACCESS_TOKEN"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_token(config):
    token = os.environ.get(ENV_TOKEN)
    if token:
        return token
    token = config.get("access_token")
    if token:
        return token
    raise RuntimeError(
        f"Token do LinkedIn ausente. Defina {ENV_TOKEN} ou preencha access_token no arquivo de config."
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

