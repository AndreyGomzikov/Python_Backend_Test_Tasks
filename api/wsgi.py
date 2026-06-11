import os

from api.constants import DJANGO_SETTINGS_MODULE
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
application = get_wsgi_application()
