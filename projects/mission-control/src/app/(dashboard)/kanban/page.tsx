"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Building2, Plus, GripVertical, Trash2,
  Clock, AlertTriangle, CheckCircle2, Circle,
  Briefcase
} from "lucide-react";
import { fetchJson } from "@/lib/fetch";

type Task = {
  id: number; title: string; description: string;
  company: string; agent: string; status: string;
  priority: string; createdAt: string; updatedAt: string;
};

const COMPANIES = [
  { id: "all",      name: "Todas",              color: "var(--accent)"   },
  { id: "mensura",  name: "Mensura Engenharia",  color: "#3b82f6"         },
  { id: "mia",      name: "MIA Engenharia",      color: "#10b981"         },
  { id: "pcs",      name: "PCS Engenharia",      color: "#f59e0b"         },
];

const COLUMNS = [
  { id: "todo",        label: "A Fazer",      icon: Circle,       color: "var(--text-muted)"  },
  { id: "in-progress", label: "Em Progresso", icon: Clock,        color: "var(--info)"        },
  { id: "review",      label: "Revisão",      icon: AlertTriangle,color: "var(--warning)"     },
  { id: "done",        label: "Concluído",    icon: CheckCircle2, color: "var(--positive)"    },
];

const PRIORITIES: Record<string, { label: string; color: string }> = {
  urgent: { label: "Urgente", color: "var(--negative)" },
  high:   { label: "Alta",    color: "#f97316"         },
  medium: { label: "Média",   color: "var(--warning)"  },
  low:    { label: "Baixa",   color: "var(--text-muted)"},
};

const AGENTS = ["main","mensura","mia","pcs","finance","rh","marketing","producao","juridico","bi","suprimentos","autopilot"];

