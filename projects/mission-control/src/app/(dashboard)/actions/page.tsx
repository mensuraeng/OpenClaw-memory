import { Shield, ShieldAlert } from 'lucide-react';

const SAFE_ACTIONS = [
  {
    id: 'refresh',
    label: 'Refresh',
    description: 'Atualiza widgets e consultas de leitura já permitidas',
  },
  {
    id: 'ack-alert',
    label: 'Acknowledge alert',
    description: 'Marca um alerta visual como visto na interface',
  },
  {
    id: 'copy-command',
    label: 'Copy command',
    description: 'Copia um comando recomendado para execução fora da UI',
  },
  {
    id: 'open-link',
    label: 'Open link',
    description: 'Abre um recurso permitido e previamente cadastrado',
  },
  {
    id: 'rerun-safe-check',
    label: 'Rerun safe check',
    description: 'Reexecuta uma checagem leve e controlada',
  },
];

export default function ActionsPage() {
  return (
    <div className="p-4 md:p-8">
      <div style={{ marginBottom: '1.5rem' }}>
        <h1
          className="text-3xl font-bold mb-2"
          style={{ fontFamily: 'var(--font-heading)', color: 'var(--text-primary)' }}
        >
          Ações leves allowlistadas
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          A v1 não expõe manutenção genérica, restart, shell ou limpeza arbitrária.
        </p>
      </div>

      <div
        style={{
          backgroundColor: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: '1rem',
          padding: '1.5rem',
          marginBottom: '1.25rem',
        }}
      >
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
          <ShieldAlert className="w-5 h-5" style={{ color: 'var(--warning, #f59e0b)', flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <strong style={{ color: 'var(--text-primary)' }}>Postura da v1</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.35rem', lineHeight: 1.7 }}>
              A interface só deve concentrar ações operacionais leves, específicas e auditáveis. Tudo que implique mutação ampla,
              execução de comando, restart de serviço ou impacto genérico no host fica fora.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {SAFE_ACTIONS.map((action) => (
          <div
            key={action.id}
            style={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '0.875rem',
              padding: '1rem',
            }}
          >
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
              <div
                style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  borderRadius: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(34,197,94,0.1)',
                  color: 'var(--success)',
                  flexShrink: 0,
                }}
              >
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <h3 style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{action.label}</h3>
                <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.6 }}>{action.description}</p>
                <div
                  style={{
                    marginTop: '0.75rem',
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                    fontFamily: 'monospace',
                  }}
                >
                  id: {action.id}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

                    {action.dangerous && <span style={{ fontSize: "0.7rem", opacity: 0.7 }}>⚠️</span>}
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Recent Results */}
      {Object.keys(results).length > 0 && (
        <div className="rounded-xl" style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>
          <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
            <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              Recent Results
            </h2>
          </div>
          <div className="divide-y" style={{ borderColor: "var(--border)" }}>
            {Object.values(results)
              .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
              .map((result) => {
                const action = ACTIONS.find((a) => a.id === result.action);
                const Icon = (action?.icon || Terminal) as React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
                return (
                  <div
                    key={result.action}
                    className="flex items-center gap-3 p-3 cursor-pointer transition-colors"
                    style={{ borderBottom: "1px solid var(--border)" }}
                    onClick={() => setSelectedResult(result)}
                    onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "var(--card-elevated)"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "transparent"; }}
                  >
                    <div style={{
                      width: "1.75rem", height: "1.75rem", borderRadius: "0.375rem",
                      backgroundColor: `color-mix(in srgb, ${action?.color || "#888"} 15%, transparent)`,
                      display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                    }}>
                      <Icon className="w-3.5 h-3.5" style={{ color: action?.color || "#888" }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                          {action?.label || result.action}
                        </span>
                        <span
                          className="px-1.5 py-0.5 rounded text-xs"
                          style={{
                            backgroundColor: result.status === "success" ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.1)",
                            color: result.status === "success" ? "var(--success)" : "var(--error)",
                          }}
                        >
                          {result.status}
                        </span>
                      </div>
                      <div className="text-xs" style={{ color: "var(--text-muted)" }}>
                        {result.duration_ms}ms · {format(new Date(result.timestamp), "HH:mm:ss")}
                      </div>
                    </div>
                    <Terminal className="w-3.5 h-3.5 flex-shrink-0" style={{ color: "var(--text-muted)" }} />
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Confirm Dialog */}
      {confirmAction && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 1000,
          backgroundColor: "rgba(0,0,0,0.75)",
          display: "flex", alignItems: "center", justifyContent: "center",
          padding: "1rem",
        }}>
          <div style={{
            backgroundColor: "var(--card)",
            borderRadius: "1rem", padding: "2rem",
            maxWidth: "400px", width: "100%",
            border: "1px solid var(--border)",
          }}>
            <h3 style={{ color: "var(--text-primary)", marginBottom: "0.75rem", fontWeight: 600 }}>
              ⚠️ Confirm: {confirmAction.label}
            </h3>
            <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
              This action may affect running services. Are you sure?
            </p>
            <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end" }}>
              <button
                onClick={() => setConfirmAction(null)}
                style={{ padding: "0.5rem 1rem", borderRadius: "0.5rem", background: "var(--card-elevated)", color: "var(--text-secondary)", border: "none", cursor: "pointer" }}
              >
                Cancel
              </button>
              <button
                onClick={() => executeAction(confirmAction)}
                style={{ padding: "0.5rem 1rem", borderRadius: "0.5rem", background: "var(--error, #ef4444)", color: "#fff", border: "none", cursor: "pointer", fontWeight: 600 }}
              >
                Run Anyway
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Output Modal */}
      {selectedResult && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 1000,
          backgroundColor: "rgba(0,0,0,0.85)",
          display: "flex", alignItems: "center", justifyContent: "center",
          padding: "1rem",
        }}>
          <div style={{
            width: "95vw", maxWidth: "800px", height: "75vh",
            backgroundColor: "#0d1117",
            borderRadius: "1rem", border: "1px solid var(--border)",
            display: "flex", flexDirection: "column",
            overflow: "hidden",
          }}>
            <div style={{
              display: "flex", alignItems: "center", gap: "0.75rem",
              padding: "0.875rem 1rem",
              borderBottom: "1px solid #30363d",
              flexShrink: 0,
            }}>
              <Terminal className="w-4 h-4" style={{ color: selectedResult.status === "success" ? "var(--success)" : "var(--error)" }} />
              <span style={{ color: "#c9d1d9", fontFamily: "monospace", fontSize: "0.9rem", flex: 1 }}>
                {ACTIONS.find((a) => a.id === selectedResult.action)?.label || selectedResult.action}
              </span>
              <span style={{ fontSize: "0.75rem", color: "#8b949e" }}>
                {selectedResult.duration_ms}ms · {format(new Date(selectedResult.timestamp), "HH:mm:ss")}
              </span>
              <button
                onClick={() => setSelectedResult(null)}
                style={{ padding: "0.375rem", borderRadius: "0.375rem", background: "none", border: "none", cursor: "pointer", color: "#8b949e" }}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div style={{ flex: 1, overflow: "auto", padding: "1rem" }}>
              <pre style={{
                fontFamily: "monospace", fontSize: "0.8rem",
                color: "#c9d1d9", whiteSpace: "pre-wrap", wordBreak: "break-all",
                lineHeight: 1.6,
              }}>
                {selectedResult.output}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
