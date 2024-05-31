import datetime
import io
import os
from os import environ

import paramiko
from celery import Celery
from minio import Minio
import pika
from pydantic import BaseModel

from src.config import config

environ.setdefault('CELERY_CONFIG_MODULE', 'src.celery_config')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')

minio = Minio(
    "minio:9000",
    "TEUoTQjIVOpGyzFJ72Y5",
    "jTK3nUA1dNtaGx9bKZHXc9844iPIysLcZh35n3HY",
    secure=False
)

PATH = '/'.join(os.path.abspath(__file__).split('/')[:-2] + ['test_rsa.key'])


def connect_to_sftp(host: str, port: int = 2222) -> paramiko.SFTPClient:
    print(f'{host = }')
    pkey = paramiko.RSAKey.from_private_key_file(PATH)
    transport = paramiko.Transport((host, port))
    transport.connect(username='admin', password='admin', pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, load_files_task.s())
    start_task.delay()


@app.task
def start_task():
    for factory in config.factories:
        if not minio.bucket_exists(factory):
            minio.make_bucket(factory)
        bucket_files = minio.list_objects(factory)
        bucket_filenames = {file.object_name for file in bucket_files}
        sftp = connect_to_sftp(factory)
        factory_files = sftp.listdir_attr('./files/')
        for file in factory_files:
            if file.filename not in bucket_filenames:
                save_file_task.s(bucket_name=factory, filename=file.filename, file_size_b=file.st_size).apply()


@app.task
def load_files_task():
    task_start_datetime = datetime.datetime.now()
    from_datatime = task_start_datetime - datetime.timedelta(seconds=10)
    for factory in config.factories:
        sftp = connect_to_sftp(factory)
        for file in sftp.listdir_attr('./files/'):
            last_modify = datetime.datetime.fromtimestamp(file.st_mtime)
            if from_datatime <= last_modify < task_start_datetime:
                if not minio.bucket_exists(factory):
                    minio.make_bucket(factory)

                save_file_task.s(bucket_name=factory, filename=file.filename, file_size_b=file.st_size).delay()


class FileAttributeDTO(BaseModel):
    filename: str
    bucket_name: str
    file_size_b: int


@app.task
def save_file_task(bucket_name: str, filename: str, file_size_b: int):
    print(f'Start saving file {filename} with size {file_size_b} to bucket {bucket_name}')
    # raise self.retry(countdown=60 * 5, exc=exc)
    sftp = connect_to_sftp(bucket_name)
    with io.BytesIO() as fl:
        sftp.getfo(f'./files/{filename}', fl)
        fl.seek(0)
        minio.put_object(bucket_name, filename, fl, file_size_b)
    print(f'Save file {filename} in bucket {bucket_name}')

    parameters = pika.URLParameters(config.broker_url)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    message = FileAttributeDTO(
        filename=filename,
        bucket_name=bucket_name,
        file_size_b=file_size_b
    )
    channel.exchange_declare(
        'external_exchange'
    )

    channel.basic_publish(
        'external_exchange',
        'file_saved',
        message.model_dump_json(),
        pika.BasicProperties(
            content_type='text/plain',
            delivery_mode=pika.DeliveryMode.Transient
        )
    )

    connection.close()
