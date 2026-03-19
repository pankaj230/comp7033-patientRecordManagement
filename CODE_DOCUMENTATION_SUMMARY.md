# Code Documentation Summary

## Project Structure Overview

```
comp7033-patientRecordManagement/
├── run.py                      # Initialization and management script
├── run_tests.py               # Test runner script
├── requirements.txt           # Python dependencies
├── app/                       # Main application package
│   ├── __init__.py
│   ├── app.py                 # Flask application factory
│   ├── auth.py                # Authentication functions
│   ├── config.py              # Configuration and database setup
│   ├── models.py              # Database models and operations
│   ├── validation.py          # Input validation utilities
│   └── routes/                # API route handlers
│       ├── __init__.py
│       ├── routes_auth.py     # Authentication routes
│       ├── routes_records.py  # Patient records routes
│       └── routes_admin.py    # Administration routes
├── static/                    # Static assets
│   ├── css/                   # Stylesheets
│   ├── js/                    # Client-side JavaScript
│   │   ├── api/               # API client code
│   │   └── auth/              # Authentication utilities
│   └── prescriptions.css
├── templates/                 # Jinja2 templates
│   ├── base templates
│   ├── authentication pages
│   ├── dashboard pages
│   └── functional pages
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── functional/            # Functional tests
├── frontend/                  # Frontend source (TypeScript)
└── docs/                      # Documentation
```

## Core Modules Documentation

### app/app.py - Main Application

#### Flask Application Factory
```python
def create_app(config_name='development'):
    """Application factory pattern for Flask app creation"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(config[config_name])
    
    # Extensions
    jwt = JWTManager(app)
    CORS(app)
    
    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    setup_error_handlers(app)
    
    return app
```

#### Key Components
- **Configuration Management**: Environment-based configuration
- **Extension Setup**: JWT, CORS, database connections
- **Blueprint Registration**: Modular route organization
- **Error Handling**: Centralized error management

### app/auth.py - Authentication System

#### Core Functions

##### User Registration
```python
def register_user(email, password, first_name, last_name, role):
    """
    Register a new user with validation and security checks.
    
    Args:
        email (str): User's email address
        password (str): Plain text password
        first_name (str): User's first name
        last_name (str): User's last name
        role (str): User role ('admin', 'clinician', 'patient')
    
    Returns:
        dict: Registration result with success status and message
    """
```

##### User Login
```python
def login_user(email, password):
    """
    Authenticate user and generate JWT token.
    
    Args:
        email (str): User's email
        password (str): User's password
    
    Returns:
        dict: Login result with token and user info
    """
```

##### Password Security
```python
def hash_password(password):
    """Hash password using bcrypt with salt"""
    
def verify_password(password, hashed):
    """Verify password against hash"""
    
def validate_password(password):
    """Validate password strength requirements"""
```

##### Input Sanitization
```python
def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    
def validate_email(email):
    """Validate email format and security"""
```

### app/models.py - Database Models

#### SQLiteDB Class
```python
class SQLiteDB:
    """SQLite database operations for user management and audit logging"""
    
    def get_user_by_email(self, email):
        """Retrieve user by email address"""
    
    def get_user_by_id(self, user_id):
        """Retrieve user by ID"""
    
    def create_user(self, user_data):
        """Create new user record"""
    
    def verify_password(self, password, hashed):
        """Verify password hash"""
    
    def log_audit(self, action, resource, resource_id, details):
        """Log audit event"""
    
    def get_audit_logs(self, limit=100):
        """Retrieve audit logs"""
```

#### MongoDB Class
```python
class MongoDB:
    """MongoDB operations for patient records, appointments, prescriptions"""
    
    def create_patient_record(self, patient_id, data):
        """Create patient medical record"""
    
    def get_patient_record(self, patient_id):
        """Retrieve patient record"""
    
    def update_patient_record(self, patient_id, data):
        """Update patient record"""
    
    def create_appointment(self, patient_id, clinician_id, date, reason):
        """Create appointment"""
    
    def get_patient_appointments(self, patient_id):
        """Get patient appointments"""
    
    def create_prescription(self, patient_id, clinician_id, medication, dosage, duration):
        """Create prescription"""
    
    def get_patient_prescriptions(self, patient_id):
        """Get patient prescriptions"""
```

### app/routes/ - API Routes

#### routes_auth.py - Authentication Routes

##### Public Routes
```python
@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    
@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
```

#### routes_records.py - Records Management Routes

##### Patient Records
```python
@records_bp.route('/patient/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_record(patient_id):
    """Get patient medical record"""
    
@records_bp.route('/patient/<int:patient_id>', methods=['POST'])
@clinician_required
def create_patient_record(patient_id):
    """Create patient record"""
    
@records_bp.route('/patient/<int:patient_id>', methods=['PUT'])
@clinician_required
def update_patient_record(patient_id):
    """Update patient record"""
```

##### Appointments
```python
@records_bp.route('/appointments', methods=['POST'])
@patient_required
def create_appointment():
    """Create new appointment"""
    
@records_bp.route('/patient/<int:patient_id>/appointments', methods=['GET'])
@jwt_required()
def get_patient_appointments(patient_id):
    """Get patient appointments"""
```

##### Prescriptions
```python
@records_bp.route('/prescriptions', methods=['POST'])
@clinician_required
def create_prescription():
    """Create prescription"""
    
@records_bp.route('/patient/<int:patient_id>/prescriptions', methods=['GET'])
@jwt_required()
def get_patient_prescriptions(patient_id):
    """Get patient prescriptions"""
```

