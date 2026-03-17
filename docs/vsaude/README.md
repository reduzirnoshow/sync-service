# vSaude Public API

Swagger: https://public-api.vsaude.com.br/api-docs/index.html

Auth: `VSAUDE-API-KEY: {key}`

Response envelope: `{ result, success, error, __abp }`

## Services

- [FilesService](./FilesService.md) - ListFolder, Upload
- [HealthCareUnitService](./HealthCareUnitService.md) - GetAll
- [HealthProfessionalService](./HealthProfessionalService.md) - AuthenticateHealthProfessional, GetAll
- [InsuranceCompanyService](./InsuranceCompanyService.md) - GetAll
- [InsurancePlanService](./InsurancePlanService.md) - GetAll
- [MedicalProcedureService](./MedicalProcedureService.md) - GetAll
- [PatientService](./PatientService.md) - Create, Get, Search, Update
- [ReportService](./ReportService.md) - GetAttendance
- [ScheduleService](./ScheduleService.md) - Accept, Cancel, CounterPartDidNotShowUp, Create, Finalize, Get, GetAll, GetAvailability, GetAvailabilityWindow, ReSchedule, Reject, Snapshot, Waiting
- [User](./User.md) - AuthenticateMobileUser

27 endpoints total
