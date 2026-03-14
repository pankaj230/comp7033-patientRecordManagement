export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: 'patient' | 'clinician' | 'admin';
    is_active: boolean;
}
export interface AuthResponse {
    success: boolean;
    message: string;
    access_token?: string;
    user?: User;
}
export interface ApiResponse<T = any> {
    success: boolean;
    message: string;
    data?: T;
    record?: any;
    appointments?: any[];
    prescriptions?: any[];
    patient?: any;
    users?: User[];
}
export interface ClinicianResponse {
    success: boolean;
    message: string;
    clinicians?: User[];
}
export interface ClinicianPatientsResponse {
    success: boolean;
    message: string;
    patients?: User[];
}
export interface MedicalRecord {
    patient_id: number;
    medical_history: string;
    allergies: string;
    blood_type: string;
    emergency_contact: string;
    age: number;
    sex: 'Male' | 'Female';
    blood_pressure: number;
    cholesterol: number;
    fasting_blood_sugar: boolean;
    resting_ecg: 'Normal' | 'Abnormal';
    exercise_induced_angina: boolean;
    max_heart_rate?: number;
    oldpeak?: number;
    slope?: string;
    ca?: number;
    thal?: string;
    diagnosis: string;
    treatment_plan: string;
    notes: string;
    created_at: string;
    updated_at: string;
}
export interface Appointment {
    _id?: string;
    patient_id: number;
    clinician_id: number;
    appointment_date: string;
    reason: string;
    status: 'scheduled' | 'completed' | 'cancelled';
    created_at: string;
    updated_at: string;
}
export interface Prescription {
    _id?: string;
    patient_id: number;
    clinician_id: number;
    medication: string;
    dosage: string;
    duration: string;
    created_at: string;
    updated_at: string;
}
export interface LoginFormData {
    email: string;
    password: string;
    role: 'patient' | 'clinician' | 'admin';
}
export interface RegisterFormData {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: 'patient' | 'clinician' | 'admin';
}
export interface MedicalRecordFormData {
    medical_history: string;
    allergies: string;
    blood_type: string;
    emergency_contact: string;
    age: number;
    sex: 'Male' | 'Female';
    blood_pressure: number;
    cholesterol: number;
    fasting_blood_sugar: boolean;
    resting_ecg: 'Normal' | 'Abnormal';
    exercise_induced_angina: boolean;
    diagnosis: string;
    treatment_plan: string;
    notes: string;
}
export interface AppointmentFormData {
    clinician_id: number;
    appointment_date: string;
    reason: string;
}
export interface PrescriptionFormData {
    patient_id: number;
    medication: string;
    dosage: string;
    duration: string;
}
export interface DashboardData {
    user: User;
    medical_record?: MedicalRecord;
    appointments?: Appointment[];
    prescriptions?: Prescription[];
}
export interface AdminDashboardData {
    total_users: number;
    total_patients: number;
    total_clinicians: number;
    recent_audit_logs: AuditLog[];
}
export interface AuditLog {
    id: number;
    user_email: string;
    action: string;
    resource: string;
    resource_id?: string;
    details?: string;
    timestamp: string;
}
//# sourceMappingURL=index.d.ts.map