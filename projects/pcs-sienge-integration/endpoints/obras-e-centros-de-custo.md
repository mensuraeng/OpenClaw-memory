# PCS Sienge — Obras e Centros de Custo

_Atualizado em 2026-04-22_

## Origem
Tabela enviada pelo Alê via imagem, contendo códigos, nomes e tipo de registro no Sienge para a PCS.

## Leitura operacional
- A listagem mistura itens do tipo **Obra e Centro de Custo** com pelo menos um item do tipo **Somente Centro de Custo**.
- Isso é útil para:
  - mapear obras válidas para integrações de RDO e financeiro
  - distinguir cadastros administrativos que não representam obra executável
  - montar chave de referência entre `codigo`, `nome` e `tipoRegistro`

## Registros identificados

| Código | Nome | Tipo de Registro |
|---:|---|---|
| 14 | FACULDADE DE DIREITO DE SBC - CENTRO JURIDICO | Obra e Centro de Custo |
| 16 | RETROFIT FACULDADE DE DIREITO DE SBC | Obra e Centro de Custo |
| 24 | MANUTENÇÃO PARANAPIACABA 2024 | Obra e Centro de Custo |
| 71 | CUSTOS COM PESSOAL - DIRETORIA | Obra e Centro de Custo |
| 83 | SMARTJAMPA | Obra e Centro de Custo |
| 100 | ADM PCS | Obra e Centro de Custo |
| 181 | RUA LAURA 181 | Obra e Centro de Custo |
| 1000 | ADM MIA ENGENHARIA | Somente Centro de Custo |
| 1354 | TEATRO MUNICÍPIO DE SUZANO | Obra e Centro de Custo |
| 1900 | REFORMA E MAN. DE ESCOLAS SP - LOTE 180 | Obra e Centro de Custo |
| 1901 | EMEI EDUARDO CARLOS PEREIRA | Obra e Centro de Custo |
| 1902 | EMEI CIDADE FERNÃO DIAS | Obra e Centro de Custo |
| 1903 | EMEI AVIADOR EDU CHAVES | Obra e Centro de Custo |
| 1904 | EMEF PROFA. ESMERALDA SALLES PEREIRA | Obra e Centro de Custo |
| 1905 | EMEI PROF. ÊNIO CORREA | Obra e Centro de Custo |
| 4412 | GERENCIAL PAVIMENTAÇÃO PARANAPICABA PCS | Obra e Centro de Custo |
| 4428 | AV. NOVE DE JULHO 4428 | Obra e Centro de Custo |
| 4500 | ATA CALÇADAS | Obra e Centro de Custo |
| 5201 | MP AUDITÓRIO RIACHUELO | Obra e Centro de Custo |
| 45000 | ATA CALÇADAS DIARIO DE OBRA 01 A 12 DE MARÇO | Obra e Centro de Custo |
| 94539 | LOCAÇÃO SÃO CAETANO - VUC PCS | Obra e Centro de Custo |
| 441 | PAVIMENTAÇÃO PARANAPIACABA | Obra e Centro de Custo |

## Observações críticas
- A presença de itens administrativos como `ADM PCS`, `ADM MIA ENGENHARIA` e `CUSTOS COM PESSOAL - DIRETORIA` indica que nem todo código listado deve ser tratado como obra física executável.
- `ADM MIA ENGENHARIA` aparece explicitamente como **Somente Centro de Custo**, então deve ser excluído de fluxos que dependem de obra real.
- Vale validar depois quais desses registros aparecem de fato no endpoint `/obras` e quais aparecem apenas em `/cost-centers`.
- Há um possível erro de grafia em `GERENCIAL PAVIMENTAÇÃO PARANAPICABA PCS` versus `PAVIMENTAÇÃO PARANAPIACABA`; isso merece conferência para evitar duplicidade ou chave inconsistente.

## Próximo passo recomendado
1. cruzar esta tabela com a resposta real dos endpoints `/cost-centers` e `/obras`
2. separar em três grupos:
   - obra executável
   - centro de custo administrativo
   - cadastro ambíguo / precisa validação
3. usar essa classificação como base para qualquer integração de RDO, suprimentos e financeiro
