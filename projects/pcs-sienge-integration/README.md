# PCS Sienge Integration

Base inicial da integração PCS ↔ Sienge.

## Objetivo

Estruturar um conector limpo, auditável e expansível para os módulos de:
- cadastros mestres
- suprimentos
- financeiro

## Estrutura inicial

```text
src/
  pcs_sienge/
    config.py
    auth.py
    client.py
    errors.py
    models.py
    endpoints/
    normalizers/
    storage/
    jobs/
```

## Estado atual

- arquitetura funcional definida
- documentação do MVP consolidada
- base inicial de código em preparação

## Próximos módulos prioritários

1. config
2. auth
3. client
4. endpoints/creditors.py
5. endpoints/cost_centers.py
6. endpoints/payables.py
