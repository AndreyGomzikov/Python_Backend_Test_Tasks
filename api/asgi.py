import os

from api.constants import DJANGO_SETTINGS_MODULE
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
application = get_asgi_application()
