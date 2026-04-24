/**
 * GA4 Data API — MENSURA + MIA
 * GET /api/ga4
 * Retorna dados reais dos últimos 7 dias para uso no dashboard.
 */
import { NextResponse } from "next/server";
import { BetaAnalyticsDataClient } from "@google-analytics/data";
import type { AnalyticsInsight } from "@/lib/executive-alerts";

const KEY_FILE = "/root/.openclaw/workspace/credentials/ga4-service-account.json";

const PROPERTIES: { empresa: string; id: string }[] = [
  { empresa: "MENSURA", id: "366003407" },
  { empresa: "MIA", id: "516543098" },
];

// Cache por 30 minutos
let cache: { data: AnalyticsInsight[]; ts: number } | null = null;
const CACHE_MS = 30 * 60 * 1000;

async function fetchInsight(
  client: BetaAnalyticsDataClient,
  empresa: string,
  propertyId: string
): Promise<AnalyticsInsight> {
  const property = `properties/${propertyId}`;

  const [mainResp, sourceResp, pageResp] = await Promise.all([
    client.runReport({
      property,
      dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
      metrics: [
        { name: "sessions" },
        { name: "activeUsers" },
        { name: "newUsers" },
        { name: "bounceRate" },
      ],
    }),
    client.runReport({
      property,
      dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
      dimensions: [{ name: "sessionSourceMedium" }],
      metrics: [{ name: "sessions" }],
      orderBys: [{ metric: { metricName: "sessions" }, desc: true }],
      limit: 1,
    }),
    client.runReport({
      property,
      dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
      dimensions: [{ name: "pagePath" }],
      metrics: [{ name: "screenPageViews" }],
      orderBys: [{ metric: { metricName: "screenPageViews" }, desc: true }],
      limit: 1,
    }),
  ]);

  const row = mainResp[0]?.rows?.[0];
  const sessoes = parseInt(row?.metricValues?.[0]?.value ?? "0");
  const usuarios = parseInt(row?.metricValues?.[1]?.value ?? "0");
  const novos = parseInt(row?.metricValues?.[2]?.value ?? "0");
  const bouncePct = parseFloat(row?.metricValues?.[3]?.value ?? "0") * 100;

  const principalOrigem =
    sourceResp[0]?.rows?.[0]?.dimensionValues?.[0]?.value ?? "—";
  const paginaTop =
    pageResp[0]?.rows?.[0]?.dimensionValues?.[0]?.value ?? "/";

  const leitura =
    sessoes === 0
      ? "Sem dados de tráfego no período."
      : bouncePct > 60
      ? `Alto bounce (${bouncePct.toFixed(1)}%) — visitantes entram mas não engajam.`
      : bouncePct > 40
      ? `Bounce moderado (${bouncePct.toFixed(1)}%) — há espaço para melhorar retenção.`
      : `Boa retenção (${bouncePct.toFixed(1)}% bounce) — tráfego engajado.`;

  return { empresa, sessoes, usuarios, novos, bouncePct, principalOrigem, paginaTop, leitura };
}

export async function GET() {
  if (cache && Date.now() - cache.ts < CACHE_MS) {
    return NextResponse.json(cache.data);
  }

  try {
    const client = new BetaAnalyticsDataClient({
      keyFilename: KEY_FILE,
    });

    const insights = await Promise.all(
      PROPERTIES.map(({ empresa, id }) => fetchInsight(client, empresa, id))
    );

    cache = { data: insights, ts: Date.now() };
    return NextResponse.json(insights);
  } catch (err) {
    console.error("[/api/ga4] erro:", err);
    return NextResponse.json({ error: "Falha ao buscar dados GA4" }, { status: 500 });
  }
}
