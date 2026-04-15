'use client';

import { useMemo } from 'react';
import { Globe, ShieldCheck, UserCircle2, Building2, Link2, CheckCircle2, AlertTriangle } from 'lucide-react';

const app = {
  name: 'OpenClaw - Mensura',
  provider: 'LinkedIn Developers',
  clientId: '7731w27uswscu1',
  appType: 'Standalone app',
  shareRequested: true,
  callbackStatus: 'pending',
};

const assets = [
  { name: 'Perfil pessoal do Alê', mode: 'assistido', owner: 'Alexandre', status: 'aguardando conexão' },
  { name: 'Página MENSURA', mode: 'governado', owner: 'Marketing', status: 'aguardando URN / publicação' },
  { name: 'Página MIA', mode: 'governado', owner: 'Marketing', status: 'aguardando URN / publicação' },
  { name: 'Página PCS', mode: 'governado', owner: 'Marketing', status: 'aguardando URN / publicação' },
];

export default function SocialPage() {
  const readyPercent = useMemo(() => {
    let done = 0;
    if (app.clientId) done += 1;
    if (app.shareRequested) done += 1;
    if (app.callbackStatus === 'configured') done += 1;
    return Math.round((done / 3) * 100);
  }, []);

  return (
    <div style={{ padding: '24px', maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <Globe size={28} style={{ color: '#60a5fa' }} />
        <div>
          <h1 style={{ color: '#fff', fontSize: 28, fontWeight: 800, margin: 0 }}>Redes Sociais</h1>
          <p style={{ color: 'rgba(255,255,255,0.5)', marginTop: 6, fontSize: 14 }}>
            Hub operacional de LinkedIn dentro do Mission Control.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16, marginBottom: 16 }}>
        <section style={card}>
          <div style={titleRow}>
            <Link2 size={18} style={{ color: '#22c55e' }} />
            <span style={title}>Integração LinkedIn</span>
          </div>

          <div style={kvGrid}>
            <Info label="App" value={app.name} />
            <Info label="Provider" value={app.provider} />
            <Info label="Client ID" value={app.clientId} mono />
            <Info label="Tipo" value={app.appType} />
          </div>

          <div style={{ marginTop: 18, display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <Badge ok>App criada</Badge>
            <Badge ok={app.shareRequested}>{app.shareRequested ? 'Share on LinkedIn solicitado' : 'Share on LinkedIn pendente'}</Badge>
            <Badge ok={app.callbackStatus === 'configured'}>
              {app.callbackStatus === 'configured' ? 'Callback configurada' : 'Callback pendente'}
            </Badge>
          </div>
        </section>

        <section style={card}>
          <div style={titleRow}>
            <ShieldCheck size={18} style={{ color: '#a78bfa' }} />
            <span style={title}>Governança</span>
          </div>

          <ul style={{ margin: 0, paddingLeft: 18, color: 'rgba(255,255,255,0.7)', lineHeight: 1.7, fontSize: 14 }}>
            <li>Marketing é owner funcional da frente</li>
            <li>Flávia/main mantém OAuth, credenciais e automação</li>
            <li>Perfil pessoal do Alê continua assistido</li>
            <li>Páginas institucionais seguem operação governada por marca</li>
          </ul>

          <div style={{ marginTop: 18 }}>
            <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, marginBottom: 6 }}>Prontidão atual</div>
            <div style={{ height: 10, borderRadius: 999, background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
              <div style={{ width: `${readyPercent}%`, height: '100%', background: 'linear-gradient(90deg,#22c55e,#60a5fa)' }} />
            </div>
            <div style={{ color: '#fff', fontSize: 13, marginTop: 8 }}>{readyPercent}% concluído</div>
          </div>
        </section>
      </div>

      <section style={{ ...card, marginBottom: 16 }}>
        <div style={titleRow}>
          <Building2 size={18} style={{ color: '#f59e0b' }} />
          <span style={title}>Ativos conectáveis</span>
        </div>

        <div style={{ display: 'grid', gap: 10 }}>
          {assets.map((asset) => (
            <div key={asset.name} style={{
              display: 'grid',
              gridTemplateColumns: '1.5fr 0.8fr 0.8fr 1fr',
              gap: 12,
              padding: '14px 16px',
              borderRadius: 12,
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              alignItems: 'center',
            }}>
              <div style={{ color: '#fff', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                {asset.name.includes('Perfil') ? <UserCircle2 size={18} /> : <Building2 size={18} />}
                {asset.name}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 13 }}>{asset.mode}</div>
              <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: 13 }}>{asset.owner}</div>
              <div style={{ color: '#fbbf24', fontSize: 13 }}>{asset.status}</div>
            </div>
          ))}
        </div>
      </section>

      <section style={card}>
        <div style={titleRow}>
          <AlertTriangle size={18} style={{ color: '#ef4444' }} />
          <span style={title}>Próximos passos bloqueantes</span>
        </div>

        <div style={{ display: 'grid', gap: 10 }}>
          <Step done>App LinkedIn criada</Step>
          <Step done>Client ID obtido</Step>
          <Step done={app.shareRequested}>Solicitação de Share on LinkedIn enviada</Step>
          <Step done={false}>Definir e configurar Redirect URI no Auth</Step>
          <Step done={false}>Completar OAuth 3-legged</Step>
          <Step done={false}>Mapear URNs do perfil pessoal e páginas MENSURA, MIA e PCS</Step>
        </div>
      </section>
    </div>
  );
}

function Info({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, marginBottom: 6 }}>{label}</div>
      <div style={{ color: '#fff', fontSize: 14, fontFamily: mono ? 'monospace' : 'inherit' }}>{value}</div>
    </div>
  );
}

function Badge({ children, ok = true }: { children: React.ReactNode; ok?: boolean }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      padding: '8px 10px',
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 700,
      background: ok ? 'rgba(34,197,94,0.14)' : 'rgba(245,158,11,0.14)',
      color: ok ? '#86efac' : '#fcd34d',
      border: ok ? '1px solid rgba(34,197,94,0.25)' : '1px solid rgba(245,158,11,0.25)',
    }}>
      {ok ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
      {children}
    </span>
  );
}

function Step({ children, done = false }: { children: React.ReactNode; done?: boolean }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      padding: '12px 14px',
      borderRadius: 10,
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.08)',
      color: done ? '#86efac' : 'rgba(255,255,255,0.75)',
      fontSize: 14,
    }}>
      {done ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} color="#f59e0b" />}
      {children}
    </div>
  );
}

const card: React.CSSProperties = {
  background: 'rgba(255,255,255,0.03)',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: 16,
  padding: 20,
};

const titleRow: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  marginBottom: 16,
};

const title: React.CSSProperties = {
  color: '#fff',
  fontSize: 16,
  fontWeight: 800,
};

const kvGrid: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 16,
};
