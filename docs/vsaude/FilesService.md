# FilesService

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/FilesService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /ListFolder

**Listar arquivos do paciente**

Retorna todos os arquivos e pastas do paciente.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `keyword` | string | nao |
| `patient` | string(uuid) | nao |
| `user` | integer(int64) | nao |
| `id` | string(uuid) | nao |
| `sorting` | string | nao |
| `deletedOnly` | boolean | nao |

---

## POST /Upload

**Upload de arquivo**

Utilizado para adicionar arquivo ao paciente.

**Query Parameters:**

| Param | Tipo | Formato |
|---|---|---|
| `parent` | string | uuid |
| `ownerUser` | integer | int64 |
| `ownerPatient` | string | uuid |
| `fileName` | string |  |

---

