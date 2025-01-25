import os

from django.core.wsgi import get_wsgi_application, WSGIHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
application: WSGIHandler = get_wsgi_application()
