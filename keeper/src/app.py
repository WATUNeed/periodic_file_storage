from os import environ

from celery import Celery

from src.config.keeper import KEEPER_CONFIG

environ.setdefault('CELERY_CONFIG_MODULE', 'src.config.celery')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from src.domain.file.server.celery.task import save_missing_files_task

    sender.add_periodic_task(KEEPER_CONFIG.period_sec, save_missing_files_task.s(), name='save_missing_files')
    save_missing_files_task.s().delay()


