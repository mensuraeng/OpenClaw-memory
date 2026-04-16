'use client';

import { useState, useCallback, useRef } from 'react';
import { Search, FileText, MessageSquare, Activity, Clock, RefreshCw, X, ChevronRight } from 'lucide-react';

interface SearchResult {
  id: string;
  type: 'activity' | 'session' | 'memory' | 'log';
  title: string;
  snippet: string;
  agentId?: string;
  timestamp?: string;
  score?: number;
  href?: string;
}

const TYPE_CONFIG = {
  activity: { icon: Activity, color: '#f59e0b', label: 'Atividade' },
  session: { icon: MessageSquare, color: '#3b82f6', label: 'Sessão' },
  memory: { icon: FileText, color: '#8b5cf6', label: 'Memória' },
  log: { icon: Clock, color: '#6b7280', label: 'Log' },
};

const AGENT_EMOJI: Record<string, string> = {
  main: '🏗️', mia: '🏛️', mensura: '📐', pcs: '🏢',
  rh: '👥', marketing: '📣', producao: '🏗️', finance: '💰',
  autopilot: '🤖', juridico: '⚖️', bi: '📊', suprimentos: '📦',
};

const SUGGESTIONS = [
  'relatório semanal', 'erro de execução', 'sessão ativa', 'memória agente',
  'cron job', 'log de erro', 'tarefa pendente', 'workflow',
];

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const [agentFilter, setAgentFilter] = useState<string>('all');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setResults([]); setSearched(false); return; }
    setLoading(true);
    setSearched(true);
    try {
      const params = new URLSearchParams({ q, type: filter !== 'all' ? filter : '', agent: agentFilter !== 'all' ? agentFilter : '' });
      const res = await fetch(`/api/search?${params}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch { setResults([]); }
    setLoading(false);
  }, [filter, agentFilter]);

  const handleInput = (val: string) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(val), 500);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (debounceRef.current) clearTimeout(debounceRef.current);
    doSearch(query);
  };

  const filteredResults = results.filter(r => {
    if (filter !== 'all' && r.type !== filter) return false;
    if (agentFilter !== 'all' && r.agentId !== agentFilter) return false;
    return true;
  });

  const typeFilter = ['all', 'activity', 'session', 'memory', 'log'];
  const agents = ['all', 'main', 'mia', 'mensura', 'pcs', 'rh', 'marketing', 'producao', 'finance', 'autopilot', 'juridico', 'bi', 'suprimentos'];

  const btnTab = (active: boolean) => ({
    padding: '5px 12px', borderRadius: 7, fontSize: 12, fontWeight: 600, cursor: 'pointer',
    backgroundColor: active ? 'rgba(255,107,53,0.15)' : 'rgba(255,255,255,0.04)',
    border: active ? '1px solid rgba(255,107,53,0.4)' : '1px solid rgba(255,255,255,0.08)',
    color: active ? '#ff6b35' : 'rgba(255,255,255,0.5)',
  });

  return (
    <div style={{ padding: '24px', maxWidth: 900 }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Search size={24} style={{ color: '#60a5fa' }} />
          Busca Global
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: 13, marginTop: 4 }}>
          Pesquise em atividades, sessões, memória e logs de todos os agentes
        </p>
      </div>

      {/* Search box */}
      <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'rgba(255,255,255,0.3)' }} />
          <input
            value={query}
            onChange={e => handleInput(e.target.value)}
            placeholder="Buscar atividades, sessões, memória..."
            autoFocus
            style={{
              width: '100%', padding: '14px 48px 14px 44px', borderRadius: 12, fontSize: 15,
              backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#fff', outline: 'none',
              boxSizing: 'border-box',
            }}
          />
          {query && (
            <button type="button" onClick={() => { setQuery(''); setResults([]); setSearched(false); }}
              style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.4)' }}>
              <X size={16} />
            </button>
          )}
        </div>
      </form>

      {/* Suggestions */}
      {!searched && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.35)', marginBottom: 8, fontWeight: 600 }}>SUGESTÕES</div>
          <div style={{ display: 'flex', gap: 7, flexWrap: 'wrap' }}>
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => { setQuery(s); doSearch(s); }}
                style={{ padding: '5px 12px', borderRadius: 20, fontSize: 12, cursor: 'pointer',
                  backgroundColor: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.6)' }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      {searched && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 4 }}>
            {typeFilter.map(t => (
              <button key={t} style={btnTab(filter === t)} onClick={() => setFilter(t)}>
                {t === 'all' ? 'Todos' : TYPE_CONFIG[t as keyof typeof TYPE_CONFIG]?.label || t}
              </button>
            ))}
          </div>
          <div style={{ marginLeft: 8, display: 'flex', gap: 4 }}>
            {agents.map(a => (
              <button key={a} style={btnTab(agentFilter === a)} onClick={() => setAgentFilter(a)}>
                {a === 'all' ? 'Todos os agentes' : `${AGENT_EMOJI[a] || '🤖'} ${a}`}
              </button>
            )).slice(0, 6)}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: 'center', padding: 40, color: 'rgba(255,255,255,0.4)' }}>
          <RefreshCw size={24} className="animate-spin" style={{ display: 'inline' }} />
          <p style={{ marginTop: 8, fontSize: 13 }}>Buscando...</p>
        </div>
      )}

      {/* No results */}
      {searched && !loading && filteredResults.length === 0 && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Search size={32} style={{ color: 'rgba(255,255,255,0.1)', display: 'block', margin: '0 auto 12px' }} />
          <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 14 }}>
            Nenhum resultado para "{query}"
          </p>
          <p style={{ color: 'rgba(255,255,255,0.25)', fontSize: 12, marginTop: 4 }}>
            Tente palavras-chave diferentes ou verifique os filtros
          </p>
        </div>
      )}

      {/* Results */}
      {!loading && filteredResults.length > 0 && (
        <div>
          <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12, marginBottom: 12 }}>
            {filteredResults.length} resultado{filteredResults.length !== 1 ? 's' : ''} para "{query}"
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filteredResults.map(r => {
              const cfg = TYPE_CONFIG[r.type] || TYPE_CONFIG.log;
              const Icon = cfg.icon;
              return (
                <a
                  key={r.id}
                  href={r.href || '#'}
                  style={{
                    display: 'flex', alignItems: 'flex-start', gap: 12, padding: '14px 16px',
                    borderRadius: 12, textDecoration: 'none',
                    backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
                    transition: 'all 150ms',
                  }}
                  onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'rgba(255,255,255,0.06)'; }}
                  onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'rgba(255,255,255,0.03)'; }}
                >
                  <div style={{ width: 36, height: 36, borderRadius: 9, backgroundColor: `${cfg.color}15`, border: `1px solid ${cfg.color}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={16} style={{ color: cfg.color }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                      <span style={{ color: '#fff', fontSize: 14, fontWeight: 600 }}>{r.title}</span>
                      <span style={{ padding: '1px 7px', borderRadius: 10, fontSize: 10, fontWeight: 600, backgroundColor: `${cfg.color}15`, color: cfg.color }}>
                        {cfg.label}
                      </span>
                      {r.agentId && (
                        <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>
                          {AGENT_EMOJI[r.agentId] || '🤖'} {r.agentId}
                        </span>
                      )}
                    </div>
                    <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 13, margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {r.snippet}
                    </p>
                    {r.timestamp && (
                      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.25)', marginTop: 3 }}>
                        {new Date(r.timestamp).toLocaleString('pt-BR')}
                      </div>
                    )}
                  </div>
                  <ChevronRight size={16} style={{ color: 'rgba(255,255,255,0.2)', flexShrink: 0, marginTop: 2 }} />
                </a>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
