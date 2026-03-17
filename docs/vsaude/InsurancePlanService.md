# InsurancePlanService

Gerencia planos de convenios.

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/InsurancePlanService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /GetAll

**Listar planos de convênios**

Retorna todos os planos de convênios de forma paginada e ordenada.

**BUG:** Retorna totalCount > 0 mas items = []. NAO usar.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `name` | string | nao |
| `company` | string | nao |
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

