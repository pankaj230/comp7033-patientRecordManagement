import { MedicalRecord, Appointment, Prescription } from '../types/index.js';
export declare class ValidationUtils {
    static isValidEmail(email: string): boolean;
    static isValidPassword(password: string): boolean;
}
export declare class FormatUtils {
    static formatDate(dateString: string): string;
    static formatDateTime(dateString: string): string;
    static formatBloodPressure(bp: number): string;
    static formatCholesterol(chol: number): string;
    static formatBoolean(value: boolean): string;
    static formatUserName(user: {
        first_name: string;
        last_name: string;
    }): string;
    static formatUserRole(role: string): string;
}
export declare class MedicalUtils {
    static getBloodPressureCategory(bp: number): string;
    static getCholesterolCategory(chol: number): string;
}
export declare class UIUtils {
    static showAlert(message: string, type?: 'success' | 'error' | 'warning' | 'info', container?: HTMLElement | null): void;
    static showLoading(element: HTMLElement, show?: boolean): void;
}
export declare class DataUtils {
    static transformMedicalRecordForDisplay(record: MedicalRecord): any;
    static transformAppointmentsForDisplay(appointments: Appointment[]): any[];
    static transformPrescriptionsForDisplay(prescriptions: Prescription[]): any[];
}
//# sourceMappingURL=index.d.ts.map