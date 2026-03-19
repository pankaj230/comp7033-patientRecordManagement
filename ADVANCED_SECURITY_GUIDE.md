# Patient Record Management System

## Overview

The Patient Record Management System is a comprehensive web application designed to manage patient medical records, appointments, prescriptions, and user administration. The system supports multiple user roles (Admin, Clinician, Patient) with role-based access control and secure authentication.

## Features

### Core Functionality
- **User Management**: Registration, authentication, and role-based access control
- **Patient Records**: Secure storage and retrieval of medical history, allergies, blood type, and emergency contacts
- **Appointments**: Scheduling and management of patient appointments
- **Prescriptions**: Clinician-issued prescriptions with medication details
- **Audit Logging**: Comprehensive logging of all system activities

### Security Features
- JWT-based authentication with secure token management
- Password hashing with bcrypt
- Input sanitization and XSS prevention
- Role-based access control (RBAC)
- Audit logging for compliance
- Secure session management

### Multi-Database Architecture
- **SQLite**: User accounts, authentication, audit logs
- **MongoDB**: Patient records, appointments, prescriptions

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Typescript, JavaScript (ES6+)
- **Databases**: SQLite, MongoDB
- **Authentication**: Flask-JWT-Extended
- **Security**: bcrypt, bleach (input sanitization)
- **Testing**: unittest, pytest

## Usage

### User Roles

#### Admin
- Manage users (create, update, deactivate)
- View system statistics and audit logs
- Access all patient records and system settings

#### Clinician
- View and update patient medical records
- Issue prescriptions
- View assigned patients

#### Patient
- View personal medical records
- Book appointments with clinicians
- View prescriptions


### API Endpoints

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

#### Records Management
- `GET /api/records/patient/{id}` - Get patient record
- `POST /api/records/patient/{id}` - Create patient record
- `PUT /api/records/patient/{id}` - Update patient record
- `POST /api/records/appointments` - Create appointment
- `POST /api/records/prescriptions` - Create prescription

#### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create user
- `GET /api/admin/dashboard-stats` - System statistics
