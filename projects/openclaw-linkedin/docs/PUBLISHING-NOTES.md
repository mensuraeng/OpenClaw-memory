# LinkedIn Publishing Notes

## Estado atual validado

- OAuth pessoal concluído com `openid profile w_member_social`
- `userinfo` funcionando
- Identidade autenticada confirmada: Alexandre Aguiar
- `sub` OIDC validado: `JYAsCudAAE`
- endpoint legado `/v2/me` não disponível com o escopo atual

## Conclusão operacional

Com a configuração atual:
- autenticação pessoal está pronta
- `w_member_social` está presente para postagem em nome do membro
- a API de Posts aceitou `urn:li:person:JYAsCudAAE`
- portanto, o `sub` OIDC validado funcionou na prática como identificador de author para publicação pessoal neste app

## Implicação prática

Para esta app e este fluxo atual:

1. já é possível publicar em nome do perfil pessoal usando a Posts API
2. não foi necessário usar `/v2/me` para fechar o primeiro post técnico
3. `r_liteprofile` continua útil como trilha clássica de perfil, mas não é bloqueador para a publicação pessoal mínima

## Regras para próximos testes

- sempre usar `POST https://api.linkedin.com/rest/posts`
- sempre enviar cabeçalhos:
  - `Authorization: Bearer <token>`
  - `X-Restli-Protocol-Version: 2.0.0`
  - `Linkedin-Version: 202604`
  - `Content-Type: application/json`
- não disparar postagem real sem confirmação explícita do Alê

## Payload-base esperado pela documentação

```json
{
  "author": "urn:li:person:{personId ou identificador compatível}",
  "commentary": "Texto de teste",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

## Resultado do teste real

Teste publicado com sucesso em `2026-04-15`.

- endpoint: `POST https://api.linkedin.com/rest/posts`
- status: `201`
- post id: `urn:li:share:7450191577479827456`
- author aceito: `urn:li:person:JYAsCudAAE`
- texto publicado: `Teste técnico de integração LinkedIn via Mission Control.`

## Próximo passo recomendado

Evoluir do teste técnico para uma rotina de publicação controlada no Mission Control, depois mapear páginas MENSURA, MIA e PCS.
