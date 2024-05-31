from os import environ

broker_url = environ['BROKER_URL'] + '//factory'
result_backend = environ['RESULT_BACKEND']
