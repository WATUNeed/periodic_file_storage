import paramiko


def sftp_client():
    pkey = paramiko.RSAKey.from_private_key_file('test_rsa.key')
    transport = paramiko.Transport(("localhost", 2222))
    transport.connect(username="admin", password="admin", pkey=pkey)

    sftp = paramiko.SFTPClient.from_transport(transport)

    print(sftp.listdir('.'))
    print(sftp.stat('client.py'))


sftp_client()
