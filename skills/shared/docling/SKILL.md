---
name: docling
description: Extrai, converte e estrutura conteúdo de PDFs, DOCX, PPTX, imagens e páginas em formatos úteis para análise, OCR e ingestão documental. Use quando o usuário pedir para converter documento, extrair texto, gerar markdown limpo, processar PDF técnico, edital, proposta, apresentação, imagem com OCR, ou preparar conteúdo documental para análise posterior no OpenClaw.
---

# docling

Use esta skill quando o trabalho exigir extração documental confiável usando o Docling instalado no workspace.

## Objetivo

Transformar documentos em saída utilizável para análise posterior, priorizando:
- markdown limpo
- texto extraído com estrutura
- OCR quando necessário
- base pronta para análise, busca ou ingestão

## Ferramenta instalada

Docling está instalado em ambiente isolado:
- `docling-env/`

Binários disponíveis:
- `docling-env/bin/docling`
- `docling-env/bin/docling-tools`
- `docling-env/bin/docling-view`

## Quando usar

Use esta skill quando o usuário pedir:
- converter PDF para markdown
- extrair texto de edital
- processar proposta ou memorial
- ler apresentação PDF/PPTX
- fazer OCR de imagem ou PDF escaneado
- preparar documento para análise posterior
- estruturar conteúdo documental para busca, resumo ou RAG

## Fluxo recomendado

1. Identificar tipo de documento
2. Escolher o modo de extração
3. Executar conversão com Docling
4. Validar qualidade da saída
5. Entregar arquivo convertido ou seguir para análise

## Tipos de uso

### 1. Conversão simples
Quando o objetivo é extrair texto ou markdown de um documento.

### 2. OCR
Quando o documento for imagem escaneada, PDF com baixa extração nativa ou material fotografado.

### 3. Pré-processamento para análise
Quando o objetivo final não é a conversão em si, mas preparar a base para leitura, resumo, indexação ou comparação.

## Regras

- Sempre preferir ambiente isolado `docling-env/`.
- Não assumir que OCR saiu bom sem verificar o resultado.
- Se a conversão vier ruim, declarar limitação do documento.
- Para documentos críticos, validar trechos manualmente antes de concluir.
- Se o pedido for só análise de PDF simples, considerar também o tool nativo `pdf`.
- Usar Docling quando a necessidade principal for extração/transformação documental mais robusta.

## Scripts locais de apoio

- `scripts/docling_converter.py`
- `scripts/docling_ingest.py`

Ler esses scripts se precisar adaptar o fluxo local.

## Referências

- `references/workflow.md`
- `references/formats.md`
- `references/validation.md`

Carregue apenas o necessário para a tarefa.