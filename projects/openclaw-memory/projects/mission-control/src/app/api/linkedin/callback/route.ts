import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state');
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  const html = `<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>LinkedIn Callback | Mission Control</title>
    <style>
      body { font-family: Inter, Arial, sans-serif; background: #0b0f17; color: #fff; margin: 0; padding: 32px; }
      .card { max-width: 760px; margin: 0 auto; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; }
      .ok { color: #86efac; }
      .warn { color: #fbbf24; }
      .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; word-break: break-all; }
      h1 { margin-top: 0; }
      code { background: rgba(255,255,255,0.08); padding: 2px 6px; border-radius: 6px; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Callback do LinkedIn recebida</h1>
      ${error ? `<p class="warn"><strong>Erro:</strong> ${escapeHtml(error)}${errorDescription ? ` - ${escapeHtml(errorDescription)}` : ''}</p>` : ''}
      ${code ? `<p class="ok">Authorization code recebido com sucesso.</p>` : '<p class="warn">Nenhum authorization code foi encontrado na URL.</p>'}
      <p>Use estas informações para concluir a troca do código por token no backend.</p>
      <p><strong>code</strong></p>
      <div class="mono">${code ? escapeHtml(code) : 'ausente'}</div>
      <p><strong>state</strong></p>
      <div class="mono">${state ? escapeHtml(state) : 'ausente'}</div>
      <p style="margin-top:24px; opacity:0.8;">Esta rota é provisória para o bootstrap local do OAuth do LinkedIn dentro do Mission Control.</p>
    </div>
  </body>
</html>`;

  return new NextResponse(html, {
    status: 200,
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
}

function escapeHtml(value: string) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
