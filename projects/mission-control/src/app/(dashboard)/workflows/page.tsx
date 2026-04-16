'use client';

import { useEffect, useState, useCallback } from 'react';
import { Zap, Plus, Trash2, Play, Pause, RefreshCw, Edit3, X, Check, Clock, Save } from 'lucide-react';

interface CronSchedule {
  kind: string;
  expr?: string;
  tz?: string;
  everyMs?: number;
  at?: string;
}

interface CronJob {
  id: string;
  name: string;
  schedule: CronSchedule | string;
  scheduleDisplay?: string;
  description?: string;
  enabled: boolean;
  agentId?: string;
  lastRun?: string | null;
  nextRun?: string | null;
}

function getCronExpr(schedule: CronSchedule | string): string {
  if (typeof schedule === 'string') return schedule;
  if (schedule?.kind === 'cron') return schedule.expr || '';
  return '';
}

function getScheduleDisplay(job: CronJob): string {
  if (job.scheduleDisplay) return job.scheduleDisplay;
  return getCronExpr(job.schedule) || String(job.schedule);
}

const AGENTS_LIST = ['main', 'mia', 'mensura', 'pcs', 'rh', 'marketing', 'producao', 'finance', 'autopilot', 'juridico', 'bi', 'suprimentos'];

interface EditForm {
  expr: string;
  tz: string;
  enabled: boolean;
}

