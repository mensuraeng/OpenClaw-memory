#!/usr/bin/env python3
"""Creative Ops Studio MVP.

Transforma um brief em um pacote operacional de geração multimodal:
marca -> canal -> use case -> direção criativa -> prompt -> gate de aprovação.
Não gera nem publica assets. É uma camada segura de roteamento e briefing.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BRANDS_PATH = ROOT / "config" / "brands.json"
ROUTER_PATH = ROOT / "config" / "model_router.json"
RUNTIME_DIR = ROOT / "runtime"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(text: str) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " -_":
            keep.append("-")
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:80] or "brief"


def choose_route(routes: list[dict[str, Any]], brand: str, asset_type: str, channel: str) -> dict[str, Any]:
    brand = brand.upper()
    channel_l = channel.lower()

    candidates = [r for r in routes if r.get("asset_type") == asset_type]
    if not candidates:
        candidates = routes

    if brand == "MENSURA" and asset_type == "image":
        return next((r for r in candidates if r["use_case"] == "linkedin_technical_visual"), candidates[0])
    if brand == "MIA" and asset_type == "image":
        return next((r for r in candidates if r["use_case"] == "premium_architecture_visual"), candidates[0])
    if brand == "PCS" and asset_type == "image":
        return next((r for r in candidates if r["use_case"] == "institutional_public_works_visual"), candidates[0])
    if "lip" in channel_l or "porta" in channel_l:
        return next((r for r in routes if r["use_case"] == "lip_sync_spokesperson"), candidates[0])
    if asset_type == "video":
        return next((r for r in routes if r["use_case"] == "short_video_concept"), candidates[0])
    return candidates[0]


def build_prompt(brief: str, brand_name: str, brand: dict[str, Any], route: dict[str, Any], channel: str, format_hint: str) -> str:
    return (
        f"Crie um asset visual para {brand_name} com finalidade de {channel}. "
        f"Formato: {format_hint}. "
        f"Brief: {brief}. "
        f"Posicionamento da marca: {brand['positioning']}. "
        f"Direção visual: {brand['visual_direction']}. "
        f"Tom: {brand['tone']}. "
        "Composição limpa, premium, profissional, sem texto pequeno, sem logotipos falsos, "
        "sem promessas técnicas ou comerciais não verificáveis. "
        f"Objetivo operacional: {route['best_for']}."
    )


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    brands = load_json(BRANDS_PATH)
    router = load_json(ROUTER_PATH)
    brand_name = args.brand.upper()
    if brand_name not in brands:
        raise SystemExit(f"Marca inválida: {args.brand}. Use: {', '.join(sorted(brands))}")

    brand = brands[brand_name]
    route = choose_route(router["routes"], brand_name, args.asset_type, args.channel)
    prompt = build_prompt(args.brief, brand_name, brand, route, args.channel, args.format)

    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "draft_requires_human_approval",
        "source": "creative-ops-studio",
        "brand": brand_name,
        "channel": args.channel,
        "format": args.format,
        "asset_type": args.asset_type,
        "brief": args.brief,
        "route": route,
        "brand_guardrails": {
            "tone": brand["tone"],
            "avoid": brand["avoid"],
            "default_channels": brand["default_channels"],
        },
        "generation_prompt": prompt,
        "approval_gate": {
            "required": True,
            "reason": "Asset gerado é rascunho; publicação externa exige validação do Alê/Flávia.",
            "blocked_actions_without_approval": ["publicar", "enviar a cliente", "usar em anúncio", "usar em proposta final"],
        },
        "next_steps": [
            "Validar se o brief está correto.",
            "Gerar 2-4 variações no modelo escolhido.",
            "Selecionar uma variação e ajustar copy/caption.",
            "Submeter para aprovação humana antes de qualquer saída externa.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera pacote de asset para Creative Ops Studio.")
    parser.add_argument("--brand", required=True, help="MENSURA, MIA ou PCS")
    parser.add_argument("--channel", required=True, help="Canal ou contexto: LinkedIn, Instagram, landing page...")
    parser.add_argument("--asset-type", choices=["image", "video"], default="image")
    parser.add_argument("--format", default="post 1:1", help="Formato visual desejado")
    parser.add_argument("--brief", required=True, help="Brief em linguagem natural")
    parser.add_argument("--output", help="Caminho de saída JSON. Padrão: runtime/<timestamp>-<brand>-<slug>.json")
    args = parser.parse_args()

    plan = build_plan(args)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if args.output:
        out = Path(args.output)
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = RUNTIME_DIR / f"{stamp}-{plan['brand'].lower()}-{slugify(args.brief)}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
