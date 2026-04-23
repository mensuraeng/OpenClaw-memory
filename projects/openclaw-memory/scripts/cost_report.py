#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

STATE_ROOT = Path("/root/.openclaw/agents")
DEFAULT_CONFIG = Path("/root/.openclaw/workspace/config/cost-guard.json")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Agrega custo estimado de sessões OpenClaw por janela de tempo.")
    p.add_argument("--days", type=int, default=None, help="Janela única em dias.")
    p.add_argument("--json", action="store_true", help="Saída JSON.")
    p.add_argument("--config", default=str(DEFAULT_CONFIG), help="Arquivo de configuração de thresholds.")
    return p.parse_args()


def load_config(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def infer_kind(key: str, meta: dict[str, Any]) -> str:
    if ":cron:" in key:
        return "cron"
    if meta.get("chatType") == "group" or ":group:" in key:
        return "group"
    if ":direct:" in key:
        return "direct"
    return "session"


def session_label(key: str, meta: dict[str, Any]) -> str:
    return meta.get("label") or meta.get("displayName") or meta.get("subject") or key


def load_session_index() -> dict[Path, dict[str, Any]]:
    index: dict[Path, dict[str, Any]] = {}
    for store in STATE_ROOT.glob("*/sessions/sessions.json"):
        agent_id = store.parent.parent.name
        try:
            data = json.loads(store.read_text())
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for key, meta in data.items():
            if not isinstance(meta, dict):
                continue
            session_file = meta.get("sessionFile")
            if not session_file:
                continue
            index[Path(session_file).resolve()] = {
                "agentId": agent_id,
                "key": key,
                "kind": infer_kind(key, meta),
                "label": session_label(key, meta),
            }
    return index


def parse_event_timestamp(rec: dict[str, Any], msg: dict[str, Any]) -> datetime | None:
    raw = rec.get("timestamp")
    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            pass
    raw = msg.get("timestamp")
    if isinstance(raw, (int, float)):
        try:
            return datetime.fromtimestamp(raw / 1000, tz=timezone.utc)
        except Exception:
            return None
    return None


def iter_cost_events(index: dict[Path, dict[str, Any]]):
    for session_file, meta in index.items():
        if not session_file.exists():
            continue
        try:
            lines = session_file.read_text().splitlines()
        except Exception:
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("type") != "message":
                continue
            msg = rec.get("message") or {}
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage") or {}
            cost = ((usage.get("cost") or {}).get("total"))
            if cost in (None, ""):
                continue
            ts = parse_event_timestamp(rec, msg)
            if ts is None:
                continue
            yield {
                **meta,
                "timestamp": ts,
                "model": msg.get("model") or "unknown",
                "provider": msg.get("provider") or "unknown",
                "costUsd": float(cost),
            }


def summarize(events: list[dict[str, Any]], now: datetime, days: int) -> dict[str, Any]:
    start = now - timedelta(days=days)
    scoped = [e for e in events if e["timestamp"] >= start]
    by_model: dict[str, float] = defaultdict(float)
    by_kind: dict[str, float] = defaultdict(float)
    by_agent: dict[str, float] = defaultdict(float)
    by_session: dict[str, float] = defaultdict(float)
    for e in scoped:
        by_model[e["model"]] += e["costUsd"]
        by_kind[e["kind"]] += e["costUsd"]
        by_agent[e["agentId"]] += e["costUsd"]
        by_session[e["label"]] += e["costUsd"]
    top_sessions = sorted(by_session.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "days": days,
        "start": start.isoformat(),
        "end": now.isoformat(),
        "assistantTurns": len(scoped),
        "totalUsd": round(sum(e["costUsd"] for e in scoped), 6),
        "byModelUsd": {k: round(v, 6) for k, v in sorted(by_model.items(), key=lambda kv: kv[1], reverse=True)},
        "byKindUsd": {k: round(v, 6) for k, v in sorted(by_kind.items(), key=lambda kv: kv[1], reverse=True)},
        "byAgentUsd": {k: round(v, 6) for k, v in sorted(by_agent.items(), key=lambda kv: kv[1], reverse=True)},
        "topSessionsUsd": [{"label": k, "usd": round(v, 6)} for k, v in top_sessions],
    }


def assess(summary: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    targets = config.get("targetsUsd") or {}
    alerts = config.get("alertsUsd") or {}
    days = summary["days"]
    key = "daily" if days == 1 else "weekly" if days == 7 else f"{days}d"
    target = targets.get(key)
    alert = alerts.get(key)
    total = summary["totalUsd"]
    return {
        "targetUsd": target,
        "alertUsd": alert,
        "aboveTarget": (target is not None and total > target),
        "aboveAlert": (alert is not None and total > alert),
    }


def render_text(summary_1d: dict[str, Any], summary_7d: dict[str, Any], assess_1d: dict[str, Any], assess_7d: dict[str, Any]) -> str:
    def fmt(label: str, summary: dict[str, Any], assess_data: dict[str, Any]) -> list[str]:
        lines = [f"{label}: US$ {summary['totalUsd']:.4f} em {summary['assistantTurns']} turns"]
        if assess_data.get("targetUsd") is not None:
            lines.append(f"  meta: US$ {assess_data['targetUsd']:.2f}")
        if assess_data.get("alertUsd") is not None:
            lines.append(f"  alerta: US$ {assess_data['alertUsd']:.2f}")
        if summary["byKindUsd"]:
            kinds = ", ".join(f"{k}=US$ {v:.4f}" for k, v in list(summary["byKindUsd"].items())[:4])
            lines.append(f"  por tipo: {kinds}")
        if summary["byModelUsd"]:
            models = ", ".join(f"{k}=US$ {v:.4f}" for k, v in list(summary["byModelUsd"].items())[:4])
            lines.append(f"  por modelo: {models}")
        if summary["topSessionsUsd"]:
            tops = ", ".join(f"{x['label']}=US$ {x['usd']:.4f}" for x in summary["topSessionsUsd"][:3])
            lines.append(f"  maiores consumidores: {tops}")
        return lines

    return "\n".join(fmt("24h", summary_1d, assess_1d) + [""] + fmt("7d", summary_7d, assess_7d))


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    index = load_session_index()
    events = list(iter_cost_events(index))
    now = datetime.now(timezone.utc)

    if args.days is not None:
        summary = summarize(events, now, args.days)
        assessment = assess(summary, config)
        payload = {"summary": summary, "assessment": assessment}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(render_text(summary, summary, assessment, assessment))
        return 0

    summary_1d = summarize(events, now, 1)
    summary_7d = summarize(events, now, 7)
    assess_1d = assess(summary_1d, config)
    assess_7d = assess(summary_7d, config)
    payload = {
        "daily": {"summary": summary_1d, "assessment": assess_1d},
        "weekly": {"summary": summary_7d, "assessment": assess_7d},
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(summary_1d, summary_7d, assess_1d, assess_7d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
