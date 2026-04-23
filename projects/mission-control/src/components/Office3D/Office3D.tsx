'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sky, Environment } from '@react-three/drei';
import { Suspense, useState, useEffect, useCallback } from 'react';
import { Vector3 } from 'three';
import { AGENTS } from './agentsConfig';
import type { AgentState } from './agentsConfig';
import AgentDesk from './AgentDesk';
import Floor from './Floor';
import { BRANDING } from '@/config/branding';
import Walls from './Walls';
import Lights from './Lights';
import AgentPanel from './AgentPanel';
import FileCabinet from './FileCabinet';
import Whiteboard from './Whiteboard';
import CoffeeMachine from './CoffeeMachine';
import PlantPot from './PlantPot';
import WallClock from './WallClock';
import FirstPersonControls from './FirstPersonControls';
import MovingAvatar from './MovingAvatar';

interface ApiAgent {
  id: string;
  name: string;
  emoji: string;
  color: string;
  model: string;
  status: 'online' | 'offline' | 'unknown';
  lastActivity?: string;
  activeSessions: number;
}

// Mapeia status da API para status 3D
function mapStatus(agent: ApiAgent): AgentState['status'] {
  if (agent.status === 'offline') return 'idle';
  if (agent.activeSessions > 0) return 'working';
  if (agent.status === 'online') return 'thinking';
  return 'idle';
}

// Formata "tarefa atual" baseado no último acesso
function formatTask(agent: ApiAgent): string | undefined {
  if (agent.activeSessions > 0) return `${agent.activeSessions} sessão${agent.activeSessions > 1 ? 'ões' : ''} ativa${agent.activeSessions > 1 ? 's' : ''}`;
  if (!agent.lastActivity) return undefined;
  const mins = Math.floor((Date.now() - new Date(agent.lastActivity).getTime()) / 60000);
  if (mins < 60) return `Ativo há ${mins}min`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `Ativo há ${hrs}h`;
  return `Ativo há ${Math.floor(hrs / 24)}d`;
}

