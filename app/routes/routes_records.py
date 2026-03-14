from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.auth import log_audit, sanitize_input, clinician_required, patient_required
from app.models import sqlite_db, mongodb

records_bp = Blueprint('records', __name__, url_prefix='/api/records')


# ============================================================================
# Patient Record CRUD Operations
# ============================================================================

@records_bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_record(patient_id):
    try:
        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        if not user or not user['is_active']:
            return jsonify({
                'success': False,
                'message': 'User not found or inactive'
            }), 404
        user_role = user['role']

        if user_role == 'patient' and user_id != patient_id:
            return jsonify({
                'success': False,
                'message': 'Access denied. You can only view your own records.'
            }), 403

        patient = sqlite_db.get_user_by_id(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404

        record = mongodb.get_patient_record(patient_id)

        if not record:
            return jsonify({
                'success': False,
                'message': 'Medical record not found'
            }, 404)

        record.pop('_id', None)

        log_audit('READ', 'patient_record', str(patient_id))

        return jsonify({
            'success': True,
            'patient': patient,
            'record': record
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving patient record: {str(e)}'
        }), 500


@records_bp.route('/patient/<int:patient_id>', methods=['POST'])
@clinician_required
def create_patient_record(patient_id):
    try:
        patient = sqlite_db.get_user_by_id(patient_id)
        if not patient or patient['role'] != 'patient':
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404

        data = request.get_json() or {}

        record_data = {
            'medical_history': sanitize_input(data.get('medical_history', '')),
            'allergies': sanitize_input(data.get('allergies', '')),
            'blood_type': sanitize_input(data.get('blood_type', '')),
            'emergency_contact': sanitize_input(data.get('emergency_contact', ''))
        }

        success = mongodb.create_patient_record(patient_id, record_data)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to create patient record'
            }), 500

        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        log_audit('CREATE', 'patient_record', str(patient_id),
                 f'Created by {user["email"]}')

        return jsonify({
            'success': True,
            'message': 'Patient record created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating patient record: {str(e)}'
        }), 500


@records_bp.route('/patient/<int:patient_id>', methods=['PUT'])
@clinician_required
def update_patient_record(patient_id):
    """Update patient medical record (Clinician only)"""
    try:
        patient = sqlite_db.get_user_by_id(patient_id)
        if not patient or patient['role'] != 'patient':
            return jsonify({
                'success': False,
                'message': 'Patient not found'
            }), 404

        record = mongodb.get_patient_record(patient_id)
        if not record:
            return jsonify({
                'success': False,
                'message': 'Medical record not found. Create record first.'
            }), 404

        data = request.get_json() or {}

        update_data = {}
        if 'medical_history' in data:
            update_data['medical_history'] = sanitize_input(data['medical_history'])
        if 'allergies' in data:
            update_data['allergies'] = sanitize_input(data['allergies'])
        if 'blood_type' in data:
            update_data['blood_type'] = sanitize_input(data['blood_type'])
        if 'emergency_contact' in data:
            update_data['emergency_contact'] = sanitize_input(data['emergency_contact'])

        success = mongodb.update_patient_record(patient_id, update_data)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to update patient record'
            }), 500

        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        log_audit('UPDATE', 'patient_record', str(patient_id),
                 f'Updated by {user["email"]}')

        return jsonify({
            'success': True,
            'message': 'Patient record updated successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating patient record: {str(e)}'
        }), 500


@records_bp.route('/patient/<int:patient_id>/appointments', methods=['GET'])
@jwt_required()
def get_patient_appointments(patient_id):
    """Get all appointments for a patient"""
    try:
        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        if not user or not user['is_active']:
            return jsonify({
                'success': False,
                'message': 'User not found or inactive'
            }), 404
        user_role = user['role']

        if user_role == 'patient' and user_id != patient_id:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        appointments = mongodb.get_patient_appointments(patient_id)

        for apt in appointments:
            apt.pop('_id', None)

        log_audit('READ', 'appointments', str(patient_id))

        return jsonify({
            'success': True,
            'appointments': appointments
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving appointments: {str(e)}'
        }), 500


