# InsuranceCompanyService

Gerencia convenios e planos de saude.

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/InsuranceCompanyService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /GetAll

**Listar convênios**

Retorna todos os convênios de forma paginada e ordenada.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `name` | string | nao |
| `procedure` | integer(int64) | nao |
| `includeInsurancePlans` | boolean | nao |
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

