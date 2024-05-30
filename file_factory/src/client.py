import os

import paramiko


path = '/'.join(os.path.abspath(__file__).split('/')[:-2] + ["test_rsa.key"])


def sftp_client():
    pkey = paramiko.RSAKey.from_private_key_file(path)
    transport = paramiko.Transport(('file_factory', 2222))
    transport.connect(username="admin", password="admin", pkey=pkey)

    sftp = paramiko.SFTPClient.from_transport(transport)

    print(sftp.listdir('.'))
    print(sftp.stat('src/client.py').st_mtime)


sftp_client()
