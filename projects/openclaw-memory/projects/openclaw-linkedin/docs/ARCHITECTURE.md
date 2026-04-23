# Arquitetura — OpenClaw LinkedIn Operations

## Separação obrigatória

### 1. Perfil pessoal
- dono: Alexandre
- operação: assistida
- publicação: com revisão/confirmação humana
- objetivo: preservar autenticidade e reduzir risco reputacional

### 2. Páginas institucionais
- MENSURA
- MIA
- PCS
- operação: estruturada por marca
- publicação: controlada por calendário, regra e permissão

## App model recomendado

Uma app LinkedIn central com:
- OAuth
- escopos mínimos
- credenciais mantidas fora do repositório
- mapeamento explícito entre identidade e página

## Camadas do sistema

### Camada de autenticação
Responsável por:
- iniciar OAuth
- armazenar tokens com segurança
- renovar tokens quando aplicável
- manter separação entre pessoal e institucional

### Camada de configuração
Responsável por:
- mapear páginas
- registrar URNs/ids
- identificar responsáveis
- definir ambiente e política de publicação

### Camada editorial
Responsável por:
- templates de post
- rascunhos
- calendário por marca
- checklist de revisão

### Camada de publicação
Responsável por:
- enviar publicação
- registrar retorno
- guardar trilha operacional
- lidar com falhas e retry seguro

## Regra de risco

- perfil pessoal nunca entra em automação cega
- credenciais nunca entram no GitHub
- cada página institucional deve ter owner claro
- qualquer permissão além do mínimo precisa ser justificada
