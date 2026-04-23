#!/usr/bin/env python3
"""
instagram_post.py — Posta no Instagram Business via OpenClaw Social app
Uso: python3 instagram_post.py --account mensura "Texto do post" [--image URL]
"""
import sys, json, argparse, urllib.request, urllib.parse

CONFIG_PATH = "/root/.openclaw/workspace/config/instagram-openclaw.json"
GRAPH = "https://graph.facebook.com/v19.0"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def graph_get(path, token, params=None):
    p = urllib.parse.urlencode({**(params or {}), "access_token": token})
    url = f"{GRAPH}/{path}?{p}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def graph_post(path, token, data):
    data["access_token"] = token
    payload = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(f"{GRAPH}/{path}", data=payload, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get_account(config, name):
    for acct in config["accounts"]:
        if name.lower() in acct["name"].lower() or name.lower() in acct["ig_username"].lower():
            return acct
    raise ValueError(f"Conta nao encontrada: {name}")

def post_text(ig_user_id, token, text, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Postaria em ig_user_id={ig_user_id}:")
        print(f"  Texto: {text[:120]}...")
        return {"dry_run": True}
    container = graph_post(f"{ig_user_id}/media", token, {"caption": text, "media_type": "TEXT"})
    container_id = container["id"]
    print(f"Container criado: {container_id}")
    result = graph_post(f"{ig_user_id}/media_publish", token, {"creation_id": container_id})
    print(f"Post publicado: {result}")
    return result

def post_image(ig_user_id, token, text, image_url, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Postaria imagem em ig_user_id={ig_user_id}:")
        print(f"  Imagem: {image_url}")
        print(f"  Caption: {text[:120]}")
        return {"dry_run": True}
    container = graph_post(f"{ig_user_id}/media", token, {
        "caption": text,
        "image_url": image_url,
        "media_type": "IMAGE"
    })
    container_id = container["id"]
    print(f"Container criado: {container_id}")
    result = graph_post(f"{ig_user_id}/media_publish", token, {"creation_id": container_id})
    print(f"Post publicado: {result}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Posta no Instagram via OpenClaw Social")
    parser.add_argument("--account", default="mensura", help="Nome da conta (default: mensura)")
    parser.add_argument("--image", default=None, help="URL da imagem")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem postar")
    parser.add_argument("text", help="Texto da publicacao")
    args = parser.parse_args()

    config = load_config()
    token = config["system_user_token"]
    acct = get_account(config, args.account)

    ig_user_id = acct["ig_user_id"]
    if "PENDING" in ig_user_id:
        print(f"ERRO: {acct['status']}")
        print("Acao necessaria: reconectar @mensuraengenharia no Meta Business Manager")
        sys.exit(1)

    print(f"Conta: {acct['name']} ({acct['ig_username']})")
    print(f"IG User ID: {ig_user_id}")

    if args.image:
        result = post_image(ig_user_id, token, args.text, args.image, dry_run=args.dry_run)
    else:
        result = post_text(ig_user_id, token, args.text, dry_run=args.dry_run)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
