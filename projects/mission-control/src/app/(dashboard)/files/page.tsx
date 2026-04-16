'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Folder, File, FolderOpen, ChevronRight, ChevronDown,
  Plus, Trash2, Save, RefreshCw, FolderPlus, Download,
  Edit3, X, Check, Terminal, AlertTriangle
} from 'lucide-react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  size?: number;
  modified?: string;
}

interface Workspace {
  id: string;
  name: string;
  emoji: string;
  path: string;
  agentName?: string;
}

function formatSize(bytes?: number): string {
  if (!bytes) return '';
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function FileTreeNode({
  node, depth, onSelect, selected, onDelete, expanded, onToggle
}: {
  node: FileNode;
  depth: number;
  onSelect: (node: FileNode) => void;
  selected: string | null;
  onDelete: (node: FileNode) => void;
  expanded: Set<string>;
  onToggle: (path: string) => void;
}) {
  const isExpanded = expanded.has(node.path);
  const isSelected = selected === node.path;

  return (
    <div>
      <div
        onClick={() => {
          if (node.type === 'directory') onToggle(node.path);
          else onSelect(node);
        }}
        style={{
          display: 'flex', alignItems: 'center', gap: 6,
          padding: `5px ${8 + depth * 16}px 5px ${8 + depth * 16}px`,
          cursor: 'pointer', borderRadius: 6,
          backgroundColor: isSelected ? 'rgba(255,107,53,0.15)' : 'transparent',
          color: isSelected ? '#ff6b35' : 'rgba(255,255,255,0.8)',
        }}
        onMouseEnter={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = 'rgba(255,255,255,0.05)'; }}
        onMouseLeave={e => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.backgroundColor = 'transparent'; }}
      >
        {node.type === 'directory'
          ? isExpanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />
          : <span style={{ width: 13 }} />
        }
        {node.type === 'directory'
          ? isExpanded ? <FolderOpen size={14} style={{ color: '#f59e0b', flexShrink: 0 }} /> : <Folder size={14} style={{ color: '#f59e0b', flexShrink: 0 }} />
          : <File size={14} style={{ color: 'rgba(255,255,255,0.4)', flexShrink: 0 }} />
        }
        <span style={{ fontSize: 13, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {node.name}
        </span>
        {node.size !== undefined && (
          <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>{formatSize(node.size)}</span>
        )}
        <button
          onClick={e => { e.stopPropagation(); onDelete(node); }}
          style={{ padding: 3, borderRadius: 4, opacity: 0, background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}
          onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '1'; }}
          onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.opacity = '0'; }}
        >
          <Trash2 size={11} />
        </button>
      </div>
      {node.type === 'directory' && isExpanded && node.children?.map(child => (
        <FileTreeNode
          key={child.path} node={child} depth={depth + 1}
          onSelect={onSelect} selected={selected}
          onDelete={onDelete} expanded={expanded} onToggle={onToggle}
        />
      ))}
    </div>
  );
}

