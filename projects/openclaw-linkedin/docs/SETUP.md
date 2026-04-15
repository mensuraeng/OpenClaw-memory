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
Exemplo:
- uma URL do Mission Control
- uma URL dedicada de backend
- ou uma rota provisória para completar OAuth

## Bootstrap local

1. copiar `.env.example` para `.env`
2. preencher credenciais
3. rodar:

```bash
npm run config:check
npm run auth:url
```

## Regra de segurança

- `.env` não entra no Git
- segredos ficam fora do repositório
- perfil pessoal continua assistido
