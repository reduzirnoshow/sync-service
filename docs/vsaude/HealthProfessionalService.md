# HealthProfessionalService

Gerencia profissionais de saude (medicos, psicologos).

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/HealthProfessionalService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /AuthenticateHealthProfessional

**Autenticar profissional**

Se nao existe profissional com o e-mail informado, sera criado, e autenticado

Se o email nao existe, cria o profissional automaticamente.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `email` | string | nao |
| `name` | string | nao |

---

## POST /GetAll

**Listar profissionais de saúde**

Retorna todos os profissionais de forma paginada e ordenada.

Retorna dados basicos. Para obter CRM/licenca, usar GET individual por ID (nao disponivel na API publica).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `text` | string | nao |
| `professional` | string(uuid) | nao |
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

