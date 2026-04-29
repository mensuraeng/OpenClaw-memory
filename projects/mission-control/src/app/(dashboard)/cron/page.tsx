"use client";

import { useState, useEffect, useCallback } from "react";
import { Clock, RefreshCw, AlertCircle, LayoutGrid, CalendarDays, Zap, X, Save } from "lucide-react";
import { CronJobCard, type CronJob } from "@/components/CronJobCard";
import { CronWeeklyTimeline } from "@/components/CronWeeklyTimeline";

type ViewMode = "cards" | "timeline";

type CronEditForm = {
  id: string;
  name: string;
  agentId: string;
  enabled: boolean;
  scheduleKind: string;
  expr: string;
  tz: string;
  everyMs: string;
  at: string;
  message: string;
  description: string;
  sessionTarget: string;
};

function getPayloadMessage(job: CronJob): string {
  const payload = job.payload || {};
  return String(payload.message || payload.text || job.description || "");
}

function toEditForm(job: CronJob): CronEditForm {
  const schedule = typeof job.schedule === "object" && job.schedule ? job.schedule as Record<string, unknown> : {};
  return {
    id: job.id,
    name: job.name || "",
    agentId: job.agentId || "main",
    enabled: Boolean(job.enabled),
    scheduleKind: String(schedule.kind || "cron"),
    expr: String(schedule.expr || ""),
    tz: String(schedule.tz || job.timezone || "America/Sao_Paulo"),
    everyMs: schedule.everyMs ? String(schedule.everyMs) : "",
    at: String(schedule.at || ""),
    message: getPayloadMessage(job),
    description: job.description || "",
    sessionTarget: job.sessionTarget || "isolated",
  };
}

