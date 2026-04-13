# Patch List Técnica V1

_Data: 2026-04-13_

## Objetivo  
Detalhar as modificações necessárias para o fork v1 do Mission Control, visando a segurança e a minimização de riscos.

### Tabela de Rotas Perigosas
| Área | Arquivo | Risco | Ação v1 | Observação |
| --- | --- | --- | --- | --- |
| API | src/... | terminal remoto | remover | fora do escopo da v1 |

### Tabela de Refactors Obrigatórios
| Componente | Problema | Refactor Necessário | Prioridade |
| --- | --- | --- | --- |
|  |

### Tabela de Adapters
| Adapter | Fonte | Saída Esperada | Sanitização |
| --- | --- | --- | --- |
| agents | openclaw config/runtime | lista de agentes | ocultar campos sensíveis |

### Tabela de Bloqueios Explícitos
| Item | Status v1 |
| --- | --- |
| terminal web | bloqueado |
| file edit genérico | bloqueado |  
