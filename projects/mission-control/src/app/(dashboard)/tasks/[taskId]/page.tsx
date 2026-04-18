import Link from 'next/link';
import { listTaskEvents, getTaskExecution, getTaskTree } from '@/lib/task-tracking';

export default async function TaskDetailPage({ params }: { params: Promise<{ taskId: string }> }) {
  const { taskId } = await params;
  const task = getTaskExecution(taskId);

  if (!task) {
    return (
      <div className="space-y-4">
        <Link href="/tasks" className="text-sm" style={{ color: 'var(--accent)' }}>← Voltar</Link>
        <div className="rounded-2xl border p-6" style={{ borderColor: 'var(--border-subtle)', background: 'var(--surface-elevated)' }}>
          <h1 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>Tarefa não encontrada</h1>
        </div>
      </div>
    );
  }

  const events = listTaskEvents(taskId);
  const tree = getTaskTree(taskId);

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Link href="/tasks" className="text-sm" style={{ color: 'var(--accent)' }}>← Voltar para tasks</Link>
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{task.title}</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{task.objective}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="rounded-2xl border p-4 lg:col-span-2" style={{ borderColor: 'var(--border-subtle)', background: 'var(--surface-elevated)' }}>
          <h2 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Resumo</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div><strong>Task ID:</strong> {task.taskId}</div>
            <div><strong>Status:</strong> {task.status}</div>
            <div><strong>Origem:</strong> {task.sourceAgent}</div>
            <div><strong>Destino:</strong> {task.targetAgent}</div>
            <div><strong>Tipo:</strong> {task.executionType}</div>
            <div><strong>Risco:</strong> {task.riskLevel}</div>
            <div><strong>Tentativa:</strong> {task.attempt}/{task.maxAttempts}</div>
            <div><strong>Validação obrigatória:</strong> {task.validationRequired ? 'sim' : 'não'}</div>
            <div><strong>Criada em:</strong> {new Date(task.createdAt).toLocaleString('pt-BR')}</div>
            <div><strong>Atualizada em:</strong> {new Date(task.updatedAt).toLocaleString('pt-BR')}</div>
            {task.blockingReason && <div className="md:col-span-2"><strong>Bloqueio:</strong> {task.blockingReason}</div>}
            {task.failureReason && <div className="md:col-span-2"><strong>Falha:</strong> {task.failureReason}</div>}
          </div>
        </div>

        <div className="rounded-2xl border p-4" style={{ borderColor: 'var(--border-subtle)', background: 'var(--surface-elevated)' }}>
          <h2 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Árvore de handoff</h2>
          <div className="space-y-2 text-sm">
            {tree.map((node) => (
              <div key={node.taskId} className="rounded-xl border p-3" style={{ borderColor: 'var(--border-subtle)' }}>
                <div><strong>{node.title}</strong></div>
                <div style={{ color: 'var(--text-secondary)' }}>{node.sourceAgent} → {node.targetAgent}</div>
                <div style={{ color: 'var(--text-secondary)' }}>{node.status}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border p-4" style={{ borderColor: 'var(--border-subtle)', background: 'var(--surface-elevated)' }}>
        <h2 className="font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>Timeline</h2>
        <div className="space-y-3">
          {events.length === 0 ? (
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Sem eventos registrados.</div>
          ) : (
            events.map((event) => (
              <div key={event.eventId} className="border-l-2 pl-3" style={{ borderColor: 'var(--accent)' }}>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{event.message}</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {event.type} · {event.agentId} · {new Date(event.timestamp).toLocaleString('pt-BR')}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
