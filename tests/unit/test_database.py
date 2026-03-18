import unittest
import bcrypt
import time
from app.models import sqlite_db, mongodb
from datetime import datetime, timedelta


class TestSQLiteDatabaseOperations(unittest.TestCase):

    def setUp(self):
        self.unique_suffix = int(time.time() * 1000)

    def test_create_user_success(self):
        email = f"unit_user_{self.unique_suffix}@example.com"
        result = sqlite_db.create_user(
            email,
            'TestPass123!',
            'Unit',
            'Test',
            'patient'
        )
        self.assertTrue(result['success'])
        self.assertIsInstance(result['user_id'], int)

    def test_get_user_by_email_existing(self):
        email = f"retrieve_{self.unique_suffix}@example.com"
        sqlite_db.create_user(email, 'Pass123!', 'Retrieve', 'Test', 'patient')

        user = sqlite_db.get_user_by_email(email)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], email)
        self.assertEqual(user['first_name'], 'Retrieve')
        self.assertEqual(user['role'], 'patient')

    def test_get_user_by_email_nonexistent(self):
        user = sqlite_db.get_user_by_email(f"nonexistent_{self.unique_suffix}@example.com")
        self.assertIsNone(user)

    def test_get_user_by_id_existing(self):
        email = f"byid_{self.unique_suffix}@example.com"
        result = sqlite_db.create_user(email, 'Pass123!', 'ById', 'Test', 'patient')
        user_id = result['user_id']

        user = sqlite_db.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], user_id)
        self.assertEqual(user['email'], email)

    def test_get_user_by_id_nonexistent(self):
        user = sqlite_db.get_user_by_id(99999)
        self.assertIsNone(user)

    def test_verify_password_correct(self):
        password = "CorrectPassword123!"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        is_valid = sqlite_db.verify_password(password, password_hash)
        self.assertTrue(is_valid)

    def test_verify_password_incorrect(self):
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword123!"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        is_valid = sqlite_db.verify_password(wrong_password, password_hash)
        self.assertFalse(is_valid)

    def test_create_user_duplicate_email(self):
        email = f"duplicate_{self.unique_suffix}@example.com"

        result1 = sqlite_db.create_user(email, 'Pass123!', 'First', 'User', 'patient')
        self.assertTrue(result1['success'])

        result2 = sqlite_db.create_user(email, 'Pass123!', 'Second', 'User', 'patient')
        self.assertFalse(result2['success'])
        self.assertIn('already exists', result2['message'])

    def test_user_fields_persisted(self):
        email = f"fields_{self.unique_suffix}@example.com"
        sqlite_db.create_user(email, 'Pass123!', 'John', 'Doe', 'clinician')

        user = sqlite_db.get_user_by_email(email)
        self.assertEqual(user['email'], email)
        self.assertEqual(user['first_name'], 'John')
        self.assertEqual(user['last_name'], 'Doe')
        self.assertEqual(user['role'], 'clinician')
        self.assertTrue(user['is_active'])


class TestAuditLogOperations(unittest.TestCase):

    def test_add_audit_log_success(self):
        result = sqlite_db.add_audit_log(
            user_id=1,
            action='CREATE',
            resource='patient_record',
            resource_id='123',
            details='Test audit log entry',
            ip_address='127.0.0.1'
        )
        self.assertTrue(result)

    def test_add_audit_log_without_optional_fields(self):
        result = sqlite_db.add_audit_log(
            user_id=1,
            action='READ',
            resource='user'
        )
        self.assertTrue(result)

    def test_get_audit_logs(self):
        sqlite_db.add_audit_log(1, 'READ', 'user', '1')
        sqlite_db.add_audit_log(1, 'UPDATE', 'record', '2')

        logs = sqlite_db.get_audit_logs(limit=100)
        self.assertGreater(len(logs), 0)
        self.assertIn('action', logs[0])
        self.assertIn('resource', logs[0])

    def test_get_audit_logs_limit(self):
        logs = sqlite_db.get_audit_logs(limit=10)
        self.assertLessEqual(len(logs), 10)

    def test_audit_log_structure(self):
        sqlite_db.add_audit_log(
            user_id=1,
            action='DELETE',
            resource='patient',
            resource_id='456',
            details='Patient deleted'
        )

        logs = sqlite_db.get_audit_logs(limit=1)
        if logs:
            log = logs[0]
            self.assertIn('id', log)
            self.assertIn('user_email', log)
            self.assertIn('action', log)
            self.assertIn('resource', log)
            self.assertIn('timestamp', log)


class TestMongoDBPatientRecords(unittest.TestCase):

    def setUp(self):
        self.unique_patient_id = int(time.time() * 1000) % 10000

    def test_create_patient_record(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        data = {
            'medical_history': 'Type 2 Diabetes',
            'allergies': 'Penicillin',
            'blood_type': 'O+',
            'age': 45,
            'sex': 'M'
        }

        result = mongodb.create_patient_record(self.unique_patient_id, data)
        self.assertTrue(result)

    def test_get_patient_record(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        data = {
            'medical_history': 'Hypertension',
            'allergies': 'Aspirin',
            'blood_type': 'A+'
        }
        mongodb.create_patient_record(self.unique_patient_id, data)

        record = mongodb.get_patient_record(self.unique_patient_id)
        if record:
            self.assertEqual(record['patient_id'], self.unique_patient_id)
            self.assertIn('medical_history', record)
            self.assertIn('created_at', record)

    def test_update_patient_record(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        data = {'medical_history': 'Initial diagnosis', 'blood_type': 'B+'}
        mongodb.create_patient_record(self.unique_patient_id, data)

        update_data = {'medical_history': 'Updated diagnosis'}
        result = mongodb.update_patient_record(self.unique_patient_id, update_data)
        self.assertTrue(result)

    def test_create_appointment(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        appointment_date = (datetime.now() + timedelta(days=5)).isoformat()
        result = mongodb.create_appointment(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            appointment_date=appointment_date,
            reason='Regular checkup'
        )
        self.assertTrue(result)

    def test_get_patient_appointments(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        appointment_date = (datetime.now() + timedelta(days=5)).isoformat()
        mongodb.create_appointment(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            appointment_date=appointment_date,
            reason='Checkup'
        )

        appointments = mongodb.get_patient_appointments(self.unique_patient_id)
        self.assertIsInstance(appointments, list)

    def test_create_prescription(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        result = mongodb.create_prescription(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            medication='Metformin',
            dosage='500mg',
            duration='30 days'
        )
        self.assertTrue(result)

    def test_get_patient_prescriptions(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        mongodb.create_prescription(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            medication='Aspirin',
            dosage='100mg',
            duration='60 days'
        )

        prescriptions = mongodb.get_patient_prescriptions(self.unique_patient_id)
        self.assertIsInstance(prescriptions, list)


if __name__ == '__main__':
    unittest.main()
