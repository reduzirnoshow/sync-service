# ReportService

Relatorios de agendamentos e atendimentos.

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/ReportService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`

---

## POST /GetAttendance

**Agendamentos/Atendimentos**

Irá retornar o relatório de agendamentos ou atendimentos.


Utilize os status 1, 10, 11, 2, 20, 21, 3, 30, 31, 4, 40, 41, 5, 50, 51, 6, 7, 82, 8, 81, 90, 100 para listar os agendamentos.


Utilize os status 8, 81, 82, 90 para listar os atendimentos

**BUG:** O filtro de data e ignorado. Retorna TODOS os ~577 registros historicos. Filtrar por data no cliente.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `fromDate` | string(date-time) | nao |
| `toDate` | string(date-time) | nao |
| `proceduresId` | array<integer> | nao |
| `insuranceCompaniesId` | array<integer> | nao |
| `insurancePlansId` | array<integer> | nao |
| `careUnitsId` | array<integer> | nao |
| `patientId` | string(uuid) | nao |
| `patientGender` | integer(int32) | nao |
| `statuses` | array<object> | nao |
| `professionals` | array<string> | nao |
| `fromAge` | integer(int32) | nao |
| `toAge` | integer(int32) | nao |
| `sorting` | string | nao |
| `skipCount` | integer(int32) | nao |
| `maxResultCount` | integer(int32) | nao |

---

