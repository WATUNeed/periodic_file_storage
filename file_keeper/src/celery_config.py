from os import environ

broker_url = environ['BROKER_URL'] + '//keeper'
result_backend = environ['RESULT_BACKEND']
