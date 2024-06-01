from src.config.rabbitmq import RABBITMQ_CONFIG

broker_url = RABBITMQ_CONFIG.connection_url('/keeper')
broker_connection_retry_on_startup = True
imports = ('src.domain.file.server.celery.task',)
