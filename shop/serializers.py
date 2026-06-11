from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Cart, CartItem, Category, Product, Subcategory
from .constants import (
    MIN_CART_ITEM_QUANTITY,
    PRODUCT_API_IMAGE_FIELDS,
    QUANTITY_POSITIVE_ERROR,
)


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'slug', 'image')


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'subcategories')


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source='category.name',
        read_only=True,
    )
    category_slug = serializers.CharField(
        source='category.slug',
        read_only=True,
    )
    subcategory = serializers.CharField(
        source='subcategory.name',
        read_only=True,
    )
    subcategory_slug = serializers.CharField(
        source='subcategory.slug',
        read_only=True,
    )
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'category',
            'category_slug',
            'subcategory',
            'subcategory_slug',
            'price',
            'images',
        )

    @extend_schema_field(serializers.ListField(child=serializers.URLField()))
    def get_images(self, obj):
        request = self.context.get('request')
        image_fields = [
            getattr(obj, field)
            for field in PRODUCT_API_IMAGE_FIELDS
        ]
        urls = []
        for image in image_fields:
            if image:
                url = image.url

                if request:
                    url = request.build_absolute_uri(url)

                urls.append(url)

        return urls


class CartProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'images')

    @extend_schema_field(serializers.ListField(child=serializers.URLField()))
    def get_images(self, obj):
        return ProductSerializer(context=self.context).get_images(obj)


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')

    def validate_quantity(self, value):
        if value < MIN_CART_ITEM_QUANTITY:
            raise serializers.ValidationError(QUANTITY_POSITIVE_ERROR)
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_quantity', 'total_price')
