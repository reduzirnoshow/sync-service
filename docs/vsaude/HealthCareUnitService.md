# HealthCareUnitService

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/HealthCareUnitService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /GetAll

**Listar unidades de atendimento**

Retorna todas as unidades de atendimento cadastradas de forma paginada e ordenada

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

