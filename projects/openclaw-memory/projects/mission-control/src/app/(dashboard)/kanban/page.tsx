"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Building2, Plus, GripVertical, Trash2, ChevronDown,
  Clock, AlertTriangle, CheckCircle2, Circle, Filter,
  BarChart3, Users, Briefcase
} from "lucide-react";

type Task = {
  id: number; title: string; description: string;
  company: string; agent: string; status: string;
  priority: string; createdAt: string; updatedAt: string;
};

const COMPANIES = [
  { id: "all", name: "Todas", color: "#6366f1" },
  { id: "mensura", name: "Mensura Engenharia", color: "#3b82f6" },
  { id: "mia", name: "MIA Engenharia", color: "#10b981" },
  { id: "pcs", name: "PCS Engenharia", color: "#f59e0b" },
];

const COLUMNS = [
  { id: "todo", label: "A Fazer", icon: Circle, color: "#94a3b8" },
  { id: "in-progress", label: "Em Progresso", icon: Clock, color: "#3b82f6" },
  { id: "review", label: "Revisão", icon: AlertTriangle, color: "#f59e0b" },
  { id: "done", label: "Concluído", icon: CheckCircle2, color: "#10b981" },
];

const PRIORITIES: Record<string, { label: string; color: string }> = {
  urgent: { label: "Urgente", color: "#ef4444" },
  high: { label: "Alta", color: "#f97316" },
  medium: { label: "Média", color: "#eab308" },
  low: { label: "Baixa", color: "#6b7280" },
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
      const res = await fetch(`/api/tasks?company=${selectedCompany}`);
      const data = await res.json();
      if (data.ok) setTasks(data.tasks);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [selectedCompany]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const createTask = async () => {
    if (!newTask.title.trim()) return;
    const res = await fetch("/api/tasks", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newTask, status: "todo" }),
    });
    const data = await res.json();
    if (data.ok) { setTasks(prev => [...prev, data.task]); setShowNewTask(false); setNewTask({ title: "", description: "", company: "mensura", agent: "mensura", priority: "medium" }); }
  };

  const updateTaskStatus = async (taskId: number, newStatus: string) => {
    const res = await fetch("/api/tasks", {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: taskId, status: newStatus }),
    });
    const data = await res.json();
    if (data.ok) setTasks(prev => prev.map(t => t.id === taskId ? { ...t, status: newStatus } : t));
  };

  const deleteTask = async (taskId: number) => {
    await fetch(`/api/tasks?id=${taskId}`, { method: "DELETE" });
    setTasks(prev => prev.filter(t => t.id !== taskId));
  };

  const handleDragStart = (task: Task) => setDraggedTask(task);
  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  const handleDrop = (status: string) => { if (draggedTask) { updateTaskStatus(draggedTask.id, status); setDraggedTask(null); } };

  const getCompanyColor = (id: string) => COMPANIES.find(c => c.id === id)?.color || "#6b7280";
  const getCompanyName = (id: string) => COMPANIES.find(c => c.id === id)?.name || id;

  const stats = {
    total: tasks.length,
    todo: tasks.filter(t => t.status === "todo").length,
    inProgress: tasks.filter(t => t.status === "in-progress").length,
    review: tasks.filter(t => t.status === "review").length,
    done: tasks.filter(t => t.status === "done").length,
  };

  return (
    <div className="p-6 space-y-6 min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Briefcase className="w-7 h-7 text-indigo-400" /> Kanban Multi-Empresa
          </h1>
          <p className="text-sm text-gray-400 mt-1">Gerencie tarefas de Mensura, MIA e PCS em um só lugar</p>
        </div>
        <button onClick={() => setShowNewTask(true)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition font-medium">
          <Plus className="w-4 h-4" /> Nova Tarefa
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "Total", value: stats.total, color: "text-white" },
          { label: "A Fazer", value: stats.todo, color: "text-slate-400" },
          { label: "Em Progresso", value: stats.inProgress, color: "text-blue-400" },
          { label: "Revisão", value: stats.review, color: "text-yellow-400" },
          { label: "Concluído", value: stats.done, color: "text-emerald-400" },
        ].map(s => (
          <div key={s.label} className="bg-gray-800/60 border border-gray-700/50 rounded-xl p-3 text-center">
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-xs text-gray-500">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Company Filter */}
      <div className="flex gap-2">
        {COMPANIES.map(c => (
          <button key={c.id} onClick={() => setSelectedCompany(c.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2 ${selectedCompany === c.id ? "text-white shadow-lg" : "bg-gray-800/40 text-gray-400 hover:bg-gray-700/60"}`}
            style={selectedCompany === c.id ? { backgroundColor: c.color } : {}}>
            <Building2 className="w-4 h-4" /> {c.name}
          </button>
        ))}
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-4 gap-4">
        {COLUMNS.map(col => {
          const colTasks = tasks.filter(t => t.status === col.id);
          const Icon = col.icon;
          return (
            <div key={col.id} className="bg-gray-800/30 border border-gray-700/40 rounded-xl p-3"
              onDragOver={handleDragOver} onDrop={() => handleDrop(col.id)}>
              <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-700/40">
                <Icon className="w-4 h-4" style={{ color: col.color }} />
                <span className="text-sm font-semibold text-gray-200">{col.label}</span>
                <span className="ml-auto text-xs bg-gray-700/60 text-gray-400 px-2 py-0.5 rounded-full">{colTasks.length}</span>
              </div>
              <div className="space-y-2 min-h-[200px]">
                {colTasks.map(task => (
                  <div key={task.id} draggable onDragStart={() => handleDragStart(task)}
                    className="bg-gray-900/80 border border-gray-700/50 rounded-lg p-3 cursor-grab hover:border-gray-600 transition group">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: getCompanyColor(task.company) }} />
                          <span className="text-xs text-gray-500">{getCompanyName(task.company)}</span>
                        </div>
                        <h3 className="text-sm font-medium text-white">{task.title}</h3>
                        {task.description && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{task.description}</p>}
                      </div>
                      <button onClick={() => deleteTask(task.id)} className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-medium" style={{ backgroundColor: PRIORITIES[task.priority]?.color + "20", color: PRIORITIES[task.priority]?.color }}>
                        {PRIORITIES[task.priority]?.label}
                      </span>
                      <span className="text-[10px] text-gray-600">@{task.agent}</span>
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
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center" onClick={() => setShowNewTask(false)}>
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md space-y-4" onClick={e => e.stopPropagation()}>
            <h2 className="text-lg font-bold text-white">Nova Tarefa</h2>
            <input value={newTask.title} onChange={e => setNewTask(p => ({ ...p, title: e.target.value }))}
              placeholder="Título da tarefa" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500" />
            <textarea value={newTask.description} onChange={e => setNewTask(p => ({ ...p, description: e.target.value }))}
              placeholder="Descrição (opcional)" rows={3} className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500" />
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Empresa</label>
                <select value={newTask.company} onChange={e => setNewTask(p => ({ ...p, company: e.target.value }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
                  {COMPANIES.filter(c => c.id !== "all").map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-gray-400 mb-1 block">Agente</label>
                <select value={newTask.agent} onChange={e => setNewTask(p => ({ ...p, agent: e.target.value }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm">
                  {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Prioridade</label>
              <div className="flex gap-2">
                {Object.entries(PRIORITIES).map(([k, v]) => (
                  <button key={k} onClick={() => setNewTask(p => ({ ...p, priority: k }))}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${newTask.priority === k ? "ring-2 ring-offset-1 ring-offset-gray-900" : "opacity-50"}`}
                    style={{ backgroundColor: v.color + "20", color: v.color, outline: `2px solid ${v.color}` }}>
                    {v.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button onClick={() => setShowNewTask(false)} className="flex-1 py-2 bg-gray-800 text-gray-400 rounded-lg text-sm hover:bg-gray-700 transition">Cancelar</button>
              <button onClick={createTask} className="flex-1 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-500 transition font-medium">Criar Tarefa</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
