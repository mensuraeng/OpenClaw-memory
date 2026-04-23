#!/usr/bin/env python3
"""
Analytics Semanal — Mensura + MIA.

Pós-FASE 5: NÃO envia HTML direto via Telegram.
Coleta dados do Google Analytics, gera HTML em reports/,
calcula um resumo executivo e entrega payload à Flávia
(domínio BI / analytics web — sem agente especializado).

A Flávia decide o que fazer: mostrar resumo no DM, agendar envio,
pedir review do Alê, ou nada (silêncio quando não há mudança relevante).

Flags:
  --skip-flavia    gera HTML localmente; não entrega à Flávia
  --print          alias retrocompat: equivale a --skip-flavia
"""

import argparse
import os
import sys
from datetime import datetime
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/root/.openclaw/workspace/credentials/ga_service_account.json"

OUTPUT_PATH = "/root/.openclaw/workspace/reports/analytics_semanal.html"

PROPRIEDADES = {
    "MENSURA": "366003407",
    "MIA": "516543098",
}

def run_report(client, property_id, dimensions, metrics, date_range="7daysAgo", limit=10):
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=date_range, end_date="today")],
        limit=limit,
    )
    return client.run_report(request)

def coletar_dados(nome, prop_id, client):
    dados = {"nome": nome, "prop_id": prop_id}

    # Visão geral
    try:
        r = run_report(client, prop_id,
                       dimensions=["date"],
                       metrics=["sessions", "totalUsers", "newUsers", "bounceRate"],
                       limit=100)
        dados["sessions"] = sum(int(row.metric_values[0].value) for row in r.rows) if r.rows else 0
        dados["users"] = sum(int(row.metric_values[1].value) for row in r.rows) if r.rows else 0
        dados["new_users"] = sum(int(row.metric_values[2].value) for row in r.rows) if r.rows else 0
        bounce_vals = [float(row.metric_values[3].value) for row in r.rows] if r.rows else []
        dados["bounce"] = round(sum(bounce_vals) / len(bounce_vals) * 100, 1) if bounce_vals else 0
    except Exception as e:
        dados["sessions"] = dados["users"] = dados["new_users"] = dados["bounce"] = 0
        dados["erro_geral"] = str(e)

    # Origem do tráfego
    try:
        r = run_report(client, prop_id,
                       dimensions=["sessionDefaultChannelGroup"],
                       metrics=["sessions"], limit=8)
        dados["origens"] = sorted(
            [(row.dimension_values[0].value or "Outros", int(row.metric_values[0].value)) for row in r.rows],
            key=lambda x: x[1], reverse=True
        )
    except:
        dados["origens"] = []

    # Páginas
    try:
        r = run_report(client, prop_id,
                       dimensions=["pagePath"],
                       metrics=["screenPageViews"], limit=5)
        dados["paginas"] = sorted(
            [(row.dimension_values[0].value or "/", int(row.metric_values[0].value)) for row in r.rows],
            key=lambda x: x[1], reverse=True
        )[:5]
    except:
        dados["paginas"] = []

    # Dispositivos
    try:
        r = run_report(client, prop_id,
                       dimensions=["deviceCategory"],
                       metrics=["sessions"], limit=5)
        rows = sorted(r.rows, key=lambda x: int(x.metric_values[0].value), reverse=True)
        total = sum(int(row.metric_values[0].value) for row in rows) or 1
        dados["dispositivos"] = [
            (row.dimension_values[0].value.capitalize(), int(row.metric_values[0].value),
             round(int(row.metric_values[0].value) / total * 100, 1))
            for row in rows
        ]
    except:
        dados["dispositivos"] = []

    # Localidade
    try:
        r = run_report(client, prop_id,
                       dimensions=["country", "city"],
                       metrics=["sessions"], limit=10)
        dados["localidades"] = sorted(
            [(row.dimension_values[1].value or "?", row.dimension_values[0].value or "?",
              int(row.metric_values[0].value)) for row in r.rows],
            key=lambda x: x[2], reverse=True
        )[:8]
    except:
        dados["localidades"] = []

    return dados

