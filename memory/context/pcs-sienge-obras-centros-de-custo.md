# PCS Sienge — obras e centros de custo (memória operacional)

_Atualizado em 2026-04-22_

## Função deste arquivo
Base operacional de referência para uso recorrente da Flávia em integrações, conferências e classificação de registros da PCS dentro do Sienge.

Não é memória institucional da empresa.
É memória operacional reutilizável.

## Origem
- Fonte: imagem enviada pelo Alê em 2026-04-22
- Contexto: listagem de obras e centros de custo da PCS no Sienge

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

## Regras de leitura
- Nem todo item com tipo `Obra e Centro de Custo` deve ser tratado automaticamente como obra física executável.
- Itens administrativos e gerenciais exigem classificação antes de entrarem em fluxos de obra, RDO, suprimentos ou consolidação financeira por projeto.
- `ADM MIA ENGENHARIA` deve ser tratado como centro de custo administrativo, não como obra.

## Alertas operacionais
- Há mistura de obra real, centro administrativo e cadastro possivelmente gerencial.
- Há possível inconsistência de grafia entre `PARANAPICABA` e `PARANAPIACABA`.
- Antes de usar esta base como chave de integração, cruzar com endpoints reais `/cost-centers` e `/obras`.

## Próximo passo útil
Classificar os registros em:
1. obra executável
2. centro de custo administrativo
3. ambíguo / validar