export default function KanbanPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [showNewTask, setShowNewTask] = useState(false);
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);
  const [newTask, setNewTask] = useState({ title: "", description: "", company: "mensura", agent: "mensura", priority: "medium" });
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    try {
      const data = await fetchJson<{ ok: boolean; tasks: Task[] }>(`/api/tasks?company=${selectedCompany}`);
      if (data.ok) setTasks(data.tasks);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [selectedCompany]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const createTask = async () => {
    if (!newTask.title.trim()) return;
    const data = await fetchJson<{ ok: boolean; task: Task }>("/api/tasks", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newTask, status: "todo" }),
    });
    if (data.ok) {
      setTasks((prev) => [...prev, data.task]);
      setShowNewTask(false);
      setNewTask({ title: "", description: "", company: "mensura", agent: "mensura", priority: "medium" });
    }
  };

  const updateTaskStatus = async (taskId: number, newStatus: string) => {
    const data = await fetchJson<{ ok: boolean; task: Task }>("/api/tasks", {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: taskId, status: newStatus }),
    });
    if (data.ok) setTasks((prev) => prev.map((t) => t.id === taskId ? { ...t, status: newStatus } : t));
  };

  const deleteTask = async (taskId: number) => {
    await fetch(`/api/tasks?id=${taskId}`, { method: "DELETE" });
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const handleDragStart = (task: Task) => setDraggedTask(task);
  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  const handleDrop = (status: string) => {
    if (draggedTask) { updateTaskStatus(draggedTask.id, status); setDraggedTask(null); }
  };

  const getCompanyColor = (id: string) => COMPANIES.find((c) => c.id === id)?.color || "var(--text-muted)";
  const getCompanyName  = (id: string) => COMPANIES.find((c) => c.id === id)?.name  || id;

  const stats = {
    total:      tasks.length,
    todo:       tasks.filter((t) => t.status === "todo").length,
    inProgress: tasks.filter((t) => t.status === "in-progress").length,
    review:     tasks.filter((t) => t.status === "review").length,
    done:       tasks.filter((t) => t.status === "done").length,
  };

  const statCards = [
    { label: "Total",        value: stats.total,      color: "var(--text-primary)"   },
    { label: "A Fazer",      value: stats.todo,       color: "var(--text-muted)"     },
    { label: "Em Progresso", value: stats.inProgress, color: "var(--info)"           },
    { label: "Revisão",      value: stats.review,     color: "var(--warning)"        },
    { label: "Concluído",    value: stats.done,       color: "var(--positive)"       },
  ];

  return (
    <div className="p-6 space-y-6" style={{ backgroundColor: "var(--background)" }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1
            className="text-2xl font-bold flex items-center gap-2"
            style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}
          >
            <Briefcase className="w-7 h-7" style={{ color: "var(--accent)" }} />
            Kanban Multi-Empresa
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            Gerencie tarefas de Mensura, MIA e PCS em um só lugar
          </p>
        </div>
        <button
          onClick={() => setShowNewTask(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg transition font-medium"
          style={{ backgroundColor: "var(--accent)", color: "var(--text-primary)" }}
        >
          <Plus className="w-4 h-4" /> Nova Tarefa
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-3">
        {statCards.map((s) => (
          <div
            key={s.label}
            className="rounded-xl p-3 text-center"
            style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}
          >
            <div className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-xs" style={{ color: "var(--text-muted)" }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Company Filter */}
      <div className="flex gap-2 flex-wrap">
        {COMPANIES.map((c) => {
          const isSelected = selectedCompany === c.id;
          return (
            <button
              key={c.id}
              onClick={() => setSelectedCompany(c.id)}
              className="px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2"
              style={isSelected
                ? { backgroundColor: c.color, color: "#fff" }
                : { backgroundColor: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-secondary)" }
              }
            >
              <Building2 className="w-4 h-4" /> {c.name}
            </button>
          );
        })}
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {COLUMNS.map((col) => {
          const colTasks = tasks.filter((t) => t.status === col.id);
          const Icon = col.icon;
          return (
            <div
              key={col.id}
              className="rounded-xl p-3"
              style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(col.id)}
            >
              <div
                className="flex items-center gap-2 mb-3 pb-2"
                style={{ borderBottom: "1px solid var(--border)" }}
              >
                <Icon className="w-4 h-4" style={{ color: col.color }} />
                <span className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{col.label}</span>
                <span
                  className="ml-auto text-xs px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-muted)" }}
                >
                  {colTasks.length}
                </span>
              </div>
              <div className="space-y-2 min-h-[200px]">
                {colTasks.map((task) => (
                  <div
                    key={task.id}
                    draggable
                    onDragStart={() => handleDragStart(task)}
                    className="rounded-lg p-3 cursor-grab transition group"
                    style={{ backgroundColor: "var(--background)", border: "1px solid var(--border)" }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: getCompanyColor(task.company) }} />
                          <span className="text-xs truncate" style={{ color: "var(--text-muted)" }}>{getCompanyName(task.company)}</span>
                        </div>
                        <h3 className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{task.title}</h3>
                        {task.description && (
                          <p className="text-xs mt-1 line-clamp-2" style={{ color: "var(--text-muted)" }}>{task.description}</p>
                        )}
                      </div>
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="opacity-0 group-hover:opacity-100 transition flex-shrink-0"
                        style={{ color: "var(--text-muted)" }}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span
                        className="text-[10px] px-1.5 py-0.5 rounded font-medium"
                        style={{
                          backgroundColor: (PRIORITIES[task.priority]?.color || "var(--text-muted)") + "20",
                          color: PRIORITIES[task.priority]?.color || "var(--text-muted)"
                        }}
                      >
                        {PRIORITIES[task.priority]?.label}
                      </span>
                      <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>@{task.agent}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Nova Tarefa */}
      {showNewTask && (
        <div
          className="fixed inset-0 backdrop-blur-sm z-50 flex items-center justify-center"
          style={{ backgroundColor: "rgba(0,0,0,0.6)" }}
          onClick={() => setShowNewTask(false)}
        >
          <div
            className="rounded-2xl p-6 w-full max-w-md space-y-4"
            style={{ backgroundColor: "var(--surface)", border: "1px solid var(--border)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-bold" style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)" }}>
              Nova Tarefa
            </h2>
            <input
              value={newTask.title}
              onChange={(e) => setNewTask((p) => ({ ...p, title: e.target.value }))}
              placeholder="Título da tarefa"
              className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none"
              style={{
                backgroundColor: "var(--background)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
              }}
            />
            <textarea
              value={newTask.description}
              onChange={(e) => setNewTask((p) => ({ ...p, description: e.target.value }))}
              placeholder="Descrição (opcional)"
              rows={3}
              className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none resize-none"
              style={{
                backgroundColor: "var(--background)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
              }}
            />
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "Empresa", key: "company" as const, options: COMPANIES.filter((c) => c.id !== "all").map((c) => ({ value: c.id, label: c.name })) },
                { label: "Agente",  key: "agent"   as const, options: AGENTS.map((a) => ({ value: a, label: a })) },
              ].map(({ label, key, options }) => (
                <div key={key}>
                  <label className="text-xs mb-1 block" style={{ color: "var(--text-muted)" }}>{label}</label>
                  <select
                    value={newTask[key]}
                    onChange={(e) => setNewTask((p) => ({ ...p, [key]: e.target.value }))}
                    className="w-full rounded-lg px-3 py-2 text-sm focus:outline-none"
                    style={{
                      backgroundColor: "var(--background)",
                      border: "1px solid var(--border)",
                      color: "var(--text-primary)",
                    }}
                  >
                    {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
              ))}
            </div>
            <div>
              <label className="text-xs mb-1 block" style={{ color: "var(--text-muted)" }}>Prioridade</label>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(PRIORITIES).map(([k, v]) => (
                  <button
                    key={k}
                    onClick={() => setNewTask((p) => ({ ...p, priority: k }))}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium transition"
                    style={{
                      backgroundColor: v.color + "20",
                      color: v.color,
                      border: `1px solid ${v.color}`,
                      opacity: newTask.priority === k ? 1 : 0.5,
                    }}
                  >
                    {v.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowNewTask(false)}
                className="flex-1 py-2 rounded-lg text-sm transition"
                style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
              >
                Cancelar
              </button>
              <button
                onClick={createTask}
                className="flex-1 py-2 rounded-lg text-sm transition font-medium"
                style={{ backgroundColor: "var(--accent)", color: "#fff" }}
              >
                Criar Tarefa
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
