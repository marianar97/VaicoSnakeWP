from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time

@shared_task
def frames2():
    time.sleep(100)
    print('hola')
    time.sleep(100)