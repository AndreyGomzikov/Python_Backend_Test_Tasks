from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem, Category, Product
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
)
from .constants import QUANTITY_REQUIRED_ERROR


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related(
        'subcategory',
        'subcategory__category',
    )
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class CartViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart = self._get_cart()
        return cart.items.select_related(
            'product',
            'product__subcategory',
            'product__subcategory__category',
        )

    def _get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @extend_schema(responses=CartSerializer)
    def list(self, request, *args, **kwargs):
        serializer = CartSerializer(
            self._get_cart(),
            context={'request': request},
        )

        return Response(serializer.data)

    @extend_schema(request=CartItemSerializer, responses=CartItemSerializer)
    def create(self, request, *args, **kwargs):
        cart = self._get_cart()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity'])
        response_serializer = self.get_serializer(item)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=CartItemSerializer, responses=CartItemSerializer)
    def partial_update(self, request, *args, **kwargs):
        item = self.get_object()
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response(
                {'quantity': QUANTITY_REQUIRED_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            item,
            data={'quantity': quantity},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        self._get_cart().items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
