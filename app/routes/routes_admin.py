from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.auth import admin_required, log_audit, sanitize_input, register_user
from app.models import sqlite_db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================================================
# User Management Routes
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (Admin and Clinician)"""
    try:
        identity = get_jwt_identity()
        user_id = int(identity)
        user = sqlite_db.get_user_by_id(user_id)
        if not user or user['role'] not in ['admin', 'clinician']:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403

        conn = sqlite_db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, email, first_name, last_name, role, is_active, created_at
            FROM users
            ORDER BY created_at DESC
        ''')

        users = cursor.fetchall()
        conn.close()

        users_list = [
            {
                'id': user[0],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'role': user[4],
                'is_active': user[5],
                'created_at': user[6]
            }
            for user in users
        ]

        identity = get_jwt_identity()
        log_audit('READ', 'all_users', '')

        return jsonify({
            'success': True,
            'users': users_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving users: {str(e)}'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    try:
        user = sqlite_db.get_user_by_id(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        log_audit('READ', 'user_details', str(user_id))

        return jsonify({
            'success': True,
            'user': user
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving user: {str(e)}'
        }), 500


@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user (Clinician or Admin) - Admin only"""
    try:
        data = request.get_json() or {}

        email = sanitize_input(data.get('email', '').strip())
        password = data.get('password', '').strip()
        first_name = sanitize_input(data.get('first_name', '').strip())
        last_name = sanitize_input(data.get('last_name', '').strip())
        role = data.get('role', 'clinician').strip()

        if not all([email, password, first_name, last_name]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        if role not in ['clinician', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Invalid role. Must be clinician or admin.'
            }), 400

        result = register_user(email, password, first_name, last_name, role)

        if result['success']:
            identity = get_jwt_identity()
            log_audit('CREATE', 'user', str(result.get('user_id')),
                     f'Role: {role}, Created by {identity.get("email")}')

            return jsonify({
                'success': True,
                'message': result['message'],
                'user_id': result.get('user_id')
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating user: {str(e)}'
        }), 500


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@admin_required
def toggle_user_status(user_id):
    try:
        user = sqlite_db.get_user_by_id(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        identity = get_jwt_identity()
        if identity.get('id') == user_id and not user['is_active']:
            return jsonify({
                'success': False,
                'message': 'Cannot disable your own account'
            }), 400

        new_status = not user['is_active']
        conn = sqlite_db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users SET is_active = ? WHERE id = ?
        ''', (new_status, user_id))

        conn.commit()
        conn.close()

        log_audit('UPDATE', 'user_status', str(user_id),
                 f'Status changed to: {"active" if new_status else "inactive"}')

        return jsonify({
            'success': True,
            'message': f'User {"activated" if new_status else "deactivated"} successfully',
            'is_active': new_status
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating user status: {str(e)}'
        }), 500


@admin_bp.route('/admins', methods=['GET'])
@admin_required
def get_admins():
    try:
        conn = sqlite_db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, email, first_name, last_name, role, is_active, created_at
            FROM users WHERE role = 'admin' ORDER BY created_at DESC
        """)
        admins = cursor.fetchall()
        conn.close()
        admins_list = [
            {
                'id': a[0],
                'email': a[1],
                'first_name': a[2],
                'last_name': a[3],
                'role': a[4],
                'is_active': a[5],
                'created_at': a[6]
            }
            for a in admins
        ]
        return jsonify({'success': True, 'admins': admins_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error retrieving admins: {str(e)}'}), 500


# ============================================================================
# Audit Log Routes
# ============================================================================

@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get audit logs (Admin only)"""
    try:
        limit = request.args.get('limit', default=100, type=int)

        if limit > 1000:
            limit = 1000  # Cap at 1000

        logs = sqlite_db.get_audit_logs(limit=limit)

        return jsonify({
            'success': True,
            'logs': logs
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving audit logs: {str(e)}'
        }), 500


@admin_bp.route('/audit-logs/user/<int:user_id>', methods=['GET'])
@admin_required
def get_user_audit_logs(user_id):
    try:
        limit = request.args.get('limit', default=50, type=int)

        conn = sqlite_db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, user_id, action, resource, resource_id, details, timestamp
            FROM audit_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))

        logs = cursor.fetchall()
        conn.close()

        logs_list = [
            {
                'id': log[0],
                'user_id': log[1],
                'action': log[2],
                'resource': log[3],
                'resource_id': log[4],
                'details': log[5],
                'timestamp': log[6]
            }
            for log in logs
        ]

        return jsonify({
            'success': True,
            'logs': logs_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving audit logs: {str(e)}'
        }), 500


# ============================================================================
# Dashboard Routes
# ============================================================================

@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics (Admin only)"""
    try:
        conn = sqlite_db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT role, COUNT(*) FROM users GROUP BY role
        ''')

        role_stats = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM audit_logs')
        total_logs = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'role_breakdown': role_stats,
                'total_audit_logs': total_logs
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving dashboard stats: {str(e)}'
        }), 500


# @admin_bp.route('/seed-clinicians', methods=['POST'])
# @admin_required
# def seed_clinicians():
#     try:
#         clinicians = [
#             {'email': f'dr{i}@hospital.com', 'password': f'clinician{i}2026', 'first_name': f'Dr{i}', 'last_name': f'Clinician{i}', 'role': 'clinician'}
#             for i in range(2, 12)
#         ]
#         created = []
#         for c in clinicians:
#             result = register_user(c['email'], c['password'], c['first_name'], c['last_name'], c['role'])
#             if result['success']:
#                 created.append({'email': c['email'], 'password': c['password'], 'user_id': result['user_id']})
#         return jsonify({'success': True, 'created': created}), 201
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500
