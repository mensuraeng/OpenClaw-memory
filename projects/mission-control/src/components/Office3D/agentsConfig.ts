/**
 * Office 3D — Configuração de Agentes MENSURA
 * Posições refletem a hierarquia real: Flávia no topo, empresas no meio, especialistas na base
 */

export interface AgentConfig {
  id: string;
  name: string;
  emoji: string;
  position: [number, number, number]; // x, y, z
  color: string;
  role: string;
}

// Layout hierárquico em 4 fileiras:
// Fileira 0 (frente): Flávia — CEO/Main
// Fileira 1: Mia, Mensura, PCS — empresas
// Fileira 2: RH, Marketing, Producao, Finance — especialistas
// Fileira 3 (fundo): Autopilot, Juridico, BI, Suprimentos — especialistas

export const AGENTS: AgentConfig[] = [
  // ── Nível 1: Main ──────────────────────────────────────────────────────────
  {
    id: "main",
    name: "Flávia",
    emoji: "🏗️",
    position: [0, 0, 7],
    color: "#ff6b35",
    role: "Agente Principal",
  },
  // ── Nível 2: Empresas ──────────────────────────────────────────────────────
  {
    id: "mia",
    name: "Mia",
    emoji: "🏛️",
    position: [-5, 0, 3],
    color: "#3B82F6",
    role: "MIA Engenharia",
  },
  {
    id: "mensura",
    name: "Mensura",
    emoji: "📐",
    position: [0, 0, 3],
    color: "#EF4444",
    role: "MENSURA Engenharia",
  },
  {
    id: "pcs",
    name: "PCS",
    emoji: "🏢",
    position: [5, 0, 3],
    color: "#7C3AED",
    role: "PCS Engenharia",
  },
  // ── Nível 3a: Especialistas ────────────────────────────────────────────────
  {
    id: "rh",
    name: "RH",
    emoji: "👥",
    position: [-7.5, 0, -1],
    color: "#8B5CF6",
    role: "Recursos Humanos",
  },
  {
    id: "marketing",
    name: "Marketing",
    emoji: "📣",
    position: [-2.5, 0, -1],
    color: "#EC4899",
    role: "Marketing & Comunicação",
  },
  {
    id: "producao",
    name: "Produção",
    emoji: "🏗️",
    position: [2.5, 0, -1],
    color: "#F59E0B",
    role: "Produção de Obras",
  },
  {
    id: "finance",
    name: "Finance",
    emoji: "💰",
    position: [7.5, 0, -1],
    color: "#10B981",
    role: "Financeiro",
  },
  // ── Nível 3b: Especialistas ────────────────────────────────────────────────
  {
    id: "autopilot",
    name: "Autopilot",
    emoji: "🤖",
    position: [-7.5, 0, -5],
    color: "#6B7280",
    role: "Automação de Obras",
  },
  {
    id: "juridico",
    name: "Jurídico",
    emoji: "⚖️",
    position: [-2.5, 0, -5],
    color: "#6366F1",
    role: "Jurídico & Contratos",
  },
  {
    id: "bi",
    name: "BI / Dados",
    emoji: "📊",
    position: [2.5, 0, -5],
    color: "#06B6D4",
    role: "Business Intelligence",
  },
  {
    id: "suprimentos",
    name: "Suprimentos",
    emoji: "📦",
    position: [7.5, 0, -5],
    color: "#D97706",
    role: "Suprimentos & Compras",
  },
];

export type AgentStatus = "idle" | "working" | "thinking" | "error";

export interface AgentState {
  id: string;
  status: AgentStatus;
  currentTask?: string;
  model?: string;
  tokensPerHour?: number;
  tasksInQueue?: number;
  uptime?: number;
}
