"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { format, subDays, startOfDay, endOfDay } from "date-fns";
import { ActivityHeatmap } from "@/components/ActivityHeatmap";
import {
  FileText,
  Search,
  MessageSquare,
  Terminal,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Filter,
  RefreshCw,
  Shield,
  Wrench,
  Calendar,
  ChevronDown,
  Timer,
  Coins,
  Brain,
  RotateCcw,
  ArrowUpDown,
  Download,
} from "lucide-react";
import { RichDescription } from "@/components/RichDescription";

interface Activity {
  id: string;
  timestamp: string;
  type: string;
  description: string;
  status: string;
  duration_ms: number | null;
  tokens_used: number | null;
  metadata?: Record<string, unknown>;
}

interface ActivitiesResponse {
  activities: Activity[];
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

const typeIcons: Record<string, React.ComponentType<{ className?: string; style?: React.CSSProperties }>> = {
  file: FileText,
  search: Search,
  message: MessageSquare,
  command: Terminal,
  security: Shield,
  build: Wrench,
  task: Zap,
  cron: RotateCcw,
  memory: Brain,
  default: Zap,
};

const typeColorVars: Record<string, string> = {
  file: "--type-file",
  search: "--type-search",
  message: "--type-message",
  command: "--type-command",
  security: "--type-security",
  build: "--type-build",
  task: "--type-task",
  cron: "--type-cron",
  memory: "--type-memory",
};

const statusConfig: Record<string, { icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>; colorVar: string }> = {
  success: { icon: CheckCircle, colorVar: "--success" },
  error: { icon: XCircle, colorVar: "--error" },
  pending: { icon: Clock, colorVar: "--warning" },
};

const allTypes = ["file", "search", "message", "command", "security", "build", "task", "cron", "memory"];

const datePresets = [
  { label: "Today", days: 0 },
  { label: "Last 7 days", days: 7 },
  { label: "Last 30 days", days: 30 },
  { label: "Todo o período", days: -1 },
];

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
}

function formatTokens(tokens: number): string {
  if (tokens < 1000) return tokens.toString();
  return `${(tokens / 1000).toFixed(1)}k`;
}

