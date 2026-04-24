# Upload Orçamento Teatro Suzano → Sienge

## Estado atual

| Item | Status |
|---|---|
| Script de upload pronto | ✅ |
| Parser Excel validado | ✅ |
| Endpoint mapeado: `building-cost-estimations` | ✅ |
| Arquivo Excel recebido | ⏳ aguardando transferência |
| Recurso `building-cost-estimation-resources-v1` habilitado | ⏳ verificar no Sienge |
| Rate limit da API | ⚠️ resetar (pode precisar de minutos) |

---

## Passo 1 — Habilitar recurso no Sienge

No painel do Sienge:
1. Acesse **Gerenciamento de API** → **Usuários de API**
2. Edite o usuário `project`
3. Em **Recursos autorizados**, adicione: `building-cost-estimation-resources-v1`
4. Salvar

---

## Passo 2 — Transferir o arquivo Excel

Do seu Windows (PowerShell ou CMD):
```powershell
scp "C:\Users\alexa\Desktop\TEATRO SUZANO - Orçamento SIENGE.xlsx" root@100.124.198.120:/tmp/teatro_suzano.xlsx
```

---

## Passo 3 — Dry-run (verificar antes de subir)

```bash
cd /root/.openclaw/workspace/projects/pcs-sienge-integration
python3 scripts/upload_budget.py \
  --file /tmp/teatro_suzano.xlsx \
  --building-id 1354 \
  --dry-run
```

Isso mostra os itens lidos sem tocar no Sienge.

---

## Passo 4 — Upload real

```bash
python3 scripts/upload_budget.py \
  --file /tmp/teatro_suzano.xlsx \
  --building-id 1354
```

---

## Formato esperado do Excel

O parser detecta colunas automaticamente por nome. Aceita variações como:
- `Código` / `Cod` / `Item`
- `Descrição` / `Desc` / `Nome` / `Serviço`
- `Unidade` / `Un` / `Und`
- `Quantidade` / `Qtd` / `Qtde`
- `Custo Unitário` / `Preço Unitário` / `Vl Unit`
- `Custo Total` / `Total` / `Valor Total`

---

## Trava orçamentária

Após o upload dos itens, a trava orçamentária é ativada pelo Sienge Web:
**Obra → Banco de Dados da Obra → [planilha] → Travar Orçamento**

Não há endpoint API publicado para esta ação — é operação de UI.
