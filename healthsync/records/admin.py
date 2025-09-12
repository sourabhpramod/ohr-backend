from django.contrib import admin
from .models import Patient, HealthRecord, SyncBatch, Conflict

admin.site.register(Patient)
admin.site.register(HealthRecord)
admin.site.register(SyncBatch)
admin.site.register(Conflict)