export default function ActivityPageClient() {
  const searchParams = useSearchParams();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>(searchParams.get("status") || "all");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [sort, setSort] = useState<"newest" | "oldest">((searchParams.get("sort") as "newest" | "oldest") || "newest");
  const [activePreset, setActivePreset] = useState<number | null>(1);

  const limit = 20;

  const fetchActivities = useCallback(async (append = false) => {
    const currentOffset = append ? offset : 0;

    if (append) setLoadingMore(true);
    else setLoading(true);

    try {
      const params = new URLSearchParams();
      params.set("limit", limit.toString());
      params.set("offset", currentOffset.toString());
      params.set("sort", sort);

      if (selectedTypes.size > 0 && selectedTypes.size < allTypes.length) {
        if (selectedTypes.size === 1) params.set("type", Array.from(selectedTypes)[0]);
      }

      if (filterStatus !== "all") params.set("status", filterStatus);

      const agentFromQuery = searchParams.get("agent");
      if (agentFromQuery) params.set("agent", agentFromQuery);
      if (startDate) params.set("startDate", startDate);
      if (endDate) params.set("endDate", endDate);

      const res = await fetch(`/api/activities?${params.toString()}`);
      const data: ActivitiesResponse = await res.json();

      let filteredActivities = data.activities;
      if (selectedTypes.size > 1) filteredActivities = data.activities.filter((a) => selectedTypes.has(a.type));

      if (append) setActivities((prev) => [...prev, ...filteredActivities]);
      else setActivities(filteredActivities);

      setTotal(data.total);
      setHasMore(data.hasMore);
      setOffset(currentOffset + data.activities.length);
    } catch (error) {
      console.error("Failed to fetch activities:", error);
      if (!append) setActivities([]);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [offset, sort, selectedTypes, filterStatus, startDate, endDate, searchParams]);

  useEffect(() => {
    setOffset(0);
    fetchActivities(false);
  }, [sort, selectedTypes, filterStatus, startDate, endDate, fetchActivities]);

  useEffect(() => {
    const explicitStart = searchParams.get("startDate");
    const explicitEnd = searchParams.get("endDate");

    if (explicitStart || explicitEnd) {
      setStartDate(explicitStart || "");
      setEndDate(explicitEnd || "");
      setActivePreset(null);
      return;
    }

    const end = format(endOfDay(new Date()), "yyyy-MM-dd");
    const start = format(startOfDay(subDays(new Date(), 7)), "yyyy-MM-dd");
    setStartDate(start);
    setEndDate(end);
  }, [searchParams]);

  const handlePresetClick = (days: number, index: number) => {
    setActivePreset(index);
    const end = format(endOfDay(new Date()), "yyyy-MM-dd");
    if (days === -1) {
      setStartDate("");
      setEndDate("");
    } else if (days === 0) {
      const today = format(startOfDay(new Date()), "yyyy-MM-dd");
      setStartDate(today);
      setEndDate(end);
    } else {
      const start = format(startOfDay(subDays(new Date(), days)), "yyyy-MM-dd");
      setStartDate(start);
      setEndDate(end);
    }
  };

  const toggleType = (type: string) => {
    const newTypes = new Set(selectedTypes);
    if (newTypes.has(type)) newTypes.delete(type);
    else newTypes.add(type);
    setSelectedTypes(newTypes);
    setActivePreset(null);
  };

  const clearTypeFilters = () => setSelectedTypes(new Set());
  const handleLoadMore = () => fetchActivities(true);

  if (loading) {
    return <div style={{ padding: '2rem' }}><div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '3rem 0' }}><RefreshCw className="w-8 h-8 animate-spin" style={{ color: 'var(--accent)' }} /></div></div>;
  }

  return (
    <div className="p-4 md:p-8">
      <div className="mb-4 md:mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>Activity Log</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Complete history of agent actions</p>
        </div>
        <a href="/api/activities?format=csv&limit=10000" download={`activities-${new Date().toISOString().split('T')[0]}.csv`} style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 1rem", borderRadius: "0.5rem", backgroundColor: "var(--card)", color: "var(--text-secondary)", border: "1px solid var(--border)", textDecoration: "none", fontSize: "0.875rem", cursor: "pointer", marginTop: "0.25rem" }}>
          <Download className="w-4 h-4" />Export CSV
        </a>
      </div>

      <div className="mb-4 md:mb-6"><ActivityHeatmap /></div>

      <div className="p-3 md:p-4 mb-4 md:mb-6 rounded-xl" style={{ backgroundColor: 'var(--card)' }}>
        <div className="flex items-center gap-3 md:gap-4 mb-3 md:mb-4">
          <Calendar className="w-4 h-4 md:w-5 md:h-5" style={{ color: 'var(--text-secondary)' }} />
          <span className="text-xs md:text-sm" style={{ color: 'var(--text-secondary)' }}>Date Range</span>
        </div>
        <div className="flex flex-wrap items-center gap-2 md:gap-3">
          {datePresets.map((preset, index) => (
            <button key={preset.label} onClick={() => handlePresetClick(preset.days, index)} className="px-3 py-1.5 rounded-lg text-xs md:text-sm" style={{ backgroundColor: activePreset === index ? 'var(--accent)' : 'var(--card-elevated)', color: activePreset === index ? 'white' : 'var(--text-secondary)', border: '1px solid var(--border)' }}>{preset.label}</button>
          ))}
        </div>
      </div>

      <div className="p-3 md:p-4 mb-4 md:mb-6 rounded-xl" style={{ backgroundColor: 'var(--card)' }}>
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <Filter className="w-4 h-4" style={{ color: 'var(--text-secondary)' }} />
          <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Filtros</span>
          {searchParams.get("agent") && <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: 'var(--accent)', color: 'white' }}>Agente: {searchParams.get("agent")}</span>}
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {allTypes.map((type) => {
            const Icon = typeIcons[type] || typeIcons.default;
            const selected = selectedTypes.has(type);
            return (
              <button key={type} onClick={() => toggleType(type)} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs md:text-sm" style={{ backgroundColor: selected ? 'var(--accent)' : 'var(--card-elevated)', color: selected ? 'white' : 'var(--text-secondary)', border: '1px solid var(--border)' }}>
                <Icon className="w-3.5 h-3.5" />{type}
              </button>
            );
          })}
          {selectedTypes.size > 0 && <button onClick={clearTypeFilters} className="px-3 py-1.5 rounded-lg text-xs md:text-sm" style={{ backgroundColor: 'var(--warning-bg)', color: 'var(--warning)', border: '1px solid var(--warning)' }}>Limpar tipos</button>}
        </div>

        <div className="flex flex-wrap gap-3 items-center">
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-3 py-2 rounded-lg text-sm" style={{ backgroundColor: 'var(--card-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>
            <option value="all">Todos status</option>
            <option value="success">Success</option>
            <option value="error">Error</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
          </select>
          <button onClick={() => setSort(sort === "newest" ? "oldest" : "newest")} className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm" style={{ backgroundColor: 'var(--card-elevated)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>
            <ArrowUpDown className="w-4 h-4" />{sort === "newest" ? "Mais novos" : "Mais antigos"}
          </button>
        </div>
      </div>

      <div className="mb-4 text-sm" style={{ color: 'var(--text-secondary)' }}>{total} atividade(s)</div>

      <div className="space-y-3">
        {activities.map((activity) => {
          const TypeIcon = typeIcons[activity.type] || typeIcons.default;
          const StatusIcon = statusConfig[activity.status]?.icon || Clock;
          const colorVar = typeColorVars[activity.type] || "--text-secondary";
          return (
            <div key={activity.id} className="rounded-xl p-4" style={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)' }}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'var(--card-elevated)' }}>
                    <TypeIcon className="w-5 h-5" style={{ color: `var(${colorVar})` }} />
                  </div>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-xs font-semibold uppercase" style={{ color: `var(${colorVar})` }}>{activity.type}</span>
                      <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{new Date(activity.timestamp).toLocaleString('pt-BR')}</span>
                    </div>
                    <RichDescription text={activity.description} className="text-sm" style={{ color: 'var(--text-primary)' }} />
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                      <span className="flex items-center gap-1"><StatusIcon className="w-3.5 h-3.5" />{activity.status}</span>
                      {activity.duration_ms !== null && <span className="flex items-center gap-1"><Timer className="w-3.5 h-3.5" />{formatDuration(activity.duration_ms)}</span>}
                      {activity.tokens_used !== null && <span className="flex items-center gap-1"><Coins className="w-3.5 h-3.5" />{formatTokens(activity.tokens_used)}</span>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {hasMore && (
        <div className="mt-6 flex justify-center">
          <button onClick={handleLoadMore} disabled={loadingMore} className="px-4 py-2 rounded-lg text-sm" style={{ backgroundColor: 'var(--card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}>
            {loadingMore ? 'Carregando...' : 'Carregar mais'}
          </button>
        </div>
      )}
    </div>
  );
}
