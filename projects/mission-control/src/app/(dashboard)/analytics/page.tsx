"use client";

import { useEffect, useState } from "react";
import { fetchJson } from "@/lib/fetch";
import { ActivityLineChart } from "@/components/charts/ActivityLineChart";
import { ActivityPieChart } from "@/components/charts/ActivityPieChart";
import { HourlyHeatmap } from "@/components/charts/HourlyHeatmap";
import { SuccessRateGauge } from "@/components/charts/SuccessRateGauge";
import { BarChart3, TrendingUp, Clock, Target } from "lucide-react";
import { PageHeader, PageShell, SectionCard } from "@/components/PageShell";

interface AnalyticsData {
  byDay: { date: string; count: number }[];
  byType: { type: string; count: number }[];
  byHour: { hour: number; day: number; count: number }[];
  successRate: number;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJson<AnalyticsData>("/api/analytics")
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div
        className="p-4 md:p-8 flex items-center justify-center min-h-screen"
        style={{ backgroundColor: "var(--background)" }}
      >
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-8 h-8 border-2 border-t-transparent rounded-full animate-spin"
            style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
          />
          <span style={{ color: "var(--text-secondary)" }}>Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-4 md:p-8" style={{ backgroundColor: "var(--background)" }}>
        <p style={{ color: "var(--error)" }}>Failed to load analytics data</p>
      </div>
    );
  }

  const totalThisWeek = data.byDay.reduce((sum, d) => sum + d.count, 0);
  const mostActiveDay = data.byDay.reduce(
    (max, d) => (d.count > max.count ? d : max),
    data.byDay[0]
  )?.date || "-";

  return (
    <PageShell>
      <PageHeader
        title="Analytics"
        subtitle="Insights e tendências da atividade operacional"
        icon={<span style={{ marginRight: 8 }}>📊</span>}
      />

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4 md:mb-6">
        <div
          className="rounded-xl p-3 md:p-4"
          style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-xs md:text-sm mb-1" style={{ color: "var(--text-secondary)" }}>Total This Week</p>
          <p className="text-xl md:text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
            {totalThisWeek}
          </p>
        </div>
        <div
          className="rounded-xl p-3 md:p-4"
          style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-xs md:text-sm mb-1" style={{ color: "var(--text-secondary)" }}>Most Active Day</p>
          <p className="text-xl md:text-2xl font-bold" style={{ color: "var(--accent)" }}>
            {mostActiveDay}
          </p>
        </div>
        <div
          className="rounded-xl p-3 md:p-4"
          style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-xs md:text-sm mb-1" style={{ color: "var(--text-secondary)" }}>Top Activity Type</p>
          <p className="text-xl md:text-2xl font-bold capitalize" style={{ color: "var(--info)" }}>
            {data.byType[0]?.type || "-"}
          </p>
        </div>
        <div
          className="rounded-xl p-3 md:p-4"
          style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}
        >
          <p className="text-xs md:text-sm mb-1" style={{ color: "var(--text-secondary)" }}>Success Rate</p>
          <p className="text-xl md:text-2xl font-bold" style={{ color: "var(--success)" }}>
            {data.successRate.toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Activity Over Time */}
        <SectionCard title="Activity Over Time" icon={<TrendingUp className="inline-block w-4 h-4 md:w-5 md:h-5 mr-2 mb-0.5" style={{ color: "var(--accent)" }} />}>
          <ActivityLineChart data={data.byDay} />
        </SectionCard>

        {/* Activity by Type */}
        <SectionCard title="Activity by Type" icon={<BarChart3 className="inline-block w-4 h-4 md:w-5 md:h-5 mr-2 mb-0.5" style={{ color: "var(--accent)" }} />}>
          <ActivityPieChart data={data.byType} />
        </SectionCard>

        {/* Hourly Heatmap */}
        <SectionCard title="Activity by Hour" icon={<Clock className="inline-block w-4 h-4 md:w-5 md:h-5 mr-2 mb-0.5" style={{ color: "var(--accent)" }} />}>
          <HourlyHeatmap data={data.byHour} />
        </SectionCard>

        {/* Success Rate Gauge */}
        <SectionCard title="Success Rate" icon={<Target className="inline-block w-4 h-4 md:w-5 md:h-5 mr-2 mb-0.5" style={{ color: "var(--accent)" }} />}>
          <SuccessRateGauge rate={data.successRate} />
        </SectionCard>
      </div>
    </PageShell>
  );
}
