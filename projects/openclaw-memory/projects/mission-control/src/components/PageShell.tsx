import { ReactNode } from "react";

export function PageShell({ children }: { children: ReactNode }) {
  return <div className="p-4 md:p-8">{children}</div>;
}

export function PageHeader({
  title,
  subtitle,
  icon,
  actions,
}: {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-4 md:mb-6 flex items-start justify-between gap-4">
      <div>
        <h1
          className="text-2xl md:text-3xl font-bold mb-1"
          style={{
            fontFamily: "var(--font-heading)",
            color: "var(--text-primary)",
            letterSpacing: "-1.5px",
          }}
        >
          {icon}
          {title}
        </h1>
        {subtitle ? (
          <p style={{ color: "var(--text-secondary)", fontSize: "14px" }}>{subtitle}</p>
        ) : null}
      </div>
      {actions ? <div>{actions}</div> : null}
    </div>
  );
}

export function SectionCard({
  children,
  title,
  icon,
  right,
}: {
  children: ReactNode;
  title?: string;
  icon?: ReactNode;
  right?: ReactNode;
}) {
  return (
    <section
      className="rounded-xl overflow-hidden"
      style={{ backgroundColor: "var(--card)", border: "1px solid var(--border)" }}
    >
      {title ? (
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: "1px solid var(--border)" }}>
          <div className="flex items-center gap-3">
            <div className="accent-line" />
            <h2
              className="text-base font-semibold"
              style={{ fontFamily: "var(--font-heading)", color: "var(--text-primary)" }}
            >
              {icon}
              {title}
            </h2>
          </div>
          {right}
        </div>
      ) : null}
      <div className="p-4 md:p-5">{children}</div>
    </section>
  );
}
