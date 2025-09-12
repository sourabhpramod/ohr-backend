from rest_framework import serializers
from .models import Patient, HealthRecord, SyncBatch, Conflict

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ("id", "server_version", "updated_at")

class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = "__all__"
        read_only_fields = ("id", "server_version", "updated_at")
