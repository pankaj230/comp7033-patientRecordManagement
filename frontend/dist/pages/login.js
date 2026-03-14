import { authManager } from '../auth/manager.js';
import { ValidationUtils, UIUtils } from '../utils/index.js';
class LoginPage {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.checkAuthentication();
    }
    initializeElements() {
        this.form = document.getElementById('loginForm');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.roleSelect = document.getElementById('role');
        this.submitButton = document.getElementById('submitButton');
        this.registerLink = document.getElementById('registerLink');
        this.alertContainer = document.getElementById('alertContainer');
    }
    attachEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.registerLink.addEventListener('click', this.handleRegisterLink.bind(this));
        this.emailInput.addEventListener('blur', this.validateEmail.bind(this));
        this.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
    }
    checkAuthentication() {
        if (authManager.isAuthenticated()) {
            authManager.redirectToDashboard();
        }
    }
    validateEmail() {
        const email = this.emailInput.value.trim();
        const isValid = ValidationUtils.isValidEmail(email);
        this.setFieldValidity(this.emailInput, isValid, 'Please enter a valid email address');
        return isValid;
    }
    validatePassword() {
        const password = this.passwordInput.value;
        const isValid = ValidationUtils.isValidPassword(password);
        this.setFieldValidity(this.passwordInput, isValid, 'Password must be at least 8 characters long');
        return isValid;
    }
    setFieldValidity(input, isValid, errorMessage) {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        if (isValid) {
            input.classList.remove('invalid');
            input.classList.add('valid');
            if (errorElement)
                errorElement.style.display = 'none';
        }
        else {
            input.classList.remove('valid');
            input.classList.add('invalid');
            if (errorElement) {
                errorElement.textContent = errorMessage;
                errorElement.style.display = 'block';
            }
        }
    }
    async handleSubmit(event) {
        event.preventDefault();
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        if (!isEmailValid || !isPasswordValid) {
            UIUtils.showAlert('Please correct the errors in the form', 'error', this.alertContainer);
            return;
        }
        const formData = {
            email: this.emailInput.value.trim(),
            password: this.passwordInput.value,
            role: this.roleSelect.value,
        };
        UIUtils.showLoading(this.submitButton, true);
        try {
            const response = await authManager.login(formData.email, formData.password, formData.role);
            if (response.success) {
                UIUtils.showAlert('Login successful! Redirecting...', 'success', this.alertContainer);
                setTimeout(() => {
                    authManager.redirectToDashboard();
                }, 1000);
            }
            else {
                UIUtils.showAlert(response.message || 'Login failed', 'error', this.alertContainer);
            }
        }
        catch (error) {
            console.error('Login error:', error);
            UIUtils.showAlert('An error occurred during login. Please try again.', 'error', this.alertContainer);
        }
        finally {
            UIUtils.showLoading(this.submitButton, false);
        }
    }
    handleRegisterLink(event) {
        event.preventDefault();
        window.location.href = '/register';
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new LoginPage();
});
//# sourceMappingURL=login.js.map