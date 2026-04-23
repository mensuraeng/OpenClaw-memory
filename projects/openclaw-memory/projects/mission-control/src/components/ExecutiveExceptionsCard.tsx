"use client";

interface ExecutiveMemorySummary {
  pendingCritical: string[];
  pendingWaitingAle: string[];
  recentDecisions: string[];
}

export function ExecutiveExceptionsCard({ executive }: { executive: ExecutiveMemorySummary }) {
  const renderList = (items: string[], empty: string, tone: "red" | "amber" | "blue") => {
    const styles = {
      red: { bg: "#ef444412", border: "#ef444430", text: "#ef4444" },
      amber: { bg: "#f59e0b12", border: "#f59e0b30", text: "#f59e0b" },
      blue: { bg: "#3b82f612", border: "#3b82f630", text: "#3b82f6" },
    }[tone];

    return (items.length > 0 ? items : [empty]).slice(0, 3).map((item) => (
      <div key={item} className="text-xs rounded-lg p-2.5" style={{ backgroundColor: styles.bg, border: `1px solid ${styles.border}`, color: "var(--text-primary)" }}>
        {item}
      </div>
    ));
  };

  return (
    <div className="rounded-xl overflow-hidden" style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}>
      <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--border)" }}>
        <h2 className="text-base font-semibold" style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary)" }}>
          Exceções executivas
        </h2>
      </div>
      <div className="p-4 space-y-4">
        <div>
          <div className="text-xs font-medium mb-2" style={{ color: "#ef4444" }}>Pendências críticas</div>
          <div className="space-y-2">
            {renderList(executive.pendingCritical, "Nenhuma pendência crítica destacada", "red")}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium mb-2" style={{ color: "#f59e0b" }}>Aguardando Alê</div>
          <div className="space-y-2">
            {renderList(executive.pendingWaitingAle, "Nada explícito aguardando input agora", "amber")}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium mb-2" style={{ color: "#3b82f6" }}>Decisões permanentes recentes</div>
          <div className="space-y-2">
            {renderList(executive.recentDecisions, "Nenhuma decisão carregada", "blue")}
          </div>
        </div>
      </div>
    </div>
  );
}
