import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

const OPENCLAW_DIR = process.env.OPENCLAW_DIR || "/root/.openclaw";
const SYSTEM_SKILLS_PATH = "/usr/lib/node_modules/openclaw/skills";
const CONFIGURED_PATH = path.join(process.cwd(), "data", "configured-skills.json");

interface SkillInfo {
  id: string;
  name: string;
  description: string;
  location: string;
  source: "workspace" | "system";
  homepage?: string;
  emoji?: string;
  fileCount: number;
  files: string[];
  agents: string[];
  installed: boolean;
}

function parseFrontMatter(content: string) {
  const m = content.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!m) return { name: "", description: "", homepage: "", emoji: "" };
  const yaml = m[1];
  const get = (key: string) => {
    const r = yaml.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
    return r ? r[1].trim().replace(/^["']|["']$/g, "") : "";
  };
  const emojiMatch = yaml.match(/"emoji":\s*"([^"]+)"/);
  return { name: get("name"), description: get("description"), homepage: get("homepage"), emoji: emojiMatch?.[1] || "" };
}

function getInstalledIds(): Set<string> {
  try {
    const cfg = JSON.parse(fs.readFileSync(CONFIGURED_PATH, "utf-8"));
    return new Set((cfg.skills || []).map((s: {name: string}) => s.name));
  } catch { return new Set(); }
}

function scanSkillDir(dir: string, source: "system" | "workspace", installedIds: Set<string>, agents: string[] = []): SkillInfo[] {
  const skills: SkillInfo[] = [];
  if (!fs.existsSync(dir)) return skills;
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(dir, entry.name);
      const skillMd = path.join(skillPath, "SKILL.md");
      if (!fs.existsSync(skillMd)) continue;
      const content = fs.readFileSync(skillMd, "utf-8");
      const { name, description, homepage, emoji } = parseFrontMatter(content);
      const files = fs.readdirSync(skillPath).filter(f => !f.startsWith("."));
      skills.push({
        id: entry.name,
        name: name || entry.name,
        description: description || content.split("\n").find(l => l.trim() && !l.startsWith("#") && !l.startsWith("---")) || "",
        location: skillPath,
        source,
        homepage: homepage || undefined,
        emoji: emoji || undefined,
        fileCount: files.length,
        files,
        agents,
        installed: installedIds.has(entry.name),
      });
    }
  } catch {}
  return skills;
}

export async function GET() {
  const installed = getInstalledIds();
  const allSkills: Map<string, SkillInfo> = new Map();

  // System skills
  const systemSkills = scanSkillDir(SYSTEM_SKILLS_PATH, "system", installed);
  for (const s of systemSkills) allSkills.set(s.id, s);

  // Workspace skills (main + all agents)
  try {
    const dirs = fs.readdirSync(OPENCLAW_DIR, { withFileTypes: true });
    for (const d of dirs) {
      if (!d.isDirectory()) continue;
      const agentId = d.name === "workspace" ? "main" : d.name.startsWith("workspace-") ? d.name.replace("workspace-", "") : null;
      if (!agentId) continue;
      const skillsDir = path.join(OPENCLAW_DIR, d.name, "skills");
      const wsSkills = scanSkillDir(skillsDir, "workspace", installed, [agentId]);
      for (const s of wsSkills) {
        if (allSkills.has(s.id)) {
          const existing = allSkills.get(s.id)!;
          if (!existing.agents.includes(agentId)) existing.agents.push(agentId);
        } else {
          allSkills.set(s.id, s);
        }
      }
    }
  } catch {}

  const skills = Array.from(allSkills.values()).sort((a, b) => {
    if (a.installed !== b.installed) return a.installed ? -1 : 1;
    if (a.source !== b.source) return a.source === "workspace" ? -1 : 1;
    return a.name.localeCompare(b.name);
  });

  return NextResponse.json({ skills, total: skills.length, installed: installed.size });
}

// POST: install a skill (add to configured-skills.json + openclaw skill install)
export async function POST(request: Request) {
  try {
    const { skillId, location } = await request.json();
    if (!skillId || typeof skillId !== "string" || !/^[a-z0-9_-]+$/.test(skillId)) {
      return NextResponse.json({ error: "Invalid skill ID" }, { status: 400 });
    }
    let cfg = { skills: [] as { name: string; location: string }[] };
    try { cfg = JSON.parse(fs.readFileSync(CONFIGURED_PATH, "utf-8")); } catch {}
    if (!cfg.skills.find(s => s.name === skillId)) {
      cfg.skills.push({ name: skillId, location: location || "system" });
      fs.writeFileSync(CONFIGURED_PATH, JSON.stringify(cfg, null, 2));
    }
    return NextResponse.json({ success: true, message: `Skill ${skillId} instalada` });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

// DELETE: uninstall a skill
export async function DELETE(request: Request) {
  try {
    const { skillId } = await request.json();
    let cfg = { skills: [] as { name: string; location: string }[] };
    try { cfg = JSON.parse(fs.readFileSync(CONFIGURED_PATH, "utf-8")); } catch {}
    cfg.skills = cfg.skills.filter(s => s.name !== skillId);
    fs.writeFileSync(CONFIGURED_PATH, JSON.stringify(cfg, null, 2));
    return NextResponse.json({ success: true });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

