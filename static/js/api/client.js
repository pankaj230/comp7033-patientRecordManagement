export class ApiClient {
    constructor(baseURL = '') {
        this.token = null;
        this.baseURL = baseURL || window.location.origin;
        this.loadTokenFromStorage();
    }
    loadTokenFromStorage() {
        this.token = localStorage.getItem('access_token');
    }
    saveTokenToStorage(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }
    clearTokenFromStorage() {
        this.token = null;
        localStorage.removeItem('access_token');
    }
    setToken(token) {
        this.saveTokenToStorage(token);
    }
    clearToken() {
        this.clearTokenFromStorage();
    }
    isAuthenticated() {
        return this.token !== null;
    }
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };
        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        if (!response.ok) {
            if (response.status === 401) {
                this.clearTokenFromStorage();
                window.location.href = '/login';
                throw new Error('Authentication required');
            }
            if (response.status === 403) {
                throw new Error('Access denied');
            }
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'API request failed');
            }
            else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        }
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            return data;
        }
        else {
            throw new Error('Invalid response format');
        }
    }
    async login(credentials) {
        const response = await fetch(`${this.baseURL}/auth/login`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: JSON.stringify(credentials),
        });
        return this.handleResponse(response);
    }
    async register(userData) {
        const response = await fetch(`${this.baseURL}/auth/register`, {
            method: 'POST',
            headers: this.getHeaders(false),
            body: JSON.stringify(userData),
        });
        return this.handleResponse(response);
    }
    async getPatientRecord(patientId) {
        const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }
    async updatePatientRecord(patientId, data) {
        const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        return this.handleResponse(response);
    }
    async createPatientRecord(patientId, data) {
        const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        return this.handleResponse(response);
    }
    async getPatientAppointments(patientId) {
        const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}/appointments`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }
    async createAppointment(appointmentData) {
        const response = await fetch(`${this.baseURL}/api/records/appointments`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(appointmentData),
        });
        return this.handleResponse(response);
    }
    async updateAppointment(appointmentId, data) {
        const response = await fetch(`${this.baseURL}/api/records/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        return this.handleResponse(response);
    }
    async getPatientPrescriptions(patientId) {
        const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}/prescriptions`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }
    async createPrescription(prescriptionData) {
        const response = await fetch(`${this.baseURL}/api/records/prescriptions`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(prescriptionData),
        });
        return this.handleResponse(response);
    }
    async getAllUsers() {
        const response = await fetch(`${this.baseURL}/api/admin/users`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }
    async createUser(userData) {
        const response = await fetch(`${this.baseURL}/api/admin/users`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData),
        });
        return this.handleResponse(response);
    }
    async updateUser(userId, userData) {
        const response = await fetch(`${this.baseURL}/api/admin/users/${userId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(userData),
        });
        return this.handleResponse(response);
    }
    async deleteUser(userId) {
        const response = await fetch(`${this.baseURL}/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });
        return this.handleResponse(response);
    }
    async getClinicians() {
        const response = await fetch(`${this.baseURL}/api/records/clinicians`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return response.json();
    }
    async getClinicianPatients() {
        const response = await fetch(`${this.baseURL}/api/records/clinician/patients`, {
            method: 'GET',
            headers: this.getHeaders(),
        });
        return response.json();
    }
}
export const apiClient = new ApiClient();
export default apiClient;
//# sourceMappingURL=client.js.map