from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

from .storage import OverwriteStorage
from .constants import (
    CATEGORY_IMAGE_UPLOAD_PATH,
    DEFAULT_NAME_MAX_LENGTH,
    PRODUCT_IMAGE_SIZES,
    PRODUCT_JPEG_FORMAT,
    PRODUCT_JPEG_QUALITY,
    PRODUCT_LARGE_IMAGE_UPLOAD_PATH,
    PRODUCT_MEDIUM_IMAGE_UPLOAD_PATH,
    PRODUCT_ORIGINAL_IMAGE_UPLOAD_PATH,
    PRODUCT_SMALL_IMAGE_UPLOAD_PATH,
    SUBCATEGORY_IMAGE_UPLOAD_PATH,
)


overwrite_storage = OverwriteStorage()


class Category(models.Model):
    name = models.CharField(
        'Наименование',
        max_length=DEFAULT_NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Slug',
        max_length=DEFAULT_NAME_MAX_LENGTH,
        unique=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to=CATEGORY_IMAGE_UPLOAD_PATH,
        storage=overwrite_storage,
    )


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name='Родительская категория',
        related_name='subcategories',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        'Наименование',
        max_length=DEFAULT_NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Slug',
        max_length=DEFAULT_NAME_MAX_LENGTH,
        unique=True,
    )
    image = models.ImageField(
        'Изображение',
        upload_to=SUBCATEGORY_IMAGE_UPLOAD_PATH,
        storage=overwrite_storage,
    )


    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category__name', 'name']

    def __str__(self):
        return f'{self.category.name} / {self.name}'


class Product(models.Model):
    subcategory = models.ForeignKey(
        Subcategory,
        verbose_name='Подкатегория',
        related_name='products',
        on_delete=models.PROTECT,
    )
    name = models.CharField(
        'Наименование',
        max_length=DEFAULT_NAME_MAX_LENGTH,
    )
    slug = models.SlugField(
        'Slug',
        max_length=DEFAULT_NAME_MAX_LENGTH,
        unique=True,
    )
    image = models.ImageField(
        'Исходное изображение',
        upload_to=PRODUCT_ORIGINAL_IMAGE_UPLOAD_PATH,
        storage=overwrite_storage,
    )
    image_small = models.ImageField(
        'Изображение 150x150',
        upload_to=PRODUCT_SMALL_IMAGE_UPLOAD_PATH,
        blank=True,
        storage=overwrite_storage,
    )
    image_medium = models.ImageField(
        'Изображение 400x400',
        upload_to=PRODUCT_MEDIUM_IMAGE_UPLOAD_PATH,
        storage=overwrite_storage,
        blank=True,
    )
    image_large = models.ImageField(
        'Изображение 800x800',
        upload_to=PRODUCT_LARGE_IMAGE_UPLOAD_PATH,
        blank=True,
        storage=overwrite_storage,
    )
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def category(self):
        return self.subcategory.category

    def save(self, *args, **kwargs):
        old_image_name = self._get_old_image_name()
        image_changed = old_image_name != self.image.name

        super().save(*args, **kwargs)

        if self.image and self._should_generate_images(image_changed):
            if image_changed:
                self._delete_old_resized_images(old_image_name)

            self._generate_resized_images()
            super().save(update_fields=['image_small', 'image_medium', 'image_large'])

    def _get_old_image_name(self):
        old_image_name = None

        if self.pk:
            old_product = Product.objects.filter(
                pk=self.pk,
            ).only('image').first()

            if old_product:
                old_image_name = old_product.image.name

        return old_image_name

    def _should_generate_images(self, image_changed):
        return image_changed or not all([self.image_small, self.image_large])

    def _delete_old_resized_images(self, old_image_name):
        if old_image_name:
            old_stem = Path(old_image_name).stem
            old_small_name = f'products/small/{old_stem}_small.jpg'
            old_large_name = f'products/large/{old_stem}_large.jpg'

            for old_file_name in [old_small_name, old_large_name]:
                if overwrite_storage.exists(old_file_name):
                    overwrite_storage.delete(old_file_name)

    def _generate_resized_images(self):
        sizes = PRODUCT_IMAGE_SIZES
        for field_name, size in sizes.items():
            resized_file = self._resize_image(size)
            filename = self._resized_filename(field_name)
            image_field = getattr(self, field_name)

            if image_field:
                image_field.delete(save=False)

            image_field.save(filename, resized_file, save=False)

    def _resize_image(self, size):
        self.image.open('rb')
        img = Image.open(self.image)
        img = img.convert('RGB')
        img.thumbnail(size)
        buffer = BytesIO()
        img.save(
            buffer,
            format=PRODUCT_JPEG_FORMAT,
            quality=PRODUCT_JPEG_QUALITY,
        )

        return ContentFile(buffer.getvalue())

    def _resized_filename(self, field_name):
        stem = Path(self.image.name).stem
        suffix = field_name.replace('image_', '')
        return f'{stem}_{suffix}.jpg'


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='cart',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина пользователя {self.user}'

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(
            item.total_price
            for item in self.items.select_related('product')
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='cart_items',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        default=1,
    )


    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.name}: {self.quantity}'

    @property
    def total_price(self):
        return self.product.price * self.quantity
