'use client';

import { useMemo, useState } from 'react';
import {
  Globe,
  ShieldCheck,
  UserCircle2,
  Building2,
  Link2,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  ChevronDown,
  KeyRound,
  Workflow,
  Send,
} from 'lucide-react';

type CompanyKey = 'pessoal' | 'mensura' | 'mia' | 'pcs';

type SocialAsset = {
  key: CompanyKey;
  label: string;
  type: 'pessoal' | 'empresa';
  mode: string;
  owner: string;
  status: string;
  color: string;
  urnStatus: string;
  publishingStatus: string;
  oauthStatus: string;
  notes: string[];
};

const app = {
  name: 'OpenClaw - Mensura',
  provider: 'LinkedIn Developers',
  clientId: '7731w27uswscu1',
  appType: 'Standalone app',
  shareRequested: true,
  callbackStatus: 'configured' as 'pending' | 'configured',
  redirectUri: 'https://mc.mensuraengenharia.com.br/api/linkedin/callback',
};

const assets: SocialAsset[] = [
  {
    key: 'pessoal',
    label: 'Perfil pessoal do Alê',
    type: 'pessoal',
    mode: 'assistido',
    owner: 'Alexandre',
    status: 'autenticado via OAuth',
    color: '#60a5fa',
    urnStatus: 'OIDC sub validado: JYAsCudAAE',
    publishingStatus: 'OAuth validado; author de publicação ainda depende da trilha final da API LinkedIn',
    oauthStatus: 'conectado',
    notes: [
      'Canal pessoal deve continuar com aprovação explícita para postagens sensíveis.',
      'OAuth 3-legged concluído com openid + profile + w_member_social.',
      'userinfo validado com nome Alexandre Aguiar; endpoint legado /v2/me segue indisponível com o escopo atual.',
    ],
  },
  {
    key: 'mensura',
    label: 'Página MENSURA',
    type: 'empresa',
    mode: 'governado',
    owner: 'Marketing',
    status: 'aguardando URN / publicação',
    color: '#22c55e',
    urnStatus: 'organization URN pendente',
    publishingStatus: 'depende de Share on LinkedIn aprovado',
    oauthStatus: 'pendente de callback + autorização do admin',
    notes: [
      'Usar esta página como piloto principal da operação institucional.',
      'Governança funcional: marketing. Segurança e integração: Flávia/main.',
      'Depois do OAuth, validar se o perfil autenticado é admin da página.',
    ],
  },
  {
    key: 'mia',
    label: 'Página MIA',
    type: 'empresa',
    mode: 'governado',
    owner: 'Marketing',
    status: 'aguardando URN / publicação',
    color: '#f59e0b',
    urnStatus: 'organization URN pendente',
    publishingStatus: 'depende de Share on LinkedIn aprovado',
    oauthStatus: 'pendente de autorização via app central',
    notes: [
      'A operação MIA deve manter voz premium e revisão final quando necessário.',
      'Pode compartilhar a mesma app central do LinkedIn.',
      'Precisa confirmar admin da página no perfil autenticado.',
    ],
  },
  {
    key: 'pcs',
    label: 'Página PCS',
    type: 'empresa',
    mode: 'governado',
    owner: 'Marketing',
    status: 'aguardando URN / publicação',
    color: '#a78bfa',
    urnStatus: 'organization URN pendente',
    publishingStatus: 'depende de Share on LinkedIn aprovado',
    oauthStatus: 'pendente de autorização via app central',
    notes: [
      'PCS precisa manter posicionamento institucional técnico-institucional.',
      'Mesmo fluxo técnico, mas com governança editorial separada por marca.',
      'Depois da conexão, mapear URN e rotina de publicação dedicada.',
    ],
  },
];

const blockers = [
  { label: 'App LinkedIn criada', done: true },
  { label: 'Client ID obtido', done: true },
  { label: 'Solicitação de Share on LinkedIn enviada', done: app.shareRequested },
  { label: 'Definir e configurar Redirect URI no Auth', done: true },
  { label: 'Completar OAuth 3-legged', done: true },
  { label: 'Mapear URNs do perfil pessoal e páginas MENSURA, MIA e PCS', done: false },
];

