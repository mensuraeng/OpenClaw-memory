import fs from "fs";
import path from "path";
import { listTaskExecutions, type TaskExecution } from "@/lib/task-tracking";

const SECOND_BRAIN_ROOT = process.env.SECOND_BRAIN_ROOT || "/root/2nd-brain";
const WORKSPACE_ROOT = process.env.OPENCLAW_WORKSPACE || "/root/.openclaw/workspace";
const RUNTIME_ROOT = path.join(WORKSPACE_ROOT, "runtime");

export type ExecutiveTone = "ok" | "attention" | "risk";

export interface ExecutiveProject {
  id: string;
  name: string;
  domain: string;
  sourcePath: string;
  status: string;
  priority: "critical" | "high" | "medium" | "low";
  risk: ExecutiveTone;
  ownerAgent: string;
  summary: string;
  nextStep: string;
  lastMovement: string | null;
  metrics: {
    openTasks: number;
    blockedTasks: number;
    documents: number;
    evidences: number;
    decisions: number;
  };
  tasks: Array<Pick<TaskExecution, "taskId" | "title" | "status" | "targetAgent" | "riskLevel" | "updatedAt">>;
  documents: ExecutiveDocument[];
  evidences: ExecutiveEvidence[];
  decisions: ExecutiveDecision[];
}

export interface ExecutiveDocument {
  id: string;
  title: string;
  path: string;
  source: "2nd-brain" | "workspace";
  category: string;
  company: string;
  projectId?: string;
  status: string;
  sensitivity: string;
  modified: string | null;
  size: number;
}

export interface ExecutiveEvidence {
  id: string;
  title: string;
  path: string;
  kind: string;
  modified: string | null;
  size: number;
}

export interface ExecutiveDecision {
  title: string;
  path: string;
  line: number;
}

export interface ExecutiveGraph {
  generatedAt: string;
  roots: { secondBrain: string; workspace: string; runtime: string };
  metrics: {
    projects: number;
    documents: number;
    openTasksLinked: number;
    evidences: number;
    decisionsLinked: number;
    risks: number;
  };
  projects: ExecutiveProject[];
  documents: ExecutiveDocument[];
  guardrails: string[];
}

const AGENT_BY_DOMAIN: Record<string, string> = {
  mensura: "mensura",
  mia: "mia",
  pcs: "pcs",
  finance: "finance",
  financeiro: "finance",
  marketing: "mensura",
  fiscal: "finance",
};

const COMPANY_BY_DOMAIN: Record<string, string> = {
  mensura: "MENSURA",
  mia: "MIA",
  pcs: "PCS",
  marketing: "MENSURA",
  fiscal: "Transversal",
  finance: "Transversal",
  financeiro: "Transversal",
};

const CATEGORY_RULES: Array<[RegExp, string]> = [
  [/prd|product|requis/i, "PRD"],
  [/adr|decis/i, "Decisão/ADR"],
  [/runbook|playbook|operacional|standard|protocolo/i, "Runbook"],
  [/apresenta|deck|proposta|one-pager|comercial/i, "Comercial"],
  [/relat[oó]rio|report|audit|evid[eê]ncia|evidence|summary|health/i, "Evidência/Relatório"],
  [/ficha|cadastral|cnpj|institucional|documentos/i, "Institucional"],
  [/fiscal|nota|nfe|nfse|dfe/i, "Fiscal"],
  [/cron|schedule|task|working/i, "Operação"],
];

function exists(p: string) {
  try { return fs.existsSync(p); } catch { return false; }
}

function statSafe(p: string) {
  try { return fs.statSync(p); } catch { return null; }
}

function readSafe(p: string, max = 90_000) {
  try { return fs.readFileSync(p, "utf-8").slice(0, max); } catch { return ""; }
}

