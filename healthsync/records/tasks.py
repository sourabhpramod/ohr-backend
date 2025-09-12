# records/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import SyncBatch, Patient, HealthRecord, ClientIdMapping, Conflict

@shared_task(bind=True)
def process_sync_batch_task(self, batch_id):
    """
    Processes a sync batch asynchronously.
    Adapted to current models: Patient, HealthRecord, ClientIdMapping, SyncBatch.
    """

    try:
        batch = SyncBatch.objects.get(id=batch_id)
    except SyncBatch.DoesNotExist:
        return {"error": "Batch not found"}

    if batch.status != "PENDING":
        return {"status": "already processed"}

    batch.status = "PROCESSING"
    batch.save()

    payload = batch.payload or {}
    changes = payload.get("changes", [])

    results = []
    conflicts = []

    for change in changes:
        try:
            patient_data = change.get("patient")
            records_data = change.get("records", [])
            device_id = change.get("device_id")  # optional

            if not patient_data:
                conflicts.append({"change": change, "error": "No patient data"})
                continue

            # Create or update patient
            patient, created = Patient.objects.update_or_create(
                id=patient_data.get("id"),
                defaults={
                    "owner_id": patient_data.get("owner_id"),
                    "name": patient_data.get("name"),
                    "dob": patient_data.get("dob"),
                    "identifiers": patient_data.get("identifiers", {}),
                    "fhir": patient_data.get("fhir", {}),
                    "server_version": patient_data.get("server_version", 1),
                    "deleted": patient_data.get("deleted", False),
                },
            )

            # Map client ID if provided
            client_id = patient_data.get("client_id")
            if client_id:
                ClientIdMapping.objects.update_or_create(
                    client_temp_id=client_id,
                    defaults={
                        "server_id": patient.id,
                        "device_id": device_id,
                    },
                )

            # Process health records
            for record_data in records_data:
                try:
                    HealthRecord.objects.update_or_create(
                        id=record_data.get("id"),
                        defaults={
                            "patient": patient,
                            "resource_type": record_data.get("resource_type", "Unknown"),
                            "data": record_data.get("data", {}),
                            "server_version": record_data.get("server_version", 1),
                            "updated_at": record_data.get("updated_at", timezone.now()),
                            "deleted": record_data.get("deleted", False),
                        },
                    )
                except Exception as rec_err:
                    conflicts.append({
                        "patient_id": patient.id,
                        "record": record_data,
                        "error": str(rec_err)
                    })

            results.append({"patient_id": patient.id, "status": "ok"})

        except Exception as e:
            conflicts.append({"change": change, "error": str(e)})

    # Save results to batch
    batch.result = {"results": results, "conflicts": conflicts}
    batch.status = "DONE"
    batch.processed_at = timezone.now()
    batch.save()

    return {"status": "done", "results": results, "conflicts": conflicts}
