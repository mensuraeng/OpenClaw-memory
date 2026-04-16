'use client';

import { useState, useRef, useEffect } from 'react';
import { Terminal, Send, Trash2, Copy, Check, RefreshCw } from 'lucide-react';

interface HistoryEntry {
  id: number;
  command: string;
  stdout: string;
  stderr: string;
  exitCode: number;
  timestamp: Date;
  loading?: boolean;
}

const QUICK_COMMANDS = [
  { label: 'Status Agentes', cmd: 'openclaw agents status --json 2>&1 | head -100' },
  { label: 'PM2 Lista', cmd: 'pm2 list 2>&1' },
  { label: 'Uso de Disco', cmd: 'df -h / 2>&1' },
  { label: 'Memória', cmd: 'free -h 2>&1' },
  { label: 'Processos', cmd: 'ps aux --sort=-%cpu | head -15 2>&1' },
  { label: 'Logs OpenClaw', cmd: 'tail -30 /root/.openclaw/logs/openclaw.log 2>&1 || journalctl -u openclaw -n 30 2>&1' },
  { label: 'Espaço Workspace', cmd: 'du -sh /root/.openclaw/workspace* 2>&1' },
  { label: 'Versão Node', cmd: 'node -v && npm -v 2>&1' },
];

export default function TerminalPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [input, setInput] = useState('');
  const [cwd, setCwd] = useState('/root/.openclaw/workspace');
  const [running, setRunning] = useState(false);
  const [cmdHistory, setCmdHistory] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const [copied, setCopied] = useState<number | null>(null);
  const outputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  let nextId = useRef(1);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [history]);

  const runCommand = async (cmd: string) => {
    if (!cmd.trim() || running) return;
    const id = nextId.current++;
    const entry: HistoryEntry = {
      id, command: cmd, stdout: '', stderr: '', exitCode: 0,
      timestamp: new Date(), loading: true,
    };
    setHistory(prev => [...prev, entry]);
    setCmdHistory(prev => [cmd, ...prev.slice(0, 49)]);
    setHistIdx(-1);
    setInput('');
    setRunning(true);

    try {
      const res = await fetch('/api/terminal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, cwd }),
      });
      const data = await res.json();
      if (!res.ok) {
        setHistory(prev => prev.map(e => e.id === id
          ? { ...e, loading: false, stderr: data.error || 'Erro', exitCode: 1 }
          : e
        ));
      } else {
        setHistory(prev => prev.map(e => e.id === id
          ? { ...e, loading: false, stdout: data.stdout || '', stderr: data.stderr || '', exitCode: data.exitCode ?? 0 }
          : e
        ));
        // Extract cwd change from cd commands
        if (cmd.trim().startsWith('cd ')) {
          const newDir = cmd.trim().slice(3).trim();
          if (newDir && !newDir.includes('..')) setCwd(newDir);
        }
      }
    } catch (e) {
      setHistory(prev => prev.map(en => en.id === id
        ? { ...en, loading: false, stderr: String(e), exitCode: 1 }
        : en
      ));
    }
    setRunning(false);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') { runCommand(input); return; }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const idx = Math.min(histIdx + 1, cmdHistory.length - 1);
      setHistIdx(idx);
      setInput(cmdHistory[idx] || '');
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const idx = Math.max(histIdx - 1, -1);
      setHistIdx(idx);
      setInput(idx === -1 ? '' : cmdHistory[idx] || '');
    }
    if (e.key === 'l' && e.ctrlKey) { e.preventDefault(); setHistory([]); }
  };

  const copyOutput = (entry: HistoryEntry) => {
    navigator.clipboard.writeText(`$ ${entry.command}\n${entry.stdout}${entry.stderr}`);
    setCopied(entry.id);
    setTimeout(() => setCopied(null), 1500);
  };

  const S = {
    page: { padding: '24px', height: '100%', display: 'flex', flexDirection: 'column' as const, gap: 16 },
    header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' as const, gap: 12 },
    title: { color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 },
    terminal: {
      flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column' as const,
      fontFamily: 'monospace', minHeight: 400,
    },
    termHeader: {
      padding: '10px 16px', backgroundColor: 'rgba(255,255,255,0.04)',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    },
    output: { flex: 1, overflowY: 'auto' as const, padding: '12px 16px' },
    cmdBlock: (exitCode: number) => ({
      marginBottom: 12, borderLeft: `3px solid ${exitCode === 0 ? '#22c55e' : '#ef4444'}`,
      paddingLeft: 12,
    }),
    cmdLine: { color: '#60a5fa', fontSize: 13, marginBottom: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' },
    stdout: { color: '#e2e8f0', fontSize: 13, whiteSpace: 'pre-wrap' as const, wordBreak: 'break-word' as const },
    stderr: { color: '#fca5a5', fontSize: 13, whiteSpace: 'pre-wrap' as const, wordBreak: 'break-word' as const },
    inputRow: {
      padding: '10px 16px', borderTop: '1px solid rgba(255,255,255,0.08)',
      display: 'flex', alignItems: 'center', gap: 8,
    },
    prompt: { color: '#22c55e', fontSize: 13, fontWeight: 700, flexShrink: 0 },
    input: {
      flex: 1, backgroundColor: 'transparent', border: 'none', outline: 'none',
      color: '#e2e8f0', fontSize: 13, fontFamily: 'monospace',
    },
    quickBtn: {
      padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600, cursor: 'pointer',
      backgroundColor: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
      color: 'rgba(255,255,255,0.6)', whiteSpace: 'nowrap' as const,
    },
  };

  return (
    <div style={S.page}>
      <div style={S.header}>
        <h1 style={S.title}>
          <Terminal size={24} style={{ color: '#22c55e' }} />
          Terminal
        </h1>
        <button
          onClick={() => setHistory([])}
          style={{ padding: '6px 14px', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer',
            backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444',
            display: 'flex', alignItems: 'center', gap: 5 }}
        >
          <Trash2 size={13} /> Limpar
        </button>
      </div>

      {/* Quick commands */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {QUICK_COMMANDS.map(q => (
          <button key={q.label} style={S.quickBtn} onClick={() => runCommand(q.cmd)} disabled={running}>
            {q.label}
          </button>
        ))}
      </div>

      {/* CWD indicator */}
      <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', fontFamily: 'monospace' }}>
        📂 {cwd}
      </div>

      {/* Terminal */}
      <div style={S.terminal} onClick={() => inputRef.current?.focus()}>
        <div style={S.termHeader}>
          <div style={{ display: 'flex', gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#ef4444' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#f59e0b' }} />
            <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#22c55e' }} />
          </div>
          <span style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>OpenClaw Terminal · Ctrl+L para limpar</span>
          <span />
        </div>

        <div style={S.output} ref={outputRef}>
          {history.length === 0 && (
            <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 13, paddingTop: 8 }}>
              Terminal pronto. Digite um comando ou use os atalhos acima. ↑↓ para histórico.
            </div>
          )}
          {history.map(entry => (
            <div key={entry.id} style={S.cmdBlock(entry.exitCode)}>
              <div style={S.cmdLine}>
                <span>$ {entry.command}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.25)' }}>
                    {entry.timestamp.toLocaleTimeString('pt-BR')}
                  </span>
                  {!entry.loading && (
                    <button onClick={() => copyOutput(entry)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.4)', padding: 2 }}>
                      {copied === entry.id ? <Check size={11} style={{ color: '#22c55e' }} /> : <Copy size={11} />}
                    </button>
                  )}
                  {entry.exitCode !== 0 && !entry.loading && (
                    <span style={{ color: '#ef4444', fontSize: 10 }}>✗ {entry.exitCode}</span>
                  )}
                </div>
              </div>
              {entry.loading && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'rgba(255,255,255,0.4)', fontSize: 12 }}>
                  <RefreshCw size={11} className="animate-spin" /> executando...
                </div>
              )}
              {entry.stdout && <div style={S.stdout}>{entry.stdout}</div>}
              {entry.stderr && <div style={S.stderr}>{entry.stderr}</div>}
            </div>
          ))}
          {running && <div style={{ color: '#60a5fa', fontSize: 12 }}>● processando...</div>}
        </div>

        <div style={S.inputRow}>
          <span style={S.prompt}>$</span>
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite um comando..."
            style={S.input}
            disabled={running}
            autoFocus
          />
          <button
            onClick={() => runCommand(input)}
            disabled={!input.trim() || running}
            style={{
              padding: '4px 10px', borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer',
              backgroundColor: running ? 'rgba(255,255,255,0.05)' : 'rgba(34,197,94,0.2)',
              border: `1px solid ${running ? 'rgba(255,255,255,0.1)' : 'rgba(34,197,94,0.4)'}`,
              color: running ? 'rgba(255,255,255,0.3)' : '#22c55e',
              display: 'flex', alignItems: 'center', gap: 4,
            }}
          >
            {running ? <RefreshCw size={12} className="animate-spin" /> : <Send size={12} />}
          </button>
        </div>
      </div>
    </div>
  );
}
