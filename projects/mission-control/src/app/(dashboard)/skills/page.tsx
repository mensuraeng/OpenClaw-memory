"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Search,
  RefreshCw,
  Puzzle,
  Package,
  FolderOpen,
  ExternalLink,
  FileText,
  X,
  Download,
  Trash2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { SectionHeader, MetricCard } from "@/components/TenacitOS";

interface Skill {
  id: string;
  name: string;
  description: string;
  location: string;
  source: "workspace" | "system";
  homepage?: string;
  emoji?: string;
  fileCount: number;
  fullContent: string;
  files: string[];
  agents: string[];
  installed: boolean;
}

interface SkillsData {
  skills: Skill[];
  total: number;
  installed: number;
}

interface Toast {
  id: number;
  type: "success" | "error";
  message: string;
}

export default function SkillsPage() {
  const [data, setData] = useState<SkillsData | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterSource, setFilterSource] = useState<"all" | "workspace" | "system">("all");
  const [filterInstalled, setFilterInstalled] = useState<"all" | "installed" | "notinstalled">("all");
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [loadingSkills, setLoadingSkills] = useState<Set<string>>(new Set());

  const fetchSkills = useCallback(() => {
    fetch("/api/skills")
      .then((res) => res.json())
      .then(setData)
      .catch(() => setData({ skills: [], total: 0, installed: 0 }));
  }, []);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const showToast = (type: "success" | "error", message: string) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  };

  const installSkill = async (skill: Skill) => {
    setLoadingSkills((prev) => new Set(prev).add(skill.id));
    try {
      const res = await fetch("/api/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skillId: skill.id, location: skill.location }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Falha ao instalar");
      }
      showToast("success", `✅ Skill "${skill.name}" instalada com sucesso!`);
      fetchSkills();
      if (selectedSkill?.id === skill.id) {
        setSelectedSkill({ ...selectedSkill, installed: true });
      }
    } catch (e: unknown) {
      showToast("error", `❌ ${e instanceof Error ? e.message : "Erro ao instalar skill"}`);
    } finally {
      setLoadingSkills((prev) => {
        const s = new Set(prev);
        s.delete(skill.id);
        return s;
      });
    }
  };

  const uninstallSkill = async (skill: Skill) => {
    setLoadingSkills((prev) => new Set(prev).add(skill.id));
    try {
      const res = await fetch("/api/skills", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ skillId: skill.id }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Falha ao desinstalar");
      }
      showToast("success", `🗑️ Skill "${skill.name}" desinstalada.`);
      fetchSkills();
      if (selectedSkill?.id === skill.id) {
        setSelectedSkill({ ...selectedSkill, installed: false });
      }
    } catch (e: unknown) {
      showToast("error", `❌ ${e instanceof Error ? e.message : "Erro ao desinstalar skill"}`);
    } finally {
      setLoadingSkills((prev) => {
        const s = new Set(prev);
        s.delete(skill.id);
        return s;
      });
    }
  };

  if (!data) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-24">
          <RefreshCw className="w-8 h-8 animate-spin" style={{ color: "var(--accent)" }} />
        </div>
      </div>
    );
  }

  const { skills } = data;
  const installedCount = skills.filter((s) => s.installed).length;

  // Filter skills
  let filteredSkills = skills;

  if (filterSource !== "all") {
    filteredSkills = filteredSkills.filter((s) => s.source === filterSource);
  }

  if (filterInstalled === "installed") {
    filteredSkills = filteredSkills.filter((s) => s.installed);
  } else if (filterInstalled === "notinstalled") {
    filteredSkills = filteredSkills.filter((s) => !s.installed);
  }

  if (searchQuery) {
    const query = searchQuery.toLowerCase();
    filteredSkills = filteredSkills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(query) ||
        skill.description.toLowerCase().includes(query) ||
        skill.id.toLowerCase().includes(query)
    );
  }

  // Group by source
  const workspaceSkills = filteredSkills.filter((s) => s.source === "workspace");
  const systemSkills = filteredSkills.filter((s) => s.source === "system");

  const workspaceCount = skills.filter((s) => s.source === "workspace").length;
  const systemCount = skills.filter((s) => s.source === "system").length;

  return (
    <div style={{ padding: "24px" }}>
      {/* Toast Notifications */}
      <div style={{ position: "fixed", top: "20px", right: "20px", zIndex: 9999, display: "flex", flexDirection: "column", gap: "8px" }}>
        {toasts.map((toast) => (
          <div
            key={toast.id}
            style={{
              padding: "12px 16px",
              borderRadius: "8px",
              backgroundColor: toast.type === "success" ? "#052e16" : "#1c0a0a",
              border: `1px solid ${toast.type === "success" ? "#16a34a" : "#dc2626"}`,
              color: toast.type === "success" ? "#4ade80" : "#f87171",
              fontSize: "13px",
              fontWeight: 500,
              maxWidth: "340px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              boxShadow: "0 4px 20px rgba(0,0,0,0.5)",
              animation: "fadeIn 0.2s ease",
            }}
          >
            {toast.type === "success" ? (
              <CheckCircle style={{ width: 16, height: 16, flexShrink: 0 }} />
            ) : (
              <AlertCircle style={{ width: 16, height: 16, flexShrink: 0 }} />
            )}
            {toast.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div style={{ marginBottom: "24px", display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <h1
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "24px",
              fontWeight: 700,
              letterSpacing: "-1px",
              color: "var(--text-primary)",
              marginBottom: "4px",
            }}
          >
            <Puzzle style={{ display: "inline", width: 24, height: 24, marginRight: 8, marginBottom: 3 }} />
            Gerenciador de Skills
          </h1>
          <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)" }}>
            Skills disponíveis no sistema OpenClaw • {installedCount} instalada{installedCount !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={fetchSkills}
          style={{
            display: "flex", alignItems: "center", gap: 6, padding: "6px 14px",
            backgroundColor: "var(--surface-elevated)", borderRadius: 6,
            border: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 13, cursor: "pointer",
          }}
        >
          <RefreshCw style={{ width: 14, height: 14 }} /> Atualizar
        </button>
      </div>

      {/* Stats */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <MetricCard icon={Puzzle} value={skills.length} label="Total de Skills" />
        <MetricCard icon={CheckCircle} value={installedCount} label="Instaladas" changeColor="positive" />
        <MetricCard icon={FolderOpen} value={workspaceCount} label="Skills Workspace" changeColor="positive" />
        <MetricCard icon={Package} value={systemCount} label="Skills Sistema" changeColor="secondary" />
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "24px", flexWrap: "wrap" }}>
        {/* Search */}
        <div style={{ position: "relative", flex: 1, minWidth: "240px" }}>
          <Search
            style={{
              position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)",
              width: "16px", height: "16px", color: "var(--text-muted)",
            }}
          />
          <input
            type="text"
            placeholder="Buscar skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%", paddingLeft: "40px", paddingRight: "16px",
              paddingTop: "12px", paddingBottom: "12px", borderRadius: "6px",
              backgroundColor: "var(--surface-elevated)", border: "1px solid var(--border)",
              color: "var(--text-primary)", fontFamily: "var(--font-body)", fontSize: "12px",
            }}
          />
        </div>

        {/* Source Filter */}
        <div style={{ display: "flex", gap: "8px" }}>
          {(["all", "workspace", "system"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilterSource(f)}
              style={{
                padding: "12px 16px", borderRadius: "6px", cursor: "pointer", transition: "all 150ms ease",
                backgroundColor: filterSource === f ? "var(--accent-soft)" : "var(--surface)",
                color: filterSource === f ? "var(--accent)" : "var(--text-secondary)",
                border: "1px solid var(--border)", fontFamily: "var(--font-body)", fontSize: "12px", fontWeight: 600,
              }}
            >
              {f === "all" ? `Todas (${skills.length})` : f === "workspace" ? `Workspace (${workspaceCount})` : `Sistema (${systemCount})`}
            </button>
          ))}
        </div>

        {/* Installed Filter */}
        <div style={{ display: "flex", gap: "8px" }}>
          {(["all", "installed", "notinstalled"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilterInstalled(f)}
              style={{
                padding: "12px 16px", borderRadius: "6px", cursor: "pointer", transition: "all 150ms ease",
                backgroundColor: filterInstalled === f ? "var(--accent-soft)" : "var(--surface)",
                color: filterInstalled === f ? "var(--accent)" : "var(--text-secondary)",
                border: "1px solid var(--border)", fontFamily: "var(--font-body)", fontSize: "12px", fontWeight: 600,
              }}
            >
              {f === "all" ? "Todas" : f === "installed" ? `✓ Instaladas (${installedCount})` : "Não instaladas"}
            </button>
          ))}
        </div>
      </div>

      {/* Skills List */}
      {filteredSkills.length === 0 ? (
        <div style={{ backgroundColor: "var(--surface)", borderRadius: "12px", padding: "48px", textAlign: "center" }}>
          <Puzzle style={{ width: "48px", height: "48px", color: "var(--text-muted)", margin: "0 auto 16px" }} />
          <p style={{ color: "var(--text-secondary)" }}>Nenhuma skill encontrada</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
          {/* Workspace Skills */}
          {workspaceSkills.length > 0 && (filterSource === "all" || filterSource === "workspace") && (
            <div>
              <SectionHeader label="SKILLS DO WORKSPACE" />
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "12px", marginTop: "16px" }}>
                {workspaceSkills.map((skill) => (
                  <SkillCard
                    key={skill.id}
                    skill={skill}
                    isLoading={loadingSkills.has(skill.id)}
                    onClick={() => setSelectedSkill(skill)}
                    onInstall={() => installSkill(skill)}
                    onUninstall={() => uninstallSkill(skill)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* System Skills */}
          {systemSkills.length > 0 && (filterSource === "all" || filterSource === "system") && (
            <div>
              <SectionHeader label="SKILLS DO SISTEMA" />
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "12px", marginTop: "16px" }}>
                {systemSkills.map((skill) => (
                  <SkillCard
                    key={skill.id}
                    skill={skill}
                    isLoading={loadingSkills.has(skill.id)}
                    onClick={() => setSelectedSkill(skill)}
                    onInstall={() => installSkill(skill)}
                    onUninstall={() => uninstallSkill(skill)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Detail Modal */}
      {selectedSkill && (
        <SkillDetailModal
          skill={selectedSkill}
          isLoading={loadingSkills.has(selectedSkill.id)}
          onClose={() => setSelectedSkill(null)}
          onInstall={() => installSkill(selectedSkill)}
          onUninstall={() => uninstallSkill(selectedSkill)}
        />
      )}
    </div>
  );
}

// Skill Card Component
function SkillCard({
  skill,
  isLoading,
  onClick,
  onInstall,
  onUninstall,
}: {
  skill: Skill;
  isLoading: boolean;
  onClick: () => void;
  onInstall: () => void;
  onUninstall: () => void;
}) {
  return (
    <div
      style={{
        backgroundColor: "var(--surface)",
        borderRadius: "8px",
        padding: "16px",
        border: skill.installed ? "1px solid var(--accent)" : "1px solid var(--border)",
        cursor: "pointer",
        transition: "all 150ms ease",
        position: "relative",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = "var(--surface-hover)";
        if (!skill.installed) e.currentTarget.style.borderColor = "var(--border-strong)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = "var(--surface)";
        e.currentTarget.style.borderColor = skill.installed ? "var(--accent)" : "var(--border)";
      }}
      onClick={onClick}
    >
      {/* Installed badge */}
      {skill.installed && (
        <div style={{
          position: "absolute", top: "10px", right: "10px",
          backgroundColor: "var(--accent)", color: "#000",
          fontSize: "9px", fontWeight: 700, padding: "2px 7px",
          borderRadius: "4px", letterSpacing: "0.5px", textTransform: "uppercase",
        }}>
          ✓ Instalada
        </div>
      )}

      {/* Skill Header */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", marginBottom: "12px", paddingRight: skill.installed ? "70px" : "0" }}>
        {skill.emoji && <span style={{ fontSize: "24px", flexShrink: 0 }}>{skill.emoji}</span>}
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontFamily: "var(--font-heading)", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
            {skill.name}
          </h3>
          <p style={{
            fontFamily: "var(--font-body)", fontSize: "12px", color: "var(--text-secondary)", lineHeight: "1.5",
            display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden",
          }}>
            {skill.description}
          </p>
        </div>
      </div>

      {/* Skill Footer */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "12px", borderTop: "1px solid var(--border)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap", flex: 1 }}>
          <div style={{
            backgroundColor: skill.source === "workspace" ? "var(--accent-soft)" : "var(--surface-elevated)",
            color: skill.source === "workspace" ? "var(--accent)" : "var(--text-muted)",
            padding: "3px 8px", borderRadius: "4px", fontSize: "9px", fontWeight: 700,
            letterSpacing: "1px", textTransform: "uppercase",
          }}>
            {skill.source === "workspace" ? "Workspace" : "Sistema"}
          </div>
          <span style={{ fontFamily: "var(--font-body)", fontSize: "10px", color: "var(--text-muted)" }}>
            {skill.fileCount} arquivo{skill.fileCount !== 1 ? "s" : ""}
          </span>
        </div>

        {/* Install/Uninstall Button */}
        <button
          onClick={(e) => { e.stopPropagation(); skill.installed ? onUninstall() : onInstall(); }}
          disabled={isLoading}
          style={{
            display: "flex", alignItems: "center", gap: "5px",
            padding: "5px 12px", borderRadius: "6px", fontSize: "11px", fontWeight: 600,
            cursor: isLoading ? "not-allowed" : "pointer",
            border: "none", transition: "all 150ms ease",
            backgroundColor: isLoading ? "var(--surface-elevated)" : skill.installed ? "#1c0a0a" : "var(--accent)",
            color: isLoading ? "var(--text-muted)" : skill.installed ? "#f87171" : "#000",
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          {isLoading ? (
            <RefreshCw style={{ width: 12, height: 12 }} className="animate-spin" />
          ) : skill.installed ? (
            <Trash2 style={{ width: 12, height: 12 }} />
          ) : (
            <Download style={{ width: 12, height: 12 }} />
          )}
          {isLoading ? "..." : skill.installed ? "Remover" : "Instalar"}
        </button>
      </div>
    </div>
  );
}

// Skill Detail Modal Component
function SkillDetailModal({
  skill,
  isLoading,
  onClose,
  onInstall,
  onUninstall,
}: {
  skill: Skill;
  isLoading: boolean;
  onClose: () => void;
  onInstall: () => void;
  onUninstall: () => void;
}) {
  return (
    <div
      style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0, 0, 0, 0.8)", display: "flex", alignItems: "center", justifyContent: "center", padding: "24px", zIndex: 100 }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "var(--surface)", borderRadius: "12px", maxWidth: "800px", width: "100%",
          maxHeight: "90vh", overflow: "auto", border: skill.installed ? "1px solid var(--accent)" : "1px solid var(--border)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{ padding: "24px", borderBottom: "1px solid var(--border)", position: "relative" }}>
          <button
            onClick={onClose}
            style={{ position: "absolute", top: "24px", right: "24px", padding: "8px", borderRadius: "6px", backgroundColor: "transparent", border: "none", cursor: "pointer", color: "var(--text-muted)" }}
          >
            <X style={{ width: "20px", height: "20px" }} />
          </button>

          <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", paddingRight: "40px" }}>
            {skill.emoji && <span style={{ fontSize: "48px" }}>{skill.emoji}</span>}
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px", flexWrap: "wrap" }}>
                <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "24px", fontWeight: 700, color: "var(--text-primary)" }}>
                  {skill.name}
                </h2>
                {skill.installed && (
                  <div style={{
                    backgroundColor: "var(--accent)", color: "#000",
                    fontSize: "10px", fontWeight: 700, padding: "3px 10px",
                    borderRadius: "4px", letterSpacing: "0.5px",
                  }}>
                    ✓ INSTALADA
                  </div>
                )}
              </div>
              <p style={{ fontFamily: "var(--font-body)", fontSize: "14px", color: "var(--text-secondary)", marginBottom: "16px" }}>
                {skill.description}
              </p>

              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
                <div style={{
                  backgroundColor: skill.source === "workspace" ? "var(--accent-soft)" : "var(--surface-elevated)",
                  color: skill.source === "workspace" ? "var(--accent)" : "var(--text-muted)",
                  padding: "4px 10px", borderRadius: "4px", fontSize: "10px", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase",
                }}>
                  {skill.source === "workspace" ? "Workspace" : "Sistema"}
                </div>
                <div style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", padding: "4px 10px", borderRadius: "4px", fontSize: "11px", fontWeight: 600 }}>
                  {skill.fileCount} arquivo{skill.fileCount !== 1 ? "s" : ""}
                </div>
                {skill.agents && skill.agents.map((agent) => (
                  <div key={agent} style={{ backgroundColor: "var(--surface-elevated)", color: "var(--text-secondary)", padding: "3px 10px", borderRadius: "4px", fontFamily: "var(--font-mono)", fontSize: "11px", fontWeight: 600, border: "1px solid var(--border)" }}>
                    @{agent}
                  </div>
                ))}
                {skill.homepage && (
                  <a href={skill.homepage} target="_blank" rel="noopener noreferrer"
                    style={{ display: "inline-flex", alignItems: "center", gap: "4px", color: "var(--accent)", fontSize: "12px", fontWeight: 600, textDecoration: "none" }}>
                    Homepage <ExternalLink style={{ width: "12px", height: "12px" }} />
                  </a>
                )}
              </div>

              {/* Install/Uninstall Button */}
              <div style={{ marginTop: "16px" }}>
                <button
                  onClick={() => skill.installed ? onUninstall() : onInstall()}
                  disabled={isLoading}
                  style={{
                    display: "inline-flex", alignItems: "center", gap: "8px",
                    padding: "10px 24px", borderRadius: "8px", fontSize: "14px", fontWeight: 700,
                    cursor: isLoading ? "not-allowed" : "pointer", border: "none", transition: "all 150ms ease",
                    backgroundColor: isLoading ? "var(--surface-elevated)" : skill.installed ? "#1c0a0a" : "var(--accent)",
                    color: isLoading ? "var(--text-muted)" : skill.installed ? "#f87171" : "#000",
                    opacity: isLoading ? 0.7 : 1,
                  }}
                >
                  {isLoading ? (
                    <RefreshCw style={{ width: 16, height: 16 }} className="animate-spin" />
                  ) : skill.installed ? (
                    <Trash2 style={{ width: 16, height: 16 }} />
                  ) : (
                    <Download style={{ width: 16, height: 16 }} />
                  )}
                  {isLoading ? "Processando..." : skill.installed ? "Desinstalar Skill" : "Instalar Skill"}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: "24px" }}>
          <h3 style={{ fontFamily: "var(--font-heading)", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "12px" }}>
            Arquivos ({skill.files.length})
          </h3>
          <div style={{ backgroundColor: "var(--bg)", borderRadius: "8px", padding: "16px", maxHeight: "400px", overflow: "auto" }}>
            {skill.files.map((file) => (
              <div key={file} style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)", padding: "4px 0", display: "flex", alignItems: "center", gap: "8px" }}>
                <FileText style={{ width: "14px", height: "14px", color: "var(--text-muted)", flexShrink: 0 }} />
                {file}
              </div>
            ))}
            {skill.files.length === 0 && (
              <p style={{ color: "var(--text-muted)", fontSize: "12px" }}>Nenhum arquivo encontrado.</p>
            )}
          </div>

          {/* Location */}
          <div style={{ marginTop: "16px" }}>
            <h3 style={{ fontFamily: "var(--font-heading)", fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "8px" }}>
              Localização
            </h3>
            <div style={{ backgroundColor: "var(--bg)", borderRadius: "8px", padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--text-muted)", wordBreak: "break-all" }}>
              {skill.location}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
