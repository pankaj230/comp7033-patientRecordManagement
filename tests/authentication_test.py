import unittest
import json
import time
from app.app import app
from app.auth import register_user

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_register_user_success(self):
        """Test successful user registration"""
        unique_suffix = int(time.time() * 1000)
        email = f"dbtest_{unique_suffix}@example.com"
        result = register_user(
            email,
            'TestPassword123!',
            'Test',
            'User',
            'patient'
        )
        self.assertTrue(result['success'])
        self.assertIn('user_id', result)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        register_user('duplicate@example.com', 'Pass123!', 'Test', 'User', 'patient')
        result = register_user('duplicate@example.com', 'Pass123!', 'Test', 'User', 'patient')
        self.assertFalse(result['success'])
        self.assertIn('already exists', result['message'])

    def test_register_user_weak_password(self):
        """Test registration with weak password"""
        result = register_user(
            'tests@example.com',
            'weak',
            'Test',
            'User',
            'patient'
        )
        self.assertFalse(result['success'])
        self.assertIn('at least 8 characters', result['message'])


    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')