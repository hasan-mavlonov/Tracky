"""
WSGI config for Tracky project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tracky.settings')

application = get_wsgi_application()

import platform

if platform.system() != "Windows":
    print("RFID not supported on Render (Linux). Skipping init.")
else:
    try:
        import your_rfid_module
    except Exception as e:
        print("RFID Init Error:", e)
