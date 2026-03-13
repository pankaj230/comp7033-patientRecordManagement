import os
from flask import Flask, render_template, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

from app.routes.routes_auth import auth_bp
from app.routes.routes_records import records_bp
from app.routes.routes_admin import admin_bp
from app.auth import setup_error_handlers
from app.models import sqlite_db, mongodb

# ============================================================================
# Flask Application Initialization
# ============================================================================

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

jwt = JWTManager(app)
CORS(app)

# ============================================================================
# Register Blueprints
# ============================================================================

app.register_blueprint(auth_bp)
app.register_blueprint(records_bp)
app.register_blueprint(admin_bp)
setup_error_handlers(app)

# ============================================================================
# Public Routes (Frontend Pages)
# ============================================================================

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/patient-dashboard')
def patient_dashboard():
    return render_template('roleSpecificDashboard/patient_dashboard.html')

@app.route('/clinician-dashboard')
def clinician_dashboard():
    return render_template('roleSpecificDashboard/clinician_dashboard.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('roleSpecificDashboard/admin_dashboard.html')


# ============================================================================
# Health Check & Status Routes
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Patient Record Management System',
        'version': '1.0.0'
    }), 200


# ============================================================================
# Error Handlers for JSON API
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'message': 'Access forbidden'
    }), 403


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'message': 'Unauthorized'
    }), 401


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == '__main__':
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('SECRET_KEY=secret-key-here\n')
            f.write('JWT_SECRET=jwt-secret-here\n')
            f.write('MONGODB_URI=mongodb+srv://user:<pass>@cluster0.lnrqzpn.mongodb.net/ \n')

    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode
    )
