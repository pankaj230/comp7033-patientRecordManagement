# Secure Patient Record Management System

---

## 📄 Project Overview
This project implements a **secure web-based patient record management system** for a private healthcare provider. The system supports clinicians, patients, and administrative staff in managing patient health records while adhering to strict data confidentiality, integrity, and regulatory compliance standards.

**Key Objectives**:
- Enable secure storage, retrieval, and updating of patient health records.
- Support role-based access control (RBAC) for clinicians, patients, and administrators.
- Mitigate risks associated with sensitive healthcare data (e.g., unauthorized access, data breaches).
- Align with legal/ethical standards (e.g., GDPR, HIPAA).

---

## 🛠️ Features
### Core Functionalities
1. **User Roles & Access Control**
   - **Patients**: View medical history, book appointments, upload prescriptions.
   - **Clinicians**: Diagnose, update records, issue prescriptions.
   - **Administrators**: Manage users, audit logs, oversee system operations.

2. **Data Management**
   - CRUD operations for patient records (e.g., demographics, medical indicators).
   - Secure storage of sensitive data (e.g., blood pressure, cholesterol levels).
   - Appointment scheduling and prescription tracking.

3. **Security & Compliance**
   - Role-based permissions (RBAC).
   - Audit logs for accountability.
   - Encryption for data at rest/in transit.

---

## 🚀 Getting Started
### Prerequisites
- Python 3.10+
- Flask (for web framework)
- SQLite (authentication database)
- MongoDB (patient records database)
- Environment variables for secret keys (e.g., `SECRET_KEY`, `JWT_SECRET`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/pankaj230/comp7033-lab-assessment.git
   cd secure-patient-record-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up databases:
   - SQLite: `sqlite3 auth.db` (create `users` table).
   - MongoDB: Use `mongod` to start the server.

4. Configure environment variables:
   ```bash
   export SECRET_KEY='your-secret-key'
   export JWT_SECRET='your-jwt-secret'
   ```

5. Run the application:
   ```bash
   python app.py
   ```
   Access the app at `http://localhost:5000`.

---

## 🔐 Security Implementation
### Key Security Measures
1. **Authentication & Authorization**
   - Password hashing (bcrypt).
   - JWT-based session management.
   - Role-based access control (RBAC).

2. **Data Protection**
   - AES-256 encryption for sensitive fields (e.g., medical history).
   - HTTPS for secure communication.

3. **Input Validation & Sanitization**
   - Prevent SQL injection (SQLite parameterized queries).
   - Prevent XSS (Flask-WTF for form validation).

4. **Threat Mitigations**
   - **Spoofing**: Multi-factor authentication (MFA) for admins.
   - **Tampering**: Digital signatures for audit logs.
   - **Repudiation**: Immutable audit trails.
   - **Information Disclosure**: Role-based data masking.
   - **Denial of Service**: Rate limiting for login attempts.
   - **Elevation of Privilege**: Least-privilege RBAC policies.

---

## 🛡️ Threat Modeling (STRIDE)
| Threat Type         | Description                                  | Mitigation Strategy                          |
|---------------------|----------------------------------------------|----------------------------------------------|
| **Spoofing**        | Unauthorized user impersonation              | MFA for admins, JWT tokens with expiration   |
| **Tampering**       | Data modification during transmission          | HTTPS, input validation                      |
| **Repudiation**     | Users denying actions                        | Immutable audit logs                         |
| **Information Disclosure** | Unauthorized data exposure               | Role-based encryption, access control        |
| **Denial of Service** | Overloading the system                       | Rate limiting, load balancing                |
| **Elevation of Privilege** | Unauthorized access to higher roles    | RBAC, privilege separation                     |

---

## 🧭 Trust Boundaries
1. **User Interface (UI)**: Client-side validation and secure form handling.
2. **Application Logic**: Server-side validation and RBAC enforcement.
3. **Data Storage**:
   - **SQLite**: Authentication data (low sensitivity).
   - **MongoDB**: Patient records (high sensitivity, encrypted).

---

## 🧭 Ethical & Compliance Considerations
- **Legal Compliance**: GDPR/HIPAA-compliant data handling.
- **Ethical Standards**: Transparency in data usage, patient consent for data collection.
- **Professional Practice**: Secure coding standards (OWASP Top 10), documentation for auditability.

---

## 📊 Evaluation & Risk Justification
- **Mitigated Risks**:
  - Unauthorized access via RBAC and encryption.
  - Data breaches via HTTPS and input sanitization.
- **Residual Risks**:
  - Potential insider threats (addressed via audit logs).
  - Trade-offs between usability and security (e.g., MFA may reduce user convenience).

---

## 📦 Additional Notes
- **AI Usage Disclosure**: This project did not use generative AI for completing the assignment.
- **Academic Integrity**: All code and documentation are original work.
- **Submission**: Push all code to GitHub and submit a zipped copy to Moodle by **20 March 2026**.

---

## 📞 Contact
For questions or feedback, contact:
- **Module Leader**: Dr. Antesar Shabut (`a.shabut@leedstrinity.ac.uk`)
- **Student**: Pankaj Kushwaha (`2515006@leedstrinity.ac.uk`)

---
