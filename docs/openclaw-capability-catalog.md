# Catálogo de Capacidades OpenClaw

_Data: 2026-04-20_
_Status: draft operacional_

## Objetivo

Manter um mapa vivo do que o ecossistema OpenClaw realmente sabe fazer, com status de maturidade, evidência e risco.

## Escala de status

- **desenhada**: ideia/arquitetura existe
- **testada**: houve teste pontual
- **validada em runtime**: prova real recente em contexto operacional
- **robusta**: já aguentou uso repetido com limite conhecido
- **produção**: pronta para uso recorrente com risco controlado

---

## Capacidades

| Capacidade | Dono principal | Status atual | Evidência / base | Riscos / gaps | Próximo passo |
|---|---|---|---|---|---|
| Delegação `main` → agentes especializados | main | validada em runtime | decisão permanente exige validação real de runtime; arquitetura especializada já adotada | precisa prova recorrente, não só pontual | manter smoke tests e evidência recente |
| Memória documental por empresa | main + agentes de frente | validada em runtime | estrutura criada em `memory/projects/mensura`, `mia`, `pcs`, `pessoal-ale` e já povoada | ainda precisa ficar mais acionável | conectar melhor à execução |
| Consulta prioritária da memória própria por agente | main / mia / mensura / pcs / finance | desenhada a testada | regra já formalizada em decisões | falta medir aderência real em uso recorrente | transformar em checklist de comportamento |
| Inbox PCS, triagem leve | pcs | testada | dry-run com Graph e recalibração das regras | ainda há risco de falso positivo; live bloqueada | novo dry-run pós-calibração |
| LinkedIn pessoal | main | validada em runtime | decisão permanente marca pessoal como operacional | sensível a token/storage | endurecer gestão de credencial |
| LinkedIn institucional / páginas | main | bloqueada / desenhada | bloqueio confirmado por Community API approval | depende de terceiro | aguardar aprovação |
| Integração PCS ↔ Sienge (basic auth) | pcs | validada em runtime | decisão permanente fixa basic auth como trilha real atual | ainda precisa ampliar para casos de uso de diário/RDO | fechar trilha operacional fim a fim |
| Mission Control / dashboard | main | desenhada a parcialmente testada | há PRD, checklist técnico, matriz de permissões, hardening plan | mais forte em intenção do que em runtime validado | endurecer v1 read-only e validar acesso seguro |
| Segundo cérebro GitHub | main | desenhada a parcialmente testada | direção oficial definida; memória e docs evoluindo | falta pipeline 10/10 de captura → consolidação → promoção | operacionalizar ciclo completo |
| Skill audit OpenClaw | main | testada | spec criada, script funcional, rodada real em 53 skills | ainda precisa segunda calibração | reduzir falso positivo e decidir adoção oficial |
| Transcrição de áudio institucional | main / mia | bloqueada | necessidade identificada; tentativa falhou sem `OPENAI_API_KEY` | dependência de credencial/runtime | destravar trilha funcional |
| WhatsApp no Mission Control | main | parcialmente testada | stack estabilizada, pairing ainda pendente | bloqueio humano no QR scan | concluir pairing real |
| Crons operacionais | main | validada em runtime | há regras permanentes para criação/auditoria/modelo | ainda precisam governança contínua e prova por capacidade | manter catálogo + revisão periódica |

---

## Leitura executiva

### Forte hoje
- especialização por agentes
- memória documental estruturada
- trilha pessoal do LinkedIn validada
- integração PCS ↔ Sienge com auth real definida
- skill audit já funcional como protótipo

### Médio / em amadurecimento
- Mission Control
- segundo cérebro GitHub
- triagem inbox PCS
- uso recorrente da memória como input automático

### Bloqueado
- LinkedIn institucional
- transcrição operacional de áudio
- pairing final do WhatsApp no dashboard

---

## Regras de manutenção

- não marcar como `produção` sem prova proporcional
- rebaixar status quando a prova ficar velha ou a dependência mudar
- manter evidência concreta, não só narrativa
- registrar fallback e limitação principal de cada capacidade
