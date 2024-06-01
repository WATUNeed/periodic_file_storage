import io

import paramiko

from src.config.sftp import SFTP_CONFIG


class FileSFTPDAO:
    def __init__(self, host: str):
        pkey = paramiko.RSAKey.from_private_key_file(SFTP_CONFIG.rsa_key_path)
        transport = paramiko.Transport((host, SFTP_CONFIG.port))
        transport.connect(username=SFTP_CONFIG.user, password=SFTP_CONFIG.password, pkey=pkey)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def get_files_attributes(self):
        factory_files = self.sftp.listdir_attr('./files/')
        return factory_files

    def write_io_by_filename(self, filename: str, fl: io.BytesIO):
        self.sftp.getfo(f'./files/{filename}', fl)
