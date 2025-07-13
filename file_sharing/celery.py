import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_sharing_project.settings')

app = Celery('file_sharing_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
