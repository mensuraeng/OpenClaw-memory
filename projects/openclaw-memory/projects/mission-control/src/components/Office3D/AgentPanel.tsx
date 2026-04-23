'use client';

import { X, Activity, MessageSquare, Clock, Cpu, ExternalLink, BarChart2 } from 'lucide-react';
import type { AgentConfig, AgentState } from './agentsConfig';

interface AgentPanelProps {
  agent: AgentConfig;
  state: AgentState;
  onClose: () => void;
}

export default function AgentPanel({ agent, state, onClose }: AgentPanelProps) {
  const statusConfig = {
    working: { label: 'Trabalhando', color: '#22c55e', bg: 'rgba(34,197,94,0.15)' },
    thinking: { label: 'Processando', color: '#3b82f6', bg: 'rgba(59,130,246,0.15)' },
    error:    { label: 'Erro',        color: '#ef4444', bg: 'rgba(239,68,68,0.15)' },
    idle:     { label: 'Ocioso',      color: '#6b7280', bg: 'rgba(107,114,128,0.15)' },
  };
  const sc = statusConfig[state.status] || statusConfig.idle;

  // Parar TODOS os eventos de pointer/mouse para não vazar para o Canvas
  const stopAll = (e: React.SyntheticEvent) => {
    e.stopPropagation();
    e.nativeEvent?.stopImmediatePropagation?.();
  };

  return (
    <div
      onPointerDown={stopAll}
      onPointerUp={stopAll}
      onClick={stopAll}
      onMouseDown={stopAll}
      onMouseUp={stopAll}
      onTouchStart={stopAll}
      style={{
        position: 'fixed',
        top: 48,        // abaixo do TopBar
        right: 0,
        bottom: 32,     // acima do StatusBar
        width: 380,
        backgroundColor: 'rgba(10,10,26,0.97)',
        backdropFilter: 'blur(16px)',
        borderLeft: `1px solid ${agent.color}40`,
        zIndex: 200,    // acima do Dock (50) e TopBar (45)
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        boxShadow: `-8px 0 40px rgba(0,0,0,0.6)`,
      }}
    >
      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div style={{
        padding: '20px 20px 16px',
        borderBottom: `1px solid ${agent.color}30`,
        background: `linear-gradient(135deg, ${agent.color}10, transparent)`,
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 52, height: 52, borderRadius: 12,
              backgroundColor: `${agent.color}25`,
              border: `2px solid ${agent.color}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 26,
            }}>
              {agent.emoji}
            </div>
            <div>
              <h2 style={{ color: '#fff', fontSize: 18, fontWeight: 700, margin: 0 }}>
                {agent.name}
              </h2>
              <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, margin: '3px 0 0' }}>
                {agent.role}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: 8, borderRadius: 8, cursor: 'pointer',
              backgroundColor: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'rgba(255,255,255,0.6)',
              display: 'flex', alignItems: 'center',
            }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Status badge */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 7,
          marginTop: 14, padding: '5px 12px', borderRadius: 20,
          backgroundColor: sc.bg, border: `1px solid ${sc.color}50`,
        }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            backgroundColor: sc.color,
            boxShadow: state.status !== 'idle' ? `0 0 6px ${sc.color}` : 'none',
            animation: state.status === 'working' || state.status === 'thinking' ? 'pulse 2s infinite' : 'none',
          }} />
          <span style={{ color: sc.color, fontSize: 11, fontWeight: 700, letterSpacing: '1px' }}>
            {sc.label.toUpperCase()}
          </span>
        </div>
      </div>

      {/* ── Corpo ──────────────────────────────────────────────────────────── */}
      <div style={{ padding: '16px 20px', flex: 1 }}>

        {/* Tarefa atual */}
        {state.currentTask && (
          <div style={{
            padding: '12px 14px', borderRadius: 10, marginBottom: 16,
            backgroundColor: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
          }}>
            <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 10, fontWeight: 600, letterSpacing: '1px', marginBottom: 5 }}>
              TAREFA ATUAL
            </div>
            <p style={{ color: '#fff', fontSize: 13, margin: 0 }}>{state.currentTask}</p>
          </div>
        )}

        {/* Stats em grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 16 }}>
          {[
            { icon: Cpu,      label: 'Modelo',   value: state.model || 'N/D' },
            { icon: Activity, label: 'Sessões',   value: `${state.tasksInQueue ?? 0} ativa${(state.tasksInQueue ?? 0) !== 1 ? 's' : ''}` },
            { icon: BarChart2,label: 'Tok/hora',  value: (state.tokensPerHour ?? 0).toLocaleString('pt-BR') },
            { icon: Clock,    label: 'Uptime',    value: state.uptime ? `${state.uptime}d` : '—' },
          ].map(({ icon: Icon, label, value }) => (
            <div key={label} style={{
              padding: '10px 12px', borderRadius: 8,
              backgroundColor: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.07)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 5 }}>
                <Icon size={11} style={{ color: 'rgba(255,255,255,0.3)' }} />
                <span style={{ color: 'rgba(255,255,255,0.35)', fontSize: 10, letterSpacing: '0.5px' }}>{label}</span>
              </div>
              <p style={{ color: '#fff', fontSize: 14, fontWeight: 700, margin: 0, fontFamily: 'monospace' }}>
                {value}
              </p>
            </div>
          ))}
        </div>

        {/* Ações rápidas */}
        <div style={{
          borderTop: '1px solid rgba(255,255,255,0.08)',
          paddingTop: 16, marginBottom: 16,
        }}>
          <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 10, fontWeight: 600, letterSpacing: '1px', marginBottom: 10 }}>
            AÇÕES RÁPIDAS
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {[
              { label: '💬 Sessões',   href: `/sessions?agent=${agent.id}`,   color: agent.color },
              { label: '🧠 Memória',   href: `/memory?agent=${agent.id}`,     color: '#8b5cf6' },
              { label: '📋 Atividade', href: `/activity?agent=${agent.id}`,   color: '#06b6d4' },
              { label: '📜 Logs',      href: `/logs?agent=${agent.id}`,       color: '#f59e0b' },
            ].map(({ label, href, color }) => (
              <a
                key={label}
                href={href}
                onClick={stopAll}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  padding: '9px 8px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  backgroundColor: `${color}15`,
                  border: `1px solid ${color}40`,
                  color: color, textDecoration: 'none',
                  cursor: 'pointer', transition: 'all 150ms',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.backgroundColor = `${color}30`; }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.backgroundColor = `${color}15`; }}
              >
                {label}
              </a>
            ))}
          </div>
        </div>

        {/* Barra de cor do agente */}
        <div style={{
          padding: '10px 14px', borderRadius: 8,
          backgroundColor: `${agent.color}10`,
          border: `1px solid ${agent.color}30`,
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <div style={{ width: 4, height: 36, borderRadius: 2, backgroundColor: agent.color, flexShrink: 0 }} />
          <div>
            <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 10, letterSpacing: '0.5px' }}>WORKSPACE</div>
            <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 11, fontFamily: 'monospace', marginTop: 2 }}>
              {agent.id}
            </div>
          </div>
          <a
            href={`/files?workspace=${agent.id}`}
            onClick={stopAll}
            style={{
              marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4,
              color: agent.color, fontSize: 11, textDecoration: 'none', fontWeight: 600,
            }}
          >
            Arquivos <ExternalLink size={10} />
          </a>
        </div>
      </div>
    </div>
  );
}
