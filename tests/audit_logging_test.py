import unittest
from app.models import sqlite_db


class TestAuditLogging(unittest.TestCase):
    def test_add_audit_log(self):
        """Test adding audit log entry"""
        result = sqlite_db.add_audit_log(
            user_id=1,
            action='CREATE',
            resource='patient_record',
            resource_id='123',
            details='Test audit log',
            ip_address='127.0.0.1'
        )
        self.assertTrue(result)

    def test_get_audit_logs(self):
        """Test retrieving audit logs"""
        sqlite_db.add_audit_log(1, 'READ', 'user', '1')
        sqlite_db.add_audit_log(1, 'UPDATE', 'record', '2')
        logs = sqlite_db.get_audit_logs(limit=10)
        self.assertGreater(len(logs), 0)