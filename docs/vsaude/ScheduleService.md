# ScheduleService

Gerencia agendamentos medicos. Permite criar, remarcar, cancelar, confirmar e finalizar consultas. Tambem consulta horarios disponiveis.

**Base URL:** `https://public-api.vsaude.com.br/api/services/app/ScheduleService`

**Auth:** `VSAUDE-API-KEY: {key}`

**Envelope:** `{ result, success, error, __abp }`


### Codigos de Status

| Codigo | Descricao | Quem |
|--------|-----------|------|
| 1 | Criado | paciente |
| 10 | Criado | profissional |
| 11 | Criado | funcionario/API |
| 2 | Remarcado | paciente |
| 20 | Remarcado | profissional |
| 21 | Remarcado | funcionario |
| 3 | Confirmado | paciente |
| 30 | Confirmado | profissional |
| 31 | Confirmado | funcionario |
| 4 | Rejeitado | paciente |
| 40 | Rejeitado | profissional |
| 41 | Rejeitado | funcionario |
| 5 | Cancelado | paciente |
| 50 | Cancelado | profissional |
| 51 | Cancelado | funcionario |
| 6 | Nao compareceu | paciente |
| 7 | Nao compareceu | profissional |
| 8 | Finalizado | paciente |
| 81 | Finalizado | profissional |
| 82 | Finalizado | funcionario |
| 9 | Aguardando | - |
| 90 | Em andamento | - |
| 100 | Expirado | - |
| 110 | Excluido | - |

---

## POST /Accept

**Aceitar um agendamento**

**Campo correto:** usar `id` para referenciar o agendamento (NAO `appointmentId`). Usando campo errado retorna "entidade nao encontrada para id 00000000".

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |

---

## POST /Cancel

**Cancelar um agendamento**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |

---

## POST /CounterPartDidNotShowUp

**Não compareceu**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |
| `patient` | string(uuid) | nao |
| `doctor` | string(uuid) | nao |

---

## POST /Create

**Agendar**

**IMPORTANTE:** O campo correto para unidade e `careUnitId` (NAO `healthCareUnitId`). Usando o nome errado retorna 500 sem detalhes.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `patientId` | string(uuid) | nao |
| `professionalId` | string(uuid) | nao |
| `procedureId` | integer(int64) | nao |
| `price` | number(float) | nao |
| `insuranceCompanyId` | integer(int64) | nao |
| `insurancePlanId` | integer(int64) | nao |
| `careUnitId` | integer(int64) | nao |
| `startDate` | string(date-time) | nao |
| `endDate` | string(date-time) | nao |
| `comments` | string | nao |
| `numberOfInstallments` | integer(int32) | nao |
| `recurrence` | string | nao |
| `signedTerms` | array<integer> | nao |
| `complementaryProcedures` | array<object> | nao |
| `paymentType` | object | nao |
| `originPlatform` | object | nao |
| `responsibleName` | string | nao |
| `responsiblePersonalIdentifier` | string | nao |

---

## POST /Finalize

**Finalizar**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |

---

## GET /Get

**Informações do agendamento**

Status do agendamento:


1 = Criado, 10 = Criado pelo profissional, 11 = Criado por um funcionário,


2 = Remarcado pelo paciente, 20 = Remarcado pelo profissional, 21 = Remarcado por um funcionário,


3 - Confirmado pelo paciente, 30 = Confirmado pelo profissional, 31 = Confirmado por um funcionário,


4 = Rejeitado pelo paciente, 40 = Rejeitado pelo profissional, 41 = Rejeitado por um funcionário,


5 = Cancelado pelo paciente, 50 = Cancelado pelo profissional, 51 = Cancelado por um funcionário,


6 = Paciente não compareceu, 7 = Profissional não compareceu,


8 = Finalizado pelo paciente, 81 = Finalizado pelo profissional, 82 = Finalizado por um funcionário,


9 = Aguardando atendimento, 90 = Em andamento,


100 = Expirado, 110 = Excluído

**Query Parameters:**

| Param | Tipo | Formato |
|---|---|---|
| `id` | string | uuid |

---

## POST /GetAll

**Listar agendamentos**

Mostra todos os agendamentos dentro do intervalo especificado


Status do agendamento:


1 = Criado, 10 = Criado pelo profissional, 11 = Criado por um funcionário,


2 = Remarcado pelo paciente, 20 = Remarcado pelo profissional, 21 = Remarcado por um funcionário,


3 - Confirmado pelo paciente, 30 = Confirmado pelo profissional, 31 = Confirmado por um funcionário,


