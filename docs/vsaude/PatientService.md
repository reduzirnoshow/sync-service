# PatientService

Base: `https://public-api.vsaude.com.br/api/services/app/PatientService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /Create

Cadastrar

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `personalIdentifier` | string |
| `dni` | string |
| `name` | string |
| `gender` | integer(int32) |
| `birthday` | string(date-time) |
| `email` | string |
| `password` | string |
| `phone` | string |
| `bloodType` | string |
| `weight` | string |
| `height` | string |
| `address` | object (11 fields) |
| `comments` | string |
| `birthInfo` | object (8 fields) |
| `mother` | object (2 fields) |
| `father` | object (2 fields) |
| `partner` | object (2 fields) |
| `sponsor` | object (2 fields) |
| `tags` | array |
| `insurance` | object (3 fields) |
| `profession` | string |
| `photo` | string |

---

## GET /Get

Dados do paciente

**Query params:**

| `Id` | string |

---

## POST /Search

Buscar paciente

**Query params:**

| `keyword` | string |

---

## PUT /Update

Atualizar

**Body:**

| Campo | Tipo |
|---|---|
| `personalIdentifier` | string |
| `dni` | string |
| `name` | string |
| `gender` | integer(int32) |
| `birthday` | string(date-time) |
| `email` | string |
| `phone` | string |
| `bloodType` | string |
| `weight` | string |
| `height` | string |
| `address` | object (11 fields) |
| `comments` | string |
| `birthInfo` | object (8 fields) |
| `mother` | object (2 fields) |
| `father` | object (2 fields) |
| `partner` | object (2 fields) |
| `sponsor` | object (2 fields) |
| `status` | object |
| `insurance` | object (3 fields) |
| `profession` | string |
| `id` | string(uuid) |

---