export default function WorkflowsPage() {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [editId, setEditId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<EditForm>({ expr: '', tz: '', enabled: true });
  const [showNew, setShowNew] = useState(false);
  const [newForm, setNewForm] = useState({ name: '', expr: '0 9 * * *', tz: 'America/Sao_Paulo', agentId: 'main', message: '' });
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);

  const showToast = (msg: string, type: 'ok' | 'err' = 'ok') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/cron');
      const data = await res.json();
      // API can return array or { jobs: [] }
      setJobs(Array.isArray(data) ? data : (data.jobs || []));
    } catch { setJobs([]); }
    setLoading(false);
  }, []);

  useEffect(() => { loadJobs(); }, [loadJobs]);

  const startEdit = (job: CronJob) => {
    setEditId(job.id);
    setEditForm({
      expr: getCronExpr(job.schedule),
      tz: (typeof job.schedule === 'object' && job.schedule?.tz) ? job.schedule.tz : 'America/Sao_Paulo',
      enabled: job.enabled,
    });
  };

  const saveEdit = async () => {
    if (!editId) return;
    setActionLoading(editId);
    try {
      const res = await fetch('/api/cron', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: editId, expr: editForm.expr, tz: editForm.tz }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.error || 'Erro');
      showToast('✅ Workflow atualizado!');
      setEditId(null);
      loadJobs();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setActionLoading(null);
  };

  const createJob = async () => {
    if (!newForm.name.trim() || !newForm.expr.trim()) {
      showToast('Nome e expressão cron são obrigatórios', 'err');
      return;
    }
    setActionLoading('new');
    try {
      const res = await fetch('/api/cron', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newForm.name,
          agentId: newForm.agentId,
          expr: newForm.expr,
          tz: newForm.tz,
          message: newForm.message || `Workflow automático: ${newForm.name}`,
        }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.error || 'Erro');
      showToast('✅ Workflow criado!');
      setShowNew(false);
      setNewForm({ name: '', expr: '0 9 * * *', tz: 'America/Sao_Paulo', agentId: 'main', message: '' });
      loadJobs();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setActionLoading(null);
  };

  const toggleJob = async (job: CronJob) => {
    setActionLoading(job.id + '-toggle');
    try {
      const res = await fetch('/api/cron', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: job.id, enabled: !job.enabled }),
      });
      if (!res.ok) throw new Error((await res.json()).error);
      showToast(job.enabled ? '⏸️ Pausado' : '▶️ Ativado');
      loadJobs();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setActionLoading(null);
  };

  const runJob = async (job: CronJob) => {
    setActionLoading(job.id + '-run');
    try {
      const res = await fetch('/api/cron/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: job.id }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.error || 'Erro');
      showToast(`▶️ Executando: ${job.name}`);
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setActionLoading(null);
  };

  const deleteJob = async (job: CronJob) => {
    if (!confirm(`Deletar workflow "${job.name}"? Esta ação não pode ser desfeita.`)) return;
    setActionLoading(job.id + '-del');
    try {
      const res = await fetch(`/api/cron?id=${encodeURIComponent(job.id)}`, { method: 'DELETE' });
      if (!res.ok) throw new Error((await res.json()).error);
      showToast('🗑️ Workflow removido');
      loadJobs();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setActionLoading(null);
  };

  const inputStyle = {
    width: '100%', padding: '8px 12px', borderRadius: 8, fontSize: 13,
    backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
    color: '#fff', outline: 'none', boxSizing: 'border-box' as const,
  };

  const btnStyle = (color: string, disabled = false) => ({
    padding: '5px 10px', borderRadius: 7, fontSize: 12, fontWeight: 600,
    cursor: disabled ? 'wait' : 'pointer',
    backgroundColor: `${color}20`, border: `1px solid ${color}50`, color,
    display: 'flex', alignItems: 'center', gap: 4,
    opacity: disabled ? 0.6 : 1,
  });

  return (
    <div style={{ padding: '24px', maxWidth: 1000 }}>
      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 70, right: 20, zIndex: 9999,
          backgroundColor: toast.type === 'ok' ? 'rgba(16,185,129,0.95)' : 'rgba(239,68,68,0.95)',
          color: '#fff', padding: '10px 18px', borderRadius: 10, fontWeight: 600, fontSize: 14,
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        }}>{toast.msg}</div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Zap size={24} style={{ color: '#f59e0b' }} />
            Workflows
            <span style={{ fontSize: 14, color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>
              {jobs.filter(j => j.enabled).length}/{jobs.length} ativos
            </span>
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 13, marginTop: 4 }}>
            Gerencie cron jobs e workflows automatizados do OpenClaw
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button style={btnStyle('#6b7280')} onClick={loadJobs}>
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} /> Atualizar
          </button>
          <button style={btnStyle('#22c55e')} onClick={() => setShowNew(v => !v)}>
            <Plus size={12} /> Novo Workflow
          </button>
        </div>
      </div>

      {/* New workflow form */}
      {showNew && (
        <div style={{
          backgroundColor: 'rgba(34,197,94,0.05)', border: '1px solid rgba(34,197,94,0.3)',
          borderRadius: 12, padding: 20, marginBottom: 16,
        }}>
          <h3 style={{ color: '#22c55e', fontSize: 15, fontWeight: 700, marginBottom: 16 }}>+ Novo Workflow</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Nome *</label>
              <input value={newForm.name} onChange={e => setNewForm(p => ({ ...p, name: e.target.value }))} style={inputStyle} placeholder="Ex: Relatório Diário" />
            </div>
            <div>
              <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Expressão Cron *</label>
              <input value={newForm.expr} onChange={e => setNewForm(p => ({ ...p, expr: e.target.value }))} style={inputStyle} placeholder="0 9 * * *" />
              <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', marginTop: 2 }}>
                min hora dia mês dia-semana · Ex: "0 9 * * 1-5" = seg-sex às 9h
              </div>
            </div>
            <div>
              <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Agente</label>
              <select value={newForm.agentId} onChange={e => setNewForm(p => ({ ...p, agentId: e.target.value }))} style={{ ...inputStyle, cursor: 'pointer' }}>
                {AGENTS_LIST.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Fuso Horário</label>
              <input value={newForm.tz} onChange={e => setNewForm(p => ({ ...p, tz: e.target.value }))} style={inputStyle} placeholder="America/Sao_Paulo" />
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Mensagem para o Agente (opcional)</label>
            <textarea value={newForm.message} onChange={e => setNewForm(p => ({ ...p, message: e.target.value }))}
              style={{ ...inputStyle, minHeight: 70, resize: 'vertical' }}
              placeholder="O que o agente deve fazer quando este workflow executar?" />
          </div>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button style={btnStyle('#6b7280')} onClick={() => setShowNew(false)}><X size={12} /> Cancelar</button>
            <button style={btnStyle('#22c55e', actionLoading === 'new')} onClick={createJob} disabled={actionLoading === 'new'}>
              {actionLoading === 'new' ? <RefreshCw size={12} className="animate-spin" /> : <Check size={12} />}
              Criar Workflow
            </button>
          </div>
        </div>
      )}

      {/* Jobs list */}
      {loading ? (
        <div style={{ color: 'rgba(255,255,255,0.4)', textAlign: 'center', padding: 40 }}>
          <RefreshCw size={24} className="animate-spin" style={{ display: 'inline' }} />
        </div>
      ) : jobs.length === 0 ? (
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.03)', border: '1px dashed rgba(255,255,255,0.1)',
          borderRadius: 12, padding: 40, textAlign: 'center',
        }}>
          <Zap size={32} style={{ color: 'rgba(255,255,255,0.1)', margin: '0 auto 12px', display: 'block' }} />
          <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 14 }}>Nenhum workflow configurado no OpenClaw</p>
          <button style={{ ...btnStyle('#22c55e'), margin: '12px auto 0', display: 'inline-flex' }} onClick={() => setShowNew(true)}>
            <Plus size={13} /> Criar primeiro workflow
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {jobs.map(job => (
            <div key={job.id} style={{
              backgroundColor: 'rgba(255,255,255,0.03)',
              border: `1px solid ${job.enabled ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.07)'}`,
              borderRadius: 12, overflow: 'hidden',
            }}>
              {editId === job.id ? (
                /* EDIT MODE */
                <div style={{ padding: 16 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                    <div>
                      <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Expressão Cron</label>
                      <input value={editForm.expr} onChange={e => setEditForm(p => ({ ...p, expr: e.target.value }))} style={inputStyle} />
                    </div>
                    <div>
                      <label style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, display: 'block', marginBottom: 4 }}>Fuso Horário</label>
                      <input value={editForm.tz} onChange={e => setEditForm(p => ({ ...p, tz: e.target.value }))} style={inputStyle} placeholder="America/Sao_Paulo" />
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                    <button style={btnStyle('#6b7280')} onClick={() => setEditId(null)}><X size={12} /> Cancelar</button>
                    <button style={btnStyle('#ff6b35', actionLoading === editId)} onClick={saveEdit} disabled={actionLoading === editId}>
                      {actionLoading === editId ? <RefreshCw size={12} className="animate-spin" /> : <Save size={12} />}
                      Salvar
                    </button>
                  </div>
                </div>
              ) : (
                /* VIEW MODE */
                <div style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                  <div style={{
                    width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
                    backgroundColor: job.enabled ? '#22c55e' : '#6b7280',
                    boxShadow: job.enabled ? '0 0 6px #22c55e' : 'none',
                  }} />
                  <div style={{ flex: 1, minWidth: 200 }}>
                    <div style={{ color: '#fff', fontSize: 14, fontWeight: 700 }}>{job.name}</div>
                    {job.description && (
                      <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12, marginTop: 2 }}>{job.description}</div>
                    )}
                    <div style={{ display: 'flex', gap: 12, marginTop: 4, flexWrap: 'wrap' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'rgba(255,255,255,0.4)', fontSize: 11 }}>
                        <Clock size={10} /> {getScheduleDisplay(job)}
                      </span>
                      {job.agentId && (
                        <span style={{ color: '#60a5fa', fontSize: 11 }}>@{job.agentId}</span>
                      )}
                      {job.nextRun && (
                        <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11 }}>
                          Próximo: {new Date(job.nextRun).toLocaleString('pt-BR')}
                        </span>
                      )}
                      {job.lastRun && (
                        <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: 11 }}>
                          Último: {new Date(job.lastRun).toLocaleString('pt-BR')}
                        </span>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 6, flexShrink: 0, flexWrap: 'wrap' }}>
                    <button style={btnStyle('#22c55e', !!actionLoading)} onClick={() => runJob(job)} title="Executar agora">
                      {actionLoading === job.id + '-run' ? <RefreshCw size={11} className="animate-spin" /> : <Play size={11} />}
                      Executar
                    </button>
                    <button style={btnStyle(job.enabled ? '#f59e0b' : '#22c55e', !!actionLoading)} onClick={() => toggleJob(job)}>
                      {job.enabled ? <Pause size={11} /> : <Play size={11} />}
                      {job.enabled ? 'Pausar' : 'Ativar'}
                    </button>
                    <button style={btnStyle('#60a5fa')} onClick={() => startEdit(job)}>
                      <Edit3 size={11} /> Editar
                    </button>
                    <button style={btnStyle('#ef4444', actionLoading === job.id + '-del')} onClick={() => deleteJob(job)}>
                      {actionLoading === job.id + '-del' ? <RefreshCw size={11} className="animate-spin" /> : <Trash2 size={11} />}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