#### routes_admin.py - Administration Routes

##### User Management
```python
@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users"""
    
@admin_bp.route('/users', methods=['POST'])
@role_required('admin')
def create_user():
    """Create new user"""
    
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """Update user"""
```

##### System Management
```python
@admin_bp.route('/dashboard-stats', methods=['GET'])
@role_required('admin')
def get_dashboard_stats():
    """Get system statistics"""
    
@admin_bp.route('/audit-logs', methods=['GET'])
@role_required('admin')
def get_audit_logs():
    """Get audit logs"""
```

### app/validation.py - Input Validation

#### Validation Functions
```python
def validate_user_registration(data):
    """Validate user registration data"""
    
def validate_patient_record(data):
    """Validate patient record data"""
    
def validate_appointment(data):
    """Validate appointment data"""
    
def validate_prescription(data):
    """Validate prescription data"""
```

### Frontend Architecture

#### static/js/api/client.js - API Client

##### ApiClient Class
```javascript
class ApiClient {
    constructor(baseURL = '') {
        this.token = null;
        this.baseURL = baseURL || window.location.origin;
        this.loadTokenFromStorage();
    }
    
    async login(credentials) {
        // Login implementation
    }
    
    async register(userData) {
        // Registration implementation
    }
    
    async getPatientRecord(patientId) {
        // Get patient record
    }
    
    async createPrescription(prescriptionData) {
        // Create prescription
    }
    
    // Other API methods...
}
```

#### static/js/auth/manager.js - Authentication Manager

##### AuthManager Class
```javascript
class AuthManager {
    constructor() {
        this.apiClient = new ApiClient();
        this.currentUser = null;
        this.init();
    }
    
    async login(email, password) {
        // Login implementation
    }
    
    async register(userData) {
        // Registration implementation
    }
    
    logout() {
        // Logout implementation
    }
    
    isAuthenticated() {
        // Check authentication status
    }
    
    getCurrentUser() {
        // Get current user info
    }
}
```

## Test Suite Structure

### tests/unit/ - Unit Tests

#### test_auth.py
- Password hashing and verification
- Input sanitization
- Email validation
- User registration validation

#### test_database.py
- Database connection and operations
- User CRUD operations
- Audit logging
- MongoDB operations (when available)

### tests/integration/ - Integration Tests

#### test_interactions.py
- End-to-end user journeys
- API integration testing
- Database integration
- Cross-component interactions

### tests/functional/ - Functional Tests

#### test_workflows.py
- User registration workflow
- Patient record management
- Appointment scheduling
- Prescription management

## Configuration Files

### app/config.py - Application Configuration

#### Configuration Classes
```python
class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///auth.db'
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/Health')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MONGODB_URI = 'mongodb://localhost:27017/HealthTest'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
```

## Key Design Patterns

### 1. Application Factory Pattern
- Centralized application creation
- Environment-specific configuration
- Testable application setup

### 2. Blueprint Pattern
- Modular route organization
- Separation of concerns
- Scalable architecture

### 3. Repository Pattern
- Database abstraction
- Consistent data access interface
- Testable data operations

### 4. Decorator Pattern
- Authorization decorators
- Cross-cutting concerns
- Reusable security logic

### 5. Strategy Pattern
- Multiple database support
- Configurable authentication
- Extensible validation

## Security Implementation Summary

### Authentication
- JWT-based stateless authentication
- bcrypt password hashing
- Secure token storage

### Authorization
- Role-based access control
- Route-level permissions
- Resource ownership validation

### Data Protection
- Input sanitization and validation
- SQL injection prevention
- XSS protection

### Audit & Compliance
- Comprehensive audit logging
- Security event monitoring
- HIPAA/GDPR considerations

## Performance Considerations

### Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy

### Caching Strategy
- Session caching
- Query result caching
- Static asset caching

### Scalability Features
- Horizontal database scaling
- Load balancing readiness
- Microservice-friendly architecture

## Error Handling

### Application-Level Error Handling
```python
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
```

### API Error Handling
```python
def handle_api_error(error):
    """Centralized API error handling"""
    response = {
        'success': False,
        'message': 'An error occurred'
    }
    
    if app.debug:
        response['debug'] = str(error)
    
    return jsonify(response), 500
```

## Deployment Considerations

### Environment Variables
```bash
SECRET_KEY=your-production-secret
JWT_SECRET=your-jwt-secret
MONGODB_URI=mongodb://prod-server:27017/Health
FLASK_ENV=production
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py", "--run"]
```

### Production Server
```python
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
```

## Maintenance and Monitoring

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks
```python
@app.route('/health')
def health_check():
    """Application health check endpoint"""
    return {
        'status': 'healthy',
        'database': check_database_connection(),
        'timestamp': datetime.utcnow().isoformat()
    }
```

## Future Enhancements

### Planned Features
- Two-factor authentication
- Advanced audit reporting
- Real-time notifications
- Mobile application API
- Advanced analytics dashboard

### Architecture Improvements
- GraphQL API implementation
- Event-driven architecture
- Container orchestration
- Multi-region deployment

## Contributing Guidelines

### Code Style
- PEP 8 compliance
- Type hints for new code
- Comprehensive documentation
- Security-focused code reviews

### Testing Requirements
- Unit test coverage > 80%
- Integration tests for all workflows
- Security testing included
- Performance benchmarks

### Documentation Standards
- Inline code documentation
- API endpoint documentation
- Architecture decision records
- Security implementation docs
