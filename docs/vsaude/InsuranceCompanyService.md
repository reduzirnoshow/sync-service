# InsuranceCompanyService

Base: `https://public-api.vsaude.com.br/api/services/app/InsuranceCompanyService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /GetAll

Listar convênios

**Body:**

| Campo | Tipo |
|---|---|
| `name` | string |
| `procedure` | integer(int64) |
| `includeInsurancePlans` | boolean |
| `sorting` | string |
| `skipCount` | integer(int32) |
| `maxResultCount` | integer(int32) |

---

