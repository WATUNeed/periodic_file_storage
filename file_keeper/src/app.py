import datetime
import io
import os
from os import environ

import paramiko
from celery import Celery
from minio import Minio
import pika

from src.celery_config import broker_url

environ.setdefault('CELERY_CONFIG_MODULE', 'src.celery_config')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')

minio = Minio(
    "minio:9000",
    "m6GynYMBB7NlzIAaVRTm",
    "pUIPy7v1zjStkQI7LLZO4OsDUoi6rohhIpARYPAI",
    secure=False
)

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
    bucket_name = "factory0"
    factory_files = sftp.listdir_attr('./files/')
    bucket_files = minio.list_objects(bucket_name)
    bucket_filenames = {file.object_name for file in bucket_files}
    for file in factory_files:
        if file.filename not in bucket_filenames:
            save_file_task.s(bucket_name=bucket_name, filename=file.filename, file_size_b=file.st_size).apply()


@app.task
def load_files_task():
    task_start_datetime = datetime.datetime.now()
    from_datatime = task_start_datetime - datetime.timedelta(seconds=10)
    sftp = connect_to_sftp()

    for file in sftp.listdir_attr('./files/'):
        last_modify = datetime.datetime.fromtimestamp(file.st_mtime)
        if from_datatime <= last_modify < task_start_datetime:
            bucket_name = "factory0"
            if not minio.bucket_exists(bucket_name):
                minio.make_bucket(bucket_name)

            save_file_task.s(bucket_name=bucket_name, filename=file.filename, file_size_b=file.st_size).apply()


@app.task
def save_file_task(bucket_name: str, filename: str, file_size_b: int):
    # raise self.retry(countdown=60 * 5, exc=exc)
    sftp = connect_to_sftp()
    with io.BytesIO() as fl:
        sftp.getfo(f'./files/{filename}', fl)
        fl.seek(0)
        minio.put_object(bucket_name, filename, fl, file_size_b)
    print(f'Save file {filename} in bucket {bucket_name}')

    parameters = pika.URLParameters(broker_url)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    channel.basic_publish(
        'test_exchange',
        'test_routing_key',
        'message body value',
        pika.BasicProperties(
            content_type='text/plain',
            delivery_mode=pika.DeliveryMode.Transient
        )
    )

    connection.close()