4 = Rejeitado pelo paciente, 40 = Rejeitado pelo profissional, 41 = Rejeitado por um funcionário,


5 = Cancelado pelo paciente, 50 = Cancelado pelo profissional, 51 = Cancelado por um funcionário,


6 = Paciente não compareceu, 7 = Profissional não compareceu,


8 = Finalizado pelo paciente, 81 = Finalizado pelo profissional, 82 = Finalizado por um funcionário,


9 = Aguardando atendimento, 90 = Em andamento,


100 = Expirado, 110 = Excluído

**BUG:** O filtro `startDate` e ignorado pela API. Retorna TODOS os registros. Filtrar no cliente.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `doctorId` | string(uuid) | nao |
| `professionals` | array<string> | nao |
| `procedures` | array<integer> | nao |
| `patientId` | string(uuid) | nao |
| `excludeExternalAppointments` | boolean | nao |
| `from` | string(date-time) | nao |
| `range` | object | nao |
| `showCanceledAppointments` | boolean | nao |
| `careUnits` | array<integer> | nao |
| `appointmentStatus` | array<object> | nao |
| `includeForDeletedPatients` | boolean | nao |

---

## POST /GetAvailability

**Obter horários disponíveis**

**BUG:** Retorna erro 500 em todos os cenarios testados. Usar `GetAvailabilityWindow` no lugar.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `medicalSpecialty` | integer(int32) | nao |
| `proposedDuration` | integer(int32) | nao |
| `doctor` | string(uuid) | nao |
| `doctorUserId` | integer(int64) | nao |
| `procedureId` | integer(int64) | nao |
| `careUnitId` | integer(int64) | nao |
| `isProfessionalRequired` | boolean | nao |
| `patient` | string(uuid) | nao |
| `appointmentId` | string(uuid) | nao |
| `date` | string(date-time) | nao |
| `client` | integer(int64) | nao |
| `host` | integer(int64) | nao |

---

## POST /GetAvailabilityWindow

**Obter janela de horários**

Retorna os proximos 10 dias com horários vagos, listando os horários e profissionais que atendem em cada horário

Retorna SOMENTE slots LIVRES. Slots ocupados ou bloqueados NAO aparecem. Para saber o status completo, comparar com a jornada do medico.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `doctor` | string(uuid) | nao |
| `procedureId` | integer(int64) | nao |
| `careUnitId` | integer(int64) | nao |
| `patientId` | string(uuid) | nao |
| `appointmentId` | string(uuid) | nao |
| `insuranceCompany` | integer(int64) | nao |
| `insurancePlanId` | integer(int64) | nao |

---

## POST /ReSchedule

**Remarcar**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `startDate` | string(date-time) | nao |
| `endDate` | string(date-time) | nao |
| `updateAllRecurrences` | boolean | nao |
| `rescheduleStatusBehaviour` | object | nao |
| `askBehaviourOnReschedule` | boolean | nao |
| `id` | string(uuid) | nao |

---

## POST /Reject

**Rejeitar um agendamento**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |
| `patient` | string(uuid) | nao |
| `doctor` | string(uuid) | nao |

---

## POST /Snapshot

**Snapshot**

Você vai chamar para obter todos os parametros necessários para realizar um agendamento!
Inicialmente com todos os parámetros como null, dessa forma você vai obter todos os procedimentos disponíveis para
agendamento.



Após o usuário selecionar o procedimento, você irá chamar o método Snapshot novamente, agora passando o ID do
procedimento selecionado.
Dessa vez, na resposta você vai receber quais profissionais atendem o procedimento seleccionado.

Fluxo de agendamento: 1) Chamar sem params para obter procedimentos. 2) Chamar com procedureId para obter profissionais. 3) Chamar com procedureId+professionalId para obter unidades e convenios.

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `professionalId` | string(uuid) | nao |
| `procedureId` | integer(int64) | nao |
| `insuranceCompanyId` | integer(int64) | nao |
| `insurancePlanId` | integer(int64) | nao |
| `careUnitId` | integer(int64) | nao |
| `order` | string | nao |
| `patientId` | string(uuid) | nao |
| `doesNotSetPatientInsuranceAutomatically` | boolean | nao |

---

## POST /Waiting

**O paciente está aguardando**

**Campo correto:** usar `id` (NAO `appointmentId`).

**Request Body:**

| Campo | Tipo | Obrigatorio |
|---|---|---|
| `id` | string(uuid) | nao |
| `comments` | string | nao |

---

