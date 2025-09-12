from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, HealthRecordViewSet, SyncUploadView, SyncDownloadView
from django.urls import path, include
from .views import TriggerSyncBatchView


router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"records", HealthRecordViewSet, basename="record")

urlpatterns = [
    path("", include(router.urls)),
    path("sync/upload/", SyncUploadView.as_view(), name="sync-upload"),
    path("sync/download/", SyncDownloadView.as_view(), name="sync-download"),
    path('sync/trigger/<uuid:batch_id>/', TriggerSyncBatchView.as_view(), name='trigger-sync-batch'),

]