def gerar_html(dados_lista):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    def badge_bounce(v):
        cor = "#e74c3c" if v > 70 else "#f39c12" if v > 50 else "#27ae60"
        return f'<span style="color:{cor};font-weight:600">{v}%</span>'

    secoes = ""
    for d in dados_lista:
        origens_html = "".join(
            f'<tr><td>{o}</td><td style="text-align:right;font-weight:500">{s:,}</td></tr>'
            for o, s in d.get("origens", [])
        ) or "<tr><td colspan='2'>Sem dados</td></tr>"

        paginas_html = "".join(
            f'<tr><td style="font-family:monospace;font-size:12px">{p}</td><td style="text-align:right;font-weight:500">{v:,}</td></tr>'
            for p, v in d.get("paginas", [])
        ) or "<tr><td colspan='2'>Sem dados</td></tr>"

        dispositivos_html = "".join(
            f'<tr><td>{dev}</td><td style="text-align:right">{s:,}</td><td style="text-align:right;color:#666">{pct}%</td></tr>'
            for dev, s, pct in d.get("dispositivos", [])
        ) or "<tr><td colspan='3'>Sem dados</td></tr>"

        localidades_html = "".join(
            f'<tr><td>{cidade}</td><td>{pais}</td><td style="text-align:right;font-weight:500">{s:,}</td></tr>'
            for cidade, pais, s in d.get("localidades", [])
        ) or "<tr><td colspan='3'>Sem dados</td></tr>"

        secoes += f"""
        <div class="empresa">
          <div class="empresa-header">{d['nome']}</div>
          <div class="cards">
            <div class="card">
              <div class="card-label">Sessões</div>
              <div class="card-value">{d.get('sessions', 0):,}</div>
            </div>
            <div class="card">
              <div class="card-label">Usuários</div>
              <div class="card-value">{d.get('users', 0):,}</div>
            </div>
            <div class="card">
              <div class="card-label">Novos usuários</div>
              <div class="card-value">{d.get('new_users', 0):,}</div>
            </div>
            <div class="card">
              <div class="card-label">Taxa de rejeição</div>
              <div class="card-value">{badge_bounce(d.get('bounce', 0))}</div>
            </div>
          </div>

          <div class="grid-2">
            <div>
              <div class="section-title">Origem do tráfego</div>
              <table class="data-table">
                <thead><tr><th>Canal</th><th style="text-align:right">Sessões</th></tr></thead>
                <tbody>{origens_html}</tbody>
              </table>
            </div>
            <div>
              <div class="section-title">Dispositivos</div>
              <table class="data-table">
                <thead><tr><th>Tipo</th><th style="text-align:right">Sessões</th><th style="text-align:right">%</th></tr></thead>
                <tbody>{dispositivos_html}</tbody>
              </table>
            </div>
          </div>

          <div class="grid-2">
            <div>
              <div class="section-title">Top 5 páginas</div>
              <table class="data-table">
                <thead><tr><th>Página</th><th style="text-align:right">Views</th></tr></thead>
                <tbody>{paginas_html}</tbody>
              </table>
            </div>
            <div>
              <div class="section-title">Top localidades</div>
              <table class="data-table">
                <thead><tr><th>Cidade</th><th>País</th><th style="text-align:right">Sessões</th></tr></thead>
                <tbody>{localidades_html}</tbody>
              </table>
            </div>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytics Semanal — Mensura + MIA</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f4f5f7; color: #1a1a2e; }}
    .header {{ background: #1a1a2e; color: white; padding: 32px 40px; }}
    .header h1 {{ font-size: 22px; font-weight: 600; letter-spacing: -0.3px; }}
    .header p {{ font-size: 13px; color: #8892a4; margin-top: 4px; }}
    .container {{ max-width: 960px; margin: 0 auto; padding: 32px 20px; }}
    .empresa {{ background: white; border-radius: 12px; margin-bottom: 28px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    .empresa-header {{ background: #1a1a2e; color: white; padding: 14px 24px; font-size: 13px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-bottom: 1px solid #f0f0f0; }}
    .card {{ padding: 20px 24px; border-right: 1px solid #f0f0f0; }}
    .card:last-child {{ border-right: none; }}
    .card-label {{ font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }}
    .card-value {{ font-size: 24px; font-weight: 700; color: #1a1a2e; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-top: 1px solid #f0f0f0; }}
    .grid-2 > div {{ padding: 20px 24px; border-right: 1px solid #f0f0f0; }}
    .grid-2 > div:last-child {{ border-right: none; }}
    .section-title {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #8892a4; margin-bottom: 12px; }}
    .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    .data-table th {{ text-align: left; font-size: 11px; color: #aaa; font-weight: 600; padding: 0 0 8px 0; border-bottom: 1px solid #f0f0f0; }}
    .data-table td {{ padding: 7px 0; border-bottom: 1px solid #f8f8f8; color: #333; }}
    .data-table tr:last-child td {{ border-bottom: none; }}
    .footer {{ text-align: center; font-size: 12px; color: #aaa; padding: 20px; }}
    @media (max-width: 600px) {{
      .cards {{ grid-template-columns: 1fr 1fr; }}
      .grid-2 {{ grid-template-columns: 1fr; }}
      .grid-2 > div {{ border-right: none; border-top: 1px solid #f0f0f0; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Analytics Semanal</h1>
    <p>Mensura + MIA · Últimos 7 dias · Gerado em {agora} BRT</p>
  </div>
  <div class="container">
    {secoes}
    <div class="footer">Flávia · Analytics via Google Analytics Data API</div>
  </div>
</body>
</html>"""

