''' Tasks related to our celery functions '''

import time
#import random
#import datetime

#from io import BytesIO
from celery import Celery, current_task
from celery.result import AsyncResult

from translate_doc import translate_docx
#from PIL import Image  
import os
import time

REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://admin:mypass@rabbit//'

CELERY = Celery('tasks',
                backend=REDIS_URL,
                broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'

def get_job(job_id):
    '''
    To be called from our web app.
    The job ID is passed and the celery job is returned.
    '''
    return AsyncResult(job_id, app=CELERY)

@CELERY.task()
def image_demension(img):
    time.sleep(2)

    return img

@CELERY.task()
def translate_docx_file(file_name):
    translate_file_name = translate_docx(file_name, file_name)

    return translate_file_name
