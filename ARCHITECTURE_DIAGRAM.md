# Frontend-Backend Integration Architecture

## Complete Data Flow

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        BROWSER (CLIENT-SIDE)                      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                   ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │                     HTML Templates                           │ ┃
┃  │                                                              │ ┃
┃  │  GET /              → home.html                              │ ┃
┃  │  GET /login         → login.html     [+ login.js]            │ ┃
┃  │  GET /register      → register.html  [+ register.js]         │ ┃
┃  │  GET /patient-dash  → patient_dashboard.html [+ dash.js]     │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                   ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │              JavaScript Modules (Compiled TS)                │ ┃
┃  │                    in static/js/                             │ ┃
┃  │                                                              │ ┃ 
┃  │  pages/                auth/              utils/             │ ┃
┃  │  ├─ login.js          ├─ manager.js       ├─ index.js        │ ┃
┃  │  ├─ register.js       │                   │                  │ ┃
┃  │  └─ patient-dash.js   │                   └─ (validation,    │ ┃
┃  │                       │                     formatting,      │ ┃
┃  │  api/                 │                     alerts, etc.)    │ ┃
┃  │  └─ client.js         │                                      │ ┃
┃  │                       │                                      │ ┃
┃  │  [Module Imports]     └─ AuthManager                         │ ┃
┃  │  pages/*.js imports from:                                    │ ┃
┃  │   - authManager (for login/register)                         │ ┃
┃  │   - apiClient (for API calls)                                │ ┃
┃  │   - UIUtils (for alerts & validation)                        │ ┃
┃  │                                                              │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                   ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │                   Data Storage (Browser)                     │ ┃
┃  │                                                              │ ┃
┃  │  localStorage:                                               │ ┃
┃  │  ├─ access_token (JWT)  ← Stored after login                 │ ┃
┃  │  └─ current_user        ← Stored user data                   │ ┃
┃  │                                                              │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                   ▲
                                   │ HTTP (JSON)
                                   │ Authorization: Bearer {token}
                                   ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                       FLASK BACKEND (SERVER-SIDE)                 ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                                   ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │                    Routes (app/app.py)                       │ ┃
┃  │                                                              │ ┃
┃  │  Public Routes:                                              │ ┃
┃  │  GET  /              → render_template('home.html')          │ ┃
┃  │  GET  /login         → render_template('login.html')         │ ┃
┃  │  GET  /register      → render_template('register.html')      │  ┃
┃  │                                                              │  ┃
┃  │  Auth Routes (app/routes/routes_auth.py):                    │  ┃
┃  │  POST /auth/register → Create user → JWT token               │  ┃
┃  │  POST /auth/login    → Verify credentials → JWT token        │  ┃
┃  │                                                              │  ┃
┃  │  Protected Routes (require valid JWT):                       │  ┃
┃  │  GET  /patient-dashboard → render_template(...)              │  ┃
┃  │  GET  /api/records/patient/{id}      [routes_records.py]     │  ┃
┃  │  POST /api/records/appointments      [routes_records.py]     │  ┃
┃  │  GET  /api/records/prescriptions/... [routes_records.py]     │  ┃
┃  │  GET  /api/admin/users               [routes_admin.py]       │  ┃
┃  │                                                              │  ┃
┃  └──────────────────────────────────────────────────────────────┘  ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐  ┃
┃  │              Authentication & Authorization                  │  ┃
┃  │                    (app/auth.py)                             │  ┃
┃  │                                                              │  ┃
┃  │  JWT Validation:                                             │  ┃
┃  │  1. Extract token from Authorization header                  │  ┃
┃  │  2. Verify signature and expiry                              │  ┃
┃  │  3. Extract user data from token                             │  ┃
┃  │  4. Check user role/permissions                              │  ┃
┃  │  5. Allow/Deny request                                       │  ┃
┃  │                                                              │  ┃
┃  └──────────────────────────────────────────────────────────────┘  ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐  ┃
┃  │                      Databases                               │  ┃
┃  │                   (app/models.py)                            │  ┃
┃  │                                                              │  ┃
┃  │  SQLite (Authentication & Users):                            │  ┃
┃  │  ├─ users (id, email, password_hash, role, ...)              │  ┃
┃  │  └─ audit_logs (user_id, action, timestamp, ...)             │  ┃
┃  │                                                              │  ┃
┃  │  MongoDB (Medical Records - if available):                   │  ┃
┃  │  ├─ medical_records (patient_id, age, blood_pressure, ...)   │  ┃
┃  │  ├─ appointments (patient_id, clinician_id, date, ...)       │  ┃
┃  │  └─ prescriptions (patient_id, medication, dosage, ...)      │  ┃
┃  │                                                              │  ┃
┃  └──────────────────────────────────────────────────────────────┘  ┃
┃                                                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## Registration Flow

```
┌─────────┐
│ Browser │
└────┬────┘
     │
     │ 1. GET /register
     ├─────────────────────────────────────────► Flask
     │                                          │
     │ 2. render_template('register.html')      │
     │◄───────────────────────────────────────── 
     │
     │ 3. <script type="module" src="js/pages/register.js">
     │ 4. JavaScript module loads and initializes form handlers
     │
     │ 5. User fills form and clicks "Register"
     │ 6. JavaScript validates locally:
     │    - Email format
     │    - Password length >= 8
     │    - Passwords match
     │    - First name & last name not empty
     │
     │ 7. POST /auth/register (JSON)
     │    {
     │      "email": "pankaj@test.com",
     │      "password": "SecurePass123",
     │      "first_name": "Pankaj",
     │      "last_name": "kushwaha",
     │      "role": "patient"
     │    }
     ├──────────────────────────────────────► Flask
     │                                       │
     │                                       ├─ Check email not in use
     │                                       ├─ Hash password
     │                                       ├─ Insert into SQLite
     │                                       ├─ Generate JWT token
     │
     │ 8. Return JSON response
     │    {
     │      "success": true,
     │      "message": "User created",
     │      "access_token": "eyJhbGc...",
     │      "user": {...}
     │    }
     │◄──────────────────────────────────────
     │
     │ 9. JavaScript handles response:
     │    - Save token to localStorage
     │    - Show success alert
     │    - Redirect to /login (3 seconds)
     │
     └─────────────────────────────────────────
```

---

## Login Flow

```
┌─────────┐
│ Browser │
└────┬────┘
     │
     │ 1. GET /login
     ├─────────────────────────────────────────► Flask
     │                                          │
     │ 2. render_template('login.html')         │
     │◄───────────────────────────────────────── 
     │
     │ 3. <script type="module" src="js/pages/login.js">
     │ 4. JavaScript initializes login form
     │
     │ 5. User enters email, password, role and clicks "Login"
     │ 6. JavaScript validates:
     │    - Valid email format
     │    - Password not empty
     │
     │ 7. POST /auth/login (JSON)
     │    {
     │      "email": "pankaj@test.com",
     │      "password": "SecurePass123",
     │      "role": "patient"
     │    }
     ├──────────────────────────────────────► Flask
     │                                       │
     │                                       ├─ Query SQLite for user
     │                                       ├─ Verify password hash
     │                                       ├─ Verify role matches
     │                                       ├─ Generate JWT token
     │
     │ 8. Return JSON response
     │    {
     │      "success": true,
     │      "message": "Login successful",
     │      "access_token": "eyJhbGc...",
     │      "user": {
     │        "id": 1,
     │        "email": "pankaj@test.com",
     │        "first_name": "pankaj",
     │        "last_name": "kushwaha",
     │        "role": "patient"
     │      }
     │    }
     │◄──────────────────────────────────────
     │
     │ 9. JavaScript handles response:
     │    ├─ Store token: localStorage.setItem('access_token', token)
     │    ├─ Store user: localStorage.setItem('current_user', user)
     │    ├─ Show success alert
     │    └─ Redirect to /patient-dashboard (1 second)
     │
     │ 10. GET /patient-dashboard
     │     Header: Authorization: Bearer {token}
     ├──────────────────────────────────────► Flask
     │                                       │
     │                                       ├─ Extract token
     │                                       ├─ Verify JWT signature
     │                                       ├─ Check expiry
     │                                       ├─ Check user role
     │                                       ├─ Allow access ✓
     │
     │ 11. render_template('patient_dashboard.html')
     │◄──────────────────────────────────────
     │
     │ 12. <script type="module" src="js/pages/patient-dashboard.js">
     │ 13. Dashboard JavaScript loads:
     │     ├─ Get token from localStorage
     │     ├─ GET /api/records/patient/1
     │     │   Header: Authorization: Bearer {token}
     │     │◄─ Medical records JSON
     │     ├─ GET /api/records/appointments/patient/1
     │     │   Header: Authorization: Bearer {token}
     │     │◄─ Appointments JSON
     │     └─ GET /api/records/prescriptions/patient/1
     │         Header: Authorization: Bearer {token}
     │         ◄─ Prescriptions JSON
     │
     │ 14. Display data in dashboard sections
     │
     └─────────────────────────────────────────
```

---

## Module Dependencies

```
login.html
  └─► login.js
      ├─► api/client.js
      │   └─► types/index.js
      │
      ├─► auth/manager.js
      │   └─► api/client.js
      │
      └─► utils/index.js
          └─► types/index.js

register.html
  └─► register.js
      ├─► api/client.js
      │
      ├─► auth/manager.js
      │   └─► api/client.js
      │
      ├─► utils/index.js
      │
      └─► types/index.js

patient_dashboard.html
  └─► patient-dashboard.js
      ├─► api/client.js
      │
      ├─► auth/manager.js
      │
      ├─► utils/index.js
      │
      └─► types/index.js
```

---

## Token Flow

```
┌────────────────────────────────────────────────────────────────┐
│                       Frontend (Browser)                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Step 1: After Login/Register                                  │
│  ┌─────────────────────────────────────┐                       │
│  │ API Response:                       │                       │
│  │ {                                   │                       │
│  │   "access_token": "eyJhbGciOi..."   │                       │
│  │   "user": {...}                     │                       │
│  │ }                                   │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ▼                                              │
│  Step 2: Store Token                                           │
│  ┌─────────────────────────────────────┐                       │
│  │ localStorage.setItem(               │                       │
│  │   'access_token',                   │                       │
│  │   'eyJhbGciOi...'                   │                       │
│  │ )                                   │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ▼                                              │
│  Step 3: Using Token in API Calls                              │
│  ┌─────────────────────────────────────┐                       │
│  │ GET /api/records/patient/1          │                       │
│  │ Headers: {                          │                       │
│  │   'Authorization': 'Bearer {token}' │                       │
│  │ }                                   │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ▼                                              │
│  Step 4: Logout                                                │
│  ┌─────────────────────────────────────┐                       │
│  │ localStorage.removeItem('access_token')                     │
│  │ localStorage.removeItem('current_user')                     │
│  │ Redirect to /login                  │                       │
│  └─────────────────────────────────────┘                       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
                         ▲
                         │ HTTP Request with Token
                         │ HTTP Response (200/401/403)
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Backend (Flask Server)                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Step 1: Receive API Request with Token                        │
│  ┌─────────────────────────────────────┐                       │
│  │ Authorization: Bearer eyJhbGciOi... │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ▼                                              │
│  Step 2: Extract Token                                         │
│  ┌─────────────────────────────────────┐                       │
│  │ token = request.headers.get(        │                       │
│  │   'Authorization'                   │                       │
│  │ ).split(' ')[1]                     │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ▼                                              │
│  Step 3: Verify Token                                          │
│  ┌─────────────────────────────────────┐                       │
│  │ try:                                │                       │
│  │   data = jwt.decode(token)          │                       │
│  │ except:                             │                       │
│  │   return 401 Unauthorized           │                       │
│  └──────────────┬──────────────────────┘                       │
│                 │                                              │
│                 ├─ Token valid?                                │
│                 │                                              │
│                 ├─YES─► Verify Expiry                          
│                 │        ├─ Expired?
│                 │        │
│                 │        ├─NO─► Check User Role
│                 │        │       ├─ Has Permission?
│                 │        │       │
│                 │        │       ├─YES─► Process Request
│                 │        │       │        Return Data (200)
│                 │        │       │
│                 │        │       └─NO─► Return 403 Forbidden
│                 │        │
│                 │        └─YES─► Return 401 Token Expired
│                 │
│                 └─NO─► Return 401 Invalid Token
│
└────────────────────────────────────────────────────────────────┘
```

---
