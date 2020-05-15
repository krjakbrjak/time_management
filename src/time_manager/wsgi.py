"""
WSGI config for time_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_manager.settings')

def __enable_debugging():
    from django.conf import settings
    # Attach debugger only in a debug mode
    if settings.DEBUG:
        try:
            import ptvsd
            ptvsd.enable_attach(address = ('0.0.0.0', 3000))
        except OSError as e:
            raise Exception("Only one instance of time_manager can run in debugging mode") from e
        finally:
            pass

def get_application():
    __enable_debugging()
    return get_wsgi_application()

application = get_application()
