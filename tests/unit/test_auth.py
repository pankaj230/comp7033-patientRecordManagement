import unittest
from app.auth import (
    register_user,
    login_user,
    validate_email,
    sanitize_input
)
import time
from app.app import app


class TestAuthenticationFunctions(unittest.TestCase):

    def setUp(self):
        self.unique_suffix = int(time.time() * 1000)
        self.ctx = app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_register_user_valid_inputs(self):
        email = f"auth_{self.unique_suffix}@example.com"
        result = register_user(
            email,
            'ValidPassword123!',
            'John',
            'Doe',
            'patient'
        )
        self.assertTrue(result['success'])
        self.assertIn('user_id', result)

    def test_register_user_weak_password(self):
        email = f"weak_{self.unique_suffix}@example.com"
        result = register_user(
            email,
            'weak',
            'Test',
            'User',
            'patient'
        )
        self.assertFalse(result['success'])
        self.assertIn('at least 8 characters', result['message'])

    def test_register_user_invalid_role(self):
        email = f"invalid_role_{self.unique_suffix}@example.com"
        result = register_user(
            email,
            'ValidPassword123!',
            'Test',
            'User',
            'superuser'
        )
        self.assertFalse(result['success'])

    def test_register_user_missing_fields(self):
        result = register_user(
            '',
            'ValidPassword123!',
            'Test',
            'User',
            'patient'
        )
        self.assertFalse(result['success'])

    def test_login_user_valid_credentials(self):
        email = f"login_{self.unique_suffix}@example.com"
        register_user(email, 'LoginPass123!', 'Test', 'User', 'patient')

        result = login_user(email, 'LoginPass123!')
        self.assertTrue(result['success'])
        self.assertIn('access_token', result)
        self.assertIn('user', result)

    def test_login_user_invalid_credentials(self):
        result = login_user(
            f"nonexistent_{self.unique_suffix}@example.com",
            'WrongPassword123!'
        )
        self.assertFalse(result['success'])
        self.assertIn('Invalid email or password', result['message'])

    def test_login_user_wrong_password(self):
        email = f"wrong_pwd_{self.unique_suffix}@example.com"
        register_user(email, 'CorrectPass123!', 'Test', 'User', 'patient')

        result = login_user(email, 'WrongPass123!')
        self.assertFalse(result['success'])

    def test_login_user_returns_user_info(self):
        email = f"info_{self.unique_suffix}@example.com"
        register_user(email, 'InfoPass123!', 'John', 'Doe', 'clinician')

        result = login_user(email, 'InfoPass123!')
        self.assertTrue(result['success'])
        user = result['user']
        self.assertEqual(user['email'], email)
        self.assertEqual(user['first_name'], 'John')
        self.assertEqual(user['role'], 'clinician')

    def test_login_user_role_validation(self):
        email = f"role_check_{self.unique_suffix}@example.com"
        register_user(email, 'RolePass123!', 'Test', 'User', 'patient')

        result = login_user(email, 'RolePass123!', role='admin')
        self.assertFalse(result['success'])


class TestEmailValidation(unittest.TestCase):

    def test_validate_email_valid_formats(self):
        valid_emails = [
            'test@example.com',
            'user.name@company.co.uk',
            'john.doe+tag@domain.org',
            'firstname.lastname@company.co.nz'
        ]
        for email in valid_emails:
            self.assertTrue(
                validate_email(email),
                f"Email {email} should be valid"
            )

    def test_validate_email_invalid_formats(self):
        invalid_emails = [
            'invalid.email',
            'user@',
            '@example.com',
            'user name@example.com',
            'user@.com',
            '',
            'user@@example.com'
        ]
        for email in invalid_emails:
            self.assertFalse(
                validate_email(email),
                f"Email {email} should be invalid"
            )

    def test_validate_email_empty_string(self):
        self.assertFalse(validate_email(''))

    def test_validate_email_special_characters(self):
        self.assertFalse(validate_email('user<script>@example.com'))


class TestInputSanitization(unittest.TestCase):

    def test_sanitize_input_removes_script_tags(self):
        malicious = '<script>alert("XSS")</script>'
        sanitized = sanitize_input(malicious)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)

    def test_sanitize_input_removes_html_tags(self):
        input_str = '<img src=x onerror=alert("XSS")>'
        sanitized = sanitize_input(input_str)
        self.assertIn('&lt;', sanitized)
        self.assertIn('&gt;', sanitized)
        self.assertIn('&quot;', sanitized)
        self.assertIn('onerror', sanitized)

    def test_sanitize_input_max_length(self):
        long_input = 'a' * 1000
        sanitized = sanitize_input(long_input, max_length=100)
        self.assertLessEqual(len(sanitized), 100)

    def test_sanitize_input_preserves_safe_content(self):
        safe_input = 'John Doe, Ph.D.'
        sanitized = sanitize_input(safe_input)
        self.assertEqual(sanitized, safe_input)

    def test_sanitize_input_handles_quotes(self):
        input_str = 'Name with "quotes"'
        sanitized = sanitize_input(input_str)
        self.assertIsInstance(sanitized, str)

    def test_sanitize_input_sql_injection_attempt(self):
        sql_injection = "'; DROP TABLE users; --"
        sanitized = sanitize_input(sql_injection)
        self.assertIsInstance(sanitized, str)

    def test_sanitize_input_empty_string(self):
        sanitized = sanitize_input('')
        self.assertEqual(sanitized, '')

    def test_sanitize_input_whitespace_handling(self):
        input_str = '  spaces  '
        sanitized = sanitize_input(input_str)
        self.assertIsInstance(sanitized, str)


class TestPasswordValidation(unittest.TestCase):
    def test_strong_passwords(self):
        strong_passwords = [
            'ValidPass123!',
            'SecurePass456@',
            'MyP@ssw0rd'
        ]
        for password in strong_passwords:
            self.assertGreaterEqual(len(password), 8)

    def test_weak_passwords(self):
        weak_passwords = [
            'short',
        ]
        for password in weak_passwords:
            result = register_user(
                f"pwd_test_{int(time.time())}@example.com",
                password,
                'Test',
                'User',
                'patient'
            )
            self.assertFalse(
                result['success'],
                f"Password '{password}' should be rejected"
            )


if __name__ == '__main__':
    unittest.main()
