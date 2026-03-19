import unittest
import json
import time
from app.app import app
from app.models import sqlite_db, mongodb
from app.auth import register_user, login_user


class TestAuthenticationDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_user_registration_persists_to_database(self):
        email = f"persist_{self.unique_suffix}@example.com"
        register_user(email, 'PersistPass123!', 'Persist', 'Test', 'patient')

        user = sqlite_db.get_user_by_email(email)
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], email)
        self.assertEqual(user['first_name'], 'Persist')

    def test_password_hashing_in_database(self):
        email = f"hash_{self.unique_suffix}@example.com"
        password = 'HashPass123!'
        register_user(email, password, 'Hash', 'Test', 'patient')

        user = sqlite_db.get_user_by_email(email)
        self.assertNotEqual(user['password_hash'], password)
        self.assertTrue(sqlite_db.verify_password(password, user['password_hash']))

    def test_login_with_database_verification(self):
        email = f"verify_{self.unique_suffix}@example.com"
        password = 'VerifyPass123!'
        register_user(email, password, 'Verify', 'Test', 'patient')

        result = login_user(email, password)
        self.assertTrue(result['success'])

        result = login_user(email, 'WrongPass123!')
        self.assertFalse(result['success'])


class TestAuditLoggingIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_login_creates_audit_log(self):
        email = f"login_audit_{self.unique_suffix}@example.com"
        register_user(email, 'AuditPass123!', 'Audit', 'Test', 'patient')

        login_user(email, 'AuditPass123!')

        logs = sqlite_db.get_audit_logs(limit=100)
        self.assertGreater(len(logs), 0)


