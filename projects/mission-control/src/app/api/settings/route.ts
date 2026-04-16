import { NextRequest, NextResponse } from 'next/server';
import { readFileSync, writeFileSync } from 'fs';

export const dynamic = 'force-dynamic';

const CONFIG_PATH = (process.env.OPENCLAW_DIR || '/root/.openclaw') + '/openclaw.json';

export async function GET() {
  try {
    const config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    const agents = (config.agents?.list || []).map((a: Record<string, unknown>) => ({
      id: a.id,
      name: a.name,
      model: a.model,
      allowAgents: a.allowAgents || [],
    }));
    return NextResponse.json({
      defaultModel: config.agents?.defaults?.model?.primary || '',
      fallbacks: config.agents?.defaults?.model?.fallbacks || [],
      agents,
    });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));

    // Update default model
    if (body.defaultModel) {
      if (!config.agents) config.agents = {};
      if (!config.agents.defaults) config.agents.defaults = {};
      if (!config.agents.defaults.model) config.agents.defaults.model = {};
      config.agents.defaults.model.primary = body.defaultModel;
    }

    // Update per-agent settings
    if (Array.isArray(body.agents)) {
      for (const update of body.agents) {
        const agent = (config.agents?.list || []).find((a: Record<string, unknown>) => a.id === update.id);
        if (!agent) continue;
        if (update.name !== undefined) agent.name = update.name;
        if (update.model !== undefined) agent.model = update.model;
      }
    }

    config.meta = config.meta || {};
    config.meta.lastTouchedAt = new Date().toISOString();
    writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));

    return NextResponse.json({ ok: true, message: 'Configurações salvas no OpenClaw.' });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
