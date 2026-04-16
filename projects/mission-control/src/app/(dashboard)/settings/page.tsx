'use client';

import { useEffect, useState } from 'react';
import { Settings, Save, RefreshCw, Cpu, User, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';

interface AgentSetting {
  id: string;
  name: string;
  model: string;
  allowAgents: string[];
}

interface SettingsData {
  defaultModel: string;
  fallbacks: string[];
  agents: AgentSetting[];
}

const MODELS = [
  'openai/gpt-5.4',
  'openai/gpt-5.4-pro',
  'openai/gpt-4o',
  'openai/gpt-4o-mini',
  'anthropic/claude-opus-4-6',
  'anthropic/claude-sonnet-4-6',
  'anthropic/claude-haiku-4-5-20251001',
];

const AGENT_EMOJI: Record<string, string> = {
  main: '🏗️', mia: '🏛️', mensura: '📐', pcs: '🏢',
  rh: '👥', marketing: '📣', producao: '🏗️', finance: '💰',
  autopilot: '🤖', juridico: '⚖️', bi: '📊', suprimentos: '📦',
};

export default function SettingsPage() {
  const [data, setData] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [defaultModel, setDefaultModel] = useState('');
  const [agents, setAgents] = useState<AgentSetting[]>([]);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);

  const showToast = (msg: string, type: 'ok' | 'err' = 'ok') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/settings');
      const d: SettingsData = await res.json();
      setData(d);
      setDefaultModel(d.defaultModel || '');
      setAgents(d.agents || []);
    } catch {
      showToast('Erro ao carregar configurações', 'err');
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const updateAgentName = (id: string, name: string) => {
    setAgents(prev => prev.map(a => a.id === id ? { ...a, name } : a));
    setDirty(true);
  };

  const updateAgentModel = (id: string, model: string) => {
    setAgents(prev => prev.map(a => a.id === id ? { ...a, model } : a));
    setDirty(true);
  };

  const handleDefaultModelChange = (v: string) => {
    setDefaultModel(v);
    setDirty(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      const res = await fetch('/api/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ defaultModel, agents }),
      });
      const d = await res.json();
      if (!res.ok) throw new Error(d.error || 'Erro ao salvar');
      showToast('✅ ' + d.message);
      setDirty(false);
    } catch (e) {
      showToast(`❌ ${e}`, 'err');
    }
    setSaving(false);
  };

  const S = {
    page: { padding: '24px', maxWidth: 900 },
    header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap' as const, gap: 12 },
    title: { color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 },
    card: {
      backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 12, padding: 20, marginBottom: 16,
    },
    cardTitle: { color: 'rgba(255,255,255,0.6)', fontSize: 11, fontWeight: 700, letterSpacing: '1px', marginBottom: 16 },
    label: { color: 'rgba(255,255,255,0.5)', fontSize: 12, fontWeight: 600, marginBottom: 6, display: 'block' },
    select: {
      width: '100%', padding: '9px 12px', borderRadius: 8, fontSize: 13,
      backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
      color: '#fff', outline: 'none', cursor: 'pointer',
    },
    input: {
      width: '100%', padding: '9px 12px', borderRadius: 8, fontSize: 13,
      backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
      color: '#fff', outline: 'none',
    },
    agentRow: {
      padding: '12px 16px', borderRadius: 10, marginBottom: 8,
      backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
    },
    saveBtn: (dirty: boolean) => ({
      padding: '9px 20px', borderRadius: 9, fontSize: 14, fontWeight: 700, cursor: dirty ? 'pointer' : 'not-allowed',
      backgroundColor: dirty ? 'rgba(255,107,53,0.2)' : 'rgba(255,255,255,0.05)',
      border: `1px solid ${dirty ? 'rgba(255,107,53,0.5)' : 'rgba(255,255,255,0.1)'}`,
      color: dirty ? '#ff6b35' : 'rgba(255,255,255,0.3)',
      display: 'flex', alignItems: 'center', gap: 6,
    }),
  };

  return (
    <div style={S.page}>
      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 70, right: 20, zIndex: 9999,
          backgroundColor: toast.type === 'ok' ? 'rgba(16,185,129,0.95)' : 'rgba(239,68,68,0.95)',
          color: '#fff', padding: '10px 18px', borderRadius: 10, fontWeight: 600, fontSize: 14,
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        }}>
          {toast.msg}
        </div>
      )}

      <div style={S.header}>
        <h1 style={S.title}>
          <Settings size={24} style={{ color: '#ff6b35' }} />
          Configurações
          {dirty && <span style={{ fontSize: 12, color: '#f59e0b', fontWeight: 400 }}>• Alterações pendentes</span>}
        </h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={load} style={{ padding: '6px 12px', borderRadius: 8, fontSize: 13, cursor: 'pointer',
            backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.7)',
            display: 'flex', alignItems: 'center', gap: 5 }}>
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Recarregar
          </button>
          <button onClick={save} disabled={!dirty || saving} style={S.saveBtn(dirty)}>
            {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />}
            {saving ? 'Salvando...' : 'Salvar no OpenClaw'}
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 14, padding: 20, textAlign: 'center' }}>
          <RefreshCw size={20} className="animate-spin" style={{ display: 'inline' }} /> Carregando...
        </div>
      ) : (
        <>
          {/* Default model */}
          <div style={S.card}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <Cpu size={16} style={{ color: '#60a5fa' }} />
              <span style={{ color: '#fff', fontSize: 15, fontWeight: 700 }}>Modelo Padrão Global</span>
            </div>
            <label style={S.label}>Modelo primário (usado por todos os agentes sem modelo específico)</label>
            <select
              value={defaultModel}
              onChange={e => handleDefaultModelChange(e.target.value)}
              style={S.select}
            >
              {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
              {!MODELS.includes(defaultModel) && defaultModel && (
                <option value={defaultModel}>{defaultModel}</option>
              )}
            </select>
            <div style={{ marginTop: 8, fontSize: 12, color: 'rgba(255,255,255,0.35)' }}>
              Atual: <code style={{ color: '#60a5fa' }}>{defaultModel}</code>
            </div>
          </div>

          {/* Agents */}
          <div style={S.card}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <User size={16} style={{ color: '#a78bfa' }} />
              <span style={{ color: '#fff', fontSize: 15, fontWeight: 700 }}>Configuração por Agente</span>
            </div>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.45)', marginBottom: 16 }}>
              Defina nome e modelo personalizado para cada agente. Deixe o modelo em branco para usar o padrão global.
            </p>

            {agents.map(agent => (
              <div key={agent.id} style={S.agentRow}>
                <div
                  style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
                  onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
                >
                  <span style={{ fontSize: 20 }}>{AGENT_EMOJI[agent.id] || '🤖'}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#fff', fontSize: 14, fontWeight: 600 }}>{agent.name || agent.id}</div>
                    <div style={{ color: 'rgba(255,255,255,0.35)', fontSize: 11, fontFamily: 'monospace' }}>
                      {agent.id} · {agent.model || defaultModel}
                    </div>
                  </div>
                  {expandedAgent === agent.id ? <ChevronUp size={16} style={{ color: 'rgba(255,255,255,0.4)' }} /> : <ChevronDown size={16} style={{ color: 'rgba(255,255,255,0.4)' }} />}
                </div>

                {expandedAgent === agent.id && (
                  <div style={{ marginTop: 14, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <div>
                      <label style={S.label}>Nome do Agente</label>
                      <input
                        value={agent.name || ''}
                        onChange={e => updateAgentName(agent.id, e.target.value)}
                        style={S.input}
                        placeholder={agent.id}
                      />
                    </div>
                    <div>
                      <label style={S.label}>Modelo (deixe vazio para usar o padrão)</label>
                      <select
                        value={agent.model || ''}
                        onChange={e => updateAgentModel(agent.id, e.target.value)}
                        style={S.select}
                      >
                        <option value="">— Usar padrão global ({defaultModel}) —</option>
                        {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
                        {agent.model && !MODELS.includes(agent.model) && (
                          <option value={agent.model}>{agent.model}</option>
                        )}
                      </select>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Save footer */}
          {dirty && (
            <div style={{
              padding: '16px 20px', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              backgroundColor: 'rgba(255,107,53,0.08)', border: '1px solid rgba(255,107,53,0.3)',
            }}>
              <span style={{ color: '#ff6b35', fontSize: 14 }}>⚠️ Você tem alterações não salvas</span>
              <button onClick={save} disabled={saving} style={S.saveBtn(true)}>
                {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />}
                {saving ? 'Salvando...' : 'Salvar no OpenClaw'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
