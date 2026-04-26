import fs from 'fs';
import path from 'path';
import { randomUUID } from 'crypto';

const root = path.resolve(new URL('..', import.meta.url).pathname);
const pendingPath = process.env.PENDING_PATH || '/root/2nd-brain/02-context/pending.md';
const tasksDir = process.env.TASKS_DIR || path.join(root, 'runtime', 'tasks');
const executionsPath = path.join(tasksDir, 'task-executions.jsonl');
const eventsPath = path.join(tasksDir, 'task-events.jsonl');
const workingDir = path.join(tasksDir, 'working');
const dryRun = process.argv.includes('--dry-run');

const now = new Date().toISOString();
const OPEN_STATUSES = new Set(['queued', 'running', 'waiting_input', 'blocked', 'failed', 'completed_unvalidated']);
const WORKING_MEMORY_RISKS = new Set(['critical', 'high']);

function ensureStore() {
  fs.mkdirSync(tasksDir, { recursive: true });
  fs.mkdirSync(workingDir, { recursive: true });
  for (const file of [executionsPath, eventsPath]) {
    if (!fs.existsSync(file)) fs.writeFileSync(file, '', 'utf8');
  }
}

function readJsonl(file) {
  ensureStore();
  const raw = fs.readFileSync(file, 'utf8').trim();
  if (!raw) return [];
  return raw.split('\n').filter(Boolean).map((line) => JSON.parse(line));
}

function appendJsonl(file, row) {
  if (dryRun) return;
  fs.appendFileSync(file, `${JSON.stringify(row)}\n`, 'utf8');
}

function writeFileIfChanged(file, content) {
  if (dryRun) return false;
  if (fs.existsSync(file) && fs.readFileSync(file, 'utf8') === content) return false;
  fs.writeFileSync(file, content, 'utf8');
  return true;
}

function slugify(value) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/`[^`]+`/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 90);
}

function stripMarkdown(value) {
  return value
    .replace(/^[-*]\s*\[[ xX]\]\s*/, '')
    .replace(/\*\*/g, '')
    .replace(/`/g, '')
    .trim();
}

function splitTitleDetail(text) {
  const clean = stripMarkdown(text);
  const match = clean.match(/^(.+?)\s+[—-]\s+(.+)$/);
  if (!match) return { title: clean, detail: '' };
  return { title: match[1].trim(), detail: match[2].trim() };
}

function classifyAgent(text) {
  const lower = text.toLowerCase();
  if (/finance|boleto|pagamento|recebimento|fluxo|fiscal|romaneio|comprovante|confirp|irpf/.test(lower)) return 'finance';
  if (/mensura|p&g|louveira|linkedin|marketing|comercial/.test(lower)) return 'mensura';
  if (/mia|ccsp|casa 7/.test(lower)) return 'mia';
  if (/pcs|sienge|sptrans|spobras|cpa|suzano|paranapiacaba|licita|condephaat|iphan/.test(lower)) return 'pcs';
  return 'main';
}

function statusForSection(section) {
  if (/aguardando al[eê]/i.test(section) || /aguardando terceiros/i.test(section)) return 'waiting_input';
  if (/cr[ií]ticas/i.test(section)) return 'queued';
  return 'queued';
}

function riskForSection(section, text) {
  const lower = `${section} ${text}`.toLowerCase();
  if (/cr[ií]ticas|segredo|token|ssh|jur[ií]dico|contratual/.test(lower)) return 'critical';
  if (/com prazo|prazo|venc|aguardando al[eê]/.test(lower)) return 'high';
  if (/em andamento interno/.test(lower)) return 'medium';
  return 'low';
}

function tagsFor(section, text) {
  const tags = ['pending-import'];
  const lower = `${section} ${text}`.toLowerCase();
  if (/cr[ií]ticas/.test(lower)) tags.push('critical');
  if (/aguardando al[eê]/.test(lower)) tags.push('waiting-ale');
  if (/aguardando terceiros/.test(lower)) tags.push('waiting-third-party');
  if (/com prazo|prazo/.test(lower)) tags.push('deadline');
  if (/segredo|token|credencial|ssh/.test(lower)) tags.push('security');
  return tags;
}

