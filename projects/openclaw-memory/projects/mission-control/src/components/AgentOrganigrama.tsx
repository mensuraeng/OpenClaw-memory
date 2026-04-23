"use client";

import { useState, useCallback, useEffect, useRef } from "react";

interface Agent {
  id: string;
  name: string;
  emoji: string;
  color: string;
  model: string;
  allowAgents: string[];
  allowAgentsDetails?: Array<{ id: string; name: string; emoji: string; color: string }>;
  status: "online" | "offline";
  activeSessions: number;
}

interface AgentOrganigramaProps {
  agents: Agent[];
}

const NODE_W = 176;
const NODE_H = 80;

function autoLayout(agents: Agent[]): Record<string, { x: number; y: number }> {
  if (agents.length === 0) return {};
  const agentMap = new Map(agents.map((a) => [a.id, a]));
  const childIds = new Set(agents.flatMap((a) => a.allowAgents || []));
  const roots = agents.filter((a) => !childIds.has(a.id));
  const H_GAP = 44;
  const V_GAP = 110;
  const positions: Record<string, { x: number; y: number }> = {};
  const leafCounter = { val: 0 };

  function getChildren(id: string): Agent[] {
    const agent = agentMap.get(id);
    if (!agent) return [];
    return (agent.allowAgents || []).map((cid) => agentMap.get(cid)).filter(Boolean) as Agent[];
  }

  function layoutDFS(agent: Agent, level: number): void {
    const children = getChildren(agent.id);
    if (children.length === 0) {
      positions[agent.id] = { x: leafCounter.val, y: level * (NODE_H + V_GAP) };
      leafCounter.val += NODE_W + H_GAP;
    } else {
      for (const child of children) layoutDFS(child, level + 1);
      const childPos = children.map((c) => positions[c.id]).filter(Boolean);
      if (childPos.length > 0) {
        const leftX = Math.min(...childPos.map((p) => p.x));
        const rightX = Math.max(...childPos.map((p) => p.x + NODE_W));
        positions[agent.id] = {
          x: leftX + (rightX - leftX) / 2 - NODE_W / 2,
          y: level * (NODE_H + V_GAP),
        };
      } else {
        positions[agent.id] = { x: leafCounter.val, y: level * (NODE_H + V_GAP) };
        leafCounter.val += NODE_W + H_GAP;
      }
    }
  }

  for (const root of roots) layoutDFS(root, 0);
  for (const agent of agents) {
    if (!positions[agent.id]) {
      positions[agent.id] = { x: leafCounter.val, y: 0 };
      leafCounter.val += NODE_W + H_GAP;
    }
  }

  const minX = Math.min(...Object.values(positions).map((p) => p.x));
  const minY = Math.min(...Object.values(positions).map((p) => p.y));
  for (const id in positions) {
    positions[id] = { x: positions[id].x - minX + 48, y: positions[id].y - minY + 48 };
  }
  return positions;
}

