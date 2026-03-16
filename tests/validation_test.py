import unittest
from app.auth import validate_email, sanitize_input
from app.validation import (
    validate_password,
    validate_email,
    validate_role,
    sanitize_input,
    validate_date,
    validate_min_length,
    validate_max_length,
    validate_numeric,
    validate_required,
    validate_combined
)
from tests.api_test import TestAPI
from tests.authentication_test import TestAuthentication
from tests.database_test import TestDatabase
from tests.audit_logging_test import TestAuditLogging


class TestValidation(unittest.TestCase):
    def test_validate_email_valid(self):
        """Test email validation with valid email"""
        self.assertTrue(validate_email('tests@example.com'))
        self.assertTrue(validate_email('user.name@company.co.uk'))

    def test_validate_email_invalid(self):
        """Test email validation with invalid email"""
        self.assertFalse(validate_email('invalid.email'))
        self.assertFalse(validate_email('user@'))
        self.assertFalse(validate_email('@example.com'))

    def test_sanitize_input_xss(self):
        """Test XSS prevention via input sanitization"""
        malicious = '<script>alert("XSS")</script>'
        sanitized = sanitize_input(malicious)
        self.assertNotIn('<script>', sanitized)
        self.assertNotIn('</script>', sanitized)

    def test_sanitize_input_max_length(self):
        """Test input truncation"""
        long_input = 'a' * 1000
        sanitized = sanitize_input(long_input, max_length=100)
        self.assertEqual(len(sanitized), 100)

    def test_validate_password_valid(self):
        """Test valid password validation"""
        self.assertTrue(validate_password('StrongPass123!'))

    def test_validate_password_weak(self):
        """Test weak password validation"""
        self.assertFalse(validate_password('weak'))
        self.assertFalse(validate_password('NoSpecial123'))  # Missing special character

    def test_validate_role_valid(self):
        """Test valid role validation"""
        self.assertTrue(validate_role('patient'))
        self.assertTrue(validate_role('clinician'))
        self.assertTrue(validate_role('admin'))

    def test_validate_role_invalid(self):
        """Test invalid role validation"""
        self.assertFalse(validate_role('invalid_role'))

    def test_validate_empty_input(self):
        """Test empty input validation"""
        self.assertFalse(validate_email(''))
        self.assertFalse(validate_password(''))

    def test_sanitize_special_characters(self):
        """Test sanitization of special characters"""
        input_str = 'Hello<script>alert("XSS")</script>'
        sanitized = sanitize_input(input_str)
        self.assertNotIn('<script>', sanitized)

    def test_validate_date_valid(self):
        """Test valid date format"""
        self.assertTrue(validate_date('2024-04-05'))

    def test_validate_date_invalid(self):
        """Test invalid date format"""
        self.assertFalse(validate_date('invalid-date'))

    def test_validate_min_length(self):
        """Test minimum length validation"""
        self.assertTrue(validate_min_length('12345678', 8))
        self.assertFalse(validate_min_length('1234567', 8))

    def test_validate_max_length(self):
        """Test maximum length validation"""
        self.assertTrue(validate_max_length('a' * 50, 100))
        self.assertFalse(validate_max_length('a' * 150, 100))

    def test_validate_numeric_input(self):
        """Test numeric input validation"""
        self.assertTrue(validate_numeric('12345'))
        self.assertFalse(validate_numeric('abc123'))

    def test_validate_email_format(self):
        """Test email format validation"""
        self.assertTrue(validate_email('test@example.com'))
        self.assertFalse(validate_email('invalid-email'))

    def test_validate_required_field(self):
        """Test required field validation"""
        self.assertTrue(validate_required('value'))
        self.assertFalse(validate_required(''))

    def test_validate_combined(self):
        """Test combined validation (email + password)"""
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123!'
        }
        self.assertTrue(validate_combined(data))

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestAPI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
