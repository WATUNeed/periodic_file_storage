from pydantic import BaseModel


class FileAttributeDTO(BaseModel):
    filename: str
    bucket_name: str
    file_size_b: int
