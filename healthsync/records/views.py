from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from .models import Patient, HealthRecord, ClientIdMapping, SyncBatch, Conflict
from .serializers import PatientSerializer, HealthRecordSerializer
from django.shortcuts import get_object_or_404
from .tasks import process_sync_batch_task

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-updated_at")
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]

class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all().order_by("-updated_at")
    serializer_class = HealthRecordSerializer
    permission_classes = [AllowAny]

class TriggerSyncBatchView(APIView):
    """
    Endpoint to trigger background processing of a SyncBatch via Celery.
    """
    permission_classes = [AllowAny]

    def post(self, request, batch_id):
        try:
            batch = SyncBatch.objects.get(id=batch_id)
        except SyncBatch.DoesNotExist:
            return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)

        task = process_sync_batch_task.delay(batch_id=batch.id)
        return Response({"status": "task started", "task_id": task.id})

class SyncUploadView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        data = request.data
        device_id = data.get("device_id")
        changes = data.get("changes", [])
        batch = SyncBatch.objects.create(device_id=device_id, payload=data)
        results = []
        conflicts = []

        for ch in changes:
            op = ch.get("operation")
            rtype = ch.get("resource_type")
            client_ver = ch.get("client_version", 0)
            client_tm_id = ch.get("client_temp_id")
            client_updated_at = ch.get("client_updated_at")

            if op == "create":
                patient_id = ch["payload"].get("patient_id")
                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    results.append({"client_temp_id": client_tm_id, "status": "patient_not_found"})
                    continue
                rec = HealthRecord.objects.create(
                    patient=patient,
                    resource_type=rtype,
                    data=ch["payload"],
                )
                ClientIdMapping.objects.create(client_temp_id=client_tm_id, server_id=rec.id, device_id=device_id)
                results.append({
                    "client_temp_id": client_tm_id,
                    "status": "created",
                    "server_id": str(rec.id),
                    "server_version": rec.server_version,
                    "updated_at": rec.updated_at.isoformat()
                })

            elif op == "update":
                server_id = ch.get("server_id")
                rec = HealthRecord.objects.filter(id=server_id).first()
                if not rec:
                    results.append({"server_id": server_id, "status": "not_found"})
                    continue

                server_updated_at = rec.updated_at
                if client_updated_at and server_updated_at and server_updated_at.isoformat() > client_updated_at:
                    Conflict.objects.create(record_server_id=rec.id, resource_type=rtype, client_payload=ch["payload"], server_payload=rec.data)
                    conflicts.append({"server_id": str(rec.id), "reason": "server_newer"})
                    results.append({"server_id": server_id, "status": "conflict"})
                    continue

                rec.data = ch["payload"]
                rec.server_version += 1
                rec.save()
                results.append({
                    "server_id": str(rec.id), "status": "updated", "server_version": rec.server_version, "updated_at": rec.updated_at.isoformat()
                })

            elif op == "delete":
                server_id = ch.get("server_id")
                rec = HealthRecord.objects.filter(id=server_id).first()
                if rec:
                    rec.deleted = True
                    rec.server_version += 1
                    rec.save()
                    results.append({"server_id": server_id, "status": "deleted"})
                else:
                    results.append({"server_id": server_id, "status": "not_found"})

        batch.status = "DONE"
        batch.result = {"results": results, "conflicts": conflicts}
        batch.processed_at = timezone.now()
        batch.save()

        return Response({"batch_id": str(batch.id), "results": results, "conflicts": conflicts}, status=status.HTTP_200_OK)

class SyncDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        since = request.query_params.get("since")
        if not since:
            return Response({"detail": "Missing 'since' query param, e.g. ?since=2025-09-12T10:00:00Z"}, status=status.HTTP_400_BAD_REQUEST)

        records = HealthRecord.objects.filter(updated_at__gt=since)
        out = []
        for r in records:
            out.append({
                "server_id": str(r.id),
                "resource_type": r.resource_type,
                "data": r.data,
                "server_version": r.server_version,
                "updated_at": r.updated_at.isoformat(),
                "deleted": r.deleted
            })
        return Response({"changes": out, "server_time": timezone.now().isoformat()})
