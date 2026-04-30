#!/usr/bin/env python3
"""Parser read-only de XML NF-e recebida para JSON normalizado.

Este script não usa certificado, não acessa SEFAZ, não transmite documento e não envia
mensagens externas. Ele lê XML local e gera evidência JSON local.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
SCHEMA_VERSION = "fiscal-nota-recebida-v0"


def text(node: ET.Element | None, path: str) -> str | None:
    if node is None:
        return None
    found = node.find(path, NS)
    if found is None or found.text is None:
        return None
    value = found.text.strip()
    return value or None


def decimal_value(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(Decimal(value))
    except (InvalidOperation, ValueError):
        return None


def slugify(value: str | None, fallback: str = "sem-empresa") -> str:
    raw = value or fallback
    normalized = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or fallback


def only_digits(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"\D", "", value)
    return digits or None


def parse_nfe_xml(xml_path: Path, *, real_data: bool, origin: str, company_slug: str | None = None) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    inf = root.find(".//nfe:infNFe", NS)
    if inf is None:
        raise ValueError("XML não parece conter infNFe de NF-e")

    emit = inf.find("nfe:emit", NS)
    dest = inf.find("nfe:dest", NS)
    ide = inf.find("nfe:ide", NS)
    total = inf.find("nfe:total/nfe:ICMSTot", NS)
    prot = root.find(".//nfe:infProt", NS)

    inf_id = inf.attrib.get("Id", "")
    access_key = text(prot, "nfe:chNFe") or (inf_id[3:] if inf_id.startswith("NFe") else inf_id or None)
    issue_date = text(ide, "nfe:dhEmi") if ide is not None else None
    competence = issue_date[:7] if issue_date and len(issue_date) >= 7 else None

    issuer = {
        "name": text(emit, "nfe:xNome"),
        "cnpj": only_digits(text(emit, "nfe:CNPJ")),
        "municipality": text(emit, "nfe:enderEmit/nfe:xMun"),
        "uf": text(emit, "nfe:enderEmit/nfe:UF"),
        "state_registration": text(emit, "nfe:IE"),
    }
    recipient = {
        "name": text(dest, "nfe:xNome"),
        "cnpj": only_digits(text(dest, "nfe:CNPJ")),
        "municipality": text(dest, "nfe:enderDest/nfe:xMun"),
        "uf": text(dest, "nfe:enderDest/nfe:UF"),
        "state_registration": text(dest, "nfe:IE"),
    }

    items = []
    for det in inf.findall("nfe:det", NS):
        prod = det.find("nfe:prod", NS)
        line_raw = det.attrib.get("nItem")
        try:
            line = int(line_raw) if line_raw else len(items) + 1
        except ValueError:
            line = len(items) + 1
        items.append({
            "line": line,
            "description": text(prod, "nfe:xProd"),
            "cfop": text(prod, "nfe:CFOP"),
            "ncm": text(prod, "nfe:NCM"),
            "quantity": decimal_value(text(prod, "nfe:qCom")),
            "unit_amount": decimal_value(text(prod, "nfe:vUnCom")),
            "total_amount": decimal_value(text(prod, "nfe:vProd")),
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "document_type": "NFe",
        "source": {
            "mode": "manual_import" if real_data else "fixture",
            "origin": origin,
            "real_data": real_data,
            "notes": "Parser local read-only; não acessa SEFAZ nem usa certificado.",
        },
        "access_key": access_key,
        "number": text(ide, "nfe:nNF") if ide is not None else None,
        "series": text(ide, "nfe:serie") if ide is not None else None,
        "model": text(ide, "nfe:mod") if ide is not None else None,
        "nature": text(ide, "nfe:natOp") if ide is not None else None,
        "issue_date": issue_date,
        "competence": competence,
        "issuer": issuer,
        "recipient": recipient,
        "items": items,
        "total_amount": decimal_value(text(total, "nfe:vNF")),
        "currency": "BRL",
        "status": {
            "code": text(prot, "nfe:cStat"),
            "description": text(prot, "nfe:xMotivo"),
        },
        "classification": {
            "company_slug": company_slug or slugify(recipient.get("name")),
            "cost_center": None,
            "project": None,
            "review_status": "pending_human_review",
        },
        "artifacts": {
            "xml_path": None,
            "pdf_path": None,
            "json_path": None,
        },
        "risk_guardrails": {
            "read_only": True,
            "no_external_send": True,
            "no_fiscal_status_change": True,
            "no_payment_approval": True,
        },
    }


def validate_minimal(payload: dict[str, Any]) -> None:
    required = ["schema_version", "document_type", "source", "access_key", "issuer", "recipient", "issue_date", "total_amount", "currency", "status", "artifacts", "risk_guardrails"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing)}")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("schema_version inválida")
    guardrails = payload.get("risk_guardrails") or {}
    for key in ["read_only", "no_external_send", "no_fiscal_status_change", "no_payment_approval"]:
        if guardrails.get(key) is not True:
            raise ValueError(f"Guardrail obrigatório não está ativo: {key}")


def persist(payload: dict[str, Any], xml_path: Path, runtime_dir: Path, *, copy_xml: bool) -> Path:
    company = slugify(payload.get("classification", {}).get("company_slug"))
    competence = payload.get("competence") or datetime.now().strftime("%Y-%m")
    number = slugify(payload.get("number"), "sem-numero")
    issuer = slugify(payload.get("issuer", {}).get("name"), "fornecedor")
    out_dir = runtime_dir / "notas-recebidas" / company / competence
    out_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"{(payload.get('issue_date') or competence)[:10]}_{issuer}_{number}"
    json_path = out_dir / f"{base_name}.json"
    xml_out = out_dir / f"{base_name}.xml"
    if copy_xml:
        shutil.copy2(xml_path, xml_out)
        payload["artifacts"]["xml_path"] = str(xml_out)
    else:
        payload["artifacts"]["xml_path"] = str(xml_path)
    payload["artifacts"]["json_path"] = str(json_path)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ledger_dir = runtime_dir / "ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = ledger_dir / "notas-recebidas.jsonl"
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "access_key": payload.get("access_key"),
            "company_slug": payload.get("classification", {}).get("company_slug"),
            "issuer": payload.get("issuer", {}).get("name"),
            "issue_date": payload.get("issue_date"),
            "total_amount": payload.get("total_amount"),
            "json_path": str(json_path),
            "read_only": True,
        }, ensure_ascii=False) + "\n")
    return json_path


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parser read-only de NF-e recebida para JSON normalizado")
    parser.add_argument("--xml", required=True, type=Path, help="Caminho do XML NF-e local")
    parser.add_argument("--runtime-dir", default=Path("runtime/fiscal"), type=Path, help="Diretório runtime fiscal")
    parser.add_argument("--company-slug", default=None, help="Slug da empresa tomadora, quando já conhecido")
    parser.add_argument("--origin", default="local", help="Origem local do arquivo")
    parser.add_argument("--real-data", action="store_true", help="Marcar como dado real importado manualmente")
    parser.add_argument("--copy-xml", action="store_true", help="Copiar XML para runtime junto do JSON")
    parser.add_argument("--stdout", action="store_true", help="Imprimir JSON em stdout sem persistir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argparser().parse_args(argv)
    if not args.xml.exists():
        print(f"XML não encontrado: {args.xml}", file=sys.stderr)
        return 2
    try:
        payload = parse_nfe_xml(args.xml, real_data=args.real_data, origin=args.origin, company_slug=args.company_slug)
        validate_minimal(payload)
        if args.stdout:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            out = persist(payload, args.xml, args.runtime_dir, copy_xml=args.copy_xml)
            print(out)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI reports safe local error
        print(f"Erro ao processar XML NF-e: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
