# InsurancePlanService

Base: `https://public-api.vsaude.com.br/api/services/app/InsurancePlanService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /GetAll

Listar planos de convênios

**Body:**

| Campo | Tipo |
|---|---|
| `name` | string |
| `company` | string |
| `sorting` | string |
| `skipCount` | integer(int32) |
| `maxResultCount` | integer(int32) |

---

