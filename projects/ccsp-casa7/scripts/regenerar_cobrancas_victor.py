#!/usr/bin/env python3
"""Regenera cobrancas-victor-current.json a partir do relatório semanal CCSP mais recente.

Objetivo operacional:
- Sempre que um relatório semanal novo for recebido/atualizado, gerar a pauta diária
  de cobrança ao Victor para a próxima semana útil.
- Saída canônica: projects/ccsp-casa7/config/cobrancas-victor-current.json

Heurística conservadora: extrai pontos críticos e plano de ação do HTML, preserva
linguagem executiva e distribui cobranças por dias úteis conforme datas detectadas.
Não envia email. Apenas prepara o arquivo consumido pelo cron diário das 9h.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "relatorios"
OUT_DEFAULT = ROOT / "config" / "cobrancas-victor-current.json"
ARCHIVE_DIR = ROOT / "config" / "historico-cobrancas-victor"

EMAIL = {
    "account": "mia",
    "user": "alexandre@miaengenharia.com.br",
    "to": "victor.evangelista@miaengenharia.com.br",
    "cc": ["alexandre@miaengenharia.com.br", "andre@miaengenharia.com.br"],
}

KEYWORDS = [
    "pintura", "sistema elétrico", "eletric", "banheiro", "1ª onda", "1a onda",
    "limpeza", "área externa", "area externa", "garagem", "tools", "aprovação",
    "aprovacao", "prazo", "laudo", "aditivo", "pendência", "pendencia", "crítico",
    "critico", "cronograma", "caminho crítico", "caminho critico",
]

WEEKDAY_LABELS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "svg"}:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg"}:
            self.skip = False
        if tag in {"h1", "h2", "h3", "h4", "p", "li", "tr", "div", "section"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip:
            return
        s = " ".join(data.split())
        if s:
            self.parts.append(s)


def html_to_text(path: Path) -> str:
    parser = TextExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    text = " ".join(parser.parts)
    return re.sub(r"\s+", " ", text).strip()


def latest_report() -> Path:
    reports = sorted(REPORTS_DIR.glob("CCSP_Casa7_Rev*_*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        raise SystemExit(f"Nenhum relatório encontrado em {REPORTS_DIR}")
    return reports[0]


def parse_report_meta(path: Path, text: str) -> dict:
    name = path.name
    rev = re.search(r"Rev(\d+)", name, re.I)
    d = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", name)
    report_date = None
    if d:
        report_date = date(int(d.group(3)), int(d.group(2)), int(d.group(1)))
    else:
        m = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
        if m:
            report_date = date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    if not report_date:
        report_date = date.today()
    return {
        "report_rev": f"Rev.{int(rev.group(1)):03d}" if rev else "Rev.???",
        "report_date": report_date.isoformat(),
    }


def split_sentences(text: str) -> list[str]:
    # Quebra conservadora por pontuação e por marcadores numerados curtos.
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+|\s+(?=\d{2}\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", text)
    out = []
    for p in parts:
        p = p.strip(" -–—\t\n")
        if 45 <= len(p) <= 360:
            out.append(p)
    return out


def relevant_sentences(text: str) -> list[str]:
    low_keywords = [k.lower() for k in KEYWORDS]
    seen = set()
    out = []
    for s in split_sentences(text):
        low = s.lower()
        if any(k in low for k in low_keywords):
            normalized = re.sub(r"\s+", " ", s).strip()
            key = normalized.lower()[:140]
            if key not in seen:
                seen.add(key)
                out.append(normalized)
    return out[:30]


def extract_date_hint(s: str, base_year: int) -> date | None:
    m = re.search(r"(\d{2})/(\d{2})(?:/(\d{4}))?", s)
    if not m:
        return None
    y = int(m.group(3) or base_year)
    try:
        return date(y, int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def next_weekdays_after(report_date: date, count: int = 5) -> list[date]:
    # Próxima segunda útil após a data do relatório; se relatório for sexta, começa segunda.
    d = report_date + timedelta(days=1)
    while d.weekday() != 0:
        d += timedelta(days=1)
    days = []
    while len(days) < count:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def clean_item(s: str) -> str:
    s = re.sub(r"\bNível\s+(Crítico|Alto|Médio|Baixo)\b", "", s, flags=re.I).strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > 280:
        s = s[:277].rstrip() + "..."
    return s


def bucket_items(sentences: list[str], days: list[date], base_year: int) -> dict[str, list[str]]:
    buckets = {d.isoformat(): [] for d in days}
    fallback_index = 0
    for s in sentences:
        item = clean_item(s)
        hint = extract_date_hint(item, base_year)
        target = None
        if hint:
            # Coloca no dia do prazo, ou no dia útil anterior se o prazo for fim de semana.
            if hint.weekday() >= 5:
                while hint.weekday() >= 5:
                    hint -= timedelta(days=1)
            candidates = [d for d in days if d <= hint]
            target = candidates[-1] if candidates else days[0]
        else:
            target = days[fallback_index % len(days)]
            fallback_index += 1
        arr = buckets[target.isoformat()]
        if item not in arr and len(arr) < 5:
            arr.append(item)
    # Garante pelo menos três cobranças por dia usando itens críticos recorrentes.
    critical_pool = sentences[:10] or ["Confirmar avanço real das frentes críticas e registrar bloqueios externos com responsável e prazo."]
    for d in days:
        key = d.isoformat()
        i = 0
        while len(buckets[key]) < 3:
            candidate = clean_item(critical_pool[i % len(critical_pool)])
            if candidate not in buckets[key]:
                buckets[key].append(candidate)
            i += 1
            if i > 20:
                break
    return buckets


def subject_for(day: date) -> str:
    return f"CCSP Casa 7 — Cobranças de {WEEKDAY_LABELS[day.weekday()].lower()} — {day.strftime('%d/%m')}"


def headline_for(day: date, items: list[str]) -> str:
    joined = " ".join(items).lower()
    if "pintura" in joined:
        return "Dia de destravar pintura e eliminar bloqueios que impactam a entrega contratual."
    if "elétr" in joined or "eletric" in joined:
        return "Dia de transformar pendências técnicas em plano executável com prazo e responsável."
    if "banheiro" in joined or "1ª onda" in joined or "1a onda" in joined:
        return "Dia de fechar frentes atrasadas e proteger rastreabilidade do cronograma."
    return "Dia de cobrar avanço objetivo, evidência e bloqueios que afetem prazo, custo ou responsabilidade."


def build_config(report_path: Path) -> dict:
    text = html_to_text(report_path)
    meta = parse_report_meta(report_path, text)
    report_date = date.fromisoformat(meta["report_date"])
    days = next_weekdays_after(report_date)
    sentences = relevant_sentences(text)
    buckets = bucket_items(sentences, days, report_date.year)
    daily = {}
    for d in days:
        key = d.isoformat()
        items = buckets[key]
        daily[key] = {
            "label": WEEKDAY_LABELS[d.weekday()],
            "subject": subject_for(d),
            "headline": headline_for(d, items),
            "items": items,
        }
    return {
        "source_report": str(report_path),
        **meta,
        "project": "CCSP Casa 7",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generator": str(Path(__file__).resolve()),
        "valid_from": days[0].isoformat(),
        "valid_to": days[-1].isoformat(),
        "email": EMAIL,
        "guardrails": {
            "external_email_authorized_by": "Alexandre Aguiar",
            "authorized_at": "2026-04-27",
            "no_telegram_direct": True,
            "daily_send_time_brt": "09:00",
            "regenerate_after_weekly_report": True,
            "source": "auto_generated_from_latest_weekly_report",
        },
        "daily": daily,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="HTML específico; padrão: relatório mais recente")
    parser.add_argument("--out", default=str(OUT_DEFAULT))
    parser.add_argument("--archive", action="store_true", default=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = Path(args.report) if args.report else latest_report()
    cfg = build_config(report)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    archived = None
    if args.archive:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archived = ARCHIVE_DIR / f"{cfg['report_rev'].replace('.', '')}-{cfg['report_date']}.json"
        archived.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    result = {
        "ok": True,
        "report": str(report),
        "out": str(out),
        "archive": str(archived) if archived else None,
        "valid_from": cfg["valid_from"],
        "valid_to": cfg["valid_to"],
        "days": list(cfg["daily"].keys()),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
