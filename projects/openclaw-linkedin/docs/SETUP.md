# Setup — OpenClaw LinkedIn Operations

## O que já está pronto

- estrutura do projeto
- modelo de governança
- separação entre pessoal e institucional
- arquivo de exemplo de ambiente
- gerador de URL OAuth
- checagem básica de configuração

## O que falta para funcionar de verdade

### 1. Criar a app no LinkedIn Developers
Você precisará informar:
- Client ID
- Client Secret
- Redirect URI válida

### 2. Confirmar as páginas administradas
Preencher em `config/pages.example.json` depois migrando para um arquivo real privado.

### 3. Definir a URL de callback
Padrão provisório adotado agora:
- `http://localhost:3000/api/linkedin/callback`

Depois, isso pode migrar para uma URL pública do Mission Control.

## Bootstrap local

1. copiar `.env.example` para `.env`
2. preencher o `LINKEDIN_CLIENT_SECRET`
3. confirmar que a app do LinkedIn usa a redirect URI `http://localhost:3000/api/linkedin/callback`
4. rodar:

```bash
npm run config:check
npm run auth:url
```

## Validação rápida

A rota provisória do Mission Control para receber o callback ficou em:
- `/api/linkedin/callback`

Exemplo local completo:
- `http://localhost:3000/api/linkedin/callback`

## Regra de segurança

- `.env` não entra no Git
- segredos ficam fora do repositório
- perfil pessoal continua assistido
