# ScheduleService

Base: `https://public-api.vsaude.com.br/api/services/app/ScheduleService`

Auth: `VSAUDE-API-KEY: {key}`

## POST /Accept

Aceitar um agendamento

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |

---

## POST /Cancel

Cancelar um agendamento

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |

---

## POST /CounterPartDidNotShowUp

Não compareceu

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |
| `patient` | string(uuid) |
| `doctor` | string(uuid) |

---

## POST /Create

Agendar

**Body:**

| Campo | Tipo |
|---|---|
| `patientId` | string(uuid) |
| `professionalId` | string(uuid) |
| `procedureId` | integer(int64) |
| `price` | number(float) |
| `insuranceCompanyId` | integer(int64) |
| `insurancePlanId` | integer(int64) |
| `careUnitId` | integer(int64) |
| `startDate` | string(date-time) |
| `endDate` | string(date-time) |
| `comments` | string |
| `numberOfInstallments` | integer(int32) |
| `recurrence` | string |
| `signedTerms` | array |
| `complementaryProcedures` | array |
| `paymentType` | object |
| `originPlatform` | object |
| `responsibleName` | string |
| `responsiblePersonalIdentifier` | string |

---

## POST /Finalize

Finalizar

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |

---

## GET /Get

Informações do agendamento

**Query params:**

| `id` | string |

---

## POST /GetAll

Listar agendamentos

**Body:**

| Campo | Tipo |
|---|---|
| `doctorId` | string(uuid) |
| `professionals` | array |
| `procedures` | array |
| `patientId` | string(uuid) |
| `excludeExternalAppointments` | boolean |
| `from` | string(date-time) |
| `range` | object |
| `showCanceledAppointments` | boolean |
| `careUnits` | array |
| `appointmentStatus` | array |
| `includeForDeletedPatients` | boolean |

---

## POST /GetAvailability

Obter horários disponíveis

**Body:**

| Campo | Tipo |
|---|---|
| `medicalSpecialty` | integer(int32) |
| `proposedDuration` | integer(int32) |
| `doctor` | string(uuid) |
| `doctorUserId` | integer(int64) |
| `procedureId` | integer(int64) |
| `careUnitId` | integer(int64) |
| `isProfessionalRequired` | boolean |
| `patient` | string(uuid) |
| `appointmentId` | string(uuid) |
| `date` | string(date-time) |
| `client` | integer(int64) |
| `host` | integer(int64) |

---

## POST /GetAvailabilityWindow

Obter janela de horários

**Body:**

| Campo | Tipo |
|---|---|
| `doctor` | string(uuid) |
| `procedureId` | integer(int64) |
| `careUnitId` | integer(int64) |
| `patientId` | string(uuid) |
| `appointmentId` | string(uuid) |
| `insuranceCompany` | integer(int64) |
| `insurancePlanId` | integer(int64) |

---

## POST /ReSchedule

Remarcar

**Body:**

| Campo | Tipo |
|---|---|
| `startDate` | string(date-time) |
| `endDate` | string(date-time) |
| `updateAllRecurrences` | boolean |
| `rescheduleStatusBehaviour` | object |
| `askBehaviourOnReschedule` | boolean |
| `id` | string(uuid) |

---

## POST /Reject

Rejeitar um agendamento

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |
| `patient` | string(uuid) |
| `doctor` | string(uuid) |

---

## POST /Snapshot

Snapshot

**Body:**

| Campo | Tipo |
|---|---|
| `professionalId` | string(uuid) |
| `procedureId` | integer(int64) |
| `insuranceCompanyId` | integer(int64) |
| `insurancePlanId` | integer(int64) |
| `careUnitId` | integer(int64) |
| `order` | string |
| `patientId` | string(uuid) |
| `doesNotSetPatientInsuranceAutomatically` | boolean |

---

## POST /Waiting

O paciente está aguardando

**Body:**

| Campo | Tipo |
|---|---|
| `id` | string(uuid) |
| `comments` | string |

---

