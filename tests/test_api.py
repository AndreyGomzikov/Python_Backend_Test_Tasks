from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shop.models import Category, Product, Subcategory


def test_image(name='test.jpg'):
    file = BytesIO()
    image = Image.new('RGB', (10, 10), color='white')
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type='image/jpeg')


class GroceryApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Фрукты',
            slug='fruits',
            image=test_image('category.jpg'),
        )
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name='Яблоки',
            slug='apples',
            image=test_image('subcategory.jpg'),
        )
        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name='Яблоко',
            slug='apple',
            image=test_image('apple.jpg'),
            price=Decimal('100.00'),
        )
        self.user = User.objects.create_user(username='buyer', password='password123')
        self.token = Token.objects.create(user=self.user)

    def test_get_categories_with_subcategories(self):
        response = self.client.get('/api/categories/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Фрукты')
        self.assertEqual(response.data['results'][0]['subcategories'][0]['name'], 'Яблоки')

    def test_get_products(self):
        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product = response.data['results'][0]
        self.assertEqual(product['name'], 'Яблоко')
        self.assertEqual(product['category'], 'Фрукты')
        self.assertEqual(product['subcategory'], 'Яблоки')
        self.assertEqual(len(product['images']), 3)

    def test_post_cart_item_requires_authentication(self):
        response = self.client.post('/api/cart/', {'product_id': self.product.id, 'quantity': 2})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_cart_item_for_authorized_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.post('/api/cart/', {'product_id': self.product.id, 'quantity': 2})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 2)

    def test_cart_summary(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.client.post('/api/cart/', {'product_id': self.product.id, 'quantity': 3})

        response = self.client.get('/api/cart/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_quantity'], 3)
        self.assertEqual(response.data['total_price'], '300.00')
