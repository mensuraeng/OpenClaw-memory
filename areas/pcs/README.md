# Mapa — Área PCS Engenharia

_Atualizado: 2026-04-25_

## Propósito
Obras públicas, licitações, contratos técnicos e capacidade operacional real. Foco em engenharia integradora com governança e previsibilidade.

## Tese central
"Engenharia integradora com foco em obras públicas e licitações, combinando planejamento, controle e execução com governança, previsibilidade e capacidade operacional real."

## Estrutura de arquivos

### `areas/pcs/` (operação viva)
| Path | Conteúdo |
|---|---|
| `comercial/base-comercial.md` | Base comercial — proposta de valor, argumentos |
| `contexto/` | Identidade, tese, linguagem institucional |
| `restauro/` | Frente PCS Restauro |
| `operacao/` | Checklists, contratos, governança |

### `memory/projects/pcs/` (contexto permanente)
| Arquivo | Conteúdo |
|---|---|
| `dados-institucionais.md` | Dados institucionais PCS |
| `cadastro-base-pcs.md` | Cadastro base para propostas/contratos |
| `ficha-cadastral.md` | Ficha cadastral completa |
| `identidade-visual.md` | Identidade visual PCS |
| `contratos-e-lastro.md` | Contratos ativos e lastro operacional |
| `estado-operacional.md` | Estado operacional atual |
| `obras-e-centros-de-custo-sienge.md` | Base PCS↔Sienge (fonte primária) |
| `teatro-suzano-orcamento-mapeamento.md` | Teatro Suzano — orçamento |
| `teatro-suzano-pedidos-compra.md` | Teatro Suzano — pedidos de compra |
| `documentos-index.md` | Índice de documentos |

## Agente responsável
`pcs` — canal: Grupo PCS, tópico 1
Skill: `pcs-autopilot`

## Obras em andamento
| Obra | Status | Referência |
|---|---|---|
| Teatro Suzano | Em mapeamento | `teatro-suzano-orcamento-mapeamento.md` |
| SPTrans (CPA) | Aguardando 1ª OS | `contratos-e-lastro.md` seção 4 |

## Integrações
- **Sienge:** obras e centros de custo — `obras-e-centros-de-custo-sienge.md`
- **M365:** tenant configurado + 14 modelos de contrato indexados no agente jurídico

## Pendências PCS
- [ ] Classificar base Sienge: obra executável / centro de custo admin / ambíguo
- [ ] Calibrar triagem inbox antes de desligar dry-run
- [ ] SPTrans: criar alertas D+10 e D+30 após 1ª OS
- [ ] Descobrir rota financeira Teatro Suzano (obra `1354`) no Sienge
