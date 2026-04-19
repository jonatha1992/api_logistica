from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# En desarrollo puede usar SQLite si no hay PostgreSQL disponible
import os
if not os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
