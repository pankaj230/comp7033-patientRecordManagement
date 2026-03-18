# Testing Documentation

## Test Structure Overview

The test suite for the Patient Record Management System is organized into three distinct categories:

```
tests/
├── unit/                          # Unit tests for individual components
│   ├── __init__.py
│   ├── test_auth.py              # Authentication function tests
│   └── test_database.py           # Database operation tests
│
├── functional/                    # Functional tests for user workflows
│   ├── __init__.py
│   └── test_workflows.py          # End-to-end workflow tests
│
├── integration/                   # Integration tests for component interactions
│   ├── __init__.py
│   └── test_interactions.py       # Cross-component integration tests
│
├── conftest.py                    # Test runner configuration
└── README.md                      # This file
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions and components in isolation

**Coverage**:
- **test_auth.py**
  - Authentication function logic (register_user, login_user)
  - Email validation
  - Password validation
  - Input sanitization
  - Each function tested independently without HTTP/database integration

- **test_database.py**
  - SQLite database CRUD operations
  - MongoDB operations
  - Audit logging functionality
  - Direct database method calls without API endpoints

  
### 2. Functional Tests (`tests/functional/`)

**Purpose**: Test complete user workflows and feature scenarios

**Coverage** (test_workflows.py):
- User registration workflows
- Login and authentication workflows
- Patient record creation and management
- Appointment scheduling
- Prescription management
- Role-based access control enforcement
- Security features (XSS prevention, input validation)

**Characteristics**:
- Test complete user journeys
- Use HTTP endpoints
- Test with real database
- Verify business logic flows
- Longer execution time than unit tests

**Example**:
```python
def test_complete_patient_registration_workflow(self):
    """Test complete patient registration workflow"""
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
```

### 3. Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between multiple components and systems

**Coverage** (test_interactions.py):
- Authentication and database integration
- API endpoints with database persistence
- Audit logging with user actions
- Patient records with MongoDB
- Complete user journeys across multiple features
- Clinician-Admin collaboration workflows

**Characteristics**:
- Test multiple components together
- Verify data persistence
- Test API with database
- Cross-feature interactions
- Comprehensive setup/teardown

**Example**:
```python
def test_user_registration_persists_to_database(self):
    """Test that user registration persists data to database"""
    email = f"persist_{self.unique_suffix}@example.com"
    register_user(email, 'PersistPass123!', 'Persist', 'Test', 'patient')
    
    # Verify data persisted in database
    user = sqlite_db.get_user_by_email(email)
    self.assertIsNotNone(user)
    self.assertEqual(user['email'], email)
```

## Running Tests

### Run All Tests
```bash
python tests/conftest.py
# or
python tests/conftest.py --type all -v
```

### Run Unit Tests Only
```bash
python tests/conftest.py --type unit
# or
python -m unittest tests.unit.test_auth tests.unit.test_database
```

### Run Functional Tests Only
```bash
python tests/conftest.py --type functional
# or
python -m unittest tests.functional.test_workflows
```

### Run Integration Tests Only
```bash
python tests/conftest.py --type integration
# or
python -m unittest tests.integration.test_interactions
```

## Test Statistics

### Unit Tests (test_auth.py + test_database.py)
- **Total Tests**: 40+
- **Focus**: Component isolation, function behavior
- **Execution Time**: < 30 seconds

### Functional Tests (test_workflows.py)
- **Total Tests**: 25+
- **Focus**: User workflows, API endpoints
- **Execution Time**: 1-2 minutes

### Integration Tests (test_interactions.py)
- **Total Tests**: 20+
- **Focus**: Multi-component interactions, data persistence
- **Execution Time**: 1-2 minutes

**Total Test Coverage**: 85+ tests
