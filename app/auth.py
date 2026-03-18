import os
from functools import wraps
from datetime import timedelta
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import sqlite_db

# ============================================================================
# JWT Configuration
# ============================================================================

JWT_CONFIG = {
    'JWT_SECRET_KEY': os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production'),
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=24)
}


# ============================================================================
# Authentication Functions
# ============================================================================

def register_user(email: str, password: str, first_name: str,
                 last_name: str, role: str) -> dict:
    if not email or not password or not first_name or not last_name:
        return {'success': False, 'message': 'Missing required fields'}
    if len(password) < 8:
        return {'success': False, 'message': 'Password must be at least 8 characters'}

    if role not in ['patient', 'clinician', 'admin']:
        return {'success': False, 'message': 'Invalid role'}
    result = sqlite_db.create_user(email, password, first_name, last_name, role)
    return result


def login_user(email: str, password: str, role: str = None) -> dict:
    if not email or not password:
        return {
            'success': False,
            'message': 'Email and password are required'
        }
    user = sqlite_db.get_user_by_email(email)
    if not user:
        return {
            'success': False,
            'message': 'Invalid email or password'
        }
    if not isinstance(user, dict):
        return {
            'success': False,
            'message': 'Database error'
        }
    if not user['is_active']:
        return {
            'success': False,
            'message': 'Account is inactive'
        }
    if not sqlite_db.verify_password(password, user['password_hash']):
        return {
            'success': False,
            'message': 'Invalid email or password'
        }

    if role and user['role'] != role:
        return {
            'success': False,
            'message': 'Account does not have the selected role'
        }

    access_token = create_access_token(
        identity=str(user['id'])
    )

    return {
        'success': True,
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role']
        }
    }


# ============================================================================
# RBAC (Role-Based Access Control) Decorators
# ============================================================================

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user_id = int(identity)
            user = sqlite_db.get_user_by_id(user_id)
            if not user or not user['is_active']:
                return jsonify({
                    'success': False,
                    'message': 'User not found or inactive'
                }), 401
            user_role = user['role']

            if user_role not in roles:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. Insufficient permissions.'
                }), 403

            return fn(*args, **kwargs)

        return wrapper
    return decorator


def admin_required(fn):
    return role_required('admin')(fn)


def clinician_required(fn):
    return role_required('clinician', 'admin')(fn)


def patient_required(fn):
    return role_required('patient', 'clinician', 'admin')(fn)


# ============================================================================
# Audit Logging
# ============================================================================

def log_audit(action: str, resource: str, resource_id: str = None,
              details: str = None, user_id: int = None):
    try:
        if user_id is None:
            try:
                identity = get_jwt_identity()
                user_id = int(identity)
            except Exception:
                return
        ip_address = request.remote_addr

        sqlite_db.add_audit_log(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address
        )
    except Exception as e:
        print(f"Error logging audit: {str(e)}")


# ============================================================================
# Input Validation & Sanitization
# ============================================================================

def sanitize_input(data: str, max_length: int = 500) -> str:
    if not isinstance(data, str):
        return str(data)
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }

    result = ''.join(html_escape_table.get(c, c) for c in data)
    return result[:max_length]


def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ============================================================================
# Error Handlers
# ============================================================================

def setup_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'success': False, 'message': 'Access forbidden'}), 403

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401

