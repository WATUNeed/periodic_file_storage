import datetime
import os
from os import environ

import paramiko
from celery import Celery

environ.setdefault('CELERY_CONFIG_MODULE', 'src.celery_config')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')

PATH = '/'.join(os.path.abspath(__file__).split('/')[:-2] + ['test_rsa.key'])


def connect_to_sftp() -> paramiko.SFTPClient:
    pkey = paramiko.RSAKey.from_private_key_file(PATH)
    transport = paramiko.Transport(('file_factory', 2222))
    transport.connect(username='admin', password='admin', pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, load_files_task.s())
    start_task.apply()


@app.task
def start_task():
    sftp = connect_to_sftp()
    for file in sftp.listdir_attr('./files/'):
        pass


@app.task
def load_files_task():
    task_start_datetime = datetime.datetime.now()
    from_datatime = task_start_datetime - datetime.timedelta(seconds=10)
    sftp = connect_to_sftp()

    for file in sftp.listdir_attr('./files/'):
        last_modify = datetime.datetime.fromtimestamp(file.st_mtime)
        if from_datatime <= last_modify < task_start_datetime:
            print(file.filename)


@app.task
def save_file_task(factory_host: str, filename: str):
    pass
