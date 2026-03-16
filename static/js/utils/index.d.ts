import { MedicalRecord, Appointment, Prescription } from '../types/index.js';
export declare class ValidationUtils {
    static isValidEmail(email: string): boolean;
    static isValidPassword(password: string): boolean;
    static isValidPhone(phone: string): boolean;
    static isValidDate(dateString: string): boolean;
    static isFutureDate(dateString: string): boolean;
    static sanitizeInput(input: string): string;
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
    static getBMICategory(bmi: number): string;
    static calculateBMI(weightKg: number, heightCm: number): number;
}
export declare class UIUtils {
    static showAlert(message: string, type?: 'success' | 'error' | 'warning' | 'info', container?: HTMLElement | null): void;
    static showLoading(element: HTMLElement, show?: boolean): void;
    static confirmDialog(message: string): Promise<boolean>;
    static scrollToTop(): void;
    static debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void;
}
export declare class DataUtils {
    static transformMedicalRecordForDisplay(record: MedicalRecord): any;
    static transformAppointmentsForDisplay(appointments: Appointment[]): any[];
    static transformPrescriptionsForDisplay(prescriptions: Prescription[]): any[];
    static sortByDate<T extends {
        created_at: string;
    }>(items: T[], ascending?: boolean): T[];
    static filterByStatus<T extends {
        status?: string;
    }>(items: T[], status: string): T[];
}
//# sourceMappingURL=index.d.ts.map