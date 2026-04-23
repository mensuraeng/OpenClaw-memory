'use client';

import { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Calendar, Play, RefreshCw, Clock } from 'lucide-react';

interface CronSchedule {
  kind: string;
  expr?: string;
  tz?: string;
  everyMs?: number;
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

function parseCronToHoursAndDays(schedule: CronSchedule | string): { hour: number; minute: number; days: number[] } | null {
  let expr = '';
  if (typeof schedule === 'string') expr = schedule;
  else if (schedule?.kind === 'cron') expr = schedule.expr || '';
  else return null;

  const parts = expr.trim().split(/\s+/);
  if (parts.length < 5) return null;
  const [min, hour, , , dow] = parts;
  const h = parseInt(hour, 10);
  const m = parseInt(min, 10);
  if (isNaN(h) || isNaN(m)) return null;

  let days = [0, 1, 2, 3, 4, 5, 6]; // all days
  if (dow !== '*') {
    days = dow.split(',').flatMap(d => {
      if (d.includes('-')) {
        const [start, end] = d.split('-').map(Number);
        return Array.from({ length: end - start + 1 }, (_, i) => start + i);
      }
      return [parseInt(d, 10)];
    }).filter(d => !isNaN(d));
  }
  return { hour: h, minute: m, days };
}

function getWeekDays(weekStart: Date): Date[] {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + i);
    return d;
  });
}

function startOfWeekMonday(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay(); // 0=Sun
  d.setDate(d.getDate() - (day === 0 ? 6 : day - 1));
  d.setHours(0, 0, 0, 0);
  return d;
}

const AGENT_COLORS: Record<string, string> = {
  main: '#ff6b35', mia: '#3b82f6', mensura: '#ef4444', pcs: '#7c3aed',
  rh: '#8b5cf6', marketing: '#ec4899', producao: '#f59e0b', finance: '#10b981',
  autopilot: '#6b7280', juridico: '#6366f1', bi: '#06b6d4', suprimentos: '#d97706',
};

const DOW_LABELS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
// Hours from 6am to 10pm
const HOURS = Array.from({ length: 17 }, (_, i) => i + 6);

