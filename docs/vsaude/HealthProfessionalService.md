# HealthProfessionalService

Base: `https://public-api.vsaude.com.br/api/services/app/HealthProfessionalService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /AuthenticateHealthProfessional

Autenticar profissional

**Body:**

| Campo | Tipo |
|---|---|
| `email` | string |
| `name` | string |

---

## POST /GetAll

Listar profissionais de saúde

**Body:**

| Campo | Tipo |
|---|---|
| `text` | string |
| `professional` | string(uuid) |
| `sorting` | string |
| `skipCount` | integer(int32) |
| `maxResultCount` | integer(int32) |

---

