import fs from "fs";
import path from "path";

export const SECOND_BRAIN_ROOT = process.env.SECOND_BRAIN_ROOT || "/root/2nd-brain";

const CANONICAL_PATHS = {
  readme: "README.md",
  pending: "02-context/pending.md",
  decisions: "02-context/decisions.md",
  lessons: "02-context/lessons.md",
  working: "06-agents/flavia/WORKING.md",
  flaviaMemory: "06-agents/flavia/memory",
  inbox: "00-inbox",
  standard: "_system/CAPTURE-AND-CONSOLIDATION-STANDARD.md",
  agentMap: "06-agents/flavia/AGENT-MAP.md",
};

type Tone = "ok" | "attention" | "risk";

export type MemorySearchResult = {
  title: string;
  path: string;
  line: number;
  score: number;
  snippet: string;
  authority: "decision" | "pending" | "project" | "lesson" | "agent" | "journal" | "system" | "inbox" | "memory";
};

export type MemoryValidatorIssue = {
  id: string;
  severity: "ok" | "attention" | "risk";
  title: string;
  detail: string;
  path?: string;
};

function safeRead(relativePath: string): string {
  try {
    return fs.readFileSync(path.join(SECOND_BRAIN_ROOT, relativePath), "utf-8");
  } catch {
    return "";
  }
}

function safeStat(relativePath: string) {
  try {
    return fs.statSync(path.join(SECOND_BRAIN_ROOT, relativePath));
  } catch {
    return null;
  }
}

function walkMarkdown(dir: string, maxFiles = 900): string[] {
  const root = path.join(SECOND_BRAIN_ROOT, dir);
  const files: string[] = [];
  function walk(current: string) {
    if (files.length >= maxFiles) return;
    let entries: fs.Dirent[] = [];
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.name.startsWith(".git")) continue;
      const full = path.join(current, entry.name);
      const rel = path.relative(SECOND_BRAIN_ROOT, full);
      if (entry.isDirectory()) walk(full);
      else if (/\.(md|mdx|yaml|yml|json)$/i.test(entry.name)) files.push(rel);
    }
  }
  walk(root);
  return files;
}

function extractHeadings(content: string, prefix = "## "): string[] {
  return content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith(prefix))
    .map((line) => line.replace(/^#+\s*/, "").trim());
}

function checklistItems(content: string): string[] {
  return content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => /^- \[[ xX]\]/.test(line));
}

function countMdFiles(relativeDir: string): number {
  return walkMarkdown(relativeDir).filter((file) => file.endsWith(".md") || file.endsWith(".mdx")).length;
}

function authorityForPath(file: string): MemorySearchResult["authority"] {
  if (file.includes("decisions.md")) return "decision";
  if (file.includes("pending.md") || file.includes("WORKING.md")) return "pending";
  if (file.includes("lessons.md")) return "lesson";
  if (file.startsWith("04-projects/")) return "project";
  if (file.startsWith("06-agents/")) return "agent";
  if (file.startsWith("05-journal/")) return "journal";
  if (file.startsWith("_system/")) return "system";
  if (file.startsWith("00-inbox/")) return "inbox";
  return "memory";
}

const AUTHORITY_WEIGHT: Record<MemorySearchResult["authority"], number> = {
  decision: 8,
  pending: 7,
  project: 6,
  lesson: 5,
  agent: 4,
  system: 4,
  journal: 2,
  inbox: 1,
  memory: 1,
};

export function searchSecondBrain(query: string): MemorySearchResult[] {
  const terms = query
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .split(/\W+/)
    .filter((term) => term.length > 2);
  if (!terms.length) return [];

  const files = walkMarkdown(".", 1200);
  const results: MemorySearchResult[] = [];

  for (const file of files) {
    const content = safeRead(file);
    if (!content) continue;
    const lines = content.split("\n");
    const normalizedLines = lines.map((line) =>
      line.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    );
    const authority = authorityForPath(file);

    normalizedLines.forEach((line, index) => {
      const hits = terms.filter((term) => line.includes(term)).length;
      if (!hits) return;
      const start = Math.max(0, index - 1);
      const end = Math.min(lines.length, index + 2);
      results.push({
        title: path.basename(file),
        path: file,
        line: index + 1,
        score: hits * 10 + AUTHORITY_WEIGHT[authority],
        snippet: lines.slice(start, end).join("\n").slice(0, 360),
        authority,
      });
    });
  }

  return results.sort((a, b) => b.score - a.score).slice(0, 30);
}

