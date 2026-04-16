import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { id } = await request.json();
    if (!id || typeof id !== "string" || !/^[a-z0-9-]+$/i.test(id)) {
      return NextResponse.json({ error: "ID inválido" }, { status: 400 });
    }
    const { stdout, stderr } = await execAsync(`openclaw cron run ${id} 2>&1`, { timeout: 30000 });
    return NextResponse.json({ success: true, output: stdout + stderr });
  } catch (error) {
    return NextResponse.json({ error: String(error), success: false }, { status: 500 });
  }
}