@records_bp.route('/patient/<int:patient_id>/prescriptions', methods=['GET'])
@jwt_required()
def get_patient_prescriptions(patient_id):
    try:
        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        if not user or not user['is_active']:
            return jsonify({
                'success': False,
                'message': 'User not found or inactive'
            }), 404
        user_role = user['role']

        if user_role == 'patient' and user_id != patient_id:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        prescriptions = mongodb.get_patient_prescriptions(patient_id)

        for presc in prescriptions:
            presc.pop('_id', None)

        log_audit('READ', 'prescriptions', str(patient_id))

        return jsonify({
            'success': True,
            'prescriptions': prescriptions
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving prescriptions: {str(e)}'
        }), 500


# ============================================================================
# Appointment Routes
# ============================================================================

@records_bp.route('/appointments', methods=['POST'])
@patient_required
def create_appointment():
    try:
        identity = get_jwt_identity()
        patient_id = int(identity)

        data = request.get_json() or {}
        if not all(k in data for k in ['clinician_id', 'appointment_date', 'reason']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        clinician_id = data.get('clinician_id')
        appointment_date = sanitize_input(data.get('appointment_date', ''))
        reason = sanitize_input(data.get('reason', ''))

        clinician = sqlite_db.get_user_by_id(clinician_id)
        if not clinician or clinician['role'] != 'clinician':
            return jsonify({
                'success': False,
                'message': 'Invalid clinician'
            }), 400

        success = mongodb.create_appointment(patient_id, clinician_id, appointment_date, reason)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to create appointment'
            }), 500

        log_audit('CREATE', 'appointment', '', f'Patient {patient_id} with clinician {clinician_id}')

        return jsonify({
            'success': True,
            'message': 'Appointment created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating appointment: {str(e)}'
        }), 500


# ============================================================================
# Prescription Routes
# ============================================================================

@records_bp.route('/prescriptions', methods=['POST'])
@clinician_required
def create_prescription():
    try:
        identity = get_jwt_identity()
        clinician_id = int(identity)

        data = request.get_json() or {}
        required_fields = ['patient_id', 'medication', 'dosage', 'duration']
        if not all(k in data for k in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        patient_id = data.get('patient_id')
        medication = sanitize_input(data.get('medication', ''))
        dosage = sanitize_input(data.get('dosage', ''))
        duration = sanitize_input(data.get('duration', ''))

        patient = sqlite_db.get_user_by_id(patient_id)
        if not patient or patient['role'] != 'patient':
            return jsonify({
                'success': False,
                'message': 'Invalid patient'
            }), 400

        success = mongodb.create_prescription(patient_id, clinician_id,
                                             medication, dosage, duration)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to create prescription'
            }), 500

        log_audit('CREATE', 'prescription', str(patient_id),
                 f'Medication: {medication}, Dosage: {dosage}')

        return jsonify({
            'success': True,
            'message': 'Prescription created successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating prescription: {str(e)}'
        }), 500


@records_bp.route('/clinicians', methods=['GET'])
@jwt_required()
def get_clinicians():
    try:
        conn = sqlite_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, email, first_name, last_name, role, is_active, created_at
            FROM users WHERE role = 'clinician' AND is_active = 1
            ORDER BY created_at DESC
        ''')
        clinicians = cursor.fetchall()
        conn.close()
        clinicians_list = [
            {
                'id': c[0],
                'email': c[1],
                'first_name': c[2],
                'last_name': c[3],
                'role': c[4],
                'is_active': c[5],
                'created_at': c[6]
            }
            for c in clinicians
        ]
        return jsonify({'success': True, 'clinicians': clinicians_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving clinicians: {str(e)}'}), 500


@records_bp.route('/clinician/patients', methods=['GET'])
@clinician_required
def get_clinician_patients():
    try:
        identity = get_jwt_identity()
        clinician_id = int(identity)
        # Example: patients assigned by appointments
        conn = sqlite_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT u.id, u.email, u.first_name, u.last_name, u.role, u.is_active, u.created_at
            FROM users u
            JOIN appointments a ON u.id = a.patient_id
            WHERE a.clinician_id = ? AND u.role = 'patient' AND u.is_active = 1
            ORDER BY u.created_at DESC
        ''', (clinician_id,))
        patients = cursor.fetchall()
        conn.close()
        patients_list = [
            {
                'id': p[0],
                'email': p[1],
                'first_name': p[2],
                'last_name': p[3],
                'role': p[4],
                'is_active': p[5],
                'created_at': p[6]
            }
            for p in patients
        ]
        return jsonify({'success': True, 'patients': patients_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving patients: {str(e)}'}), 500
