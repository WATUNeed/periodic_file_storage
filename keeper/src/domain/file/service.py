import io
import logging

from src.app import app
from src.config.factory import FACTORY_CONFIG
from src.domain.file.dal.minio import FileMinioDAO
from src.domain.file.dal.rabbitmq import FileRabbitmqDAO
from src.domain.file.dal.redis import FileRedisDAO
from src.domain.file.dal.sftp import FileSFTPDAO
from src.domain.file.exception import FileAlreadyInProcessError

logger = logging.getLogger(__name__)


def save_missing_files():
    for factory in FACTORY_CONFIG.names:
        bucket_filenames = FileMinioDAO(factory).get_bucket_filenames()
        factory_files = FileSFTPDAO(factory).get_files_attributes()
        files_in_process = FileRedisDAO().get_in_process_files_in_bucket(factory)
        for file in factory_files:
            if file.filename not in bucket_filenames.union(files_in_process):
                app.send_task(
                    'src.domain.file.server.celery.task.save_file_task',
                    kwargs={'factory': factory, 'filename': file.filename, 'file_size_b': file.st_size}
                )


def save_file(factory: str, filename: str, file_size_b: int):
    file_in_process = FileRedisDAO().in_process(factory, filename)
    if file_in_process:
        raise FileAlreadyInProcessError()
    else:
        FileRedisDAO().set_in_process(factory, filename)
    logger.info(f'Start saving file "{filename}" with size "{file_size_b}" to bucket "{factory}".')
    with io.BytesIO() as fl:
        FileSFTPDAO(factory).write_io_by_filename(filename, fl)
        fl.seek(0)
        FileMinioDAO(factory).save_file(filename, fl, file_size_b)

    FileRedisDAO().delete_in_process(factory, filename)
    logger.info(f'File "{filename}" with size "{file_size_b}" in bucket "{factory}" saved.')
    FileRabbitmqDAO().send_notification_after_file_loaded(factory, filename, file_size_b)
