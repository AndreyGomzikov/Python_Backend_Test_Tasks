from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from shop.views import CartViewSet, CategoryViewSet, ProductViewSet
from . import constants as api_constants

router = DefaultRouter()
router.register(
    api_constants.CATEGORIES_ROUTE,
    CategoryViewSet,
    basename=api_constants.CATEGORY_BASENAME,
)
router.register(
    api_constants.PRODUCTS_ROUTE,
    ProductViewSet,
    basename=api_constants.PRODUCT_BASENAME,
)
router.register(
    api_constants.CART_ROUTE,
    CartViewSet,
    basename=api_constants.CART_BASENAME,
)

urlpatterns = [
    path(
        api_constants.ADMIN_URL,
        admin.site.urls,
    ),
    path(
        api_constants.API_TOKEN_URL,
        obtain_auth_token,
        name=api_constants.API_TOKEN_NAME,
    ),
    path(
        api_constants.API_SCHEMA_URL,
        SpectacularAPIView.as_view(),
        name=api_constants.API_SCHEMA_NAME,
    ),
    path(
        api_constants.API_DOCS_URL,
        SpectacularSwaggerView.as_view(
            url_name=api_constants.API_SCHEMA_NAME
        ),
        name=api_constants.API_SWAGGER_NAME,
    ),
    path(
        api_constants.API_ROOT_URL,
        include(router.urls),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
