import pika

from src.config.rabbitmq import RABBITMQ_CONFIG
from src.domain.file.dto import FileAttributeDTO


class FileRabbitmqDAO:
    def send_notification_after_file_loaded(self, bucket_name: str, filename: str, file_size_b: int):
        parameters = pika.URLParameters(RABBITMQ_CONFIG.connection_url())
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
