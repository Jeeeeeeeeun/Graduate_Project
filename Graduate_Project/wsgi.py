"""
WSGI config for Graduate_Project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fun25.config.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()