export function AgentOrganigrama({ agents }: AgentOrganigramaProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [editMode, setEditMode] = useState(false);

  // Posições: localStorage (apenas visual)
  const posStorageKey = `organigrama-pos-v2-${agents.map((a) => a.id).sort().join(",")}`;
  const [nodePos, setNodePos] = useState<Record<string, { x: number; y: number }>>({});

  // Conexões: vêm sempre dos props (OpenClaw), editáveis mas só persistem via API
  const [connections, setConnections] = useState<Record<string, string[]>>({});
  const [pendingChanges, setPendingChanges] = useState(false);

  const [dragging, setDragging] = useState<{
    id: string;
    startClientX: number;
    startClientY: number;
    origX: number;
    origY: number;
  } | null>(null);
  const [wasDragging, setWasDragging] = useState(false);
  const [connectFrom, setConnectFrom] = useState<string | null>(null);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [saveMsg, setSaveMsg] = useState("");

  // Inicializar: posições do localStorage, conexões dos props
  useEffect(() => {
    if (agents.length === 0) return;

    // Posições: tentar localStorage
    try {
      const saved = localStorage.getItem(posStorageKey);
      if (saved) {
        setNodePos(JSON.parse(saved));
      } else {
        setNodePos(autoLayout(agents));
      }
    } catch {
      setNodePos(autoLayout(agents));
    }

    // Conexões: SEMPRE dos props (OpenClaw é a fonte de verdade)
    setConnections(Object.fromEntries(agents.map((a) => [a.id, a.allowAgents || []])));
    setPendingChanges(false);
  }, [agents, posStorageKey]);

  // ── Salvar posições no localStorage ────────────────────────────────────────
  const savePositions = useCallback(() => {
    try {
      localStorage.setItem(posStorageKey, JSON.stringify(nodePos));
    } catch {}
  }, [posStorageKey, nodePos]);

  // ── Salvar conexões no OpenClaw via API ────────────────────────────────────
  const saveToOpenClaw = useCallback(async () => {
    setSaveState("saving");
    setSaveMsg("Salvando no OpenClaw...");
    try {
      const res = await fetch("/api/agents/hierarchy", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ connections }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Erro desconhecido");

      // Salvar posições no localStorage junto
      savePositions();
      setPendingChanges(false);
      setSaveState("saved");
      setSaveMsg(`✓ ${data.message}`);
      setTimeout(() => setSaveState("idle"), 3000);
    } catch (e: unknown) {
      setSaveState("error");
      setSaveMsg(`✗ ${e instanceof Error ? e.message : "Falha ao salvar"}`);
      setTimeout(() => setSaveState("idle"), 4000);
    }
  }, [connections, savePositions]);

  // ── Reset: layout automático baseado nos dados do OpenClaw ─────────────────
  const resetLayout = useCallback(() => {
    try { localStorage.removeItem(posStorageKey); } catch {}
    setNodePos(autoLayout(agents));
    setConnections(Object.fromEntries(agents.map((a) => [a.id, a.allowAgents || []])));
    setPendingChanges(false);
    setConnectFrom(null);
  }, [agents, posStorageKey]);

  // ── Drag handlers ──────────────────────────────────────────────────────────
  const handleNodeMouseDown = useCallback(
    (e: React.MouseEvent, id: string) => {
      if (!editMode) return;
      e.preventDefault();
      e.stopPropagation();
      setWasDragging(false);
      setDragging({
        id,
        startClientX: e.clientX,
        startClientY: e.clientY,
        origX: nodePos[id]?.x ?? 0,
        origY: nodePos[id]?.y ?? 0,
      });
    },
    [editMode, nodePos]
  );

  const handleSvgMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!dragging) return;
      const dx = e.clientX - dragging.startClientX;
      const dy = e.clientY - dragging.startClientY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) setWasDragging(true);
      setNodePos((prev) => ({
        ...prev,
        [dragging.id]: {
          x: Math.max(0, dragging.origX + dx),
          y: Math.max(0, dragging.origY + dy),
        },
      }));
    },
    [dragging]
  );

  const handleSvgMouseUp = useCallback(() => setDragging(null), []);

  // ── Connection click ───────────────────────────────────────────────────────
  const handleNodeClick = useCallback(
    (e: React.MouseEvent, id: string) => {
      if (!editMode) return;
      e.stopPropagation();
      if (wasDragging) { setWasDragging(false); return; }

      if (!connectFrom) {
        setConnectFrom(id);
      } else if (connectFrom === id) {
        setConnectFrom(null);
      } else {
        setConnections((prev) => {
          const fromList = prev[connectFrom] || [];
          const has = fromList.includes(id);
          const updated = { ...prev, [connectFrom]: has ? fromList.filter((c) => c !== id) : [...fromList, id] };
          return updated;
        });
        setPendingChanges(true);
        setConnectFrom(null);
      }
    },
    [editMode, connectFrom, wasDragging]
  );

  const handleSvgClick = useCallback(() => {
    if (editMode) setConnectFrom(null);
  }, [editMode]);

  // ── Render ─────────────────────────────────────────────────────────────────
  if (agents.length === 0 || Object.keys(nodePos).length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
        Nenhum agente configurado
      </div>
    );
  }

  const agentMap = new Map(agents.map((a) => [a.id, a]));
  const allPos = Object.values(nodePos);
  const svgW = Math.max(900, Math.max(...allPos.map((p) => p.x)) + NODE_W + 80);
  const svgH = Math.max(400, Math.max(...allPos.map((p) => p.y)) + NODE_H + 80);

  const edges: Array<{ fromId: string; toId: string }> = [];
  for (const [fromId, toIds] of Object.entries(connections)) {
    for (const toId of toIds) {
      if (nodePos[fromId] && nodePos[toId] && agentMap.has(toId)) {
        edges.push({ fromId, toId });
      }
    }
  }

  const totalConns = edges.length;
  const saveBtnColor = saveState === "saving" ? "#1e3a5f"
    : saveState === "saved" ? "#052e16"
    : saveState === "error" ? "#1c0a0a"
    : pendingChanges ? "var(--accent)" : "var(--surface)";
  const saveBtnTextColor = saveState === "saving" ? "#60a5fa"
    : saveState === "saved" ? "#4ade80"
    : saveState === "error" ? "#f87171"
    : pendingChanges ? "#000" : "var(--text-muted)";

  return (
    <div style={{ userSelect: editMode ? "none" : "auto", fontFamily: "var(--font-body, sans-serif)" }}>

      {/* ── Toolbar ── */}
      <div style={{
        display: "flex", gap: 8, padding: "10px 16px",
        borderBottom: "1px solid var(--border)",
        alignItems: "center", flexWrap: "wrap",
        backgroundColor: "var(--surface-elevated)",
      }}>
        <button
          onClick={() => { setEditMode(!editMode); setConnectFrom(null); }}
          style={{
            padding: "6px 16px", borderRadius: 6, fontSize: 12, fontWeight: 700,
            cursor: "pointer", border: "none", transition: "all 150ms",
            backgroundColor: editMode ? "var(--accent)" : "var(--surface)",
            color: editMode ? "#000" : "var(--text-secondary)",
            outline: "1px solid var(--border)",
          }}
        >
          {editMode ? "✏️ Editando" : "✏️ Modo Edição"}
        </button>

        {editMode ? (
          <>
            <div style={{
              padding: "5px 12px", borderRadius: 6, fontSize: 12,
              backgroundColor: "var(--surface)", border: "1px solid var(--border)",
              color: connectFrom ? "var(--accent)" : "var(--text-muted)",
            }}>
              {connectFrom
                ? `🔗 Conectando "${agentMap.get(connectFrom)?.name}" → clique no destino (ou no mesmo para cancelar)`
                : "⠿ Arraste para mover  •  Clique para criar/remover conexão"}
            </div>

            {pendingChanges && (
              <div style={{
                padding: "5px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                backgroundColor: "#2a1a00", border: "1px solid #f59e0b", color: "#f59e0b",
              }}>
                ⚠ Alterações não salvas
              </div>
            )}

            <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
              {/* Salvar no OpenClaw */}
              <button
                onClick={saveToOpenClaw}
                disabled={saveState === "saving"}
                title="Salva conexões no openclaw.json + posições no navegador"
                style={{
                  padding: "6px 16px", borderRadius: 6, fontSize: 12, fontWeight: 700,
                  cursor: saveState === "saving" ? "not-allowed" : "pointer",
                  border: `1px solid ${saveState === "error" ? "#dc2626" : saveState === "saved" ? "#16a34a" : pendingChanges ? "transparent" : "var(--border)"}`,
                  backgroundColor: saveBtnColor,
                  color: saveBtnTextColor,
                  transition: "all 150ms",
                  opacity: saveState === "saving" ? 0.7 : 1,
                }}
              >
                {saveState === "saving" ? "⏳ Salvando..." :
                  saveState === "saved" ? "✓ Salvo no OpenClaw!" :
                  saveState === "error" ? "✗ Erro!" :
                  pendingChanges ? "💾 Salvar no OpenClaw" : "💾 Salvar"}
              </button>

              <button
                onClick={resetLayout}
                title="Volta para o layout automático baseado no OpenClaw"
                style={{
                  padding: "6px 14px", borderRadius: 6, fontSize: 12, fontWeight: 600,
                  cursor: "pointer", backgroundColor: "var(--surface)",
                  color: "var(--text-muted)", border: "1px solid var(--border)",
                }}
              >
                ↺ Resetar
              </button>
            </div>
          </>
        ) : (
          <>
            <span style={{ fontSize: 12, color: "var(--text-muted)", marginLeft: 4 }}>
              {agents.length} agente{agents.length !== 1 ? "s" : ""} • {totalConns} conexão{totalConns !== 1 ? "ões" : ""}
            </span>
            {saveMsg && saveState === "saved" && (
              <span style={{ fontSize: 11, color: "#4ade80", marginLeft: 8 }}>✓ {saveMsg}</span>
            )}
          </>
        )}
      </div>

      {/* Mensagem de feedback fora do edit mode */}
      {saveState !== "idle" && !editMode && (
        <div style={{
          padding: "8px 16px", fontSize: 12, fontWeight: 500,
          backgroundColor: saveState === "saved" ? "#052e16" : "#1c0a0a",
          color: saveState === "saved" ? "#4ade80" : "#f87171",
          borderBottom: "1px solid var(--border)",
        }}>
          {saveMsg}
        </div>
      )}

      {/* ── SVG Canvas ── */}
      <div style={{
        overflowX: "auto", overflowY: "auto",
        backgroundColor: editMode ? "var(--bg)" : "transparent",
      }}>
        <svg
          ref={svgRef}
          width={svgW}
          height={svgH}
          viewBox={`0 0 ${svgW} ${svgH}`}
          onMouseMove={handleSvgMouseMove}
          onMouseUp={handleSvgMouseUp}
          onMouseLeave={handleSvgMouseUp}
          onClick={handleSvgClick}
          style={{
            display: "block",
            cursor: dragging ? "grabbing" : editMode ? "crosshair" : "default",
          }}
        >
          <defs>
            <marker id="mc-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="var(--border)" />
            </marker>
            <marker id="mc-arrow-hi" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="var(--accent)" />
            </marker>
          </defs>

          {/* Grid de apoio (edit mode) */}
          {editMode && (
            <>
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="var(--border)" strokeWidth="0.4" opacity={0.35} />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </>
          )}

          {/* ── Arestas ── */}
          {edges.map(({ fromId, toId }, i) => {
            const from = nodePos[fromId];
            const to = nodePos[toId];
            if (!from || !to) return null;

            const x1 = from.x + NODE_W / 2;
            const y1 = from.y + NODE_H;
            const x2 = to.x + NODE_W / 2;
            const y2 = to.y;
            const midY = y1 + (y2 - y1) * 0.5;

            const isHi =
              hoveredId === fromId || hoveredId === toId ||
              connectFrom === fromId || connectFrom === toId;

            return (
              <path
                key={`${fromId}→${toId}-${i}`}
                d={`M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`}
                fill="none"
                stroke={isHi ? "var(--accent)" : "var(--border)"}
                strokeWidth={isHi ? 2.5 : 1.5}
                opacity={isHi ? 1 : 0.5}
                strokeDasharray={isHi ? "none" : "5,4"}
                markerEnd={isHi ? "url(#mc-arrow-hi)" : "url(#mc-arrow)"}
                style={{ transition: "stroke 0.15s, opacity 0.15s" }}
              />
            );
          })}

          {/* ── Nós ── */}
          {agents.map((agent) => {
            const pos = nodePos[agent.id];
            if (!pos) return null;
            const { x, y } = pos;
            const isHi = hoveredId === agent.id;
            const isCF = connectFrom === agent.id;
            const isOnline = agent.status === "online";
            const subCount = (connections[agent.id] || []).length;
            const isDraggingThis = dragging?.id === agent.id;

            return (
              <g
                key={agent.id}
                onMouseEnter={() => setHoveredId(agent.id)}
                onMouseLeave={() => setHoveredId(null)}
                onMouseDown={(e) => handleNodeMouseDown(e, agent.id)}
                onClick={(e) => handleNodeClick(e, agent.id)}
                style={{
                  cursor: editMode
                    ? isDraggingThis ? "grabbing" : "grab"
                    : "default",
                }}
              >
                {/* Anel de seleção (connectFrom) */}
                {isCF && (
                  <rect
                    x={x - 5} y={y - 5}
                    width={NODE_W + 10} height={NODE_H + 10}
                    rx={14} ry={14}
                    fill="none"
                    stroke="var(--accent)"
                    strokeWidth={2}
                    strokeDasharray="6 3"
                    opacity={0.9}
                  />
                )}

                {/* Card */}
                <rect
                  x={x} y={y} width={NODE_W} height={NODE_H}
                  rx={10} ry={10}
                  fill={isCF ? `${agent.color}30` : isHi ? `${agent.color}18` : "var(--card)"}
                  stroke={isCF ? agent.color : isHi ? agent.color : "var(--border)"}
                  strokeWidth={isCF ? 2.5 : isHi ? 2 : 1}
                  style={{
                    transition: "all 0.15s",
                    filter: (isHi || isCF || isDraggingThis)
                      ? "drop-shadow(0 6px 18px rgba(0,0,0,0.55))"
                      : "none",
                  }}
                />

                {/* Barra de cor */}
                <rect x={x} y={y + 8} width={4} height={NODE_H - 16} rx={2} fill={agent.color} />

                {/* Emoji */}
                <text x={x + 28} y={y + NODE_H / 2 + 8} fontSize={22} textAnchor="middle">
                  {agent.emoji}
                </text>

                {/* Nome */}
                <text
                  x={x + 48} y={y + NODE_H / 2 - 8}
                  fill="var(--text-primary)" fontSize={13} fontWeight={700}
                  fontFamily="var(--font-heading, sans-serif)"
                >
                  {agent.name.length > 13 ? agent.name.slice(0, 12) + "…" : agent.name}
                </text>

                {/* Modelo */}
                <text x={x + 48} y={y + NODE_H / 2 + 8} fill="var(--text-muted)" fontSize={10}>
                  {(agent.model.split("/").pop() || "").slice(0, 18)}
                </text>

                {/* Sub-agentes */}
                {subCount > 0 && (
                  <text x={x + 48} y={y + NODE_H / 2 + 22} fill={agent.color} fontSize={9} fontWeight={600}>
                    {subCount} sub-agente{subCount !== 1 ? "s" : ""}
                  </text>
                )}

                {/* Status dot */}
                <circle cx={x + NODE_W - 14} cy={y + 14} r={5} fill={isOnline ? "#4ade80" : "#6b7280"} />
                {isOnline && <circle cx={x + NODE_W - 14} cy={y + 14} r={9} fill="#4ade8020" />}

                {/* Sessões */}
                {agent.activeSessions > 0 && (
                  <g>
                    <rect x={x + NODE_W - 28} y={y + NODE_H - 22} width={22} height={14} rx={4}
                      fill="var(--accent)" opacity={0.15} />
                    <text x={x + NODE_W - 17} y={y + NODE_H - 11}
                      fontSize={9} fill="var(--accent)" textAnchor="middle" fontWeight={700}>
                      {agent.activeSessions}▶
                    </text>
                  </g>
                )}

                {/* Ícone arrastar */}
                {editMode && (
                  <text x={x + NODE_W / 2} y={y + NODE_H - 5}
                    fontSize={8} fill="var(--text-muted)" textAnchor="middle" opacity={0.4}>
                    ⠿
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* ── Legenda ── */}
      <div style={{
        display: "flex", gap: "1.5rem", justifyContent: "center",
        padding: "10px 16px", borderTop: "1px solid var(--border)",
        fontSize: 11, color: "var(--text-muted)", flexWrap: "wrap",
      }}>
        <span><span style={{ color: "#4ade80" }}>●</span> Online</span>
        <span><span style={{ color: "#6b7280" }}>●</span> Offline</span>
        <span>╌╌▶ Pode invocar</span>
        {editMode && (
          <span style={{ color: "var(--accent)", fontWeight: 600 }}>
            ✏️ Arraste para reposicionar  •  Clique para conectar/desconectar  •  Salvar grava no OpenClaw
          </span>
        )}
      </div>
    </div>
  );
}
