'use client';

import { useState, useCallback, useEffect } from 'react';
import { Zap, RefreshCw, Play, CheckCircle, AlertTriangle, Activity, RotateCcw, Power, Database, Terminal } from 'lucide-react';

interface Action {
  id: string;
  icon: string;
  label: string;
  description: string;
  category: string;
  color: string;
  confirmRequired?: boolean;
  apiEndpoint?: string;
  apiMethod?: string;
  apiBody?: Record<string, unknown>;
}

const ACTIONS: Action[] = [
  // Agentes
  {
    id: 'refresh-agents',
    icon: '🔄',
    label: 'Atualizar Status dos Agentes',
    description: 'Atualiza o status de todos os agentes no dashboard',
    category: 'Agentes',
    color: '#22c55e',
    apiEndpoint: '/api/agents',
    apiMethod: 'GET',
  },
  {
    id: 'restart-mc',
    icon: '♻️',
    label: 'Reiniciar Mission Control',
    description: 'Reinicia o processo do Mission Control via PM2',
    category: 'Agentes',
    color: '#f59e0b',
    confirmRequired: true,
    apiEndpoint: '/api/system',
    apiMethod: 'POST',
    apiBody: { action: 'restart-pm2', target: 'mission-control' },
  },
  // Sistema
  {
    id: 'health-check',
    icon: '❤️',
    label: 'Health Check',
    description: 'Verifica saúde do sistema e conexões',
    category: 'Sistema',
    color: '#3b82f6',
    apiEndpoint: '/api/health',
    apiMethod: 'GET',
  },
  {
    id: 'clear-logs',
    icon: '🧹',
    label: 'Limpar Logs Antigos',
    description: 'Remove logs com mais de 30 dias do workspace',
    category: 'Sistema',
    color: '#8b5cf6',
    confirmRequired: true,
    apiEndpoint: '/api/system',
    apiMethod: 'POST',
    apiBody: { action: 'clear-old-logs' },
  },
  // Cron
  {
    id: 'run-all-cron',
    icon: '⏰',
    label: 'Executar Todos os Cron Jobs',
    description: 'Força execução imediata de todos os workflows ativos',
    category: 'Cron',
    color: '#f59e0b',
    confirmRequired: true,
    apiEndpoint: '/api/cron/run',
    apiMethod: 'POST',
    apiBody: { all: true },
  },
  // Memória
  {
    id: 'memory-backup',
    icon: '💾',
    label: 'Backup de Memória',
    description: 'Cria backup dos arquivos de memória de todos os agentes',
    category: 'Memória',
    color: '#06b6d4',
    apiEndpoint: '/api/system',
    apiMethod: 'POST',
    apiBody: { action: 'backup-memory' },
  },
  {
    id: 'reload-config',
    icon: '🔧',
    label: 'Recarregar Config OpenClaw',
    description: 'Recarrega openclaw.json sem reiniciar o sistema',
    category: 'Sistema',
    color: '#ff6b35',
    apiEndpoint: '/api/system',
    apiMethod: 'POST',
    apiBody: { action: 'reload-config' },
  },
];

interface ActionResult {
  id: string;
  status: 'running' | 'success' | 'error';
  message: string;
  timestamp: Date;
}

