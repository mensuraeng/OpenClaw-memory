"use client";

import { Dock, TopBar, StatusBar } from "@/components/TenacitOS";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="tenacios-shell" style={{ minHeight: "100vh" }}>
      <Dock />
      <TopBar />
      
      <main
        style={{
          marginLeft: "68px",
          marginTop: "48px",
          marginBottom: "32px",
          minHeight: "calc(100vh - 48px - 32px)",
          padding: "24px",
          maxWidth: "1600px",
        }}
      >
        {children}
      </main>

      <StatusBar />
    </div>
  );
}
