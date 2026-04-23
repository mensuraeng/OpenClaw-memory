# Workflow de Publicação — LinkedIn

## 1. Perfil pessoal do Alê

Modelo operacional: **assistido com aprovação explícita**.

### Etapas
1. gerar rascunho
2. revisar tom, risco reputacional e sensibilidade
3. aprovar explicitamente
4. publicar via API
5. registrar resultado e id do post

### Regra
- nenhum post pessoal sai sem aprovação explícita do Alê
- posts técnicos, institucionais ou experimentais continuam passando por confirmação
- usar API apenas depois do texto final estar congelado

### Saída mínima esperada
- objetivo do post
- texto final
- CTA, se houver
- confirmação de aprovação
- `post id` retornado pela API

## 2. Páginas institucionais

Modelo operacional: **governado por marca**.

### Etapas
1. definir marca alvo (`mensura`, `mia`, `pcs`)
2. confirmar owner/editor/admin da página no perfil autenticado
3. mapear `organization URN`
4. gerar rascunho conforme playbook da marca
5. validar aprovação interna
6. publicar via API
7. registrar resultado e id do post

### Regra
- marketing lidera estratégia e calendário
- Flávia/main opera credenciais, OAuth e publicação técnica
- cada marca precisa de voz, aprovação e rotina próprias

## 3. Estado atual por ativo

### pessoal
- OAuth validado
- author pessoal validado na prática
- publicação mínima já testada com sucesso

### mensura
- falta confirmar admin da página
- falta mapear organization URN
- depois disso pode virar piloto institucional

### mia
- falta confirmar admin da página
- falta mapear organization URN

### pcs
- falta confirmar admin da página
- falta mapear organization URN

## 4. Próximo bloco de execução

1. refletir capacidade real no Mission Control
2. transformar publicação pessoal em fluxo de rascunho + aprovação
3. mapear as 3 páginas para liberar publicação institucional
