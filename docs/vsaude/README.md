# vSaude Public API

Documentacao completa da API publica do vSaude para integracao.

**Swagger oficial:** https://public-api.vsaude.com.br/api-docs/index.html

**Base URL:** `https://public-api.vsaude.com.br/api/services/app`

**Auth:** Header `VSAUDE-API-KEY: {key}`

**Response:** Todas as respostas seguem o envelope ABP:
```json
{
  "result": {},
  "success": true,
  "error": null,
  "__abp": true
}
```

## Servicos

### [FilesService](./FilesService.md)

Endpoints: `ListFolder`, `Upload`

### [HealthCareUnitService](./HealthCareUnitService.md)

Endpoints: `GetAll`

### [HealthProfessionalService](./HealthProfessionalService.md)

Gerencia profissionais de saude (medicos, psicologos).

Endpoints: `AuthenticateHealthProfessional`, `GetAll`

### [InsuranceCompanyService](./InsuranceCompanyService.md)

Gerencia convenios e planos de saude.

Endpoints: `GetAll`

### [InsurancePlanService](./InsurancePlanService.md)

Gerencia planos de convenios.

Endpoints: `GetAll`

### [MedicalProcedureService](./MedicalProcedureService.md)

Gerencia procedimentos medicos (consultas, exames).

Endpoints: `GetAll`

### [PatientService](./PatientService.md)

Gerencia pacientes. Permite buscar, criar, atualizar e consultar dados de pacientes.

Endpoints: `Create`, `Get`, `Search`, `Update`

### [ReportService](./ReportService.md)

Relatorios de agendamentos e atendimentos.

Endpoints: `GetAttendance`

### [ScheduleService](./ScheduleService.md)

Gerencia agendamentos medicos. Permite criar, remarcar, cancelar, confirmar e finalizar consultas. Tambem consulta horarios disponiveis.

Endpoints: `Accept`, `Cancel`, `CounterPartDidNotShowUp`, `Create`, `Finalize`, `Get`, `GetAll`, `GetAvailability`, `GetAvailabilityWindow`, `ReSchedule`, `Reject`, `Snapshot`, `Waiting`

### [User](./User.md)

Endpoints: `AuthenticateMobileUser`

## Bugs e Limitacoes Conhecidos

| Endpoint | Problema |
|---|---|
| `ScheduleService/Create` | Campo `careUnitId` (NAO `healthCareUnitId`), campo errado retorna 500 |
| `ScheduleService/*` (acoes) | Campo `id` (NAO `appointmentId`), campo errado retorna 00000000 |
| `ScheduleService/GetAvailability` | Retorna 500 sempre. Usar `GetAvailabilityWindow` |
| `ReportService/GetAttendance` | Ignora filtro de data. Filtrar no cliente |
| `InsurancePlanService/GetAll` | totalCount > 0 mas items vazio |
| `PatientService/Search` | keyword na query string, NAO no body |
| `MedicalProcedureService/GetAll` | NAO retorna status ativo/inativo |

Total: 27 endpoints em 10 servicos
