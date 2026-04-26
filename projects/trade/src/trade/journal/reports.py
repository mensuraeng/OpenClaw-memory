"""Markdown reporting helpers for Trade radar."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable


def _fmt_money(value: float | None, currency: str | None) -> str:
    if value is None:
        return "—"
    prefix = {"USD": "US$", "BRL": "R$"}.get(currency or "", currency or "")
    return f"{prefix} {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:+.2f}%".replace(".", ",")


def render_market_snapshot(snapshot: dict) -> str:
    generated_at = snapshot["generated_at"]
    lines = [
        "# Trade Radar — Snapshot de Mercado",
        "",
        f"Gerado em: `{generated_at}`",
        "",
        "> Radar informativo. Sem recomendação, sem ordem e sem execução real.",
        "",
    ]

    for market_key, title in [("us", "EUA"), ("br", "Brasil")]:
        market = snapshot["markets"].get(market_key, {})
        lines += [f"## {title}", "", "### Benchmarks", "", "| Ativo | Preço | Var. | Volume | Fonte |", "|---|---:|---:|---:|---|"]
        for q in market.get("benchmarks", []):
            lines.append(_quote_row(q))
        lines += ["", "### Watchlist", "", "| Ativo | Preço | Var. | Volume | Fonte |", "|---|---:|---:|---:|---|"]
        for q in market.get("watchlist", []):
            lines.append(_quote_row(q))
        lines.append("")

    lines += [
        "## Leitura automática simples",
        "",
        *snapshot.get("notes", []),
        "",
        "## Próxima ação",
        "",
        "- Fase atual: Market Radar sem execução.",
        "- Próximo passo técnico: adicionar variação semanal/mensal e relatório de risco com QuantStats.",
    ]
    return "\n".join(lines) + "\n"


def _quote_row(q: dict) -> str:
    volume = q.get("volume")
    volume_text = f"{volume:,}".replace(",", ".") if volume is not None else "—"
    source = q.get("source", "—") if not q.get("error") else f"erro: {q.get('error')[:60]}"
    return f"| {q.get('symbol')} | {_fmt_money(q.get('regular_market_price'), q.get('currency'))} | {_fmt_pct(q.get('change_pct'))} | {volume_text} | {source} |"


def write_report(markdown: str, reports_dir: Path, now: datetime) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"market-radar-{now.strftime('%Y-%m-%d-%H%M%S')}.md"
    path.write_text(markdown, encoding="utf-8")
    latest = reports_dir / "market-radar-latest.md"
    latest.write_text(markdown, encoding="utf-8")
    return path
