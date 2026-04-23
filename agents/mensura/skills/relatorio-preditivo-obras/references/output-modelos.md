# Modelos de Saída — Relatório Preditivo de Obras

> Estrutura dos 3 tipos de relatório. Usar como esqueleto — preencher com dados reais, nunca com dados inventados.

---

## MODELO A — RELATÓRIO COMPLETO (1ª análise)

```
RELATÓRIO DE OBRA Nº 001
[NOME DA OBRA] | [CLIENTE / GERENCIADORA / CONSTRUTORA]
PMO: MENSURA Engenharia | Data: [DATA] | Data-base: [DATA-BASE]
CONFIDENCIAL — Sob NDA
────────────────────────────────────────────────────────────

NÍVEL DE CONFIANÇA: [Alto/Médio/Baixo]
Justificativa: [1 linha se Médio ou Baixo]

1. SUMÁRIO EXECUTIVO
[Situação geral — 1 frase direta]
Avanço físico: [X]% | Tempo consumido: [Y]% | Desvio: [+/-Z dias]
Atraso projetado: [N dias]
Top riscos: (1) [risco] | (2) [risco] | (3) [risco]
Recomendação: [ação principal em 1 linha]

2. DADOS GERAIS
Início: [data] | Término baseline: [data] | Término projetado: [data]
Duração total: [N dias] | Dias decorridos: [N] | Dias restantes: [N]
Atividades: [total] total | [concluídas] concluídas | [em andamento] em andamento | [não iniciadas] não iniciadas

3. INDICADORES EVM
SPI: [valor] | BEI: [valor] | CPLI: [valor]
EAC (otimista): [data] | EAC (realista): [data] | EAC (pessimista): [data]
Custo indireto acumulado por atraso: R$ [valor] (se disponível)

4. DIAGNÓSTICO POR FRENTE
| Frente | Status | Desvio | Causa | Impacto |
|--------|--------|--------|-------|---------|
| [frente] | 🔴/🟡/🟢 | [dias] | [causa raiz] | [impacto no CP] |

5. CAMINHO CRÍTICO
[Se identificado:]
Atividades críticas: [lista com folga = 0]
Atividade mais atrasada no CP: [nome] — [N dias]

[Se não identificado:]
⚠️ Caminho crítico não identificável — ausência de predecessoras no cronograma fornecido.

6. MAPA DE RISCOS
| Risco | Probabilidade | Impacto | Score | Ação |
|-------|--------------|---------|-------|------|
| [risco] | Alta/Média/Baixa | Alto/Médio/Baixo | [score] | [ação] |

7. PLANO DE AÇÃO
| Ação | Responsável | Prazo | Métrica de conclusão |
|------|-------------|-------|----------------------|
| [ação acionável] | [Obra/Cliente/Projetista/Fornecedor] | [data] | [como saber que foi feita] |

8. PRÓXIMOS MARCOS
| Marco | Baseline | Projetado | Desvio | Risco |
|-------|----------|-----------|--------|-------|
| [marco] | [data] | [data] | [dias] | 🔴/🟡/🟢 |

DADO ADICIONAL QUE MELHORARIA ESTA ANÁLISE:
[O que falta e o que seria possível com esse dado]
```

---

## MODELO B — RELATÓRIO COMPARATIVO SEMANAL (atualização)

```
RELATÓRIO DE OBRA Nº [X]
[NOME DA OBRA] | Semana: [ISO WXX] | Data-base: [DATA]
PMO: MENSURA Engenharia | CONFIDENCIAL
────────────────────────────────────────────────────────────

NÍVEL DE CONFIANÇA: [Alto/Médio/Baixo]

1. DELTA SEMANAL
SPI: [anterior] → [atual] ([+/-delta])
BEI: [anterior] → [atual]
Avanço físico: [anterior]% → [atual]% (ganho: [+X]%)
Atraso projetado: [anterior] → [atual] dias ([tendência: melhorando/piorando/estável])

2. AUDITORIA DE AÇÕES ANTERIORES
| Ação comprometida | Status | Observação |
|-------------------|--------|------------|
| [ação] | ✅ Executada / ⚠️ Parcial / ❌ Não executada | [motivo se não executada] |

[Se ações não executadas pela 2ª semana:]
⚠️ ALERTA: [N] ações repetidas sem execução — risco sistêmico.

[Se pela 3ª semana:]
🔴 ESCALAR: [N] ações pendentes há 3 semanas — requer decisão gerencial.

3. SITUAÇÃO ATUAL DAS FRENTES
[tabela resumida por frente com delta vs semana anterior]

4. PLANO DE AÇÃO DA SEMANA
[apenas ações novas ou ações carregadas com atualização de prazo]

TENDÊNCIA: [Acelerando / Desacelerando / Estável — com base em SPI das últimas 3 semanas]
```

---

## MODELO C — RESUMO EXECUTIVO RÁPIDO (máx. 15 linhas)

```
RESUMO EXECUTIVO — [NOME DA OBRA]
Data-base: [DATA] | Relatório Nº [X]
────────────────────────────────────

Status: [🔴 CRÍTICO / 🟡 ATENÇÃO / 🟢 CONTROLADO]
Avanço: [X]% / Previsto: [Y]% → desvio de [Z]%
Projeção de término: [DATA] ([+/-N dias vs baseline])
SPI: [valor] | BEI: [valor]

Top 3 riscos desta semana:
1. [risco + impacto em 1 linha]
2. [risco + impacto em 1 linha]
3. [risco + impacto em 1 linha]

Ação urgente: [o que precisa acontecer HOJE ou essa semana]
Decisão necessária de: [quem deve decidir o quê até quando]
```

---

*Modelos v1.0 — Padrão MENSURA Engenharia*
