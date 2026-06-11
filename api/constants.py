DJANGO_SETTINGS_MODULE = 'api.settings'

SECRET_KEY = 'dev-secret-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

SQLITE_DATABASE_NAME = 'db.sqlite3'

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

API_PAGE_SIZE = 10

SPECTACULAR_TITLE = 'Grocery Store API'
SPECTACULAR_DESCRIPTION = (
    'API магазина продуктов: категории, продукты, корзина, '
    'token auth.'
)
SPECTACULAR_VERSION = '1.0.0'

ADMIN_URL = 'admin/'
API_ROOT_URL = 'api/'
API_TOKEN_URL = 'api/token/'
API_SCHEMA_URL = 'api/schema/'
API_DOCS_URL = 'api/docs/'

API_TOKEN_NAME = 'api-token'
API_SCHEMA_NAME = 'schema'
API_SWAGGER_NAME = 'swagger-ui'

CATEGORIES_ROUTE = 'categories'
PRODUCTS_ROUTE = 'products'
CART_ROUTE = 'cart'

CATEGORY_BASENAME = 'category'
PRODUCT_BASENAME = 'product'
CART_BASENAME = 'cart'
