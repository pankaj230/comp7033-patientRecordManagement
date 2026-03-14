import { ApiResponse, AuthResponse, User, MedicalRecord, Appointment, Prescription, ClinicianResponse, ClinicianPatientsResponse } from '../types/index.js';
export declare class ApiClient {
    private baseURL;
    private token;
    constructor(baseURL?: string);
    private loadTokenFromStorage;
    private saveTokenToStorage;
    private clearTokenFromStorage;
    setToken(token: string): void;
    clearToken(): void;
    isAuthenticated(): boolean;
    private getHeaders;
    private handleResponse;
    login(credentials: {
        email: string;
        password: string;
        role: string;
    }): Promise<AuthResponse>;
    register(userData: {
        email: string;
        password: string;
        first_name: string;
        last_name: string;
        role: string;
    }): Promise<AuthResponse>;
    getPatientRecord(patientId: number): Promise<ApiResponse<MedicalRecord>>;
    updatePatientRecord(patientId: number, data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>>;
    createPatientRecord(patientId: number, data: Partial<MedicalRecord>): Promise<ApiResponse<MedicalRecord>>;
    getPatientAppointments(patientId: number): Promise<ApiResponse<Appointment[]>>;
    createAppointment(appointmentData: {
        patient_id: number;
        clinician_id: number;
        appointment_date: string;
        reason: string;
    }): Promise<ApiResponse<Appointment>>;
    updateAppointment(appointmentId: string, data: Partial<Appointment>): Promise<ApiResponse<Appointment>>;
    getPatientPrescriptions(patientId: number): Promise<ApiResponse<Prescription[]>>;
    createPrescription(prescriptionData: {
        patient_id: number;
        clinician_id: number;
        medication: string;
        dosage: string;
        duration: string;
    }): Promise<ApiResponse<Prescription>>;
    getAllUsers(): Promise<ApiResponse<User[]>>;
    createUser(userData: {
        email: string;
        password: string;
        first_name: string;
        last_name: string;
        role: string;
    }): Promise<ApiResponse<User>>;
    updateUser(userId: number, userData: Partial<User>): Promise<ApiResponse<User>>;
    deleteUser(userId: number): Promise<ApiResponse<void>>;
    getClinicians(): Promise<ClinicianResponse>;
    getClinicianPatients(): Promise<ClinicianPatientsResponse>;
}
export declare const apiClient: ApiClient;
export default apiClient;
//# sourceMappingURL=client.d.ts.map