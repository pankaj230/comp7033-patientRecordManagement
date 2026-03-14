import sqlite3
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo import MongoClient
import os

# ============================================================================
# SQLite Database (Authentication)
# ============================================================================

class SQLiteDB:

    def __init__(self, db_path: str = 'auth.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('patient', 'clinician', 'admin')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_user(self, email: str, password: str, first_name: str,
                   last_name: str, role: str) -> Dict[str, Any]:
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, password_hash, first_name, last_name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (email, password_hash, first_name, last_name, role))
                user_id = cursor.lastrowid
                conn.commit()
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
        except sqlite3.IntegrityError:
            return {
                'success': False,
                'message': 'Email already exists'
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, email, password_hash, first_name, last_name, role, is_active
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'password_hash': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'role': user[5],
                'is_active': user[6]
            }
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, email, first_name, last_name, role, is_active
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'role': user[4],
                'is_active': user[5]
            }
        return None

    def verify_password(self, password: str, password_hash: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)

    def add_audit_log(self, user_id: int, action: str, resource: str,
                     resource_id: Optional[str] = None, details: Optional[str] = None,
                     ip_address: Optional[str] = None) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_logs 
                    (user_id, action, resource, resource_id, details, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, action, resource, resource_id, details, ip_address))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding audit log: {str(e)}")
            return False

    def get_audit_logs(self, limit: int = 100) -> list:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT al.id, u.email, al.action, al.resource, al.resource_id, 
                       al.details, al.timestamp
                FROM audit_logs al
                JOIN users u ON al.user_id = u.id
                ORDER BY al.timestamp DESC
                LIMIT ?
            ''', (limit,))
            logs = cursor.fetchall()
        return [
            {
                'id': log[0],
                'user_email': log[1],
                'action': log[2],
                'resource': log[3],
                'resource_id': log[4],
                'details': log[5],
                'timestamp': log[6]
            }
            for log in logs
        ]


# ============================================================================
# MongoDB Database (Patient Records)
# ============================================================================

class MongoDB:
    def __init__(self, uri: str = None, db_name: str = 'Health'):
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb+srv://username:<passkey>@cluster0.lnrqzpn.mongodb.net/')
        self.db_name = db_name
        self.client = None
        self.db = None
        self.connected = False
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=20000, connectTimeoutMS=20000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.connected = True
            print("✓ Connected to MongoDB successfully")
        except Exception as e:
            print(f"⚠ MongoDB connection warning: {str(e)}")
            print("⚠ Running in MongoDB-lite mode. Patient records features will be limited.")
            self.client = None
            self.db = None
            self.connected = False

    def create_indexes(self):
        if self.db is not None:
            self.db.patient_records.create_index('patient_id', unique=True)
            self.db.patient_records.create_index('created_at')

            self.db.appointments.create_index([('patient_id', 1), ('appointment_date', 1)])
            self.db.appointments.create_index('clinician_id')
            self.db.prescriptions.create_index('patient_id')
            self.db.prescriptions.create_index('clinician_id')

    def create_patient_record(self, patient_id: int, data: Dict[str, Any]) -> bool:
        if not self.connected:
            print("⚠ MongoDB not available. Patient record not saved.")
            return False
        try:
            record = {
                'patient_id': patient_id,
                'medical_history': data.get('medical_history', ''),
                'allergies': data.get('allergies', ''),
                'blood_type': data.get('blood_type', ''),
                'emergency_contact': data.get('emergency_contact', ''),

                # Heart Disease/Diabetes Dataset Attributes
                'age': data.get('age', 0),
                'sex': data.get('sex', ''),
                'blood_pressure': data.get('blood_pressure', 0),
                'cholesterol': data.get('cholesterol', 0),
                'fasting_blood_sugar': data.get('fasting_blood_sugar', False),
                'resting_ecg': data.get('resting_ecg', 'Normal'),
                'exercise_induced_angina': data.get('exercise_induced_angina', False),

                # Additional clinical data
                'max_heart_rate': data.get('max_heart_rate', 0),
                'oldpeak': data.get('oldpeak', 0.0),
                'slope': data.get('slope', ''),
                'ca': data.get('ca', 0),
                'thal': data.get('thal', ''),

                'diagnosis': data.get('diagnosis', ''),
                'treatment_plan': data.get('treatment_plan', ''),
                'notes': data.get('notes', ''),

                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            self.db.patient_records.insert_one(record)
            return True
        except Exception as e:
            print(f"Error creating patient record: {str(e)}")
            return False

    def get_patient_record(self, patient_id: int) -> Optional[Dict[str, Any]]:
        if not self.connected:
            return None
        try:
            record = self.db.patient_records.find_one({'patient_id': patient_id})
            return record
        except Exception as e:
            print(f"Error retrieving patient record: {str(e)}")
            return None

    def update_patient_record(self, patient_id: int, data: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        try:
            data['updated_at'] = datetime.utcnow()
            self.db.patient_records.update_one(
                {'patient_id': patient_id},
                {'$set': data}
            )
            return True
        except Exception as e:
            print(f"Error updating patient record: {str(e)}")
            return False

    def create_appointment(self, patient_id: int, clinician_id: int,
                          appointment_date: str, reason: str) -> bool:
        if not self.connected:
            return False
        try:
            appointment = {
                'patient_id': patient_id,
                'clinician_id': clinician_id,
                'appointment_date': appointment_date,
                'reason': reason,
                'status': 'scheduled',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            self.db.appointments.insert_one(appointment)
            return True
        except Exception as e:
            print(f"Error creating appointment: {str(e)}")
            return False

    def get_patient_appointments(self, patient_id: int) -> list:
        if not self.connected:
            return []
        try:
            appointments = list(self.db.appointments.find({'patient_id': patient_id}))
            return appointments
        except Exception as e:
            print(f"Error retrieving appointments: {str(e)}")
            return []

    def create_prescription(self, patient_id: int, clinician_id: int,
                           medication: str, dosage: str, duration: str) -> bool:
        if not self.connected:
            return False
        try:
            prescription = {
                'patient_id': patient_id,
                'clinician_id': clinician_id,
                'medication': medication,
                'dosage': dosage,
                'duration': duration,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            self.db.prescriptions.insert_one(prescription)
            return True
        except Exception as e:
            print(f"Error creating prescription: {str(e)}")
            return False

    def get_patient_prescriptions(self, patient_id: int) -> list:
        if not self.connected:
            return []
        try:
            prescriptions = list(self.db.prescriptions.find({'patient_id': patient_id}))
            return prescriptions
        except Exception as e:
            print(f"Error retrieving prescriptions: {str(e)}")
            return []

    def close(self):
        if self.client:
            self.client.close()


sqlite_db = SQLiteDB()
mongodb = MongoDB()

