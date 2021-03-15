from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smi.settings')

app = Celery('smi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'sync-sap-product': {
        'task': 'project.product.tasks.sync_product_table',
        'schedule': crontab(minute=0, hour='1'),
    },
    'sync-nekonv-error-close': {
        'task': 'project.order.tasks.sync_nekonv_error_close',
        'schedule': crontab(minute='*/20')
    },
    'sync-konv-error-close': {
        'task': 'project.order.tasks.sync_konv_error_close',
        'schedule': crontab(minute='*/20')
    },
    'sync-reload-transfer': {
        'task': 'project.movement.tasks.sync_reload_transfer',
        'schedule': crontab(minute='*/20')
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
