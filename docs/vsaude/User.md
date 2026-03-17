# User

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/User`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /AuthenticateMobileUser

**Autenticar paciente**

Você vai chamar para obter o token JWT do paciente.


Enviar no cabeçalho das requisições o Token recebido em accessToken para identificar ao paciente.

**Authorization:** Bearer {AccessToken}

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `userNameOrEmailAddress` | string | nao |
| `password` | string | nao |

---