export default function ActionsPage() {
  const [results, setResults] = useState<ActionResult[]>([]);
  const [running, setRunning] = useState<Set<string>>(new Set());

  const categories = [...new Set(ACTIONS.map(a => a.category))];

  const executeAction = useCallback(async (action: Action) => {
    if (action.confirmRequired) {
      if (!confirm(`Executar: "${action.label}"?\n\n${action.description}`)) return;
    }

    setRunning(prev => new Set([...prev, action.id]));
    setResults(prev => [
      { id: action.id, status: 'running', message: 'Executando...', timestamp: new Date() },
      ...prev.filter(r => r.id !== action.id).slice(0, 19),
    ]);

    try {
      const endpoint = action.apiEndpoint || '/api/health';
      const method = action.apiMethod || 'GET';
      const opts: RequestInit = { method };
      if (method !== 'GET' && action.apiBody) {
        opts.headers = { 'Content-Type': 'application/json' };
        opts.body = JSON.stringify(action.apiBody);
      }

      const res = await fetch(endpoint, opts);
      const data = await res.json().catch(() => ({}));

      setResults(prev => prev.map(r => r.id === action.id ? {
        ...r,
        status: res.ok ? 'success' : 'error',
        message: data.message || data.error || (res.ok ? 'Concluído com sucesso' : `Erro ${res.status}`),
      } : r));
    } catch (e) {
      setResults(prev => prev.map(r => r.id === action.id ? {
        ...r, status: 'error', message: String(e),
      } : r));
    }

    setRunning(prev => { const n = new Set(prev); n.delete(action.id); return n; });
  }, []);

  const getResult = (id: string) => results.find(r => r.id === id);

  const btnStyle = (color: string, disabled: boolean) => ({
    display: 'flex', alignItems: 'center', gap: 8,
    padding: '12px 16px', borderRadius: 10, cursor: disabled ? 'wait' : 'pointer',
    backgroundColor: `${color}12`, border: `1px solid ${color}35`,
    width: '100%', textAlign: 'left' as const,
    opacity: disabled ? 0.6 : 1,
    transition: 'all 150ms',
  });

  return (
    <div style={{ padding: '24px', maxWidth: 900 }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Zap size={24} style={{ color: '#f59e0b' }} />
          Ações Rápidas
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 13, marginTop: 4 }}>
          Execute ações administrativas no sistema OpenClaw
        </p>
      </div>

      {/* Results log */}
      {results.length > 0 && (
        <div style={{
          marginBottom: 24, backgroundColor: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 12, padding: 16,
        }}>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, fontWeight: 700, letterSpacing: '1px', marginBottom: 10 }}>
            LOG DE EXECUÇÃO
          </div>
          {results.map((r, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 6 }}>
              {r.status === 'running' && <RefreshCw size={13} className="animate-spin" style={{ color: '#60a5fa', marginTop: 1, flexShrink: 0 }} />}
              {r.status === 'success' && <CheckCircle size={13} style={{ color: '#22c55e', marginTop: 1, flexShrink: 0 }} />}
              {r.status === 'error' && <AlertTriangle size={13} style={{ color: '#ef4444', marginTop: 1, flexShrink: 0 }} />}
              <div style={{ flex: 1 }}>
                <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>
                  {r.timestamp.toLocaleTimeString('pt-BR')} · {ACTIONS.find(a => a.id === r.id)?.label}:
                </span>
                <span style={{
                  fontSize: 11, marginLeft: 6,
                  color: r.status === 'success' ? '#22c55e' : r.status === 'error' ? '#ef4444' : '#60a5fa',
                }}>
                  {r.message}
                </span>
              </div>
            </div>
          ))}
          <button
            onClick={() => setResults([])}
            style={{ marginTop: 8, fontSize: 11, color: 'rgba(255,255,255,0.3)', background: 'none', border: 'none', cursor: 'pointer' }}>
            Limpar log
          </button>
        </div>
      )}

      {/* Actions by category */}
      {categories.map(cat => (
        <div key={cat} style={{ marginBottom: 24 }}>
          <h2 style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, fontWeight: 700, letterSpacing: '1px', marginBottom: 12 }}>
            {cat.toUpperCase()}
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
            {ACTIONS.filter(a => a.category === cat).map(action => {
              const result = getResult(action.id);
              const isRunning = running.has(action.id);
              return (
                <button
                  key={action.id}
                  style={btnStyle(action.color, isRunning)}
                  onClick={() => executeAction(action)}
                  disabled={isRunning}
                  onMouseEnter={e => { if (!isRunning) (e.currentTarget as HTMLButtonElement).style.backgroundColor = `${action.color}20`; }}
                  onMouseLeave={e => { if (!isRunning) (e.currentTarget as HTMLButtonElement).style.backgroundColor = `${action.color}12`; }}
                >
                  <span style={{ fontSize: 22 }}>{action.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#fff', fontSize: 13, fontWeight: 600 }}>{action.label}</div>
                    <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginTop: 2 }}>{action.description}</div>
                    {result && result.status !== 'running' && (
                      <div style={{
                        fontSize: 11, marginTop: 4,
                        color: result.status === 'success' ? '#22c55e' : '#ef4444',
                      }}>
                        {result.status === 'success' ? '✓ ' : '✗ '}{result.message}
                      </div>
                    )}
                  </div>
                  <div style={{ flexShrink: 0 }}>
                    {isRunning
                      ? <RefreshCw size={16} className="animate-spin" style={{ color: action.color }} />
                      : result?.status === 'success'
                        ? <CheckCircle size={16} style={{ color: '#22c55e' }} />
                        : result?.status === 'error'
                          ? <AlertTriangle size={16} style={{ color: '#ef4444' }} />
                          : <Play size={16} style={{ color: action.color }} />
                    }
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
