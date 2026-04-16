"use client";
import dynamic from "next/dynamic";
import { useState, useRef, useCallback } from "react";

const Office3D = dynamic(
  () => import("@/components/Office3D/Office3D"),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">
        Carregando escritorio 3D...
      </div>
    ),
  }
);

const AGENTS = [
  { id: "main",        name: "Flavia",         color: "#ff6b35" },
  { id: "rh",          name: "RH",             color: "#8B5CF6" },
  { id: "marketing",   name: "Marketing",      color: "#EC4899" },
  { id: "producao",    name: "Producao",       color: "#F59E0B" },
  { id: "finance",     name: "Finance",        color: "#10B981" },
  { id: "mia",         name: "Mia",            color: "#3B82F6" },
  { id: "mensura",     name: "Mensura",        color: "#EF4444" },
  { id: "autopilot",   name: "Autopilot",      color: "#6B7280" },
  { id: "juridico",    name: "Juridico",       color: "#6366F1" },
  { id: "bi",          name: "BI Dados",       color: "#06B6D4" },
  { id: "suprimentos", name: "Suprimentos",    color: "#D97706" },
  { id: "pcs",         name: "PCS",            color: "#7C3AED" },
];

interface Job {
  jobId: string;
  agentId: string;
  agentName: string;
  message: string;
  status: "running" | "done" | "error";
  output: string;
  startedAt: number;
}

export default function OfficePage() {
  const [agentId, setAgentId] = useState("main");
  const [message, setMessage] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [sending, setSending] = useState(false);
  const [showCompose, setShowCompose] = useState(false);
  const pollRefs = useRef<Record<string, ReturnType<typeof setInterval>>>({});

  const selectedAgent = AGENTS.find((a) => a.id === agentId) ?? AGENTS[0];

  const pollJob = useCallback((jobId: string) => {
    const iv = setInterval(async () => {
      try {
        const r = await fetch(`/api/office/run?jobId=${jobId}`);
        const data = await r.json();
        setJobs((prev) =>
          prev.map((j) =>
            j.jobId === jobId
              ? { ...j, status: data.status, output: data.output ?? "" }
              : j
          )
        );
        if (data.status !== "running") {
          clearInterval(iv);
          delete pollRefs.current[jobId];
        }
      } catch {
        clearInterval(iv);
      }
    }, 2000);
    pollRefs.current[jobId] = iv;
  }, []);

  const send = async () => {
    if (!message.trim() || sending) return;
    setSending(true);
    try {
      const r = await fetch("/api/office/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agentId, message: message.trim() }),
      });
      const data = await r.json();
      const newJob: Job = {
        jobId: data.jobId,
        agentId,
        agentName: selectedAgent.name,
        message: message.trim(),
        status: "running",
        output: "",
        startedAt: Date.now(),
      };
      setJobs((prev) => [newJob, ...prev]);
      pollJob(data.jobId);
      setMessage("");
      setShowCompose(false);
    } catch (e) {
      alert("Erro: " + e);
    } finally {
      setSending(false);
    }
  };

  const elapsed = (ms: number) => {
    const s = Math.floor((Date.now() - ms) / 1000);
    if (s < 60) return `${s}s`;
    return `${Math.floor(s / 60)}m ${s % 60}s`;
  };

  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 48px)" }}>
      <div className="flex-1 min-h-0 relative">
        <Office3D />

        <button
          onClick={() => setShowCompose((v) => !v)}
          className="absolute bottom-4 right-4 z-10 px-4 py-2 rounded-full text-sm font-semibold text-white shadow-lg"
          style={{ backgroundColor: selectedAgent.color }}
        >
          {showCompose ? "Fechar" : "Enviar ordem"}
        </button>

        {jobs.length > 0 && (
          <div className="absolute top-3 right-3 z-10 flex flex-col gap-1 max-w-xs">
            {jobs.slice(0, 5).map((job) => (
              <div
                key={job.jobId}
                className="flex items-center gap-2 bg-gray-900 bg-opacity-90 text-white text-xs px-3 py-1.5 rounded-full shadow"
              >
                {job.status === "running" && (
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                )}
                {job.status === "done" && (
                  <span className="w-2 h-2 rounded-full bg-green-400" />
                )}
                {job.status === "error" && (
                  <span className="w-2 h-2 rounded-full bg-red-400" />
                )}
                <span className="truncate">{job.agentName}: {job.message}</span>
                <span className="text-gray-400 flex-shrink-0">{elapsed(job.startedAt)}</span>
              </div>
            ))}
          </div>
        )}

        {showCompose && (
          <div className="absolute bottom-14 right-4 z-20 w-80 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-2xl p-4 space-y-3">
            <div className="flex items-center gap-2">
              <span
                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                style={{ backgroundColor: selectedAgent.color }}
              >
                {selectedAgent.name.substring(0, 2).toUpperCase()}
              </span>
              <select
                value={agentId}
                onChange={(e) => setAgentId(e.target.value)}
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {AGENTS.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send();
              }}
              placeholder={`Ordem para ${selectedAgent.name}... (Ctrl+Enter)`}
              rows={3}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              autoFocus
            />
            <button
              onClick={send}
              disabled={!message.trim() || sending}
              className="w-full py-2 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
              style={{ backgroundColor: selectedAgent.color }}
            >
              {sending ? "Enviando..." : `Enviar para ${selectedAgent.name}`}
            </button>
            {jobs.length > 0 && jobs[0].output && (
              <pre className="text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 rounded p-2 overflow-auto max-h-32 whitespace-pre-wrap">
                {jobs[0].output}
              </pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
