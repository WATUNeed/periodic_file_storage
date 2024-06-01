import datetime
import os
from os import environ
from random import randint

from celery import Celery

environ.setdefault('CELERY_CONFIG_MODULE', 'src.config.celery')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # create_file_task.s().delay()
    sender.add_periodic_task(60.0, create_file_task.s(), name='add every 10')


@app.task
def create_file_task():
    size = randint(1073741814, 1073741814 * 2)
    filename = f'{int(datetime.datetime.now(datetime.UTC).timestamp())}'
    path = '/'.join(os.path.abspath(__file__).split('/')[:-2] + ['files'] + [filename])
    print(f'{path = }')
    with open(path, mode='wb+') as file:
        file.seek(size - 1)
        file.write(b"\0")
