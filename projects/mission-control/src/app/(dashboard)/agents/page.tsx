import { Suspense } from "react";
import AgentsPageClient from "./AgentsPageClient";

export default function AgentsPage() {
  return (
    <Suspense fallback={<div className="p-8" style={{ color: 'var(--text-secondary)' }}>Carregando agentes...</div>}>
      <AgentsPageClient />
    </Suspense>
  );
}
