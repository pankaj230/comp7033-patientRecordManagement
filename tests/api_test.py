import unittest
import json
from app.app import app
from app.models import sqlite_db
from app.auth import register_user, login_user



class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up tests client and application context"""
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()

        with self.ctx:
            result = register_user(
                'apitest@example.com',
                'ApiTest123!',
                'API',
                'Test',
                'patient'
            )
            if not result['success']:
                print(f"User registration failed: {result}")
            login_result = login_user('apitest@example.com', 'ApiTest123!')
            if not login_result['success']:
                print(f"Login failed: {login_result}")
            self.token = login_result['access_token']
            self.user_id = login_result['user']['id']

    def tearDown(self):
        """Clean up test data"""
        if hasattr(self, 'unique_suffix'):
            user = sqlite_db.get_user_by_email(f"newuser_{self.unique_suffix}@example.com")
            if user:
                sqlite_db.delete_user(user['id'])
        self.ctx.pop()

    def test_login_endpoint(self):
        """Test login endpoint"""
        response = self.app.post('/auth/login', json={
            'email': 'apitest@example.com',
            'password': 'ApiTest123!'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = self.app.post('/auth/login', json={
            'email': 'apitest@example.com',
            'password': 'WrongPassword123!'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.app.post('/auth/login', json={
            'email': 'invalid@example.com',
            'password': 'WrongPass123!'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid email or password', data['message'])