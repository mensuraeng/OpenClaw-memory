import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import {
  getDatabase,
  getCostSummary,
  getCostByAgent,
  getCostByModel,
  getDailyCost,
  getHourlyCost,
} from "@/lib/usage-queries";
import path from "path";

const DB_PATH = path.join(process.cwd(), "data", "usage-tracking.db");
const DEFAULT_BUDGET = 100.0;

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const timeframe = searchParams.get("timeframe") || "30d";
  const days = parseInt(timeframe.replace(/\D/g, ""), 10) || 30;

  try {
    const db = getDatabase(DB_PATH);
    if (!db) {
      return NextResponse.json({
        today: 0, yesterday: 0, thisMonth: 0, lastMonth: 0,
        projected: 0, budget: DEFAULT_BUDGET,
        byAgent: [], byModel: [], daily: [], hourly: [],
        message: "No usage data collected yet. Run collect-usage script first.",
      });
    }
    const summary = getCostSummary(db);
    const byAgent = getCostByAgent(db, days);
    const byModel = getCostByModel(db, days);
    const daily = getDailyCost(db, days);
    const hourly = getHourlyCost(db);
    db.close();
    return NextResponse.json({ ...summary, budget: DEFAULT_BUDGET, byAgent, byModel, daily, hourly });
  } catch (error) {
    console.error("Error fetching cost data:", error);
    return NextResponse.json({ error: "Failed to fetch cost data" }, { status: 500 });
  }
}

// POST disabled in v1
export async function POST() {
  return NextResponse.json(
    { error: "budget update via browser disabled in v1", code: "DISABLED_IN_V1" },
    { status: 403 }
  );
}