export function validateSecondBrain(): MemoryValidatorIssue[] {
  const issues: MemoryValidatorIssue[] = [];
  const inboxFiles = walkMarkdown(CANONICAL_PATHS.inbox).filter((file) => file.endsWith(".md") && !file.includes("/_templates/") && !file.includes("/_archive/"));
  const missingSidecars = inboxFiles.filter((file) => !fs.existsSync(path.join(SECOND_BRAIN_ROOT, `${file}.meta.yaml`)));
  issues.push({
    id: "inbox-sidecars",
    severity: missingSidecars.length ? "attention" : "ok",
    title: "Capturas com sidecar",
    detail: missingSidecars.length ? `${missingSidecars.length} captura(s) sem .meta.yaml` : "Todas as capturas elegíveis têm sidecar.",
    path: CANONICAL_PATHS.inbox,
  });

  const decisions = safeRead(CANONICAL_PATHS.decisions);
  const decisionHeadings = extractHeadings(decisions).filter((h) => h && !/^Decis/.test(h));
  const decisionsWithoutDate = decisionHeadings.filter((h) => !/20\d{2}-\d{2}-\d{2}|\(20\d{2}-\d{2}-\d{2}\)/.test(h));
  issues.push({
    id: "decision-dates",
    severity: decisionsWithoutDate.length > 8 ? "attention" : "ok",
    title: "Decisões datadas",
    detail: decisionsWithoutDate.length ? `${decisionsWithoutDate.length} heading(s) de decisão sem data explícita.` : "Decisões recentes estão datadas.",
    path: CANONICAL_PATHS.decisions,
  });

  const pending = safeRead(CANONICAL_PATHS.pending);
  const pendingItems = checklistItems(pending);
  const weakPending = pendingItems.filter((item) => !/(dono|owner|próximo passo|proximo passo|deadline|até|ate|aguardando)/i.test(item));
  issues.push({
    id: "pending-actionability",
    severity: weakPending.length > 12 ? "attention" : "ok",
    title: "Pendências acionáveis",
    detail: pendingItems.length ? `${pendingItems.length} pendência(s), ${weakPending.length} com baixa ação explícita.` : "Sem checklist de pendências detectado.",
    path: CANONICAL_PATHS.pending,
  });

  const files = walkMarkdown(".", 1400);
  const secretPattern = /(api[_-]?key|client[_-]?secret|password|senha|token|authorization:\s*bearer|-----BEGIN)/i;
  const suspicious = files.filter((file) => {
    if (file.includes("_archive") || file.endsWith(".meta.yaml")) return false;
    const content = safeRead(file);
    return secretPattern.test(content) && !/não inserir credenciais|nunca imprimir segredo|sem segredo|credenciais nunca/i.test(content);
  });
  issues.push({
    id: "secret-hygiene",
    severity: suspicious.length ? "risk" : "ok",
    title: "Higiene de segredos",
    detail: suspicious.length ? `${suspicious.length} arquivo(s) com padrão sensível para revisar.` : "Nenhum padrão sensível óbvio detectado em markdown/yaml/json.",
  });

  const agentMapExists = Boolean(safeStat(CANONICAL_PATHS.agentMap));
  const standardExists = Boolean(safeStat(CANONICAL_PATHS.standard));
  issues.push({
    id: "canonical-entrypoints",
    severity: agentMapExists && standardExists ? "ok" : "risk",
    title: "Entradas canônicas",
    detail: agentMapExists && standardExists ? "AGENT-MAP e padrão de captura encontrados." : "Falta AGENT-MAP ou padrão de captura.",
  });

  return issues;
}

export function getOpenClawMemoryControl() {
  const pending = safeRead(CANONICAL_PATHS.pending);
  const decisions = safeRead(CANONICAL_PATHS.decisions);
  const lessons = safeRead(CANONICAL_PATHS.lessons);
  const working = safeRead(CANONICAL_PATHS.working);
  const validators = validateSecondBrain();
  const riskCount = validators.filter((v) => v.severity === "risk").length;
  const attentionCount = validators.filter((v) => v.severity === "attention").length;

  const paths = Object.entries(CANONICAL_PATHS).map(([key, relPath]) => {
    const stat = safeStat(relPath);
    return {
      key,
      path: path.join(SECOND_BRAIN_ROOT, relPath),
      exists: Boolean(stat),
      size: stat?.size || 0,
      modified: stat?.mtime.toISOString() || null,
    };
  });

  const score = Math.max(0, Math.min(10, 10 - riskCount * 0.9 - attentionCount * 0.25));
  const tone: Tone = riskCount ? "risk" : attentionCount ? "attention" : "ok";

  return {
    generatedAt: new Date().toISOString(),
    root: SECOND_BRAIN_ROOT,
    routeRecommendation: {
      preferred: "openclaw.mensuraengenharia.com.br",
      alternative: "mensuraengenharia.com.br/openclaw",
      guardrail: "read-only e protegido; sem publicação pública de memória operacional.",
    },
    score: Number(score.toFixed(1)),
    tone,
    metrics: {
      pendingItems: checklistItems(pending).length,
      decisions: extractHeadings(decisions).length,
      lessons: extractHeadings(lessons).length,
      workingItems: (working.match(/^###\s+FLV-WORK-/gm) || []).length,
      projects: countMdFiles("04-projects"),
      agentMemoryFiles: countMdFiles("06-agents"),
      inboxCaptures: walkMarkdown(CANONICAL_PATHS.inbox).filter((file) => file.endsWith(".md") && !file.includes("/_templates/")).length,
    },
    recent: {
      decisions: extractHeadings(decisions).slice(-8).reverse(),
      lessons: extractHeadings(lessons).slice(-6).reverse(),
      working: extractHeadings(working, "### ").filter((h) => h.startsWith("FLV-WORK-")).slice(0, 8),
    },
    validators,
    paths,
  };
}
