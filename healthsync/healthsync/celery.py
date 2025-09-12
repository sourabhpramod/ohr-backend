# healthsync/celery.py
import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthsync.settings")

app = Celery("healthsync")

# Load config from Django settings, using CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