function walkFiles(root: string, options: { maxFiles?: number; maxDepth?: number; exts?: RegExp } = {}) {
  const maxFiles = options.maxFiles ?? 800;
  const maxDepth = options.maxDepth ?? 5;
  const exts = options.exts ?? /\.(md|mdx|yaml|yml|json|pdf|csv|xlsx|txt)$/i;
  const files: string[] = [];
  function walk(current: string, depth: number) {
    if (files.length >= maxFiles || depth > maxDepth) return;
    let entries: fs.Dirent[] = [];
    try { entries = fs.readdirSync(current, { withFileTypes: true }); } catch { return; }
    for (const entry of entries) {
      if (entry.name.startsWith(".git") || entry.name === "node_modules" || entry.name === ".next") continue;
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) walk(full, depth + 1);
      else if (exts.test(entry.name)) files.push(full);
      if (files.length >= maxFiles) return;
    }
  }
  if (exists(root)) walk(root, 0);
  return files;
}

function slug(input: string) {
  return input
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "projeto";
}

function titleCaseFromSlug(value: string) {
  return value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.length <= 3 ? part.toUpperCase() : part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function firstHeading(content: string) {
  const heading = content.split("\n").find((line) => /^#\s+/.test(line.trim()));
  return heading?.replace(/^#\s+/, "").trim() || "";
}

function firstMeaningfulParagraph(content: string) {
  return content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#") && !line.startsWith("_") && !line.startsWith("|") && !line.startsWith("- ["))
    .slice(0, 2)
    .join(" ")
    .slice(0, 260);
}

function extractNextStep(content: string) {
  const lines = content.split("\n").map((line) => line.trim());
  const headingIndex = lines.findIndex((line) => /pr[oó]ximo passo|next step|pend[eê]ncia|backlog|a fazer/i.test(line));
  const candidates = headingIndex >= 0 ? lines.slice(headingIndex + 1) : lines;
  const item = candidates.find((line) => /^- \[ \]|^- /.test(line) && !/conclu[ií]d|feito|ok/i.test(line));
  return item?.replace(/^- \[ \]\s*/, "").replace(/^-\s*/, "").slice(0, 220) || "Revisar projeto e definir próximo avanço interno seguro.";
}

function inferPriority(text: string): ExecutiveProject["priority"] {
  if (/cr[ií]tic|jur[ií]dic|financeir|fiscal|bloque|risco alto|urgent|sienge|nota fiscal/i.test(text)) return "critical";
  if (/prioridade|alto|high|mission control|crm|mensura|capacidade real/i.test(text)) return "high";
  if (/baixo|low|futuro|posterior/i.test(text)) return "low";
  return "medium";
}

function inferRisk(text: string): ExecutiveTone {
  if (/bloque|falh|risco|jur[ií]dic|fiscal|financeir|segredo|credencial|rate limit|429/i.test(text)) return "risk";
  if (/pendente|aguard|validar|aten[cç][aã]o|parcial/i.test(text)) return "attention";
  return "ok";
}

function inferStatus(text: string) {
  if (/bloque|blocked|rate limit|aguardando|pendente/i.test(text)) return "bloqueado/pendente";
  if (/em implanta|in progress|andamento|pr[oó]ximo salto/i.test(text)) return "em andamento";
  if (/conclu[ií]d|validado|100%|feito/i.test(text)) return "validado";
  return "ativo";
}

function inferDomain(filePath: string, content = "") {
  const rel = filePath.toLowerCase();
  const text = `${rel}\n${content.slice(0, 5000)}`.toLowerCase();
  if (/mensura/.test(text)) return "mensura";
  if (/mia/.test(text)) return "mia";
  if (/pcs|sienge|teatro|sptrans|spobras/.test(text)) return "pcs";
  if (/finance|financeiro|boleto|pagamento/.test(text)) return "financeiro";
  if (/fiscal|nota|nfs|nfe|dfe/.test(text)) return "fiscal";
  if (/marketing|linkedin|crm|lead|hubspot/.test(text)) return "marketing";
  if (/mission-control|openclaw|mem[oó]ria|agent|cron/.test(text)) return "openclaw";
  return "transversal";
}

function inferCategory(filePath: string, content = "") {
  const hay = `${filePath}\n${content.slice(0, 4000)}`;
  return CATEGORY_RULES.find(([pattern]) => pattern.test(hay))?.[1] || "Documento";
}

function documentStatus(content: string) {
  if (/status:\s*aprovado|\[ATIVA\]|validado/i.test(content)) return "validado";
  if (/status:\s*rascunho|rascunho|draft/i.test(content)) return "rascunho";
  if (/pendente|parcial|aguardando|status:\s*revis/i.test(content)) return "revisão/pendente";
  return "ativo";
}

function sensitivity(content: string, filePath: string) {
  const text = `${filePath}\n${content.slice(0, 4000)}`;
  if (/segredo|credencial|token|senha|certificado|banc[aá]rio|jur[ií]dic|contrat/i.test(text)) return "sensível";
  if (/interno|operacional|runtime|evid[eê]ncia/i.test(text)) return "interno";
  return "normal";
}

function safeRelative(root: string, full: string) {
  return path.relative(root, full).replaceAll(path.sep, "/");
}

function makeDocument(fullPath: string, root: string, source: ExecutiveDocument["source"], projectId?: string): ExecutiveDocument | null {
  const st = statSafe(fullPath);
  if (!st?.isFile()) return null;
  const content = /\.(md|mdx|yaml|yml|json|txt)$/i.test(fullPath) ? readSafe(fullPath, 60_000) : "";
  const rel = safeRelative(root, fullPath);
  const title = firstHeading(content) || titleCaseFromSlug(path.basename(fullPath).replace(/\.[^.]+$/, ""));
  const domain = inferDomain(rel, content);
  return {
    id: slug(`${source}-${rel}`),
    title,
    path: `${source}:${rel}`,
    source,
    category: inferCategory(rel, content),
    company: COMPANY_BY_DOMAIN[domain] || titleCaseFromSlug(domain),
    projectId,
    status: documentStatus(content),
    sensitivity: sensitivity(content, rel),
    modified: st.mtime.toISOString(),
    size: st.size,
  };
}

function loadDocuments(): ExecutiveDocument[] {
  const roots: Array<{ root: string; source: ExecutiveDocument["source"]; maxDepth: number }> = [
    { root: path.join(SECOND_BRAIN_ROOT, "04-projects"), source: "2nd-brain", maxDepth: 6 },
    { root: path.join(SECOND_BRAIN_ROOT, "02-context"), source: "2nd-brain", maxDepth: 2 },
    { root: path.join(WORKSPACE_ROOT, "docs"), source: "workspace", maxDepth: 5 },
    { root: path.join(WORKSPACE_ROOT, "projects"), source: "workspace", maxDepth: 4 },
  ];
  const docs: ExecutiveDocument[] = [];
  for (const item of roots) {
    for (const file of walkFiles(item.root, { maxFiles: 500, maxDepth: item.maxDepth })) {
      if (/node_modules|\.next|package-lock\.json|tsconfig\.json$/i.test(file)) continue;
      const rel = safeRelative(item.root, file);
      if (item.root.endsWith("projects") && !/\/docs\/|\/documentos\/|README\.md$|MAP\.md$/i.test(rel)) continue;
      const projectId = inferProjectIdFromPath(file);
      const doc = makeDocument(file, item.root, item.source, projectId);
      if (doc) docs.push(doc);
    }
  }
  const seen = new Set<string>();
  return docs
    .filter((doc) => {
      if (seen.has(doc.path)) return false;
      seen.add(doc.path);
      return true;
    })
    .sort((a, b) => (b.modified || "").localeCompare(a.modified || ""))
    .slice(0, 240);
}

function inferProjectIdFromPath(fullPath: string) {
  const normalized = fullPath.replaceAll(path.sep, "/");
  const secondBrainMatch = normalized.match(/04-projects\/([^/]+)/);
  if (secondBrainMatch) return slug(secondBrainMatch[1].replace(/\.md$/, ""));
  const workspaceMatch = normalized.match(/projects\/([^/]+)/);
  if (workspaceMatch) return slug(workspaceMatch[1]);
  const docsMatch = normalized.match(/docs\/([^/]+)/);
  if (docsMatch) return slug(docsMatch[1]);
  return undefined;
}

function loadDecisions() {
  const decisionsPath = path.join(SECOND_BRAIN_ROOT, "02-context", "decisions.md");
  const content = readSafe(decisionsPath, 180_000);
  return content.split("\n").flatMap((line, index) => {
    if (!line.startsWith("### ")) return [];
    return [{ title: line.replace(/^###\s+/, "").trim(), path: "2nd-brain:02-context/decisions.md", line: index + 1 }];
  });
}

function relevantTextForProject(project: { id: string; name: string; domain: string }) {
  return [project.id, project.name, project.domain, project.name.replace(/\s+/g, "-")]
    .map((value) => value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""));
}

function matchesProject(text: string, project: { id: string; name: string; domain: string }) {
  const normalized = text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  return relevantTextForProject(project).some((term) => term.length > 2 && normalized.includes(term));
}

function loadEvidences(project: { id: string; name: string; domain: string }): ExecutiveEvidence[] {
  const files = walkFiles(RUNTIME_ROOT, { maxFiles: 700, maxDepth: 6, exts: /\.(json|jsonl|csv|txt|md|log)$/i });
  return files
    .filter((file) => matchesProject(file, project))
    .map((file) => {
      const st = statSafe(file);
      return {
        id: slug(`evidence-${safeRelative(RUNTIME_ROOT, file)}`),
        title: titleCaseFromSlug(path.basename(file).replace(/\.[^.]+$/, "")),
        path: `runtime:${safeRelative(RUNTIME_ROOT, file)}`,
        kind: path.extname(file).replace(".", "") || "arquivo",
        modified: st?.mtime.toISOString() || null,
        size: st?.size || 0,
      };
    })
    .sort((a, b) => (b.modified || "").localeCompare(a.modified || ""))
    .slice(0, 8);
}

function loadProjectSources() {
  const projectRoot = path.join(SECOND_BRAIN_ROOT, "04-projects");
  const files: string[] = [];
  if (exists(projectRoot)) {
    for (const entry of fs.readdirSync(projectRoot, { withFileTypes: true })) {
      if (entry.name.startsWith(".")) continue;
      const full = path.join(projectRoot, entry.name);
      if (entry.isDirectory()) {
        const map = path.join(full, "MAP.md");
        const readme = path.join(full, "README.md");
        files.push(exists(map) ? map : exists(readme) ? readme : full);
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        files.push(full);
      }
    }
  }
  const workspaceProjectDocs = walkFiles(path.join(WORKSPACE_ROOT, "projects"), { maxFiles: 200, maxDepth: 3, exts: /README\.md$|MAP\.md$/i });
  return [...files, ...workspaceProjectDocs];
}

export function getExecutiveGraph(): ExecutiveGraph {
  const tasks = listTaskExecutions();
  const documents = loadDocuments();
  const allDecisions = loadDecisions();
  const projects: ExecutiveProject[] = loadProjectSources().map((source) => {
    const st = statSafe(source);
    const isDir = st?.isDirectory();
    const content = isDir ? "" : readSafe(source, 120_000);
    const name = firstHeading(content) || titleCaseFromSlug(path.basename(source).replace(/\.md$/, ""));
    const id = inferProjectIdFromPath(source) || slug(name);
    const domain = inferDomain(source, content);
    const matchedTasks = tasks
      .filter((task) => matchesProject(`${task.title}\n${task.objective}\n${task.tags?.join(" ")}\n${JSON.stringify(task.metadata || {})}`, { id, name, domain }))
      .slice(0, 8)
      .map((task) => ({ taskId: task.taskId, title: task.title, status: task.status, targetAgent: task.targetAgent, riskLevel: task.riskLevel, updatedAt: task.updatedAt }));
    const projectDocs = documents.filter((doc) => doc.projectId === id || matchesProject(`${doc.path}\n${doc.title}\n${doc.company}`, { id, name, domain })).slice(0, 8);
    const evidences = loadEvidences({ id, name, domain });
    const decisions = allDecisions.filter((decision) => matchesProject(decision.title, { id, name, domain })).slice(0, 6);
    const timestamps = [st?.mtime.toISOString(), ...matchedTasks.map((task) => task.updatedAt), ...projectDocs.map((doc) => doc.modified), ...evidences.map((e) => e.modified)].filter(Boolean) as string[];
    const openTasks = matchedTasks.filter((task) => !["completed_validated", "completed_unvalidated", "cancelled"].includes(task.status)).length;
    const blockedTasks = matchedTasks.filter((task) => ["blocked", "waiting_input", "failed"].includes(task.status)).length;

    return {
      id,
      name,
      domain,
      sourcePath: source.startsWith(SECOND_BRAIN_ROOT) ? `2nd-brain:${safeRelative(SECOND_BRAIN_ROOT, source)}` : `workspace:${safeRelative(WORKSPACE_ROOT, source)}`,
      status: inferStatus(`${content}\n${matchedTasks.map((task) => task.status).join(" ")}`),
      priority: inferPriority(`${content}\n${matchedTasks.map((task) => task.riskLevel).join(" ")}`),
      risk: blockedTasks ? "risk" : inferRisk(content),
      ownerAgent: AGENT_BY_DOMAIN[domain] || "main",
      summary: firstMeaningfulParagraph(content) || "Projeto detectado a partir das fontes canônicas; resumo executivo ainda não consolidado.",
      nextStep: extractNextStep(content),
      lastMovement: timestamps.sort().at(-1) || null,
      metrics: { openTasks, blockedTasks, documents: projectDocs.length, evidences: evidences.length, decisions: decisions.length },
      tasks: matchedTasks,
      documents: projectDocs,
      evidences,
      decisions,
    };
  });

  const uniqueProjects = Array.from(new Map(projects.map((project) => [project.id, project])).values())
    .sort((a, b) => {
      const priorityWeight = { critical: 4, high: 3, medium: 2, low: 1 };
      return priorityWeight[b.priority] - priorityWeight[a.priority] || (b.lastMovement || "").localeCompare(a.lastMovement || "");
    })
    .slice(0, 80);

  return {
    generatedAt: new Date().toISOString(),
    roots: { secondBrain: SECOND_BRAIN_ROOT, workspace: WORKSPACE_ROOT, runtime: RUNTIME_ROOT },
    metrics: {
      projects: uniqueProjects.length,
      documents: documents.length,
      openTasksLinked: uniqueProjects.reduce((sum, project) => sum + project.metrics.openTasks, 0),
      evidences: uniqueProjects.reduce((sum, project) => sum + project.metrics.evidences, 0),
      decisionsLinked: uniqueProjects.reduce((sum, project) => sum + project.metrics.decisions, 0),
      risks: uniqueProjects.filter((project) => project.risk === "risk").length,
    },
    projects: uniqueProjects,
    documents,
    guardrails: [
      "read-only: esta API não cria, edita, envia ou apaga arquivos",
      "Mission Control é cockpit; GitHub e 2nd-brain continuam fonte de verdade",
      "notificações externas, fiscal, financeiro e cliente continuam exigindo aprovação explícita",
      "segredos e certificados nunca são exibidos; só metadados de arquivo e caminhos internos",
    ],
  };
}
