import { ApiResponse, AuthResponse, User, MedicalRecord, Appointment, Prescription, ClinicianResponse, ClinicianPatientsResponse } from '../types/index.js';

export class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = '') {
    this.baseURL = baseURL || window.location.origin;
    this.loadTokenFromStorage();
  }

  private loadTokenFromStorage(): void {
    this.token = localStorage.getItem('access_token');
  }

  private saveTokenToStorage(token: string): void {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  private clearTokenFromStorage(): void {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  setToken(token: string): void {
    this.saveTokenToStorage(token);
  }

  clearToken(): void {
    this.clearTokenFromStorage();
  }

  isAuthenticated(): boolean {
    return this.token !== null;
  }

  private getHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
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
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }

    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      return data;
    } else {
      throw new Error('Invalid response format');
    }
  }

  async login(credentials: { email: string; password: string; role: string }): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(false),
      body: JSON.stringify(credentials),
    });

    return this.handleResponse<AuthResponse>(response);
  }

  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
  }): Promise<AuthResponse> {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(false),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<AuthResponse>(response);
  }

  async getPatientRecord(patientId: number): Promise<ApiResponse<MedicalRecord>> {
    const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<MedicalRecord>(response);
  }

  async updatePatientRecord(patientId: number, data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>> {
    const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<MedicalRecord>(response);
  }

  async createPatientRecord(patientId: number, data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>> {
    const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<MedicalRecord>(response);
  }

  async getPatientAppointments(patientId: number): Promise<ApiResponse<Appointment[]>> {
    const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}/appointments`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<Appointment[]>(response);
  }

  async createAppointment(appointmentData: {
    patient_id: number;
    clinician_id: number;
    appointment_date: string;
    reason: string;
  }): Promise<ApiResponse<Appointment>> {
    const response = await fetch(`${this.baseURL}/api/records/appointments`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(appointmentData),
    });

    return this.handleResponse<Appointment>(response);
  }

  async updateAppointment(appointmentId: string, data: Partial<Appointment>): Promise<ApiResponse<Appointment>> {
    const response = await fetch(`${this.baseURL}/api/records/appointments/${appointmentId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse<Appointment>(response);
  }


  async getPatientPrescriptions(patientId: number): Promise<ApiResponse<Prescription[]>> {
    const response = await fetch(`${this.baseURL}/api/records/patient/${patientId}/prescriptions`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<Prescription[]>(response);
  }

  async createPrescription(prescriptionData: {
    patient_id: number;
    clinician_id: number;
    medication: string;
    dosage: string;
    duration: string;
  }): Promise<ApiResponse<Prescription>> {
    const response = await fetch(`${this.baseURL}/api/records/prescriptions`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(prescriptionData),
    });

    return this.handleResponse<Prescription>(response);
  }


  async getAllUsers(): Promise<ApiResponse<User[]>> {
    const response = await fetch(`${this.baseURL}/api/admin/users`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<User[]>(response);
  }

  async createUser(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
  }): Promise<ApiResponse<User>> {
    const response = await fetch(`${this.baseURL}/api/admin/users`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<User>(response);
  }

  async updateUser(userId: number, userData: Partial<User>): Promise<ApiResponse<User>> {
    const response = await fetch(`${this.baseURL}/api/admin/users/${userId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });

    return this.handleResponse<User>(response);
  }

  async deleteUser(userId: number): Promise<ApiResponse<void>> {
    const response = await fetch(`${this.baseURL}/api/admin/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    return this.handleResponse<void>(response);
  }

  async getClinicians(): Promise<ClinicianResponse> {
    const response = await fetch(`${this.baseURL}/api/records/clinicians`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    return response.json();
  }

  async getClinicianPatients(): Promise<ClinicianPatientsResponse> {
    const response = await fetch(`${this.baseURL}/api/records/clinician/patients`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    return response.json();
  }
}

export const apiClient = new ApiClient();
export default apiClient;
