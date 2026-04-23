# Piloto Institucional — MENSURA

## Objetivo

Usar a página da MENSURA como primeiro piloto institucional de publicação via LinkedIn API.

## Estado atual

### O que já está validado
- app LinkedIn criada
- callback pública funcionando
- OAuth pessoal funcionando
- publicação pessoal validada com sucesso
- author pessoal validado com `urn:li:person:JYAsCudAAE`

### O que foi testado agora
Consulta da trilha institucional via:
- `GET https://api.linkedin.com/rest/organizationAcls?q=roleAssignee`

### Resultado
- status: `403`
- erro: `ACCESS_DENIED`
- mensagem: `Not enough permissions to access: partnerApiOrganizationAcls.FINDER-roleAssignee.20260401`

## Conclusão direta

Hoje a app **não tem permissão suficiente** para consultar os vínculos institucionais do perfil autenticado com páginas da empresa.

Isso impede, neste momento:
- descobrir por API se o perfil do Alê é admin da página MENSURA
- listar organization ACLs
- confirmar por API a organization URN da MENSURA usando essa trilha

## Diagnóstico

A frente pessoal está operacional.
A frente institucional ainda depende de permissão/produto adicional da app para Organization APIs.

## Próximo passo recomendado

No LinkedIn Developers, verificar e habilitar o produto/permissão institucional necessário para Organization APIs, especialmente a família ligada a:
- `organizationAcls`
- `w_organization_social`
- permissões/admin de organização aplicáveis

## Regra operacional

Não vale perder tempo tentando forçar publicação institucional antes de liberar Organization APIs. O gargalo agora é de permissão da app, não de implementação local.
