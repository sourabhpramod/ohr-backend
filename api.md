
```markdown
# HealthSync API Documentation

This document provides the full API reference for the HealthSync backend. It is intended for frontend developers integrating with the system.

---

## Base URL
```

http\:///api/



## All endpoints are prefixed with `/api/`.

---

## Authentication
Currently, all endpoints are open (`AllowAny`).  
No authentication headers are required.  

---

## Endpoints

### 1. Patients

**Base Path:** `/api/patients/`  

#### List Patients
- **Method:** `GET`  
- **URL:** `/api/patients/`  
- **Description:** Retrieve all patients.  
- **Request Parameters:** None  
- **Response Example:**
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "owner": null,
    "name": "John Doe",
    "dob": "1990-01-01",
    "mobile_number": "+919876543210",
    "identifiers": {},
    "fhir": null,
    "server_version": 1,
    "updated_at": "2025-09-12T19:25:18.331Z",
    "deleted": false
  }
]
```


#### Create Patient

* **Method:** `POST`
* **URL:** `/api/patients/`
* **Body Example:**

```json
{
  "name": "John Doe",
  "dob": "1990-01-01",
  "mobile_number": "+919876543210",
  "identifiers": {},
  "fhir": {}
}
```

* **Response:** Returns the created patient object.

#### Retrieve Patient

* **Method:** `GET`
* **URL:** `/api/patients/{id}/`
* **Response:** Patient object with the given ID.

### Get Patient by Mobile

Method: GET
URL: `/api/patients/by_mobile/?mobile={number}`
Description: Fetch a single patient by their mobile number.

Example Request:

GET `/api/patients/by_mobile/?mobile=9876543210`


Response Example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "owner": null,
  "name": "John Doe",
  "dob": "1990-01-01",
  "mobile_number": "9876543210",
  "identifiers": {},
  "fhir": null,
  "server_version": 1,
  "updated_at": "2025-09-12T19:25:18.331Z",
  "deleted": false
}

```
Error Responses:

400 → { "error": "mobile query param required" }

404 → { "error": "not found" }
#### Update Patient

* **Method:** `PUT` / `PATCH`
* **URL:** `/api/patients/{id}/`
* **Body Example:** Same as create.
* **Response:** Updated patient object.

#### Delete Patient

* **Method:** `DELETE`
* **URL:** `/api/patients/{id}/`
* **Response:** `HTTP 204 No Content`

---


## 2. Health Records

Base Path: `/api/records/`

### List Health Records

Method: GET

URL: `/api/records/`

Description: Retrieve all health records.

Response Example:
```json
[
  {
    "id": "uuid-of-record",
    "patient": "uuid-of-patient",
    "mobile_number": "8590169903",
    "resource_type": "Observation",
    "data": {},
    "server_version": 1,
    "updated_at": "2025-09-12T19:25:18.331Z",
    "deleted": false
  }
]
```

### Create Health Record

Method: POST

URL: `/api/records/`

Description: Create a health record. You can provide either the patient UUID or the mobile_number of the patient. The backend will automatically resolve mobile_number to the corresponding patient.

Request Body Examples:

Using patient UUID:
```json
{
  "resource_type": "Observation",
  "data": {},
  "deleted": false,
  "patient": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```
Using mobile_number:
```json
{
  "resource_type": "Observation",
  "data": {},
  "deleted": false,
  "mobile_number": "8590169903"
}

```
Response: Created health record object with both patient and mobile_number fields populated.

Retrieve / Update / Delete Record

Methods: GET, PUT / PATCH, DELETE

URL: /api/records/{id}/

### 3. Sync Upload

**Path:** `/api/sync/upload/`
**Method:** `POST`
**Description:** Upload a batch of changes from a client device.
Changes are applied to patients and health records.

#### Request Body Example:

```json
{
  "device_id": "device123",
  "changes": [
    {
      "operation": "create",
      "resource_type": "Observation",
      "client_temp_id": "temp123",
      "payload": {
        "patient_id": "uuid-of-patient",
        "value": "Some observation data"
      }
    },
    {
      "operation": "update",
      "resource_type": "Observation",
      "server_id": "uuid-of-record",
      "client_updated_at": "2025-09-12T10:00:00Z",
      "payload": {
        "value": "Updated data"
      }
    }
  ]
}
```

#### Response Example:

```json
{
  "batch_id": "uuid-of-syncbatch",
  "results": [
    {"client_temp_id": "temp123", "status": "created", "server_id": "uuid-of-record"},
    {"server_id": "uuid-of-record", "status": "updated", "server_version": 2}
  ],
  "conflicts": [
    {"server_id": "uuid-of-record", "reason": "server_newer"}
  ]
}
```

---

### 4. Sync Download

**Path:** `/api/sync/download/`
**Method:** `GET`
**Description:** Download all records updated after a given timestamp.

#### Query Parameters:

* `since` (required) – ISO8601 timestamp.
  Example: `?since=2025-09-12T10:00:00Z`

#### Response Example:

```json
{
  "changes": [
    {
      "server_id": "uuid-of-record",
      "resource_type": "Observation",
      "data": {},
      "server_version": 2,
      "updated_at": "2025-09-12T19:25:18.331Z",
      "deleted": false
    }
  ],
  "server_time": "2025-09-12T19:30:00.123Z"
}
```

---

### 5. Trigger Sync Batch (Celery)

**Path:** `/api/sync/trigger/{batch_id}/`
**Method:** `POST`
**Description:** Trigger asynchronous processing of a SyncBatch using Celery.

#### URL Parameters:

* `batch_id` – UUID of the sync batch created by `SyncUploadView`.

#### Response Example:

```json
{
  "status": "task started",
  "task_id": "celery-task-id"
}
```

---

## Notes

* All timestamps are in ISO8601 format.
* All UUIDs are string representations of the model’s primary key.
* `server_version` increments on every update to a record or patient.
* Conflicts occur if the server record is newer than client-submitted data.

---

## Models

### Patient

* `id`
* `owner`
* `name`
* `dob`
* `identifiers`
* `fhir`
* `server_version`
* `updated_at`
* `deleted`

### HealthRecord

* `id`
* `patient`
* `resource_type`
* `data`
* `server_version`
* `updated_at`
* `deleted`

---

## Additional Info

* CORS is enabled for local development.
* Celery is configured to handle background sync tasks.

```


```