export default function CalendarPage() {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [weekStart, setWeekStart] = useState(() => startOfWeekMonday(new Date()));
  const [runningJob, setRunningJob] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  useEffect(() => {
    fetch('/api/cron')
      .then(r => r.json())
      .then(d => setJobs(Array.isArray(d) ? d : (d.jobs || [])))
      .catch(() => setJobs([]))
      .finally(() => setLoading(false));
  }, []);

  const days = getWeekDays(weekStart);
  const todayMidnight = new Date();
  todayMidnight.setHours(0, 0, 0, 0);

  const getJobsForSlot = (day: Date, hour: number) => {
    return jobs.filter(job => {
      const parsed = parseCronToHoursAndDays(job.schedule);
      if (!parsed) return false;
      if (parsed.hour !== hour) return false;
      const jsDay = day.getDay(); // 0=Sun,1=Mon...6=Sat
      // cron: 0=Sun, 1=Mon...7=Sun; or Mon=1 format
      return parsed.days.includes(jsDay) || parsed.days.includes(jsDay === 0 ? 7 : jsDay);
    });
  };

  const runJob = async (job: CronJob) => {
    setRunningJob(job.id);
    try {
      const res = await fetch('/api/cron/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: job.id }),
      });
      const d = await res.json();
      showToast(res.ok ? `▶️ ${job.name} iniciado!` : `❌ ${d.error}`);
    } catch (e) { showToast(`❌ ${e}`); }
    setRunningJob(null);
  };

  const prevWeek = () => { const d = new Date(weekStart); d.setDate(d.getDate() - 7); setWeekStart(d); };
  const nextWeek = () => { const d = new Date(weekStart); d.setDate(d.getDate() + 7); setWeekStart(d); };
  const goToday = () => setWeekStart(startOfWeekMonday(new Date()));

  const isToday = (d: Date) => d.getTime() === todayMidnight.getTime();
  const isPast = (d: Date) => d.getTime() < todayMidnight.getTime();

  // For every jobs, show next occurrence
  const everyJobs = jobs.filter(j => {
    if (typeof j.schedule === 'object' && j.schedule?.kind === 'every') return true;
    return false;
  });

  return (
    <div style={{ padding: '24px', height: '100%', display: 'flex', flexDirection: 'column', gap: 16 }}>
      {toast && (
        <div style={{
          position: 'fixed', top: 70, right: 20, zIndex: 9999,
          backgroundColor: 'rgba(16,185,129,0.95)', color: '#fff',
          padding: '10px 18px', borderRadius: 10, fontWeight: 600, fontSize: 14,
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        }}>{toast}</div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <h1 style={{ color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, margin: 0 }}>
          <Calendar size={24} style={{ color: '#3b82f6' }} />
          Calendário de Workflows
          <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', fontWeight: 400 }}>
            {jobs.filter(j => j.enabled).length} ativos
          </span>
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button onClick={prevWeek} style={{ padding: 7, borderRadius: 7, cursor: 'pointer', backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}>
            <ChevronLeft size={16} />
          </button>
          <button onClick={goToday} style={{ padding: '5px 12px', borderRadius: 7, cursor: 'pointer', fontSize: 12, fontWeight: 600, backgroundColor: 'rgba(59,130,246,0.15)', border: '1px solid rgba(59,130,246,0.4)', color: '#60a5fa' }}>
            Hoje
          </button>
          <button onClick={nextWeek} style={{ padding: 7, borderRadius: 7, cursor: 'pointer', backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}>
            <ChevronRight size={16} />
          </button>
          <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: 600, minWidth: 140 }}>
            {days[0].toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })} – {days[6].toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })}
          </span>
        </div>
      </div>

      {loading ? (
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <RefreshCw size={28} className="animate-spin" style={{ color: 'rgba(255,255,255,0.3)' }} />
        </div>
      ) : jobs.length === 0 ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, color: 'rgba(255,255,255,0.3)' }}>
          <Calendar size={40} style={{ opacity: 0.3 }} />
          <p>Nenhum workflow configurado.</p>
          <a href="/workflows" style={{ color: '#60a5fa', fontSize: 13 }}>Configurar em Workflows →</a>
        </div>
      ) : (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <div style={{ minWidth: 700 }}>
            {/* Day headers */}
            <div style={{ display: 'grid', gridTemplateColumns: '56px repeat(7, 1fr)', gap: 3, marginBottom: 4 }}>
              <div />
              {days.map((d, i) => (
                <div key={i} style={{
                  textAlign: 'center', padding: '8px 4px', borderRadius: 8,
                  backgroundColor: isToday(d) ? 'rgba(59,130,246,0.2)' : 'rgba(255,255,255,0.03)',
                  border: `1px solid ${isToday(d) ? 'rgba(59,130,246,0.5)' : 'rgba(255,255,255,0.06)'}`,
                }}>
                  <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, fontWeight: 600 }}>{DOW_LABELS[i]}</div>
                  <div style={{ color: isToday(d) ? '#60a5fa' : isPast(d) ? 'rgba(255,255,255,0.3)' : '#fff', fontSize: 18, fontWeight: 700 }}>
                    {d.getDate()}
                  </div>
                </div>
              ))}
            </div>

            {/* Hour slots */}
            {HOURS.map(hour => (
              <div key={hour} style={{ display: 'grid', gridTemplateColumns: '56px repeat(7, 1fr)', gap: 3, marginBottom: 2 }}>
                <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11, paddingTop: 8, textAlign: 'right', paddingRight: 8 }}>
                  {String(hour).padStart(2, '0')}h
                </div>
                {days.map((day, dayIdx) => {
                  const slotJobs = getJobsForSlot(day, hour);
                  return (
                    <div key={dayIdx} style={{
                      minHeight: 44, borderRadius: 5, padding: 3,
                      backgroundColor: slotJobs.length > 0 ? 'rgba(255,255,255,0.02)' : 'transparent',
                      border: `1px solid ${slotJobs.length > 0 ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.02)'}`,
                    }}>
                      {slotJobs.map(job => {
                        const color = AGENT_COLORS[job.agentId || 'main'] || '#ff6b35';
                        return (
                          <div key={job.id} style={{
                            padding: '3px 6px', borderRadius: 5, marginBottom: 2, fontSize: 10, fontWeight: 600,
                            backgroundColor: `${color}20`, border: `1px solid ${color}40`, color,
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 3,
                            opacity: job.enabled ? 1 : 0.4, cursor: 'pointer',
                          }}
                            title={`${job.name}\n${job.description || ''}\nCron: ${typeof job.schedule === 'object' ? job.schedule.expr || '' : job.schedule}`}
                            onClick={() => runJob(job)}
                          >
                            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {!job.enabled && '⏸ '}{job.name}
                            </span>
                            {runningJob === job.id
                              ? <RefreshCw size={8} className="animate-spin" />
                              : <Play size={8} />
                            }
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>

          {/* "Every X" jobs section */}
          {everyJobs.length > 0 && (
            <div style={{ marginTop: 20 }}>
              <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, fontWeight: 700, letterSpacing: '1px', marginBottom: 10 }}>
                INTERVALOS REGULARES
              </div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {everyJobs.map(job => {
                  const color = AGENT_COLORS[job.agentId || 'main'] || '#ff6b35';
                  const sched = typeof job.schedule === 'object' ? job.schedule : null;
                  const ms = sched?.everyMs || 0;
                  const label = ms >= 3600000 ? `a cada ${ms/3600000}h` : ms >= 60000 ? `a cada ${ms/60000}min` : `a cada ${ms/1000}s`;
                  return (
                    <div key={job.id} style={{
                      display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderRadius: 10,
                      backgroundColor: `${color}10`, border: `1px solid ${color}30`, opacity: job.enabled ? 1 : 0.5,
                    }}>
                      <Clock size={13} style={{ color }} />
                      <div>
                        <div style={{ color: '#fff', fontSize: 12, fontWeight: 700 }}>{job.name}</div>
                        <div style={{ color, fontSize: 11 }}>{label} · @{job.agentId}</div>
                      </div>
                      <button onClick={() => runJob(job)} style={{
                        padding: '3px 8px', borderRadius: 5, fontSize: 10, fontWeight: 600, cursor: 'pointer',
                        backgroundColor: `${color}20`, border: `1px solid ${color}40`, color,
                        display: 'flex', alignItems: 'center', gap: 3,
                      }}>
                        {runningJob === job.id ? <RefreshCw size={9} className="animate-spin" /> : <Play size={9} />}
                        Executar
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Legend */}
          <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {jobs.map(job => {
              const color = AGENT_COLORS[job.agentId || 'main'] || '#ff6b35';
              return (
                <div key={job.id} style={{
                  display: 'flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 20,
                  backgroundColor: `${color}10`, border: `1px solid ${color}25`,
                  opacity: job.enabled ? 1 : 0.45,
                }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: color, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)' }}>{job.name}</span>
                  <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>@{job.agentId || 'main'}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
