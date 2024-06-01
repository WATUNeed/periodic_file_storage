from src.config.rabbitmq import RABBITMQ_CONFIG

broker_url = RABBITMQ_CONFIG.connection_url('/factory')
broker_connection_retry_on_startup = True
