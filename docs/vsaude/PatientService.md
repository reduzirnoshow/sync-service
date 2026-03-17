# PatientService

Gerencia pacientes. Permite buscar, criar, atualizar e consultar dados de pacientes.

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/PatientService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /Create

**Cadastrar**

Utilize para cadastrar um novo paciente (e pegar o id) para o qual você quer agendar um procedimento.
            Você pode enviar o e-mail e senha do paciente, dessa forma será gerado automaticamente o usuário para acesso do paciente.
            Recomendamos primeiro pesquisar pelo paciente, para não gerar duplicidade.

Cria paciente E usuario automaticamente. Recomendado buscar antes (Search) para evitar duplicidade.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `personalIdentifier` | string | nao |
| `dni` | string | nao |
| `name` | string | nao |
| `gender` | integer(int32) | nao |
| `birthday` | string(date-time) | nao |
| `email` | string | nao |
| `password` | string | nao |
| `phone` | string | nao |
| `bloodType` | string | nao |
| `weight` | string | nao |
| `height` | string | nao |
| `address` | object | nao |
| `comments` | string | nao |
| `birthInfo` | object | nao |
| `mother` | object | nao |
| `father` | object | nao |
| `partner` | object | nao |
| `sponsor` | object | nao |
| `tags` | array<integer> | nao |
| `insurance` | object | nao |
| `profession` | string | nao |
| `photo` | string | nao |

---

## GET /Get

**Dados do paciente**

**Metodo:** GET com query param `Id` (NAO POST).

**Query Parameters:**

| Param | Tipo | Formato |
|---|---|---|
| `Id` | string | uuid |

---

## POST /Search

**Buscar paciente**

Retorna a lista de pacientes cadastrados segundo o termo da pesquisa. Utilize para buscar o paciente (id) para o qual você quer agendar um procedimento.

**IMPORTANTE:** O `keyword` deve ir na QUERY STRING, NAO no body. Se mandar no body, retorna array vazio.

**Query Parameters:**

| Param | Tipo | Formato |
|---|---|---|
| `keyword` | string |  |

---

## PUT /Update

**Atualizar**

Utilize para atualizar um paciente. Obrigatório enviar o ID do paciente.

**Metodo:** PUT (NAO POST). Requer enviar o objeto completo do paciente com o ID.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `personalIdentifier` | string | nao |
| `dni` | string | nao |
| `name` | string | nao |
| `gender` | integer(int32) | nao |
| `birthday` | string(date-time) | nao |
| `email` | string | nao |
| `phone` | string | nao |
| `bloodType` | string | nao |
| `weight` | string | nao |
| `height` | string | nao |
| `address` | object | nao |
| `comments` | string | nao |
| `birthInfo` | object | nao |
| `mother` | object | nao |
| `father` | object | nao |
| `partner` | object | nao |
| `sponsor` | object | nao |
| `status` | object | nao |
| `insurance` | object | nao |
| `profession` | string | nao |
| `id` | string(uuid) | nao |

---

