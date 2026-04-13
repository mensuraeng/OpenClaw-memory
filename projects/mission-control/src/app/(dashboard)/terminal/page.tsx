import { ShieldOff, Terminal } from 'lucide-react';

export default function TerminalPage() {
  return (
    <div className="p-4 md:p-8">
      <div
        style={{
          backgroundColor: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: '1rem',
          padding: '2rem',
          maxWidth: '840px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <div
            style={{
              width: '3rem',
              height: '3rem',
              borderRadius: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(239,68,68,0.12)',
              color: 'var(--error)',
            }}
          >
            <ShieldOff className="w-6 h-6" />
          </div>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Terminal desativado
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              O terminal web foi removido do escopo da v1 por risco excessivo.
            </p>
          </div>
        </div>

        <div style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          <p>Motivo: mesmo com allowlist, essa superfície continua sensível demais para a primeira versão.</p>
          <p>Direção da v1: observabilidade, leitura controlada e ações leves explicitamente permitidas.</p>
        </div>

        <div
          style={{
            marginTop: '1.25rem',
            padding: '1rem',
            borderRadius: '0.75rem',
            background: 'var(--card-elevated)',
            border: '1px solid var(--border)',
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'flex-start',
          }}
        >
          <Terminal className="w-5 h-5" style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <strong style={{ color: 'var(--text-primary)' }}>Alternativa</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Quando necessário, a operação sensível continua fora da interface web, via OpenClaw e trilha operacional controlada.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
        )}
      </div>

      {/* Input */}
      <div style={{
        display: "flex", alignItems: "center", gap: "0.75rem",
        margin: "0 1.5rem 1.5rem",
        padding: "0.625rem 1rem",
        backgroundColor: "#0d1117",
        borderRadius: "0.75rem",
        border: "1px solid #30363d",
        flexShrink: 0,
      }}>
        <span style={{ color: "#4ade80", fontFamily: "monospace", fontSize: "0.875rem", flexShrink: 0 }}>$</span>
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          placeholder="Enter command..."
          autoComplete="off"
          spellCheck={false}
          style={{
            flex: 1,
            background: "transparent",
            border: "none",
            outline: "none",
            color: "#c9d1d9",
            fontFamily: "monospace",
            fontSize: "0.875rem",
          }}
        />
        <button
          onClick={() => runCommand(input)}
          disabled={loading || !input.trim()}
          style={{
            padding: "0.375rem 0.75rem",
            borderRadius: "0.5rem",
            backgroundColor: input.trim() && !loading ? "rgba(74,222,128,0.15)" : "transparent",
            color: input.trim() && !loading ? "#4ade80" : "#484f58",
            border: "none", cursor: input.trim() && !loading ? "pointer" : "not-allowed",
            display: "flex", alignItems: "center", gap: "0.375rem",
            fontSize: "0.8rem",
          }}
        >
          <Send className="w-3.5 h-3.5" />
          Run
        </button>
      </div>
    </div>
  );
}
