export class ValidationUtils {
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    static isValidPassword(password) {
        return password.length >= 8;
    }
}
export class FormatUtils {
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    }
    static formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    }
    static formatBloodPressure(bp) {
        return `${bp} mmHg`;
    }
    static formatCholesterol(chol) {
        return `${chol} mg/dL`;
    }
    static formatBoolean(value) {
        return value ? 'Yes' : 'No';
    }
    static formatUserName(user) {
        return `${user.first_name} ${user.last_name}`;
    }
    static formatUserRole(role) {
        return role.charAt(0).toUpperCase() + role.slice(1);
    }
}
export class MedicalUtils {
    static getBloodPressureCategory(bp) {
        if (bp < 120)
            return 'Normal';
        if (bp < 130)
            return 'Elevated';
        if (bp < 140)
            return 'High Blood Pressure (Stage 1)';
        if (bp < 180)
            return 'High Blood Pressure (Stage 2)';
        return 'Hypertensive Crisis';
    }
    static getCholesterolCategory(chol) {
        if (chol < 200)
            return 'Desirable';
        if (chol < 240)
            return 'Borderline High';
        return 'High';
    }
}
export class UIUtils {
    static showAlert(message, type = 'info', container) {
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
        }
        else {
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
    static showLoading(element, show = true) {
        if (show) {
            const originalText = element.textContent;
            element.setAttribute('data-original-text', originalText || '');
            element.textContent = 'Loading...';
            element.style.pointerEvents = 'none';
            element.style.opacity = '0.6';
        }
        else {
            const originalText = element.getAttribute('data-original-text') || 'Submit';
            element.textContent = originalText;
            if (element instanceof HTMLButtonElement) {
                element.disabled = false;
            }
            element.style.pointerEvents = 'auto';
            element.style.opacity = '1';
        }
    }
}
export class DataUtils {
    static transformMedicalRecordForDisplay(record) {
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
    static transformAppointmentsForDisplay(appointments) {
        return appointments.map(apt => ({
            ...apt,
            formatted_date: FormatUtils.formatDateTime(apt.appointment_date),
            status_badge: apt.status.charAt(0).toUpperCase() + apt.status.slice(1),
        }));
    }
    static transformPrescriptionsForDisplay(prescriptions) {
        return prescriptions.map(pres => ({
            ...pres,
            formatted_created_at: FormatUtils.formatDateTime(pres.created_at),
        }));
    }
}
//# sourceMappingURL=index.js.map