export default function FilesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<string>('workspace');
  const [tree, setTree] = useState<FileNode[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState('');
  const [editContent, setEditContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);
  const [newFileName, setNewFileName] = useState('');
  const [showNewFile, setShowNewFile] = useState(false);
  const [newDirName, setNewDirName] = useState('');
  const [showNewDir, setShowNewDir] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  const showToast = (msg: string, type: 'ok' | 'err' = 'ok') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3500);
  };

  const loadWorkspaces = async () => {
    try {
      const res = await fetch('/api/files/workspaces');
      const data = await res.json();
      setWorkspaces(data.workspaces || []);
    } catch { /* ignore */ }
  };

  const loadTree = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/files?workspace=${activeWorkspace}`);
      const data = await res.json();
      setTree(Array.isArray(data) ? data : []);
    } catch { setTree([]); }
    setLoading(false);
  }, [activeWorkspace]);

  useEffect(() => { loadWorkspaces(); }, []);
  useEffect(() => {
    setSelectedFile(null);
    setFileContent('');
    setIsEditing(false);
    loadTree();
  }, [activeWorkspace, loadTree]);

  const loadFile = async (node: FileNode) => {
    setSelectedFile(node.path);
    setIsEditing(false);
    try {
      const res = await fetch(`/api/files?workspace=${activeWorkspace}&path=${encodeURIComponent(node.path)}`);
      const data = await res.json();
      setFileContent(data.content ?? '');
      setEditContent(data.content ?? '');
    } catch { setFileContent('Erro ao carregar arquivo.'); }
  };

  const saveFile = async () => {
    if (!selectedFile) return;
    setSaving(true);
    try {
      const res = await fetch('/api/files/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: activeWorkspace, path: selectedFile, content: editContent }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Erro ao salvar');
      setFileContent(editContent);
      setIsEditing(false);
      showToast('✅ Arquivo salvo com sucesso!');
    } catch (e) {
      showToast(`❌ ${e}`, 'err');
    }
    setSaving(false);
  };

  const createFile = async () => {
    if (!newFileName.trim()) return;
    try {
      const res = await fetch('/api/files/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: activeWorkspace, path: newFileName.trim(), content: '' }),
      });
      if (!res.ok) throw new Error((await res.json()).error);
      showToast('✅ Arquivo criado!');
      setNewFileName('');
      setShowNewFile(false);
      loadTree();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
  };

  const createDir = async () => {
    if (!newDirName.trim()) return;
    try {
      const res = await fetch('/api/files/mkdir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: activeWorkspace, path: newDirName.trim() }),
      });
      if (!res.ok) throw new Error((await res.json()).error);
      showToast('✅ Pasta criada!');
      setNewDirName('');
      setShowNewDir(false);
      loadTree();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
  };

  const deleteNode = async (node: FileNode) => {
    if (!confirm(`Deletar "${node.name}"?`)) return;
    setDeleting(node.path);
    try {
      const res = await fetch('/api/files/write', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workspace: activeWorkspace, path: node.path }),
      });
      if (!res.ok) throw new Error((await res.json()).error);
      showToast('🗑️ Deletado!');
      if (selectedFile === node.path) { setSelectedFile(null); setFileContent(''); }
      loadTree();
    } catch (e) { showToast(`❌ ${e}`, 'err'); }
    setDeleting(null);
  };

  const toggleExpanded = (p: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(p) ? next.delete(p) : next.add(p);
      return next;
    });
  };

  const downloadFile = () => {
    if (!selectedFile) return;
    const blob = new Blob([fileContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = selectedFile.split('/').pop() || 'file.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const S = {
    page: { padding: '24px', height: '100%', display: 'flex', flexDirection: 'column' as const, gap: 16 },
    header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' as const, gap: 12 },
    title: { color: '#fff', fontSize: 24, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10, margin: 0 },
    tabs: { display: 'flex', gap: 8, flexWrap: 'wrap' as const },
    tab: (active: boolean) => ({
      padding: '6px 14px', borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: 'pointer',
      backgroundColor: active ? 'rgba(255,107,53,0.2)' : 'rgba(255,255,255,0.05)',
      border: active ? '1px solid rgba(255,107,53,0.5)' : '1px solid rgba(255,255,255,0.1)',
      color: active ? '#ff6b35' : 'rgba(255,255,255,0.7)',
    }),
    body: { display: 'grid', gridTemplateColumns: '280px 1fr', gap: 12, flex: 1, minHeight: 0 },
    panel: { backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column' as const },
    panelHeader: { padding: '10px 14px', borderBottom: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
    panelBody: { flex: 1, overflow: 'auto' as const, padding: '8px 4px' },
    btn: (color = '#ff6b35') => ({
      padding: '5px 10px', borderRadius: 7, fontSize: 12, fontWeight: 600, cursor: 'pointer',
      backgroundColor: `${color}20`, border: `1px solid ${color}50`, color,
      display: 'flex', alignItems: 'center', gap: 5,
    }),
    editor: {
      width: '100%', flex: 1, backgroundColor: 'rgba(0,0,0,0.3)',
      border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8,
      color: '#e2e8f0', fontSize: 13, fontFamily: 'monospace',
      padding: 16, resize: 'none' as const, outline: 'none',
    },
    viewer: {
      flex: 1, overflow: 'auto' as const, padding: 16,
      fontFamily: 'monospace', fontSize: 13, color: '#e2e8f0',
      whiteSpace: 'pre-wrap' as const, wordBreak: 'break-word' as const,
    },
  };

  return (
    <div style={S.page}>
      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 70, right: 20, zIndex: 9999,
          backgroundColor: toast.type === 'ok' ? 'rgba(16,185,129,0.95)' : 'rgba(239,68,68,0.95)',
          color: '#fff', padding: '10px 18px', borderRadius: 10, fontWeight: 600, fontSize: 14,
          boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        }}>
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div style={S.header}>
        <h1 style={S.title}>
          <Folder size={24} style={{ color: '#f59e0b' }} />
          Arquivos
        </h1>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <button style={S.btn('#6b7280')} onClick={loadTree}>
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Atualizar
          </button>
          <button style={S.btn('#22c55e')} onClick={() => setShowNewFile(v => !v)}>
            <Plus size={13} /> Novo Arquivo
          </button>
          <button style={S.btn('#3b82f6')} onClick={() => setShowNewDir(v => !v)}>
            <FolderPlus size={13} /> Nova Pasta
          </button>
        </div>
      </div>

      {/* Workspace tabs */}
      <div style={S.tabs}>
        {workspaces.map(ws => (
          <button key={ws.id} onClick={() => setActiveWorkspace(ws.id)} style={S.tab(activeWorkspace === ws.id)}>
            {ws.emoji} {ws.name} {ws.agentName && <span style={{ opacity: 0.6 }}>({ws.agentName})</span>}
          </button>
        ))}
      </div>

      {/* New file/dir inputs */}
      {showNewFile && (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            value={newFileName}
            onChange={e => setNewFileName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && createFile()}
            placeholder="nome-do-arquivo.md"
            autoFocus
            style={{
              flex: 1, maxWidth: 320, padding: '7px 12px', borderRadius: 8, fontSize: 13,
              backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#fff', outline: 'none',
            }}
          />
          <button style={S.btn('#22c55e')} onClick={createFile}><Check size={13} /> Criar</button>
          <button style={S.btn('#6b7280')} onClick={() => setShowNewFile(false)}><X size={13} /></button>
        </div>
      )}
      {showNewDir && (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            value={newDirName}
            onChange={e => setNewDirName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && createDir()}
            placeholder="nome-da-pasta"
            autoFocus
            style={{
              flex: 1, maxWidth: 320, padding: '7px 12px', borderRadius: 8, fontSize: 13,
              backgroundColor: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#fff', outline: 'none',
            }}
          />
          <button style={S.btn('#3b82f6')} onClick={createDir}><Check size={13} /> Criar</button>
          <button style={S.btn('#6b7280')} onClick={() => setShowNewDir(false)}><X size={13} /></button>
        </div>
      )}

      {/* Main body */}
      <div style={S.body}>
        {/* File tree */}
        <div style={S.panel}>
          <div style={S.panelHeader}>
            <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12, fontWeight: 600, letterSpacing: '0.5px' }}>
              ARQUIVOS
            </span>
            {loading && <RefreshCw size={12} className="animate-spin" style={{ color: '#ff6b35' }} />}
          </div>
          <div style={S.panelBody}>
            {tree.length === 0 && !loading && (
              <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 13, padding: '20px', textAlign: 'center' }}>
                Workspace vazio
              </div>
            )}
            {tree.map(node => (
              <FileTreeNode
                key={node.path} node={node} depth={0}
                onSelect={loadFile} selected={selectedFile}
                onDelete={deleteNode} expanded={expanded} onToggle={toggleExpanded}
              />
            ))}
          </div>
        </div>

        {/* File editor/viewer */}
        <div style={{ ...S.panel, display: 'flex', flexDirection: 'column' }}>
          {selectedFile ? (
            <>
              <div style={S.panelHeader}>
                <span style={{ color: '#fff', fontSize: 13, fontWeight: 600, fontFamily: 'monospace' }}>
                  {selectedFile}
                </span>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button style={S.btn('#6b7280')} onClick={downloadFile}>
                    <Download size={12} /> Baixar
                  </button>
                  {isEditing ? (
                    <>
                      <button style={S.btn('#22c55e')} onClick={saveFile} disabled={saving}>
                        {saving ? <RefreshCw size={12} className="animate-spin" /> : <Save size={12} />}
                        {saving ? 'Salvando...' : 'Salvar'}
                      </button>
                      <button style={S.btn('#6b7280')} onClick={() => { setIsEditing(false); setEditContent(fileContent); }}>
                        <X size={12} /> Cancelar
                      </button>
                    </>
                  ) : (
                    <button style={S.btn('#ff6b35')} onClick={() => setIsEditing(true)}>
                      <Edit3 size={12} /> Editar
                    </button>
                  )}
                </div>
              </div>
              {isEditing ? (
                <textarea
                  value={editContent}
                  onChange={e => setEditContent(e.target.value)}
                  style={{ ...S.editor, flex: 1 }}
                />
              ) : (
                <div style={S.viewer}>{fileContent}</div>
              )}
            </>
          ) : (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 12 }}>
              <File size={40} style={{ color: 'rgba(255,255,255,0.1)' }} />
              <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 14 }}>
                Selecione um arquivo para visualizar ou editar
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
