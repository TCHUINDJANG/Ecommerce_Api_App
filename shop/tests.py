from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Product , Category
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status


User = get_user_model()


class ProductApiTestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test")
        self.product = Product.objects.create(
            name = "Test Product",
            category = self.category,
            price = 100
        )


    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code , 200)




class AuthTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_registration(self):
        url = reverse('user_register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_jwt_login(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_protected_endpoint(self):
        # First authenticate
        login_url = reverse('token_obtain_pair')
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(login_url, login_data)
        token = login_response.data['access']

        # Test protected endpoint
        profile_url = reverse('user_profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_token_refresh(self):
        # First get refresh token
        login_url = reverse('token_obtain_pair')
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Test refresh
        refresh_url = reverse('token_refresh')
        response = self.client.post(refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

############################# TESTS PROFILE #####################################################################

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_profile_detail(self):
        url = reverse("profile-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        url = reverse("profile-update")
        data = {"phone": "+123456789", "city": "Paris"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)



 