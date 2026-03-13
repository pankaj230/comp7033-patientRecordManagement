from flask import Blueprint, render_template, request, url_for, session, jsonify
from app.auth import register_user, login_user, log_audit, validate_email, sanitize_input
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Display registration page"""
    return render_template('register.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or request.form

        # Extract and sanitize input
        email = sanitize_input(data.get('email', '').strip())
        password = data.get('password', '').strip()
        first_name = sanitize_input(data.get('first_name', '').strip())
        last_name = sanitize_input(data.get('last_name', '').strip())
        role = data.get('role', 'patient').strip()

        if not all([email, password, first_name, last_name]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400

        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }), 400

        if role not in ['patient']:
            return jsonify({
                'success': False,
                'message': 'Invalid role. Only patient registration is allowed.'
            }), 400

        result = register_user(email, password, first_name, last_name, role)

        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'redirect': url_for('auth.login_page')
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration error: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or request.form

        email = sanitize_input(data.get('email', '').strip())
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        result = login_user(email, password, role)

        if result['success']:
            session['user'] = result['user']
            session['access_token'] = result['access_token']

            try:
                log_audit('LOGIN', 'user_authentication', str(result['user']['id']))
            except:
                pass

            return jsonify({
                'success': True,
                'message': result['message'],
                'access_token': result['access_token'],
                'user': result['user'],
                'redirect': _get_dashboard_redirect(result['user']['role'])
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        identity = get_jwt_identity()
        user_id = identity.get('id')

        log_audit('LOGOUT', 'user_authentication', str(user_id))

        session.clear()

        return jsonify({
            'success': True,
            'message': 'Logged out successfully',
            'redirect': url_for('home')
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout error: {str(e)}'
        }), 500


@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token validity"""
    try:
        identity = get_jwt_identity()
        return jsonify({
            'success': True,
            'valid': True,
            'user': identity
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'message': str(e)
        }), 401


# ============================================================================
# Helper Functions
# ============================================================================

def _get_dashboard_redirect(role: str) -> str:
    role_redirects = {
        'patient': url_for('patient_dashboard'),
        'clinician': url_for('clinician_dashboard'),
        'admin': url_for('admin_dashboard')
    }
    return role_redirects.get(role, url_for('home'))
