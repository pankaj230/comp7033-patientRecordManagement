import { MedicalRecord, Appointment, Prescription } from '../types/index.js';

export class ValidationUtils {
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static isValidPassword(password: string): boolean {
    return password.length >= 8;
  }

  static isValidPhone(phone: string): boolean {
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    return phoneRegex.test(phone);
  }

  static isValidDate(dateString: string): boolean {
    const date = new Date(dateString);
    return !isNaN(date.getTime());
  }

  static isFutureDate(dateString: string): boolean {
    const date = new Date(dateString);
    const now = new Date();
    return date > now;
  }

  static sanitizeInput(input: string): string {
    return input.trim().replace(/[<>]/g, '');
  }
}


export class FormatUtils {
  static formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  static formatDateTime(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  static formatBloodPressure(bp: number): string {
    return `${bp} mmHg`;
  }

  static formatCholesterol(chol: number): string {
    return `${chol} mg/dL`;
  }

  static formatBoolean(value: boolean): string {
    return value ? 'Yes' : 'No';
  }

  static formatUserName(user: { first_name: string; last_name: string }): string {
    return `${user.first_name} ${user.last_name}`;
  }

  static formatUserRole(role: string): string {
    return role.charAt(0).toUpperCase() + role.slice(1);
  }
}

export class MedicalUtils {
  static getBloodPressureCategory(bp: number): string {
    if (bp < 120) return 'Normal';
    if (bp < 130) return 'Elevated';
    if (bp < 140) return 'High Blood Pressure (Stage 1)';
    if (bp < 180) return 'High Blood Pressure (Stage 2)';
    return 'Hypertensive Crisis';
  }

  static getCholesterolCategory(chol: number): string {
    if (chol < 200) return 'Desirable';
    if (chol < 240) return 'Borderline High';
    return 'High';
  }

  static getBMICategory(bmi: number): string {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  static calculateBMI(weightKg: number, heightCm: number): number {
    const heightM = heightCm / 100;
    return weightKg / (heightM * heightM);
  }
}


export class UIUtils {
  static showAlert(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', container?: HTMLElement | null): void {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    let targetContainer = container;
    if (!targetContainer) {
      targetContainer = document.getElementById('alertContainer');
    }

    if (targetContainer) {
      alertDiv.style.cssText = `
        padding: 15px 20px;
        border-radius: 5px;
        margin-bottom: 10px;
        border: 1px solid;
      `;

      switch (type) {
        case 'success':
          alertDiv.style.backgroundColor = '#d4edda';
          alertDiv.style.color = '#155724';
          alertDiv.style.borderColor = '#c3e6cb';
          break;
        case 'error':
          alertDiv.style.backgroundColor = '#f8d7da';
          alertDiv.style.color = '#721c24';
          alertDiv.style.borderColor = '#f5c6cb';
          break;
        case 'warning':
          alertDiv.style.backgroundColor = '#fff3cd';
          alertDiv.style.color = '#856404';
          alertDiv.style.borderColor = '#ffeeba';
          break;
        default:
          alertDiv.style.backgroundColor = '#d1ecf1';
          alertDiv.style.color = '#0c5460';
          alertDiv.style.borderColor = '#bee5eb';
      }

      targetContainer.appendChild(alertDiv);

      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.parentNode.removeChild(alertDiv);
        }
      }, 5000);
    } else {
      alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        max-width: 400px;
      `;

      switch (type) {
        case 'success':
          alertDiv.style.backgroundColor = '#4CAF50';
          break;
        case 'error':
          alertDiv.style.backgroundColor = '#f44336';
          break;
        case 'warning':
          alertDiv.style.backgroundColor = '#ff9800';
          break;
        default:
          alertDiv.style.backgroundColor = '#2196F3';
      }

      document.body.appendChild(alertDiv);

      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.parentNode.removeChild(alertDiv);
        }
      }, 5000);
    }
  }

  static showLoading(element: HTMLElement, show: boolean = true): void {
    if (show) {
      const originalText = element.textContent;
      element.setAttribute('data-original-text', originalText || '');
      element.textContent = 'Loading...';
      element.style.pointerEvents = 'none';
      element.style.opacity = '0.6';
    } else {
      const originalText = element.getAttribute('data-original-text') || 'Submit';
      element.textContent = originalText;
      if (element instanceof HTMLButtonElement) {
        element.disabled = false;
      }
      element.style.pointerEvents = 'auto';
      element.style.opacity = '1';
    }
  }

  static confirmDialog(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      const result = confirm(message);
      resolve(result);
    });
  }

  static scrollToTop(): void {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: number;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
    };
  }
}

export class DataUtils {
  static transformMedicalRecordForDisplay(record: MedicalRecord): any {
    return {
      ...record,
      formatted_blood_pressure: FormatUtils.formatBloodPressure(record.blood_pressure),
      formatted_cholesterol: FormatUtils.formatCholesterol(record.cholesterol),
      blood_pressure_category: MedicalUtils.getBloodPressureCategory(record.blood_pressure),
      cholesterol_category: MedicalUtils.getCholesterolCategory(record.cholesterol),
      formatted_created_at: FormatUtils.formatDateTime(record.created_at),
      formatted_updated_at: FormatUtils.formatDateTime(record.updated_at),
    };
  }

  static transformAppointmentsForDisplay(appointments: Appointment[]): any[] {
    return appointments.map(apt => ({
      ...apt,
      formatted_date: FormatUtils.formatDateTime(apt.appointment_date),
      status_badge: apt.status.charAt(0).toUpperCase() + apt.status.slice(1),
    }));
  }

  static transformPrescriptionsForDisplay(prescriptions: Prescription[]): any[] {
    return prescriptions.map(pres => ({
      ...pres,
      formatted_created_at: FormatUtils.formatDateTime(pres.created_at),
    }));
  }

  static sortByDate<T extends { created_at: string }>(items: T[], ascending: boolean = false): T[] {
    return items.sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return ascending ? dateA - dateB : dateB - dateA;
    });
  }

  static filterByStatus<T extends { status?: string }>(items: T[], status: string): T[] {
    return items.filter(item => item.status === status);
  }
}
