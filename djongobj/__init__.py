try:
    from django.conf import settings
    if hasattr(settings, 'MONGO_DEFAULT_HOST'):
        HOST = settings.MONGO_DEFAULT_HOST
    else:
        HOST = 'localhost'

    if hasattr(settings, 'MONGO_DEFAULT_PORT'):
        PORT = settings.MONGO_DEFAULT_PORT
    else:
        PORT = 27017

except ImportError:
    HOST = 'localhost'
    PORT = 27017
