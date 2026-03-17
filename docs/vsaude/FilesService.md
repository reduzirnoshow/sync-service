# FilesService

Base: `https://public-api.vsaude.com.br/api/services/app/FilesService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /ListFolder

Listar arquivos do paciente

**Body:**

| Campo | Tipo |
|---|---|
| `keyword` | string |
| `patient` | string(uuid) |
| `user` | integer(int64) |
| `id` | string(uuid) |
| `sorting` | string |
| `deletedOnly` | boolean |

---

## POST /Upload

Upload de arquivo

**Query params:**

| `parent` | string |
| `ownerUser` | integer |
| `ownerPatient` | string |
| `fileName` | string |

---