function parsePending(markdown) {
  const rows = [];
  let section = 'Sem seção';
  for (const rawLine of markdown.split('\n')) {
    const line = rawLine.trim();
    const sectionMatch = line.match(/^##\s+(.+)$/);
    if (sectionMatch) {
      section = stripMarkdown(sectionMatch[1]);
      continue;
    }

    const bulletMatch = line.match(/^- \[[ xX]\]\s+(.+)$/);
    if (bulletMatch) {
      const { title, detail } = splitTitleDetail(bulletMatch[1]);
      if (title) rows.push({ section, title, detail, sourceLine: line });
      continue;
    }

    const tableMatch = line.match(/^\|\s*\*\*(.+?)\*\*\s*(?:—\s*(.*?))?\s*\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|$/);
    if (tableMatch && !/item/i.test(tableMatch[1])) {
      const title = stripMarkdown(tableMatch[1]);
      const detail = stripMarkdown(tableMatch[2] || `Prazo: ${tableMatch[3]} · Fonte: ${tableMatch[4]}`);
      rows.push({ section, title, detail, sourceLine: line, dueLabel: stripMarkdown(tableMatch[3]), source: stripMarkdown(tableMatch[4]) });
    }
  }
  return rows;
}

function workingMemoryPath(task) {
  return path.join(workingDir, `${task.taskId}.md`);
}

function shouldHaveWorkingMemory(task) {
  return WORKING_MEMORY_RISKS.has(task.riskLevel) && OPEN_STATUSES.has(task.status);
}

function buildWorkingMemory(task) {
  return `# Working Memory — ${task.title}\n\n` +
    `- Task ID: ${task.taskId}\n` +
    `- Status: ${task.status}\n` +
    `- Risco: ${task.riskLevel}\n` +
    `- Responsável sugerido: ${task.targetAgent}\n` +
    `- Origem: ${task.metadata?.source || 'manual'}${task.metadata?.sourceSection ? ` / ${task.metadata.sourceSection}` : ''}\n` +
    `- Criado em: ${task.createdAt}\n` +
    `- Atualizado em: ${task.updatedAt}\n\n` +
    `## Objetivo\n\n${task.objective || 'Sem objetivo informado.'}\n\n` +
    `## Critério de sucesso\n\n${task.successCriteria || 'Definir critério antes de executar.'}\n\n` +
    `## Próximo passo\n\n` +
    (task.status === 'waiting_input'
      ? `Aguardar input externo: ${task.blockingReason || 'sem detalhe registrado'}.\n`
      : `Definir primeira ação executável, registrar evento e atualizar status.\n`) +
    `\n## Notas\n\n- Arquivo criado automaticamente pelo importador do Task Board Lite.\n- Atualizar manualmente quando houver decisão, bloqueio, execução ou validação relevante.\n`;
}

function ensureWorkingMemory(task) {
  if (!shouldHaveWorkingMemory(task)) return { created: false, path: null };
  const filePath = workingMemoryPath(task);
  const created = !fs.existsSync(filePath);
  if (created) writeFileIfChanged(filePath, buildWorkingMemory(task));
  return { created, path: filePath };
}

function createTask(item) {
  const taskId = randomUUID();
  const text = `${item.title} ${item.detail} ${item.section}`;
  const targetAgent = classifyAgent(text);
  const status = statusForSection(item.section);
  const riskLevel = riskForSection(item.section, text);
  const task = {
    taskId,
    parentTaskId: null,
    rootTaskId: taskId,
    sessionKey: null,
    childSessionKey: null,
    sourceAgent: 'main',
    targetAgent,
    executionType: targetAgent === 'main' ? 'direct' : 'delegation',
    title: item.title,
    objective: item.detail || `Resolver pendência registrada em ${item.section}`,
    inputSummary: item.sourceLine,
    expectedOutput: 'Pendência atualizada, resolvida ou bloqueio explicitado no 2nd-brain e no Mission Control.',
    successCriteria: 'Status rastreável com próximo passo claro; se exigir decisão externa, marcar como waiting_input.',
    riskLevel,
    status,
    attempt: 1,
    maxAttempts: 2,
    createdAt: now,
    updatedAt: now,
    finishedAt: null,
    slaMinutes: null,
    dueAt: null,
    staleAfterMinutes: status === 'waiting_input' ? 1440 : 240,
    validationRequired: true,
    validatedAt: null,
    validatedBy: null,
    blockingReason: status === 'waiting_input' ? `Aguardando input externo: ${item.section}` : null,
    failureReason: null,
    handoffDepth: 0,
    tags: tagsFor(item.section, text),
    metadata: {
      source: '2nd-brain/02-context/pending.md',
      sourceSection: item.section,
      sourceSlug: slugify(`${item.section}-${item.title}`),
      sourceDueLabel: item.dueLabel || null,
      sourceReference: item.source || null,
      importedAt: now,
    },
  };
  if (shouldHaveWorkingMemory(task)) {
    task.metadata.workingMemoryPath = workingMemoryPath(task);
  }
  return task;
}

function summarizeTasks(tasks) {
  const byAgent = {};
  const byStatus = {};
  const byRisk = {};
  for (const task of tasks) {
    byAgent[task.targetAgent] = (byAgent[task.targetAgent] || 0) + 1;
    byStatus[task.status] = (byStatus[task.status] || 0) + 1;
    byRisk[task.riskLevel] = (byRisk[task.riskLevel] || 0) + 1;
  }
  return { byAgent, byStatus, byRisk };
}

function main() {
  ensureStore();
  const markdown = fs.readFileSync(pendingPath, 'utf8');
  const pendingItems = parsePending(markdown);
  const existing = readJsonl(executionsPath);
  const activeSlugs = new Set(
    existing
      .filter((task) => OPEN_STATUSES.has(task.status))
      .map((task) => task.metadata?.sourceSlug)
      .filter(Boolean)
  );

  const created = [];
  const skipped = [];
  let workingCreated = 0;

  for (const task of existing) {
    const result = ensureWorkingMemory(task);
    if (result.created) workingCreated += 1;
  }

  for (const item of pendingItems) {
    const sourceSlug = slugify(`${item.section}-${item.title}`);
    if (activeSlugs.has(sourceSlug)) {
      skipped.push(item.title);
      continue;
    }
    const task = createTask(item);
    const working = ensureWorkingMemory(task);
    if (working.created) workingCreated += 1;
    appendJsonl(executionsPath, task);
    appendJsonl(eventsPath, {
      eventId: randomUUID(),
      taskId: task.taskId,
      timestamp: now,
      agentId: 'main',
      type: 'created',
      message: `Importada do pending.md: ${task.title}`,
      payload: { sourceSection: item.section, targetAgent: task.targetAgent, sourceSlug, workingMemoryPath: working.path },
    });
    activeSlugs.add(sourceSlug);
    created.push(task);
  }

  const imported = existing.concat(created).filter((task) => task.metadata?.source === '2nd-brain/02-context/pending.md');
  console.log(JSON.stringify({
    ok: true,
    dryRun,
    pendingItems: pendingItems.length,
    created: created.length,
    skipped: skipped.length,
    workingMemoryCreated: workingCreated,
    tasksDir,
    ...summarizeTasks(imported),
  }, null, 2));
}

main();