export default function Office3D() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [interactionModal, setInteractionModal] = useState<string | null>(null);
  const [controlMode, setControlMode] = useState<'orbit' | 'fps'>('orbit');
  const [avatarPositions, setAvatarPositions] = useState<Map<string, Vector3>>(new Map());
  const [agentStates, setAgentStates] = useState<Record<string, AgentState>>({});
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Buscar dados reais dos agentes
  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch('/api/agents');
      const data = await res.json();
      const agents: ApiAgent[] = data.agents || [];

      const states: Record<string, AgentState> = {};
      for (const agent of agents) {
        states[agent.id] = {
          id: agent.id,
          status: mapStatus(agent),
          currentTask: formatTask(agent),
          model: agent.model?.split('/').pop() || 'gpt',
          tokensPerHour: agent.activeSessions * 5000,
          tasksInQueue: agent.activeSessions,
          uptime: undefined,
        };
      }
      setAgentStates(states);
      setLastUpdate(new Date());
    } catch (e) {
      console.error('[Office3D] Erro ao buscar agentes:', e);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 15000);
    return () => clearInterval(interval);
  }, [fetchAgents]);

  // Estado padrão para agentes sem dados
  const getState = (id: string): AgentState =>
    agentStates[id] || { id, status: 'idle', model: 'gpt' };

  const obstacles = [
    ...AGENTS.map(agent => ({
      position: new Vector3(agent.position[0], 0, agent.position[2]),
      radius: 1.5,
    })),
    { position: new Vector3(-10, 0, -7), radius: 0.8 },
    { position: new Vector3(0, 0, -10), radius: 1.5 },
    { position: new Vector3(10, 0, -7), radius: 0.6 },
    { position: new Vector3(-10, 0, 8), radius: 0.5 },
    { position: new Vector3(10, 0, 8), radius: 0.5 },
  ];

  const onlineCount = Object.values(agentStates).filter(s => s.status !== 'idle').length;
  const workingCount = Object.values(agentStates).filter(s => s.status === 'working').length;

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: '#0a0a1a' }}>

      {/* ── HUD overlay ─────────────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, zIndex: 10,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '10px 20px',
        background: 'linear-gradient(to bottom, rgba(0,0,0,0.8), transparent)',
        pointerEvents: 'none',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 20 }}>🏗️</span>
          <div>
            <div style={{ color: '#fff', fontSize: 14, fontWeight: 700, letterSpacing: '-0.5px' }}>
              {BRANDING.companyName} — Office Virtual
            </div>
            <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11 }}>
              {AGENTS.length} agentes •{' '}
              <span style={{ color: '#4ade80' }}>{onlineCount} ativos</span> •{' '}
              <span style={{ color: '#f59e0b' }}>{workingCount} trabalhando</span>
              {lastUpdate && (
                <span style={{ marginLeft: 8 }}>
                  · Atualizado {new Date(lastUpdate).toLocaleTimeString('pt-BR')}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Controles */}
        <div style={{ display: 'flex', gap: 8, pointerEvents: 'all' }}>
          <button
            onClick={() => setControlMode(controlMode === 'orbit' ? 'fps' : 'orbit')}
            style={{
              padding: '5px 12px', borderRadius: 6, fontSize: 11, fontWeight: 600,
              backgroundColor: 'rgba(0,0,0,0.7)', border: '1px solid rgba(255,255,255,0.2)',
              color: '#fff', cursor: 'pointer',
            }}
          >
            {controlMode === 'orbit' ? '🎮 Modo FPS' : '🌐 Modo Órbita'}
          </button>
          <button
            onClick={fetchAgents}
            style={{
              padding: '5px 12px', borderRadius: 6, fontSize: 11, fontWeight: 600,
              backgroundColor: 'rgba(0,0,0,0.7)', border: '1px solid rgba(255,255,255,0.2)',
              color: '#fff', cursor: 'pointer',
            }}
          >
            🔄 Atualizar
          </button>
          <a
            href="/agents"
            style={{
              padding: '5px 12px', borderRadius: 6, fontSize: 11, fontWeight: 600,
              backgroundColor: 'rgba(0,0,0,0.7)', border: '1px solid rgba(255,255,255,0.2)',
              color: '#fff', textDecoration: 'none',
            }}
          >
            ← Voltar
          </a>
        </div>
      </div>

      {/* ── Status bar inferior ──────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, zIndex: 10,
        padding: '8px 20px',
        background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
        display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap',
        pointerEvents: 'none',
      }}>
        {AGENTS.map(agent => {
          const state = getState(agent.id);
          const dotColor = state.status === 'working' ? '#4ade80'
            : state.status === 'thinking' ? '#60a5fa'
            : state.status === 'error' ? '#f87171' : '#6b7280';
          return (
            <div key={agent.id} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: dotColor }} />
              <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10 }}>
                {agent.emoji} {agent.name}
              </span>
            </div>
          );
        })}
      </div>

      {/* ── Modal de interação ───────────────────────────────────────────────── */}
      {interactionModal && (
        <div style={{
          position: 'absolute', inset: 0, zIndex: 50,
          backgroundColor: 'rgba(0,0,0,0.85)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
          onClick={() => setInteractionModal(null)}
        >
          <div style={{
            backgroundColor: '#1a1a2e', borderRadius: 16, padding: 32,
            border: '1px solid rgba(255,255,255,0.1)', maxWidth: 480, width: '90%',
          }}
            onClick={e => e.stopPropagation()}
          >
            <h2 style={{ color: '#fff', fontSize: 20, fontWeight: 700, marginBottom: 8 }}>
              {interactionModal === 'memory' ? '🗄️ Arquivo de Memória'
                : interactionModal === 'roadmap' ? '📋 Quadro de Tarefas'
                : '☕ Máquina de Café'}
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: 14, marginBottom: 24 }}>
              {interactionModal === 'memory' ? `Arquivos de memória dos agentes ${BRANDING.companyName}`
                : interactionModal === 'roadmap' ? 'Próximos marcos e tarefas da equipe'
                : 'Pausa para café... os agentes agradecem!'}
            </p>
            <a
              href={interactionModal === 'memory' ? '/memory' : interactionModal === 'roadmap' ? '/workflows' : '#'}
              style={{
                display: 'inline-block', padding: '8px 20px', borderRadius: 8,
                backgroundColor: 'var(--accent, #ff6b35)', color: '#000',
                textDecoration: 'none', fontWeight: 700, fontSize: 13,
              }}
              onClick={() => setInteractionModal(null)}
            >
              {interactionModal === 'energy' ? 'Fechar ☕' : 'Abrir →'}
            </a>
          </div>
        </div>
      )}

      {/* ── Canvas 3D ───────────────────────────────────────────────────────── */}
      <Canvas
        camera={{ position: [0, 10, 16], fov: 55 }}
        shadows
        gl={{ antialias: true, alpha: false }}
        style={{ width: '100%', height: '100%' }}
      >
        <Suspense fallback={
          <mesh>
            <boxGeometry args={[2, 2, 2]} />
            <meshStandardMaterial color="#ff6b35" />
          </mesh>
        }>
          <Lights />
          <Sky sunPosition={[100, 20, 100]} />
          <Environment preset="city" />
          <Floor />
          <Walls />

          {/* Mesas dos agentes com dados reais */}
          {AGENTS.map((agent) => (
            <AgentDesk
              key={agent.id}
              agent={agent}
              state={getState(agent.id)}
              onClick={() => setSelectedAgent(agent.id)}
              isSelected={selectedAgent === agent.id}
            />
          ))}

          {/* Avatares móveis */}
          {AGENTS.map((agent) => (
            <MovingAvatar
              key={`avatar-${agent.id}`}
              agent={agent}
              state={getState(agent.id)}
              officeBounds={{ minX: -10, maxX: 10, minZ: -8, maxZ: 9 }}
              obstacles={obstacles}
              otherAvatarPositions={avatarPositions}
              onPositionUpdate={(id, pos) =>
                setAvatarPositions(prev => new Map(prev).set(id, pos))
              }
            />
          ))}

          {/* Mobiliário interativo */}
          <FileCabinet position={[-10, 0, -7]} onClick={() => setInteractionModal('memory')} />
          <Whiteboard position={[0, 0, -10]} rotation={[0, 0, 0]} onClick={() => setInteractionModal('roadmap')} />
          <CoffeeMachine position={[10, 0.8, -7]} onClick={() => setInteractionModal('energy')} />

          {/* Decoração */}
          <PlantPot position={[-10, 0, 8]} size="large" />
          <PlantPot position={[10, 0, 8]} size="medium" />
          <PlantPot position={[-11, 0, 0]} size="small" />
          <PlantPot position={[11, 0, 0]} size="small" />
          <WallClock position={[0, 2.5, -10.4]} rotation={[0, 0, 0]} />

          {/* Controles de câmera */}
          {controlMode === 'orbit' ? (
            <OrbitControls
              enableDamping
              dampingFactor={0.05}
              minDistance={6}
              maxDistance={35}
              maxPolarAngle={Math.PI / 2.2}
              target={[0, 0, 0]}
            />
          ) : (
            <FirstPersonControls moveSpeed={5} />
          )}
        </Suspense>
      </Canvas>

      {/* ── Painel lateral do agente selecionado ─────────────────────────────── */}
      {selectedAgent && (() => {
        const agentCfg = AGENTS.find(a => a.id === selectedAgent);
        if (!agentCfg) return null;
        return (
          <AgentPanel
            agent={agentCfg}
            state={getState(selectedAgent)}
            onClose={() => setSelectedAgent(null)}
          />
        );
      })()}
    </div>
  );
}
