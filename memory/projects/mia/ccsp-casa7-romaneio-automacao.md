---
name: CCSP Casa 7 - Automação de Romaneio
description: Procedimento padrão para processar romaneios da CCSP Casa 7 recebidos por e-mail
type: project
---

# CCSP Casa 7 — Automação de Romaneio

**Gatilho:** Chegada de e-mail com romaneio da CCSP Casa 7 (assunto contém "ROMANEIO" ou anexos PDF + .xlsm com "ROMANEIO")

**Why:** O Alê pediu em 23/04/2026 que sempre que chegar romaneio por e-mail, os dados sejam automaticamente extraídos e lançados no Controle Financeiro no SharePoint.

**How to apply:** Ao detectar e-mail com romaneio CCSP Casa 7, executar o fluxo abaixo.

---

## Fluxo de Processamento

### 1. Extração dos Dados (PDF + Excel TOOLS)

Ler o PDF do romaneio e identificar:
- Número do romaneio (ex: 031)
- Data da romaneio
- Para cada item:
  - Tipo (SERVIÇO / MATERIAL)
  - Contrato referente (MC_XXX)
  - Número do documento (NF-e / NFS-e / Fatura)
  - Valor total
  - Data de emissão
  - Data de vencimento
  - Descrição
  - Nome do fornecedor
  - CNPJ do fornecedor
  - Retenções (INSS, ISS, se houver)

Ler também a planilha Excel TOOLS para confirmar itens e pegar o total do romaneio.

### 2. Preencher Controle Financeiro

**SharePoint:** https://miaengenharia.sharepoint.com/:f:/s/CCSP-CasaCapela3/IgCE3eOHVqieSZRMp-33niZEAdc_2kSfT0V0B7_rAc3ALt4?e=PvhrZ7

**Arquivo alvo:** `CCSP Casa 7 - Controle Financeiro`

Delegar ao agente Finance (finance) via `sessions_spawn` com os dados extraídos para:
- Localizar o arquivo no SharePoint
- Inserir nova linha/registro para cada item do romaneio
- Confirmar total batendo com o romaneio

### 3. Notificar Alê

Após confirmação do agente Finance, notificar via Telegram com resumo:
- Número do romaneio
- Total lançado
- Eventuais divergências ou pendências

---

## Dados do Romaneio 031 (processado em 23/04/2026)

| # | Tipo | Contrato | NF | Valor | Emissão | Vencimento | Fornecedor |
|---|------|----------|----|-------|---------|------------|------------|
| 1 | SERVIÇO | MC_167 | 2118 | R$ 11.000,00 | 07/04/26 | 15/04/26 | PROTEGE PISO |
| 2 | SERVIÇO | — | 4 | R$ 5.000,00 | 06/04/26 | 15/04/26 | MONTEIRO SISTEMAS |
| 3 | SERVIÇO | — | 53317 | R$ 35.000,00 | 06/04/26 | 15/04/26 | MONTEIRO SISTEMAS |
| 4 | MATERIAL | MC_166 | 172573 | R$ 1.087,69 | 23/03/26 | 15/04/26 | 7 OLIVEIRAS |
| 5 | SERVIÇO | MC_169 | 9 | R$ 8.800,00 | 07/04/26 | 15/04/26 | JD SOLUÇÕES ELÉTRICAS |
| 6 | SERVIÇO | MC_168 | 81 | R$ 13.045,45 | 08/04/26 | 15/04/26 | SOUSA CONSTRUÇÕES |
| 7 | MATERIAL | MC_166 | 174165 | R$ 490,00 | 08/04/26 | 15/04/26 | 7 OLIVEIRAS |
| 8 | SERVIÇO | — | 53 | R$ 30.000,00 | 14/04/26 | 15/04/26 | MIA ENGENHARIA |

**Total Romaneio 031: R$ 104.423,14**
