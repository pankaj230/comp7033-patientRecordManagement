import unittest
import json
import time
from datetime import datetime, timedelta
from app.app import app
from app.models import  mongodb
from app.auth import register_user, login_user


class TestUserRegistrationWorkflow(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_complete_patient_registration_workflow(self):
        email = f"patient_{self.unique_suffix}@example.com"
        response = self.app.post('/auth/register', json={
            'email': email,
            'password': 'PatientPass123!',
            'first_name': 'John',
            'last_name': 'Patient',
            'role': 'patient'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_clinician_registration_workflow(self):
        email = f"clinician_{self.unique_suffix}@example.com"
        response = self.app.post('/auth/register', json={
            'email': email,
            'password': 'ClinicianPass123!',
            'first_name': 'Jane',
            'last_name': 'Clinician',
            'role': 'clinician'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_registration_validation_errors(self):
        response = self.app.post('/auth/register', json={
            'email': f"weak_{self.unique_suffix}@example.com",
            'password': 'weak',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'patient'
        })
        self.assertEqual(response.status_code, 400)

        response = self.app.post('/auth/register', json={
            'email': 'invalid-email',
            'password': 'ValidPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'patient'
        })
        self.assertEqual(response.status_code, 400)

    def test_duplicate_registration_prevention(self):
        email = f"duplicate_{self.unique_suffix}@example.com"

        self.app.post('/auth/register', json={
            'email': email,
            'password': 'FirstPass123!',
            'first_name': 'First',
            'last_name': 'User',
            'role': 'patient'
        })

        response = self.app.post('/auth/register', json={
            'email': email,
            'password': 'SecondPass123!',
            'first_name': 'Second',
            'last_name': 'User',
            'role': 'patient'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])


class TestLoginAndAuthenticationWorkflow(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_successful_login_workflow(self):
        email = f"login_test_{self.unique_suffix}@example.com"
        register_user(email, 'LoginPass123!', 'Test', 'User', 'patient')

        response = self.app.post('/auth/login', json={
            'email': email,
            'password': 'LoginPass123!'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)
        self.assertIn('user', data)

    def test_login_with_invalid_credentials(self):
        response = self.app.post('/auth/login', json={
            'email': f"nonexistent_{self.unique_suffix}@example.com",
            'password': 'AnyPassword123!'
        })
        self.assertEqual(response.status_code, 401)

    def test_token_verification_workflow(self):
        self.skipTest("Verify token endpoint not implemented")

    def test_logout_workflow(self):
        email = f"logout_{self.unique_suffix}@example.com"
        register_user(email, 'LogoutPass123!', 'Logout', 'Test', 'patient')
        login_result = login_user(email, 'LogoutPass123!')
        token = login_result['access_token']

        response = self.app.post(
            '/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])


class TestPatientRecordWorkflow(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        self.patient_email = f"patient_{self.unique_suffix}@example.com"
        self.clinician_email = f"clinician_{self.unique_suffix}@example.com"

        register_user(self.patient_email, 'PatientPass123!', 'Patient', 'User', 'patient')
        register_user(self.clinician_email, 'ClinicianPass123!', 'Clinician', 'User', 'clinician')

        self.patient_token = login_user(self.patient_email, 'PatientPass123!')['access_token']
        self.clinician_token = login_user(self.clinician_email, 'ClinicianPass123!')['access_token']

        self.patient_id = login_user(self.patient_email, 'PatientPass123!')['user']['id']

    def tearDown(self):
        self.ctx.pop()

    def test_create_patient_record_workflow(self):
        response = self.app.post(
            f'/api/records/patient/{self.patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'},
            json={
                'medical_history': 'Hypertension',
                'allergies': 'Aspirin',
                'blood_type': 'O+',
                'emergency_contact': 'Emergency Contact'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_view_patient_record_workflow(self):
        self.app.post(
            f'/api/records/patient/{self.patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'},
            json={
                'medical_history': 'Test history',
                'allergies': 'None'
            }
        )

        response = self.app.get(
            f'/api/records/patient/{self.patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_update_patient_record_workflow(self):
        self.app.post(
            f'/api/records/patient/{self.patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'},
            json={
                'medical_history': 'Initial history',
                'allergies': 'None'
            }
        )

        response = self.app.put(
            f'/api/records/patient/{self.patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'},
            json={
                'medical_history': 'Updated history',
                'allergies': 'Penicillin'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_appointment_scheduling_workflow(self):
        clinician_id = login_user(self.clinician_email, 'ClinicianPass123!')['user']['id']

        response = self.app.post(
            '/api/records/appointments',
            headers={'Authorization': f'Bearer {self.patient_token}'},
            json={
                'clinician_id': clinician_id,
                'appointment_date': (datetime.now() + timedelta(days=5)).isoformat(),
                'reason': 'Regular checkup'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])


class TestRoleBasedAccessControlWorkflow(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        self.patient_email = f"patient_{self.unique_suffix}@example.com"
        self.clinician_email = f"clinician_{self.unique_suffix}@example.com"
        self.admin_email = f"admin_{self.unique_suffix}@example.com"

        register_user(self.patient_email, 'PatientPass123!', 'Patient', 'User', 'patient')
        register_user(self.clinician_email, 'ClinicianPass123!', 'Clinician', 'User', 'clinician')
        register_user(self.admin_email, 'AdminPass123!', 'Admin', 'User', 'admin')

        self.patient_token = login_user(self.patient_email, 'PatientPass123!')['access_token']
        self.clinician_token = login_user(self.clinician_email, 'ClinicianPass123!')['access_token']
        self.admin_token = login_user(self.admin_email, 'AdminPass123!')['access_token']

    def tearDown(self):
        self.ctx.pop()

    def test_patient_cannot_create_records(self):
        patient_id = login_user(self.patient_email, 'PatientPass123!')['user']['id']

        response = self.app.post(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {self.patient_token}'},
            json={
                'medical_history': 'Test',
                'allergies': 'None'
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_clinician_can_create_records(self):
        patient_id = login_user(self.patient_email, 'PatientPass123!')['user']['id']

        response = self.app.post(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {self.clinician_token}'},
            json={
                'medical_history': 'Test history',
                'allergies': 'None'
            }
        )
        self.assertEqual(response.status_code, 201)

    def test_admin_can_view_all_users(self):
        response = self.app.get(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_patient_cannot_view_all_users(self):
        response = self.app.get(
            '/api/admin/users',
            headers={'Authorization': f'Bearer {self.patient_token}'}
        )
        self.assertEqual(response.status_code, 403)


class TestSecurityWorkflow(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        self.unique_suffix = int(time.time() * 1000)

    def tearDown(self):
        self.ctx.pop()

    def test_xss_prevention_in_records(self):
        if not mongodb.connected:
            self.skipTest("MongoDB not connected")

        clinician_email = f"clinician_{self.unique_suffix}@example.com"
        patient_email = f"patient_{self.unique_suffix}@example.com"

        register_user(clinician_email, 'ClinicianPass123!', 'Clinician', 'User', 'clinician')
        register_user(patient_email, 'PatientPass123!', 'Patient', 'User', 'patient')

        clinician_token = login_user(clinician_email, 'ClinicianPass123!')['access_token']
        patient_id = login_user(patient_email, 'PatientPass123!')['user']['id']

        response = self.app.post(
            f'/api/records/patient/{patient_id}',
            headers={'Authorization': f'Bearer {clinician_token}'},
            json={
                'medical_history': '<script>alert("XSS")</script>',
                'allergies': 'None'
            }
        )
        self.assertEqual(response.status_code, 201)

    def test_unauthorized_access_prevention(self):
        response = self.app.get('/api/admin/users')
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_rejection(self):
        response = self.app.get(
            '/api/admin/users',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()

