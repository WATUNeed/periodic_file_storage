import io

from minio import Minio

from src.config.minio import MINIO_CONFIG


class FileMinioDAO:
    def __init__(self, bucket_name: str):
        self.minio = Minio(MINIO_CONFIG.endpoint(), MINIO_CONFIG.access_key, MINIO_CONFIG.secret_key, secure=False)
        self.bucket_name = bucket_name
        if not self.minio.bucket_exists(self.bucket_name):
            self.minio.make_bucket(self.bucket_name)

    def get_bucket_filenames(self) -> set[str]:
        bucket_files = self.minio.list_objects(self.bucket_name)
        bucket_filenames = {file.object_name for file in bucket_files}
        return bucket_filenames

    def save_file(self, filename: str, fl: io.BytesIO, file_size_b: int):
        self.minio.put_object(self.bucket_name, filename, fl, file_size_b)

