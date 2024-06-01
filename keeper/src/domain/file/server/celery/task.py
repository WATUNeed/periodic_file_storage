import logging

from celery import shared_task

from src.config.keeper import KEEPER_CONFIG
from src.domain.file.exception import FileAlreadyInProcessError
from src.domain.file.service import save_missing_files, save_file


logger = logging.getLogger(__name__)


@shared_task
def save_missing_files_task():
    save_missing_files()


@shared_task(bind=True)
def save_file_task(self, factory: str, filename: str, file_size_b: int):
    try:
        save_file(factory, filename, file_size_b)
    except FileAlreadyInProcessError:
        return
    except FileNotFoundError:
        return logger.warning(f'File "{filename}" not found.')
    except Exception as exc:
        raise self.retry(countdown=KEEPER_CONFIG.retry_countdown, exc=exc)
