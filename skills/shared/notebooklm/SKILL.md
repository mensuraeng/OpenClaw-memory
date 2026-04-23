---
name: notebooklm
description: Integração com Google NotebookLM para criar notebooks, adicionar fontes, gerar podcasts, resumos, quizzes e outros artefatos. CLI em /root/.openclaw/workspace/.venvs/notebooklm/bin/notebooklm. Ativa em pedidos como "cria podcast sobre", "resume esses documentos", "gera quiz", "cria notebook no NotebookLM", "audio overview".
---

# NotebookLM — Google AI Notebook Integration

Acesso programático completo ao Google NotebookLM via CLI instalada localmente.

## Configuração

- **CLI:** `/root/.openclaw/workspace/.venvs/notebooklm/bin/notebooklm`
- **Venv:** `/root/.openclaw/workspace/.venvs/notebooklm/`
- **Auth:** Google OAuth (executar `notebooklm login` para autenticar)
- **Config:** `~/.notebooklm/`

## Ativar ambiente

```bash
source /root/.openclaw/workspace/.venvs/notebooklm/bin/activate
# OU usar caminho completo:
/root/.openclaw/workspace/.venvs/notebooklm/bin/notebooklm <comando>
```

## Comandos disponíveis

| Comando | Uso |
|---------|-----|
| `notebooklm login` | Autenticar com Google |
| `notebooklm status` | Verificar autenticação |
| `notebooklm list` | Listar notebooks |
| `notebooklm create <nome>` | Criar notebook |
| `notebooklm use <id>` | Selecionar notebook ativo |
| `notebooklm add-source <url/file>` | Adicionar fonte |
| `notebooklm chat <mensagem>` | Chat com notebook |
| `notebooklm generate podcast` | Gerar audio overview |
| `notebooklm generate summary` | Gerar resumo |
| `notebooklm generate quiz` | Gerar quiz |
| `notebooklm generate briefing` | Gerar briefing |
| `notebooklm generate faq` | Gerar FAQ |
| `notebooklm download <formato>` | Baixar artefato |

## Tipos de fonte suportados

URLs, YouTube (transcrição automática), PDFs, áudio, vídeo, imagens, texto puro.

## Quando usar

- Criar podcast / audio overview de documentos técnicos
- Resumir pesquisas longas
- Gerar material de estudo (quiz, flashcards)
- Analisar conjunto de documentos como base de conhecimento
- Briefings executivos de múltiplas fontes

## Exemplos

```bash
# Verificar auth
/root/.openclaw/workspace/.venvs/notebooklm/bin/notebooklm status

# Criar notebook e adicionar fontes
notebooklm create "Analise Tecnica Obra X"
notebooklm add-source https://site.com/documento.pdf

# Gerar podcast
notebooklm generate podcast
notebooklm download mp3

# Chat com o notebook
notebooklm chat "Qual o principal risco identificado?"
```

## Boas práticas

- Verificar `status` antes de qualquer operação
- Para agentes paralelos: `export NOTEBOOKLM_HOME=/tmp/agent-$ID`
- Podcasts levam alguns minutos — usar polling para aguardar
- Adicionar múltiplas fontes aumenta qualidade das análises
