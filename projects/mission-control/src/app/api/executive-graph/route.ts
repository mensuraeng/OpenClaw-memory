import { NextRequest, NextResponse } from "next/server";
import { getExecutiveGraph } from "@/lib/executive-graph";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  try {
    const graph = getExecutiveGraph();
    const { searchParams } = new URL(request.url);
    const mode = searchParams.get("mode");
    const q = searchParams.get("q")?.trim().toLowerCase() || "";

    if (mode === "documents") {
      const documents = q
        ? graph.documents.filter((doc) => `${doc.title} ${doc.path} ${doc.category} ${doc.company}`.toLowerCase().includes(q))
        : graph.documents;
      return NextResponse.json({ generatedAt: graph.generatedAt, roots: graph.roots, documents, guardrails: graph.guardrails });
    }

    if (q) {
      const projects = graph.projects.filter((project) =>
        `${project.name} ${project.domain} ${project.summary} ${project.nextStep}`.toLowerCase().includes(q)
      );
      return NextResponse.json({ ...graph, projects });
    }

    return NextResponse.json(graph);
  } catch (error) {
    console.error("Failed to build executive graph:", error);
    return NextResponse.json({ error: "Failed to build executive graph" }, { status: 500 });
  }
}
