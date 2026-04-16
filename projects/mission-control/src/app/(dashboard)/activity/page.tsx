import { Suspense } from "react";
import ActivityPageClient from "./ActivityPageClient";

export default function ActivityPage() {
  return (
    <Suspense fallback={<div className="p-8" style={{ color: 'var(--text-secondary)' }}>Carregando atividade...</div>}>
      <ActivityPageClient />
    </Suspense>
  );
}
