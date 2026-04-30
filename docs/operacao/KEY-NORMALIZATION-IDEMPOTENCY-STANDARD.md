# Padrão — Key Normalization & Idempotency

Atualizado em 2026-04-30.

## Por que existe

Qualquer sistema que cria chave a partir de entrada bruta pode quebrar controle, deduplicação ou rate limit.

Exemplo de risco:

- `/googlechat`
- `/googlechat/`
- `/googlechat?x=1`

Se essas variantes representam o mesmo recurso, mas geram chaves diferentes, o sistema cria buckets separados e abre bypass/fragmentação.

Esse padrão vale para a infraestrutura da Flávia/MENSURA sempre que houver:

- rate limit;
- webhook;
- idempotency key;
- deduplicação;
- suppression list;
- lead/email/domain matching;
- manifest/backup identifier;
- path de arquivo;
- URL externa/interna;
- chave de cache;
- fingerprint de segredo;
- rota Mission Control;
- lookup em banco.

## Regra principal

Nunca gerar chave operacional a partir de input bruto.

Sempre transformar primeiro em identidade canônica.

```text
raw input → parse/validate → normalize/canonicalize → key
```

## Checklist obrigatório

### URL / webhook / rota

- remover query string quando ela não fizer parte da identidade;
- normalizar trailing slash;
- normalizar percent-encoding quando aplicável;
- rejeitar path ambíguo;
- gerar key a partir do path resolvido/canônico, não de `req.url` bruto.

### Email

- `trim`;
- lowercase;
- validar formato;
- separar local-part e domínio;
- domínio lowercase;
- não misturar aliases sem regra explícita.

### Domínio

- lowercase;
- remover ponto final terminal;
- normalizar `www.` quando a regra de negócio exigir;
- validar DNS quando impactar campanha/outreach.

### Arquivo/path

- resolver path absoluto ou relativo com regra fixa;
- normalizar `.`/`..`;
- preservar raiz permitida;
- não usar path textual bruto em manifest/hash sem canonicalização.

### JSON/objeto

- ordenar campos antes de hash quando a ordem não importar;
- remover campos voláteis (`timestamp`, query, request id) se não fizerem parte da identidade;
- declarar quais campos compõem a chave.

### Segredos/fingerprints

- nunca imprimir segredo;
- fingerprint por hash de valor normalizado;
- registrar tipo lógico, caminho e severidade;
- não usar valor bruto como chave visível.

## Teste mínimo obrigatório

Toda automação que cria chave deve ter teste de estabilidade:

- variantes equivalentes geram a mesma chave;
- variantes realmente diferentes geram chaves diferentes;
- input inválido falha fechado;
- query/trailing slash/case não fragmentam bucket quando não deveriam.

Exemplos:

```text
/googlechat == /googlechat/
/googlechat?foo=bar == /googlechat quando query não é identidade
EMAIL@DOMINIO.COM == email@dominio.com
/path/a/../b == /path/b quando dentro da raiz permitida
```

## Aplicação nos loops atuais

### Skill Intake

Detectar e apontar:

- rate-limit/idempotency/dedup baseado em URL/path bruto;
- uso de `req.url` sem `new URL(...).pathname` ou resolver equivalente;
- comparação de arquivos/paths sem canonicalização;
- permission creep mascarado por chaves fragmentáveis.

### Secret Hygiene

Detectar e apontar:

- fingerprints diferentes para o mesmo segredo por whitespace/case/path;
- path de segredo não normalizado;
- duplicidade de achados por caminho textual diferente.

### Restore Drill

Implantar/verificar o padrão `key_normalization_and_idempotency` antes de considerar o restore drill concluído.

Detectar e apontar:

- manifest keys instáveis;
- backup id dependente de path textual bruto;
- hash comparado com path não canônico;
- restore validado contra local errado por trailing slash/relative path;
- tentativa de restore sobre produção.

Exigir:

- manifest keys, backup identifiers, paths e hashes canonicalizados antes de comparação;
- testes de estabilidade para path relativo/absoluto e trailing slash quando aplicável;
- restore sempre em diretório temporário/sandbox, nunca sobre produção.

### CRM/CDP

Detectar e apontar:

- email/domínio sem normalização;
- suppression que não pega variação de domínio/email;
- lead duplicado por diferença de case, trailing dot ou `www.`;
- idempotency key de campanha com fonte instável.

## Critério de bloqueio

Bloquear merge/implantação quando:

- chave operacional usa input bruto;
- não há teste de estabilidade para variantes equivalentes;
- existe risco de bypass de rate limit, dedup, suppression ou idempotência;
- chave contém segredo ou dado sensível em claro.

## Saída esperada em reviews

Formato mínimo:

```text
[key_normalization_and_idempotency]
Status: pass | review | block
Achado: ...
Risco: rate-limit bypass | dedup fragmentation | suppression miss | restore mismatch | secret exposure
Correção: gerar key a partir de <campo canônico>
Teste mínimo: <variantes equivalentes>
```