def montar_resumo_texto(dados_lista):
    """Resumo executivo curto em texto plano para a Flávia."""
    linhas = ["📊 Analytics Semanal (últimos 7 dias)\n"]
    for d in dados_lista:
        linhas.append(f"*{d['nome']}*")
        linhas.append(f"  Sessões: {d.get('sessions', 0):,} | Usuários: {d.get('users', 0):,}"
                      f" | Novos: {d.get('new_users', 0):,} | Bounce: {d.get('bounce', 0)}%")
        if d.get("origens"):
            top_origens = ", ".join(f"{o} ({s:,})" for o, s in d["origens"][:3])
            linhas.append(f"  Top origens: {top_origens}")
        if d.get("paginas"):
            top_paginas = ", ".join(f"{p} ({v:,})" for p, v in d["paginas"][:3])
            linhas.append(f"  Top páginas: {top_paginas}")
        linhas.append("")
    return "\n".join(linhas).strip()


def montar_metrics_estruturado(dados_lista):
    """Métricas resumidas em dict para a Flávia raciocinar."""
    out = {}
    for d in dados_lista:
        out[d["nome"]] = {
            "sessions": d.get("sessions", 0),
            "users": d.get("users", 0),
            "new_users": d.get("new_users", 0),
            "bounce_pct": d.get("bounce", 0),
            "top_origens": d.get("origens", [])[:5],
            "top_paginas": d.get("paginas", [])[:5],
            "dispositivos": d.get("dispositivos", []),
        }
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Gera HTML localmente; não entrega à Flávia")
    parser.add_argument("--print", action="store_true",
                        help="Alias retrocompat para --skip-flavia")
    args = parser.parse_args()
    skip_flavia = args.skip_flavia or args.print

    client = BetaAnalyticsDataClient()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    dados_lista = []
    for nome, prop_id in PROPRIEDADES.items():
        print(f"Coletando {nome}...", file=sys.stderr)
        dados_lista.append(coletar_dados(nome, prop_id, client))

    html = gerar_html(dados_lista)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML gerado: {OUTPUT_PATH}", file=sys.stderr)

    if skip_flavia:
        return 0

    payload = {
        "source": "relatorio_analytics.py",
        "kind": "analytics_semanal",
        "project": None,
        "company": None,
        "domain": "bi_web",
        "urgency": "low",
        "scheduled_at": datetime.now().isoformat(),
        "metrics": montar_metrics_estruturado(dados_lista),
        "html_path": OUTPUT_PATH,
        "body": montar_resumo_texto(dados_lista),
    }
    return send_to_flavia(payload)


if __name__ == "__main__":
    sys.exit(main())
