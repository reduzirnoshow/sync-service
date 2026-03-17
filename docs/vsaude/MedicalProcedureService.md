# MedicalProcedureService

Base: `https://public-api.vsaude.com.br/api/services/app/MedicalProcedureService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /GetAll

Listar procedimentos

**Body:**

| Campo | Tipo |
|---|---|
| `insuranceCompany` | string |
| `parent` | integer(int64) |
| `exclude` | array |
| `sorting` | string |
| `skipCount` | integer(int32) |
| `maxResultCount` | integer(int32) |

---

