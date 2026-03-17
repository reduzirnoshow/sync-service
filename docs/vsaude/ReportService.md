# ReportService

Base: `https://public-api.vsaude.com.br/api/services/app/ReportService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /GetAttendance

Agendamentos/Atendimentos

**Body:**

| Campo | Tipo |
|---|---|
| `fromDate` | string(date-time) |
| `toDate` | string(date-time) |
| `proceduresId` | array |
| `insuranceCompaniesId` | array |
| `insurancePlansId` | array |
| `careUnitsId` | array |
| `patientId` | string(uuid) |
| `patientGender` | integer(int32) |
| `statuses` | array |
| `professionals` | array |
| `fromAge` | integer(int32) |
| `toAge` | integer(int32) |
| `sorting` | string |
| `skipCount` | integer(int32) |
| `maxResultCount` | integer(int32) |

---

