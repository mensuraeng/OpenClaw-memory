import { readFileSync, existsSync } from "fs";

const PENDING_PATH = "/root/.openclaw/workspace/memory/context/pending.md";
const DECISIONS_PATH = "/root/.openclaw/workspace/memory/context/decisions.md";

export interface ExecutiveMemorySummary {
  pendingCritical: string[];
  pendingWaitingAle: string[];
  recentDecisions: string[];
}

function extractChecklistItems(sectionText: string): string[] {
  return sectionText
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("- [ ]") || line.startsWith("- [x]"))
    .map((line) => line.replace(/^- \[[ x]\]\s*/, "").trim())
    .slice(0, 6);
}

function extractSection(content: string, heading: string): string {
  const marker = `## ${heading}`;
  const start = content.indexOf(marker);
  if (start === -1) return "";
  const rest = content.slice(start + marker.length);
  const next = rest.search(/\n##\s+/);
  return next === -1 ? rest : rest.slice(0, next);
}

function extractDecisionBullets(content: string): string[] {
  return content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("### "))
    .map((line) => line.replace(/^###\s*/, "").trim())
    .slice(-6)
    .reverse();
}

export function getExecutiveMemorySummary(): ExecutiveMemorySummary {
  const pendingContent = existsSync(PENDING_PATH) ? readFileSync(PENDING_PATH, "utf-8") : "";
  const decisionsContent = existsSync(DECISIONS_PATH) ? readFileSync(DECISIONS_PATH, "utf-8") : "";

  const pendingCritical = extractChecklistItems(extractSection(pendingContent, "Críticas"));
  const pendingWaitingAle = extractChecklistItems(extractSection(pendingContent, "Aguardando Alê"));
  const recentDecisions = extractDecisionBullets(decisionsContent);

  return { pendingCritical, pendingWaitingAle, recentDecisions };
}
