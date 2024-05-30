import datetime
from os import environ
from random import randint

from celery import Celery
from paramiko.channel import Channel

environ.setdefault('CELERY_CONFIG_MODULE', 'src.celery_config')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, create_file_task.s(), name='add every 10')


@app.task
def create_file_task():
    size = randint(1, 1000)
    path = f'{int(datetime.datetime.now(datetime.UTC).timestamp())}'
    with open(path, mode='wb+') as file:
        file.seek(size - 1)
        file.write(b"\0")
