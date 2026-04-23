---
name: postiz
description: Agendamento e publicação de posts em redes sociais via Postiz (http://localhost:3000). Use para criar posts, agendar publicações, gerenciar canais de mídia social. Ativa em pedidos como "agenda post no Instagram", "publica no LinkedIn", "distribui conteúdo nas redes".
---

# Postiz — Social Media Scheduling

Acesso à instância Postiz local para agendamento e publicação em múltiplas redes sociais.

## Configuração

- **URL base:** `http://localhost:3000`
- **Painel web:** http://localhost:3000

## Funcionalidades principais

- Agendar posts para múltiplas plataformas simultaneamente
- Gerenciar canais conectados (Instagram, LinkedIn, Twitter/X, Facebook, etc.)
- Calendário editorial visual
- Reutilização de conteúdo entre plataformas

## Quando usar

- Distribuir conteúdo do Ghost CMS para redes sociais
- Agendar campanha de posts
- Gerenciar calendário editorial de múltiplos canais
- Automatizar pipeline: Ghost publica → Postiz distribui

## Pipeline de conteúdo

```
1. Conteúdo gerado/revisado no Ghost CMS
2. Adaptar formato para cada rede social
3. Agendar via Postiz com data/hora específica
4. Monitorar engajamento
```

## Integração com n8n

```
Trigger: Ghost post publicado (webhook)
  → n8n extrai título + excerpt + link
  → Formata para cada rede social
  → POST Postiz API → agendar publicação
```

## Boas práticas

- Adaptar o texto para cada rede (tom, tamanho, hashtags)
- Imagens: dimensões específicas por plataforma
- Verificar tokens de OAuth das redes periodicamente (expiram)
- Nunca agendar posts críticos sem revisar preview