export default function CronJobsPage() {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("cards");
  const [runToast, setRunToast] = useState<{ id: string; status: "success" | "error"; name: string } | null>(null);
  const [editingJob, setEditingJob] = useState<CronJob | null>(null);
  const [editForm, setEditForm] = useState<CronEditForm | null>(null);
  const [isSavingEdit, setIsSavingEdit] = useState(false);

  const fetchJobs = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch("/api/cron");
      if (!res.ok) throw new Error("Failed to fetch jobs");
      const data = await res.json();
      setJobs(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      const res = await fetch("/api/cron", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, enabled }),
      });
      if (!res.ok) throw new Error("Failed to update job");
      setJobs((prev) =>
        prev.map((job) => (job.id === id ? { ...job, enabled } : job))
      );
    } catch (err) {
      console.error("Toggle error:", err);
      setError("Failed to update job status");
    }
  };

  const handleDelete = async (id: string) => {
    if (deleteConfirm !== id) {
      setDeleteConfirm(id);
      return;
    }
    try {
      const res = await fetch(`/api/cron?id=${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Failed to delete job");
      setJobs((prev) => prev.filter((job) => job.id !== id));
      setDeleteConfirm(null);
    } catch (err) {
      console.error("Delete error:", err);
      setError("Failed to delete job");
    }
  };

  const handleRun = async (id: string) => {
    const job = jobs.find((j) => j.id === id);
    const res = await fetch("/api/cron/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      setRunToast({ id, status: "error", name: job?.name || id });
      setTimeout(() => setRunToast(null), 4000);
      throw new Error(data.error || "Trigger failed");
    }

    setRunToast({ id, status: "success", name: job?.name || id });
    setTimeout(() => setRunToast(null), 4000);
  };

  const openEdit = (job: CronJob) => {
    setEditingJob(job);
    setEditForm(toEditForm(job));
    setError(null);
  };

  const closeEdit = () => {
    if (isSavingEdit) return;
    setEditingJob(null);
    setEditForm(null);
  };

  const saveEdit = async () => {
    if (!editForm) return;
    setIsSavingEdit(true);
    try {
      const res = await fetch("/api/cron", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editForm),
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || "Falha ao salvar cron");
      await fetchJobs();
      closeEdit();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao salvar cron");
    } finally {
      setIsSavingEdit(false);
    }
  };

  const activeJobs = jobs.filter((j) => j.enabled).length;
  const pausedJobs = jobs.length - activeJobs;

  return (
    <div className="p-4 md:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4 md:mb-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold mb-1" style={{ 
            color: 'var(--text-primary)',
            fontFamily: 'var(--font-heading)'
          }}>
            Cron Jobs
          </h1>
          <p className="text-sm md:text-base" style={{ color: 'var(--text-secondary)' }}>
            Scheduled tasks from OpenClaw Gateway
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* View mode toggle */}
          <div
            style={{
              display: 'flex',
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '0.5rem',
              padding: '3px',
            }}
          >
            <button
              onClick={() => setViewMode("cards")}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.4rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                backgroundColor: viewMode === "cards" ? 'var(--accent)' : 'transparent',
                color: viewMode === "cards" ? 'white' : 'var(--text-secondary)',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              Cards
            </button>
            <button
              onClick={() => setViewMode("timeline")}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.4rem 0.75rem',
                borderRadius: '0.35rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                backgroundColor: viewMode === "timeline" ? 'var(--accent)' : 'transparent',
                color: viewMode === "timeline" ? 'white' : 'var(--text-secondary)',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.15s',
              }}
            >
              <CalendarDays className="w-3.5 h-3.5" />
              Timeline
            </button>
          </div>

          <button
            onClick={() => { setIsLoading(true); fetchJobs(); }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              backgroundColor: 'var(--card)',
              color: 'var(--text-primary)',
              borderRadius: '0.5rem',
              border: '1px solid var(--border)',
              cursor: 'pointer',
              fontWeight: 500,
              transition: 'opacity 0.2s'
            }}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4 mb-4 md:mb-8">
        <div style={{
          backgroundColor: 'color-mix(in srgb, var(--card) 50%, transparent)',
          border: '1px solid var(--border)',
          borderRadius: '0.75rem',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{ padding: '0.75rem', backgroundColor: 'color-mix(in srgb, var(--info) 20%, transparent)', borderRadius: '0.5rem' }}>
            <Clock className="w-6 h-6" style={{ color: 'var(--info)' }} />
          </div>
          <div>
            <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{jobs.length}</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Total Jobs</p>
          </div>
        </div>
        <div style={{
          backgroundColor: 'color-mix(in srgb, var(--card) 50%, transparent)',
          border: '1px solid var(--border)',
          borderRadius: '0.75rem',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{ padding: '0.75rem', backgroundColor: 'color-mix(in srgb, var(--success) 20%, transparent)', borderRadius: '0.5rem' }}>
            <RefreshCw className="w-6 h-6" style={{ color: 'var(--success)' }} />
          </div>
          <div>
            <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{activeJobs}</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Active</p>
          </div>
        </div>
        <div style={{
          backgroundColor: 'color-mix(in srgb, var(--card) 50%, transparent)',
          border: '1px solid var(--border)',
          borderRadius: '0.75rem',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1rem'
        }}>
          <div style={{ padding: '0.75rem', backgroundColor: 'color-mix(in srgb, var(--warning) 20%, transparent)', borderRadius: '0.5rem' }}>
            <AlertCircle className="w-6 h-6" style={{ color: 'var(--warning)' }} />
          </div>
          <div>
            <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{pausedJobs}</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Paused</p>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          marginBottom: '1.5rem',
          padding: '1rem',
          backgroundColor: 'color-mix(in srgb, var(--error) 10%, transparent)',
          border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)',
          borderRadius: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <AlertCircle className="w-5 h-5" style={{ color: 'var(--error)' }} />
          <span style={{ color: 'var(--error)' }}>{error}</span>
          <button onClick={() => setError(null)} style={{ marginLeft: 'auto', color: 'var(--error)', background: 'none', border: 'none', cursor: 'pointer' }}>
            Dismiss
          </button>
        </div>
      )}

      {/* Loading */}
      {isLoading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '3rem 0' }}>
          <div style={{
            width: '2rem', height: '2rem',
            border: '2px solid var(--accent)', borderTopColor: 'transparent',
            borderRadius: '50%', animation: 'spin 1s linear infinite'
          }} />
        </div>
      ) : jobs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0' }}>
          <Clock className="w-8 h-8 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
            No cron jobs found
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Create cron jobs via Telegram or the OpenClaw CLI
          </p>
        </div>
      ) : viewMode === "timeline" ? (
        /* Timeline View */
        <div
          className="rounded-xl overflow-hidden"
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--border)',
            padding: '1.25rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              marginBottom: '1.25rem',
              paddingBottom: '1rem',
              borderBottom: '1px solid var(--border)',
            }}
          >
            <CalendarDays className="w-5 h-5" style={{ color: 'var(--accent)' }} />
            <h2
              style={{
                fontSize: '1rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-heading)',
              }}
            >
              7-Day Schedule Overview
            </h2>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                backgroundColor: 'var(--card-elevated)',
                padding: '0.25rem 0.6rem',
                borderRadius: '0.35rem',
              }}
            >
              All times in local timezone
            </span>
          </div>
          <CronWeeklyTimeline jobs={jobs} />
        </div>
      ) : (
        /* Cards View */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-4">
          {jobs.map((job) => (
            <div key={job.id} style={{ position: 'relative' }}>
              <CronJobCard
                job={job}
                onToggle={handleToggle}
                onEdit={openEdit}
                onDelete={handleDelete}
                onRun={handleRun}
              />
              {deleteConfirm === job.id && (
                <div style={{
                  position: 'absolute', inset: 0,
                  backgroundColor: 'rgba(12, 12, 12, 0.9)',
                  borderRadius: '0.75rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  backdropFilter: 'blur(4px)',
                  zIndex: 10,
                }}>
                  <div style={{ textAlign: 'center' }}>
                    <p style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>Delete &quot;{job.name}&quot;?</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <button onClick={() => setDeleteConfirm(null)}
                        style={{ padding: '0.5rem 1rem', color: 'var(--text-secondary)', background: 'none', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }}>
                        Cancel
                      </button>
                      <button onClick={() => handleDelete(job.id)}
                        style={{ padding: '0.5rem 1rem', backgroundColor: 'var(--error)', color: 'var(--text-primary)', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }}>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {editingJob && editForm && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 60,
            background: "rgba(0,0,0,0.72)",
            backdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "1rem",
          }}
        >
          <div
            style={{
              width: "min(860px, 100%)",
              maxHeight: "90vh",
              overflow: "auto",
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: "1rem",
              boxShadow: "0 24px 80px rgba(0,0,0,0.45)",
            }}
          >
            <div className="flex items-start justify-between gap-4" style={{ padding: "1.25rem", borderBottom: "1px solid var(--border)" }}>
              <div>
                <h2 style={{ color: "var(--text-primary)", fontFamily: "var(--font-heading)", fontSize: "1.25rem", fontWeight: 700 }}>Editar cron</h2>
                <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Alterações internas no scheduler. Ações externas continuam exigindo aprovação fora daqui.</p>
                <code className="text-xs" style={{ color: "var(--text-muted)" }}>{editingJob.id}</code>
              </div>
              <button onClick={closeEdit} style={{ background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}>
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4" style={{ padding: "1.25rem" }}>
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Nome
                <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
              </label>
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Agent ID
                <input value={editForm.agentId} onChange={(e) => setEditForm({ ...editForm, agentId: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
              </label>
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Tipo de agenda
                <select value={editForm.scheduleKind} onChange={(e) => setEditForm({ ...editForm, scheduleKind: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
                  <option value="cron">cron</option>
                  <option value="every">every</option>
                  <option value="at">at</option>
                </select>
              </label>
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Timezone
                <input value={editForm.tz} onChange={(e) => setEditForm({ ...editForm, tz: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} placeholder="America/Sao_Paulo" />
              </label>

              {editForm.scheduleKind === "cron" && (
                <label className="text-sm md:col-span-2" style={{ color: "var(--text-secondary)" }}>
                  Expressão cron
                  <input value={editForm.expr} onChange={(e) => setEditForm({ ...editForm, expr: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2 font-mono" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} placeholder="0 8 * * 1-5" />
                </label>
              )}
              {editForm.scheduleKind === "every" && (
                <label className="text-sm md:col-span-2" style={{ color: "var(--text-secondary)" }}>
                  Intervalo em ms
                  <input value={editForm.everyMs} onChange={(e) => setEditForm({ ...editForm, everyMs: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2 font-mono" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} placeholder="3600000" />
                </label>
              )}
              {editForm.scheduleKind === "at" && (
                <label className="text-sm md:col-span-2" style={{ color: "var(--text-secondary)" }}>
                  Executar em ISO
                  <input value={editForm.at} onChange={(e) => setEditForm({ ...editForm, at: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2 font-mono" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} placeholder="2026-04-29T20:00:00-03:00" />
                </label>
              )}
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Session target
                <input value={editForm.sessionTarget} onChange={(e) => setEditForm({ ...editForm, sessionTarget: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} placeholder="isolated | main | current" />
              </label>
              <label className="text-sm" style={{ color: "var(--text-secondary)" }}>
                Ativo
                <select value={String(editForm.enabled)} onChange={(e) => setEditForm({ ...editForm, enabled: e.target.value === "true" })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }}>
                  <option value="true">ativo</option>
                  <option value="false">pausado</option>
                </select>
              </label>
              <label className="text-sm md:col-span-2" style={{ color: "var(--text-secondary)" }}>
                Descrição
                <input value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)" }} />
              </label>
              <label className="text-sm md:col-span-2" style={{ color: "var(--text-secondary)" }}>
                Mensagem / payload
                <textarea value={editForm.message} onChange={(e) => setEditForm({ ...editForm, message: e.target.value })} rows={7} className="mt-1 w-full rounded-lg px-3 py-2" style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text-primary)", fontFamily: "var(--font-mono, monospace)" }} />
              </label>
            </div>

            <div className="flex items-center justify-between gap-3" style={{ padding: "1rem 1.25rem", borderTop: "1px solid var(--border)" }}>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>Dica: para health limpo, mantenha instrução de responder NO_REPLY quando não houver problema.</p>
              <div className="flex gap-2">
                <button onClick={closeEdit} disabled={isSavingEdit} className="rounded-lg px-4 py-2 text-sm" style={{ color: "var(--text-secondary)", background: "transparent", border: "1px solid var(--border)", cursor: "pointer" }}>Cancelar</button>
                <button onClick={saveEdit} disabled={isSavingEdit} className="rounded-lg px-4 py-2 text-sm font-semibold" style={{ color: "white", background: "var(--accent)", border: "none", cursor: isSavingEdit ? "not-allowed" : "pointer", opacity: isSavingEdit ? 0.7 : 1 }}>
                  <Save className="w-4 h-4 inline mr-2" />{isSavingEdit ? "Salvando..." : "Salvar cron"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Run toast notification */}
      {runToast && (
        <div
          style={{
            position: 'fixed',
            bottom: '2.5rem',
            right: '1.5rem',
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.875rem 1.25rem',
            borderRadius: '0.75rem',
            backdropFilter: 'blur(12px)',
            backgroundColor: runToast.status === "success"
              ? 'color-mix(in srgb, var(--success) 15%, rgba(12,12,12,0.95))'
              : 'color-mix(in srgb, var(--error) 15%, rgba(12,12,12,0.95))',
            border: `1px solid ${runToast.status === "success" ? 'color-mix(in srgb, var(--success) 40%, transparent)' : 'color-mix(in srgb, var(--error) 40%, transparent)'}`,
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            color: 'var(--text-primary)',
            fontSize: '0.875rem',
            fontWeight: 500,
            animation: 'slideInRight 0.3s ease',
          }}
        >
          <Zap
            className="w-4 h-4"
            style={{ color: runToast.status === "success" ? 'var(--success)' : 'var(--error)' }}
          />
          {runToast.status === "success"
            ? `✓ "${runToast.name}" triggered!`
            : `✗ Failed to trigger "${runToast.name}"`}
        </div>
      )}

      <style jsx global>{`
        @keyframes slideInRight {
          from { transform: translateX(2rem); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}
