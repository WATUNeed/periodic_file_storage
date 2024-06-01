from typing import Set

import redis

from src.config.redis import REDIS_CONFIG

redis_connection = redis.Redis.from_url(REDIS_CONFIG.get_connection_url(), encoding='utf8', decode_responses=True)


class FileRedisDAO:
    def set_in_process(self, bucket_name: str, filename: str):
        redis_connection.set(f'{bucket_name},{filename}', 1)
    
    def in_process(self, bucket_name: str, filename: str) -> bool:
        return redis_connection.get(f'{bucket_name},{filename}') is not None
    
    def delete_in_process(self, bucket_name: str, filename: str):
        redis_connection.delete(f'{bucket_name},{filename}')
    
    def get_in_process_files_in_bucket(self, bucket_name: str) -> Set[str]:
        return {key.split(',')[1] for key in redis_connection.keys(f'{bucket_name},*')}
