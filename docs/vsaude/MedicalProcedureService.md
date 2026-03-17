# MedicalProcedureService

Gerencia procedimentos medicos (consultas, exames).

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/MedicalProcedureService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /GetAll

**Listar procedimentos**

Retorna todos os procedimentos de forma paginada e ordenada.

NAO retorna campo de status ativo/inativo. Todos os procedimentos sao retornados independente do status no painel.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `insuranceCompany` | string | nao |
| `parent` | integer(int64) | nao |
| `exclude` | array<integer> | nao |
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

