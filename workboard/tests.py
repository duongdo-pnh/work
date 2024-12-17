from django.contrib.auth.models import User
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

class AuthenticationTestCase(TestCase):
    
    def setUp(self):
        """
        Tạo người dùng test cho việc đăng nhập.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login(self):
        """
        Kiểm tra đăng nhập với JWT token.
        """
        url = reverse('token_obtain_pair')  # Lấy URL theo tên route
        
        data = {'username': 'testuser', 'password': 'testpassword'}
        
        response = self.client.post(url, data)
        
        # Kiểm tra mã trạng thái
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Kiểm tra xem token có được trả về không
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_login_invalid_credentials(self):
        """
        Kiểm tra đăng nhập với thông tin sai.
        """
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        
        response = self.client.post(url, data)
        
        # Kiểm tra mã trạng thái lỗi
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Kiểm tra xem response không trả về token
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

