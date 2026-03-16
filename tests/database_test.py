import unittest
import bcrypt
import time
from app.models import sqlite_db

class TestDatabase(unittest.TestCase):
    def test_create_user1(self):
        """Test creating a user in database"""
        unique_suffix = int(time.time() * 1000)
        email = f"dbtest_{unique_suffix}@example.com"

        password_hash = bcrypt.hashpw('TestPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        result = sqlite_db.create_user(
            email,
            password_hash,
            'Database',
            'Test',
            'patient'
        )
        self.assertTrue(result['success'])
        self.assertIn('user_id', result)

    def test_get_user_by_email(self):
        """Test retrieving user by email"""
        sqlite_db.create_user(
            'retrieve@example.com',
            'TestPass123!',
            'Retrieve',
            'Test',
            'patient'
        )
        user = sqlite_db.get_user_by_email('retrieve@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], 'retrieve@example.com')

    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        unique_suffix = int(time.time() * 1000)
        email = f"dbtest_{unique_suffix}@example.com"
        result = sqlite_db.create_user(
            email,
            'TestPass123!',
            'ById',
            'Test',
            'patient'
        )
        user_id = result['user_id']
        user = sqlite_db.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], user_id)

    def test_verify_password(self):
        """Test password verification"""
        password = "TestPassword123!"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.assertTrue(sqlite_db.verify_password(password, password_hash))
        self.assertFalse(sqlite_db.verify_password("WrongPassword", password_hash))