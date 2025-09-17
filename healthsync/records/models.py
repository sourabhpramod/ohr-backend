import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=256)
    dob = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)  # <-- Added field
    identifiers = models.JSONField(default=dict, blank=True)
    fhir = models.JSONField(null=True, blank=True)
    server_version = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

class HealthRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="records")
    mobile_number = models.CharField(max_length=15, null=True, blank=True)  # New field
    resource_type = models.CharField(max_length=128)
    data = models.JSONField()
    server_version = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.mobile_number and self.patient:
            self.mobile_number = self.patient.mobile_number
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.resource_type} - {self.id}"

class ClientIdMapping(models.Model):
    client_temp_id = models.CharField(max_length=200, db_index=True)
    server_id = models.UUIDField()
    device_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SyncBatch(models.Model):
    STATUS_CHOICES = (("PENDING", "PENDING"), ("PROCESSING", "PROCESSING"), ("DONE", "DONE"), ("FAILED", "FAILED"))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=200)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="PENDING")
    payload = models.JSONField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

class Conflict(models.Model):
    record_server_id = models.UUIDField(null=True, blank=True)
    resource_type = models.CharField(max_length=128)
    client_payload = models.JSONField()
    server_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
