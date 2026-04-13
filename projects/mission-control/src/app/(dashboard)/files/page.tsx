import { FolderLock, ShieldAlert } from 'lucide-react';

export default function FilesPage() {
  return (
    <div className="p-4 md:p-8">
      <div
        style={{
          backgroundColor: 'var(--card)',
          border: '1px solid var(--border)',
          borderRadius: '1rem',
          padding: '2rem',
          maxWidth: '900px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <div
            style={{
              width: '3rem',
              height: '3rem',
              borderRadius: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(245,158,11,0.12)',
              color: 'var(--warning, #f59e0b)',
            }}
          >
            <FolderLock className="w-6 h-6" />
          </div>
          <div>
            <h1 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Navegação de arquivos desativada
            </h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              O navegador genérico de arquivos saiu do escopo da v1.
            </p>
          </div>
        </div>

        <div style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          <p>Motivo: leitura ampla, download e edição de arquivos aumentam demais a superfície de exposição.</p>
          <p>Direção: substituir isso por visões dedicadas, com paths e conteúdos explicitamente permitidos.</p>
        </div>

        <div
          style={{
            marginTop: '1.25rem',
            padding: '1rem',
            borderRadius: '0.75rem',
            background: 'var(--card-elevated)',
            border: '1px solid var(--border)',
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'flex-start',
          }}
        >
          <ShieldAlert className="w-5 h-5" style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <strong style={{ color: 'var(--text-primary)' }}>Próximo formato</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Entradas futuras devem usar leitores específicos para memória, docs operacionais e painéis de status, sem browser arbitrário.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

              {/* File list */}
              <div style={{ flex: 1, padding: "0" }}>
                <FileBrowser
                  workspace={selectedWorkspace}
                  path={currentPath}
                  onNavigate={setCurrentPath}
                  viewMode={viewMode}
                />
              </div>
            </>
          ) : (
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--text-muted)",
                fontSize: "14px",
              }}
            >
              Selecciona un workspace para explorar sus archivos
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
