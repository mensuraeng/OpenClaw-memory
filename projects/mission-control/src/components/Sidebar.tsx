"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Activity,
  Timer,
  Brain,
  Search,
  BarChart3,
  FileBarChart,
  Puzzle,
  FolderOpen,
  BookOpen,
  Terminal,
  LogOut,
  User,
  Menu,
  X,
  Users,
  Gamepad2,
  Workflow,
  Zap,
  Server,
  GitFork,
  SquareTerminal,
  History,
  Globe,
  CheckSquare,
  ShieldCheck,
  Cpu,
} from "lucide-react";
import { getAgentDisplayName, BRANDING } from "@/config/branding";

const navItems = [
  { href: "/", label: "Painel", icon: LayoutDashboard },
  { href: "/agents", label: "Agentes", icon: Users },
  { href: "/ops", label: "Ops 360", icon: ShieldCheck },
  { href: "/openclaw", label: "OpenClaw", icon: Cpu },
  { href: "/office", label: "Office", icon: Gamepad2, highlight: true },
  { href: "/actions", label: "Quick Actions", icon: Zap },
  { href: "/system", label: "Sistema", icon: Server },
  { href: "/logs", label: "Live Logs", icon: Terminal },
  { href: "/terminal", label: "Terminal", icon: SquareTerminal },
  { href: "/git", label: "Git", icon: GitFork },
  { href: "/social", label: "Redes Sociais", icon: Globe },
  { href: "/workflows", label: "Workflows", icon: Workflow },
  { href: "/activity", label: "Atividade", icon: Activity },
  { href: "/projects", label: "Projetos", icon: FolderOpen },
  { href: "/docs", label: "Docs", icon: BookOpen },
  { href: "/tasks", label: "Tasks", icon: CheckSquare },
  { href: "/memory", label: "Memória", icon: Brain },
  { href: "/files", label: "Arquivos", icon: FolderOpen },
  { href: "/cron", label: "Cron Jobs", icon: Timer },
  { href: "/sessions", label: "Sessões", icon: History },
  { href: "/search", label: "Buscar", icon: Search },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/reports", label: "Reports", icon: FileBarChart },
  { href: "/skills", label: "Skills", icon: Puzzle },
  { href: "/about", label: getAgentDisplayName(), icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isDesktopHovered, setIsDesktopHovered] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 1024;
      setIsMobile(mobile);
      if (!mobile) {
        setIsOpen(false);
      }
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  useEffect(() => {
    if (isMobile) {
      setIsOpen(false);
    }
  }, [pathname, isMobile]);

  useEffect(() => {
    document.body.style.overflow = isOpen && isMobile ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen, isMobile]);

  useEffect(() => {
    const main = document.querySelector(".mc-main");
    if (!main) return;
    if (!isMobile && isDesktopHovered) {
      main.classList.add("sidebar-hovered");
    } else {
      main.classList.remove("sidebar-hovered");
    }
  }, [isDesktopHovered, isMobile]);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  };

  return (
    <>
      {isMobile && (
        <button
          onClick={() => setIsOpen(true)}
          className="mc-mobile-menu-button"
          aria-label="Abrir menu"
        >
          <Menu size={20} />
        </button>
      )}

      {isMobile && isOpen && (
        <div
          className="mc-mobile-overlay"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`mc-sidebar ${isMobile && isOpen ? "mobile-open" : ""}`}
        onMouseEnter={() => {
          if (!isMobile) setIsDesktopHovered(true);
        }}
        onMouseLeave={() => {
          if (!isMobile) setIsDesktopHovered(false);
        }}
      >
        <div className="mc-sidebar-inner">
          <div className="mc-sidebar-brand">
            <div className="mc-brand-mark">
              <Terminal size={18} />
            </div>

            <div className="mc-brand-copy">
              <p className="mc-brand-kicker">{BRANDING.companyName}</p>
              <div className="mc-brand-title">
                Mission <em>Control</em>
              </div>
            </div>

            {isMobile && (
              <button
                onClick={() => setIsOpen(false)}
                aria-label="Fechar menu"
                style={{
                  marginLeft: "auto",
                  background: "transparent",
                  border: "none",
                  color: "rgba(249,249,247,0.82)",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                }}
              >
                <X size={20} />
              </button>
            )}
          </div>

          <nav className="mc-nav">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                pathname === item.href ||
                (item.href !== "/" && pathname?.startsWith(item.href));

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`mc-nav-item ${isActive ? "active" : ""} ${item.highlight ? "highlight" : ""}`}
                >
                  <Icon className="mc-nav-icon" />
                  <span className="mc-nav-label">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="mc-sidebar-footer">
            <button
              onClick={handleLogout}
              className="mc-nav-item"
              style={{
                width: "100%",
                background: "transparent",
                cursor: "pointer",
              }}
            >
              <LogOut className="mc-nav-icon" />
              <span className="mc-nav-label">Sair</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