export default function SocialPage() {
  const [selected, setSelected] = useState<CompanyKey>('mensura');
  const [expanded, setExpanded] = useState<Record<CompanyKey, boolean>>({
    pessoal: false,
    mensura: true,
    mia: false,
    pcs: false,
  });

  const readyPercent = useMemo(() => {
    let done = 0;
    if (app.clientId) done += 1;
    if (app.shareRequested) done += 1;
    if (app.callbackStatus === 'configured') done += 1;
    return Math.round((done / 3) * 100);
  }, []);

  const current = assets.find((asset) => asset.key === selected) || assets[0];

  const toggle = (key: CompanyKey) => {
    setSelected(key);
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <Globe size={28} style={{ color: '#60a5fa' }} />
        <div>
          <h1 style={{ color: '#fff', fontSize: 28, fontWeight: 800, margin: 0 }}>Redes Sociais</h1>
          <p style={{ color: 'rgba(255,255,255,0.5)', marginTop: 6, fontSize: 14 }}>
            Hub interativo de LinkedIn por empresa e perfil pessoal dentro do Mission Control.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: 16, marginBottom: 16 }}>
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
            <Info label="Redirect URI" value={app.redirectUri} mono />
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

      <div style={{ display: 'grid', gridTemplateColumns: '0.95fr 1.35fr', gap: 16, marginBottom: 16 }}>
        <section style={card}>
          <div style={titleRow}>
            <Building2 size={18} style={{ color: '#f59e0b' }} />
            <span style={title}>Empresas e perfil</span>
          </div>

          <div style={{ display: 'grid', gap: 10 }}>
            {assets.map((asset) => {
              const isSelected = selected === asset.key;
              const isExpanded = expanded[asset.key];
              return (
                <div
                  key={asset.key}
                  style={{
                    borderRadius: 14,
                    background: isSelected ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.03)',
                    border: isSelected ? `1px solid ${asset.color}` : '1px solid rgba(255,255,255,0.08)',
                    overflow: 'hidden',
                  }}
                >
                  <button
                    onClick={() => toggle(asset.key)}
                    style={{
                      width: '100%',
                      background: 'transparent',
                      border: 'none',
                      padding: '14px 16px',
                      color: '#fff',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 10,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, textAlign: 'left' }}>
                      {asset.type === 'pessoal' ? <UserCircle2 size={18} color={asset.color} /> : <Building2 size={18} color={asset.color} />}
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 14 }}>{asset.label}</div>
                        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>{asset.status}</div>
                      </div>
                    </div>
                    {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  </button>

                  {isExpanded && (
                    <div style={{ padding: '0 16px 14px 16px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ display: 'grid', gap: 6, marginTop: 12, fontSize: 12, color: 'rgba(255,255,255,0.65)' }}>
                        <div><strong style={{ color: '#fff' }}>Modo:</strong> {asset.mode}</div>
                        <div><strong style={{ color: '#fff' }}>Owner:</strong> {asset.owner}</div>
                        <div><strong style={{ color: '#fff' }}>OAuth:</strong> {asset.oauthStatus}</div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>

        <section style={card}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, marginBottom: 16 }}>
            <div style={titleRow}>
              {current.type === 'pessoal' ? <UserCircle2 size={18} color={current.color} /> : <Building2 size={18} color={current.color} />}
              <span style={title}>{current.label}</span>
            </div>
            <span style={{
              padding: '6px 10px',
              borderRadius: 999,
              background: 'rgba(255,255,255,0.06)',
              color: current.color,
              fontSize: 12,
              fontWeight: 800,
            }}>
              {current.mode}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <DetailCard icon={<KeyRound size={16} color={current.color} />} label="OAuth" value={current.oauthStatus} />
            <DetailCard icon={<Workflow size={16} color={current.color} />} label="URN" value={current.urnStatus} />
            <DetailCard icon={<Send size={16} color={current.color} />} label="Publicação" value={current.publishingStatus} />
            <DetailCard icon={<ShieldCheck size={16} color={current.color} />} label="Owner" value={current.owner} />
          </div>

          <div style={{
            padding: 16,
            borderRadius: 14,
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
            marginBottom: 14,
          }}>
            <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, marginBottom: 8 }}>Status atual</div>
            <div style={{ color: '#fff', fontSize: 15, fontWeight: 700 }}>{current.status}</div>
          </div>

          <div style={{
            padding: 16,
            borderRadius: 14,
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
          }}>
            <div style={{ color: 'rgba(255,255,255,0.45)', fontSize: 12, marginBottom: 10 }}>Notas operacionais</div>
            <ul style={{ margin: 0, paddingLeft: 18, color: 'rgba(255,255,255,0.75)', lineHeight: 1.8, fontSize: 14 }}>
              {current.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      <section style={card}>
        <div style={titleRow}>
          <AlertTriangle size={18} style={{ color: '#ef4444' }} />
          <span style={title}>Próximos passos bloqueantes</span>
        </div>

        <div style={{ display: 'grid', gap: 10 }}>
          {blockers.map((item) => (
            <Step key={item.label} done={item.done}>{item.label}</Step>
          ))}
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

function DetailCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div style={{
      padding: 14,
      borderRadius: 12,
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.08)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        {icon}
        <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>{label}</span>
      </div>
      <div style={{ color: '#fff', fontSize: 13, lineHeight: 1.5 }}>{value}</div>
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