class TestPatientRecordDatabaseIntegration(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_patient_id = int(time.time() * 1000000)

    def tearDown(self):
        if mongodb.connected:
            mongodb.delete_patient_record(self.unique_patient_id)
        self.ctx.pop()

    def test_create_and_retrieve_patient_record(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        data = {
            'medical_history': 'Integration test history',
            'allergies': 'Ibuprofen',
            'blood_type': 'AB+',
            'age': 50
        }

        create_result = mongodb.create_patient_record(self.unique_patient_id, data)
        self.assertTrue(create_result)

        record = mongodb.get_patient_record(self.unique_patient_id)
        self.assertIsNotNone(record)
        self.assertEqual(record['patient_id'], self.unique_patient_id)
        self.assertEqual(record['allergies'], 'Ibuprofen')

    def test_update_existing_patient_record(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        initial_data = {'medical_history': 'Initial', 'blood_type': 'O+'}
        mongodb.create_patient_record(self.unique_patient_id, initial_data)

        update_data = {'medical_history': 'Updated after integration test'}
        update_result = mongodb.update_patient_record(self.unique_patient_id, update_data)
        self.assertTrue(update_result)

        record = mongodb.get_patient_record(self.unique_patient_id)
        self.assertEqual(record['medical_history'], 'Updated after integration test')

    def test_appointment_lifecycle(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        from datetime import datetime, timedelta

        appointment_date = (datetime.now() + timedelta(days=7)).isoformat()

        create_result = mongodb.create_appointment(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            appointment_date=appointment_date,
            reason='Integration test appointment'
        )
        self.assertTrue(create_result)

        appointments = mongodb.get_patient_appointments(self.unique_patient_id)
        self.assertIsInstance(appointments, list)

    def test_prescription_workflow(self):
        clinician_email = f"clinician_{int(time.time() * 1000)}@example.com"
        register_user(clinician_email, 'ClinicianPass123!', 'Test', 'Clinician', 'clinician')
        clinician_login = login_user(clinician_email, 'ClinicianPass123!')
        clinician_token = clinician_login['access_token']

        patient_email = f"patient_{int(time.time() * 1000)}@example.com"
        register_user(patient_email, 'PatientPass123!', 'Test', 'Patient', 'patient')
        patient = sqlite_db.get_user_by_email(patient_email)
        patient_id = patient['id']

        response = self.app.post(
            '/api/records/prescriptions',
            headers={'Authorization': f'Bearer {clinician_token}'},
            json={
                'patient_id': patient_id,
                'medication': 'Metformin',
                'dosage': '500mg',
                'duration': '30 days'
            }
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.get(
            f'/api/records/patient/{patient_id}/prescriptions',
            headers={'Authorization': f'Bearer {clinician_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_prescription_lifecycle(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        create_result = mongodb.create_prescription(
            patient_id=self.unique_patient_id,
            clinician_id=1,
            medication='Integration Test Drug',
            dosage='250mg',
            duration='45 days'
        )
        self.assertTrue(create_result)

        prescriptions = mongodb.get_patient_prescriptions(self.unique_patient_id)
        self.assertIsInstance(prescriptions, list)


class TestAPIIntegrationWithDatabase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

        self.admin_email = f"admin_{self.unique_suffix}@example.com"
        register_user(self.admin_email, 'AdminPass123!', 'Admin', 'Test', 'admin')
        self.admin_token = login_user(self.admin_email, 'AdminPass123!')['access_token']

    def tearDown(self):
        self.ctx.pop()

    def test_create_user_via_api_persists_to_database(self):
        new_email = f"created_{self.unique_suffix}@example.com"

        response = self.app.post(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'email': new_email,
                'password': 'NewPass123!',
                'first_name': 'API',
                'last_name': 'Created',
                'role': 'clinician'
            }
        )
        self.assertEqual(response.status_code, 201)

        user = sqlite_db.get_user_by_email(new_email)
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'clinician')

    def test_get_users_via_api_returns_database_data(self):
        response = self.app.get(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['users']), 0)

    def test_dashboard_stats_integration(self):
        response = self.app.get(
            '/api/admin/dashboard-stats',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('stats', data)
        self.assertIn('total_users', data['stats'])


class TestEndToEndUserJourney(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_patient_complete_journey(self):
        patient_email = f"journey_patient_{self.unique_suffix}@example.com"
        clinician_email = f"journey_clinician_{self.unique_suffix}@example.com"

        response = self.app.post('/auth/register', json={
            'email': patient_email,
            'password': 'PatientJourney123!',
            'first_name': 'Journey',
            'last_name': 'Patient',
            'role': 'patient'
        })
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/auth/register', json={
            'email': clinician_email,
            'password': 'ClinicianJourney123!',
            'first_name': 'Journey',
            'last_name': 'Clinician',
            'role': 'clinician'
        })
        self.assertEqual(response.status_code, 200)

        patient_login = login_user(patient_email, 'PatientJourney123!')
        self.assertTrue(patient_login['success'])
        patient_token = patient_login['access_token']
        patient_id = patient_login['user']['id']

        clinician_login = login_user(clinician_email, 'ClinicianJourney123!')
        self.assertTrue(clinician_login['success'])
        clinician_token = clinician_login['access_token']

        response = self.app.post(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {clinician_token}'},
            json={
                'medical_history': 'Patient journey test',
                'allergies': 'Journey test allergens',
                'blood_type': 'B+'
            }
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.get(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {patient_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('record', data)

    def test_clinician_admin_collaboration(self):
        clinician_email = f"collab_clinic_{self.unique_suffix}@example.com"
        admin_email = f"collab_admin_{self.unique_suffix}@example.com"
        patient_email = f"collab_patient_{self.unique_suffix}@example.com"

        register_user(clinician_email, 'ClinicPass123!', 'Collab', 'Clinician', 'clinician')
        register_user(admin_email, 'AdminPass123!', 'Collab', 'Admin', 'admin')
        register_user(patient_email, 'PatientPass123!', 'Collab', 'Patient', 'patient')

        clinician_token = login_user(clinician_email, 'ClinicPass123!')['access_token']
        admin_token = login_user(admin_email, 'AdminPass123!')['access_token']
        patient_id = login_user(patient_email, 'PatientPass123!')['user']['id']

        response = self.app.post(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {clinician_token}'},
            json={'medical_history': 'Collaboration test', 'blood_type': 'AB+'}
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.get(
            '/api/admin/audit-logs',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()

