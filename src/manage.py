#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'time_manager.settings')
    try:
        from django.core.management import execute_from_command_line
        from django.conf import settings
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Attach debugger only in a debug mode
    if settings.DEBUG:
        # It is nice to be able to run server with 'reloading' capability, but
        # that would start two servers: 1 - app, 2 - reloader. That is how django
        # runs things internally. To avoid the problem of address being already
        # in use, we attach the debugger only once. From django's source code one
        # can see that when a process for the reloader starts then the following
        # environment variables are set
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            import ptvsd
            ptvsd.enable_attach(address = ('0.0.0.0', 3000))

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
