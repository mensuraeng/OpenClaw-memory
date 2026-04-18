"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, Clock3, PauseCircle, PlayCircle, XCircle } from "lucide-react";

type TaskStatus =
  | "queued"
  | "running"
  | "waiting_input"
  | "blocked"
  | "failed"
  | "completed_unvalidated"
  | "completed_validated"
  | "cancelled";

interface TaskExecution {
  taskId: string;
  title: string;
  objective: string;
  sourceAgent: string;
  targetAgent: string;
  executionType: string;
  status: TaskStatus;
  riskLevel: "low" | "medium" | "high" | "critical";
  attempt: number;
  createdAt: string;
  updatedAt: string;
  dueAt?: string | null;
  staleAfterMinutes?: number | null;
  blockingReason?: string | null;
}

interface TaskMetrics {
  total: number;
  open: number;
  blocked: number;
  validated: number;
  failed: number;
  slaBreached: number;
  stale: number;
  orphaned: number;
  retrying: number;
}

function statusMeta(status: TaskStatus) {
  switch (status) {
    case "queued":
      return { label: "Na fila", color: "#94a3b8", icon: Clock3 };
    case "running":
      return { label: "Rodando", color: "#3b82f6", icon: PlayCircle };
    case "waiting_input":
      return { label: "Aguardando input", color: "#f59e0b", icon: PauseCircle };
    case "blocked":
      return { label: "Bloqueada", color: "#f97316", icon: AlertTriangle };
    case "failed":
      return { label: "Falhou", color: "#ef4444", icon: XCircle };
    case "completed_unvalidated":
      return { label: "Concluída sem validação", color: "#a855f7", icon: CheckCircle2 };
    case "completed_validated":
      return { label: "Validada", color: "#22c55e", icon: CheckCircle2 };
    case "cancelled":
      return { label: "Cancelada", color: "#6b7280", icon: XCircle };
    default:
      return { label: status, color: "#94a3b8", icon: Clock3 };
  }
}

function isSlaBreached(task: TaskExecution) {
  return Boolean(task.dueAt && ["queued", "running", "waiting_input", "blocked"].includes(task.status) && new Date(task.dueAt).getTime() < Date.now());
}

function isStale(task: TaskExecution) {
  if (!["queued", "running", "waiting_input", "blocked"].includes(task.status)) return false;
  const staleAfter = task.staleAfterMinutes ?? 30;
  return Date.now() - new Date(task.updatedAt).getTime() > staleAfter * 60 * 1000;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskExecution[]>([]);
  const [metrics, setMetrics] = useState<TaskMetrics>({ total: 0, open: 0, blocked: 0, validated: 0, failed: 0, slaBreached: 0, stale: 0, orphaned: 0, retrying: 0 });

  useEffect(() => {
    fetch("/api/tasks")
      .then((r) => r.json())
      .then((data) => {
        setTasks(data.tasks || []);
        setMetrics(data.metrics || { total: 0, open: 0, blocked: 0, validated: 0, failed: 0, slaBreached: 0, stale: 0, orphaned: 0, retrying: 0 });
      })
      .catch(console.error);
  }, []);

  const blockedOrWaiting = useMemo(
    () => tasks.filter((task) => task.status === "blocked" || task.status === "waiting_input"),
    [tasks]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold" style={{ color: "var(--text-primary)" }}>Task Tracking</h1>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Trilha inicial de tarefas, delegações, bloqueios e validações do sistema multiagente.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-9 gap-4">
        {[
          ["Total", metrics.total],
          ["Abertas", metrics.open],
          ["Bloqueadas", metrics.blocked],
          ["SLA vencido", metrics.slaBreached],
          ["Paradas", metrics.stale],
          ["Validadas", metrics.validated],
          ["Órfãs", metrics.orphaned],
          ["Retry", metrics.retrying],
          ["Falhas", metrics.failed],
        ].map(([label, value]) => (
          <div key={String(label)} className="rounded-2xl border p-4" style={{ borderColor: "var(--border-subtle)", background: "var(--surface-elevated)" }}>
            <div className="text-xs uppercase tracking-wide" style={{ color: "var(--text-secondary)" }}>{label}</div>
            <div className="text-3xl font-semibold mt-2" style={{ color: "var(--text-primary)" }}>{value}</div>
          </div>
        ))}
      </div>

      {(blockedOrWaiting.length > 0 || tasks.some(isSlaBreached) || tasks.some(isStale)) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="rounded-2xl border p-4" style={{ borderColor: "rgba(249,115,22,0.35)", background: "rgba(249,115,22,0.08)" }}>
            <div className="flex items-center gap-2 mb-3" style={{ color: "#f97316" }}>
              <AlertTriangle size={18} />
              <h2 className="font-semibold">Bloqueios e espera de input</h2>
            </div>
            <div className="space-y-2">
              {blockedOrWaiting.slice(0, 5).map((task) => (
                <div key={task.taskId} className="text-sm" style={{ color: "var(--text-primary)" }}>
                  <strong>{task.title}</strong> · {task.targetAgent} · {task.blockingReason || "Sem motivo registrado"}
                </div>
              ))}
              {blockedOrWaiting.length === 0 && <div className="text-sm" style={{ color: "var(--text-secondary)" }}>Nenhum bloqueio ativo.</div>}
            </div>
          </div>

          <div className="rounded-2xl border p-4" style={{ borderColor: "rgba(239,68,68,0.35)", background: "rgba(239,68,68,0.08)" }}>
            <div className="flex items-center gap-2 mb-3" style={{ color: "#ef4444" }}>
              <XCircle size={18} />
              <h2 className="font-semibold">SLA vencido</h2>
            </div>
            <div className="space-y-2">
              {tasks.filter(isSlaBreached).slice(0, 5).map((task) => (
                <div key={task.taskId} className="text-sm" style={{ color: "var(--text-primary)" }}>
                  <strong>{task.title}</strong> · {task.targetAgent}
                </div>
              ))}
              {tasks.filter(isSlaBreached).length === 0 && <div className="text-sm" style={{ color: "var(--text-secondary)" }}>Nenhuma tarefa com SLA estourado.</div>}
            </div>
          </div>

          <div className="rounded-2xl border p-4" style={{ borderColor: "rgba(245,158,11,0.35)", background: "rgba(245,158,11,0.08)" }}>
            <div className="flex items-center gap-2 mb-3" style={{ color: "#f59e0b" }}>
              <PauseCircle size={18} />
              <h2 className="font-semibold">Tarefas paradas</h2>
            </div>
            <div className="space-y-2">
              {tasks.filter(isStale).slice(0, 5).map((task) => (
                <div key={task.taskId} className="text-sm" style={{ color: "var(--text-primary)" }}>
                  <strong>{task.title}</strong> · {task.targetAgent}
                </div>
              ))}
              {tasks.filter(isStale).length === 0 && <div className="text-sm" style={{ color: "var(--text-secondary)" }}>Nenhuma tarefa parada além da janela.</div>}
            </div>
          </div>
        </div>
      )}

      <div className="rounded-2xl border overflow-hidden" style={{ borderColor: "var(--border-subtle)", background: "var(--surface-elevated)" }}>
        <div className="px-4 py-3 border-b" style={{ borderColor: "var(--border-subtle)" }}>
          <h2 className="font-semibold" style={{ color: "var(--text-primary)" }}>Tarefas recentes</h2>
        </div>
        <div className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
          {tasks.length === 0 ? (
            <div className="p-6 text-sm" style={{ color: "var(--text-secondary)" }}>
              Nenhuma tarefa registrada ainda.
            </div>
          ) : (
            tasks.map((task) => {
              const meta = statusMeta(task.status);
              const Icon = meta.icon;
              return (
                <Link key={task.taskId} href={`/tasks/${task.taskId}`} className="block p-4 hover:bg-white/5 transition-colors">
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full" style={{ background: `${meta.color}1A`, color: meta.color }}>
                          <Icon size={14} /> {meta.label}
                        </span>
                        <span className="text-xs uppercase" style={{ color: "var(--text-secondary)" }}>{task.executionType}</span>
                        <span className="text-xs uppercase" style={{ color: "var(--text-secondary)" }}>risco {task.riskLevel}</span>
                        {isSlaBreached(task) && <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444' }}>SLA vencido</span>}
                        {isStale(task) && <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'rgba(245,158,11,0.15)', color: '#f59e0b' }}>Parada</span>}
                        {task.blockingReason?.includes('Sessão não encontrada na reconciliação') && <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444' }}>Órfã</span>}
                        {task.status === 'queued' && <span className="text-xs px-2 py-1 rounded-full" style={{ background: 'rgba(59,130,246,0.15)', color: '#3b82f6' }}>Em retry/fila</span>}
                      </div>
                      <div className="font-semibold" style={{ color: "var(--text-primary)" }}>{task.title}</div>
                      <div className="text-sm" style={{ color: "var(--text-secondary)" }}>{task.objective}</div>
                    </div>
                    <div className="text-xs md:text-right" style={{ color: "var(--text-secondary)" }}>
                      <div>{task.sourceAgent} → {task.targetAgent}</div>
                      <div>Tentativa {task.attempt}</div>
                      <div>{new Date(task.updatedAt).toLocaleString("pt-BR")}</div>
                    </div>
                  </div>
                </Link>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
