import { authManager } from '../auth/manager.js';
import { ValidationUtils, UIUtils } from '../utils/index.js';
class RegisterPage {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.checkAuthentication();
    }
    initializeElements() {
        this.form = document.getElementById('registerForm');
        this.firstNameInput = document.getElementById('firstName');
        this.lastNameInput = document.getElementById('lastName');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.confirmPasswordInput = document.getElementById('confirmPassword');
        this.roleSelect = document.getElementById('role');
        this.submitButton = document.getElementById('submitButton');
        this.loginLink = document.getElementById('loginLink');
        this.alertContainer = document.getElementById('alertContainer');
    }
    attachEventListeners() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.loginLink.addEventListener('click', this.handleLoginLink.bind(this));
        this.firstNameInput.addEventListener('blur', this.validateFirstName.bind(this));
        this.lastNameInput.addEventListener('blur', this.validateLastName.bind(this));
        this.emailInput.addEventListener('blur', this.validateEmail.bind(this));
        this.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
        this.confirmPasswordInput.addEventListener('blur', this.validateConfirmPassword.bind(this));
    }
    checkAuthentication() {
        if (authManager.isAuthenticated()) {
            authManager.redirectToDashboard();
        }
    }
    validateFirstName() {
        const firstName = this.firstNameInput.value.trim();
        const isValid = firstName.length > 0;
        this.setFieldValidity(this.firstNameInput, isValid, 'First name is required');
        return isValid;
    }
    validateLastName() {
        const lastName = this.lastNameInput.value.trim();
        const isValid = lastName.length > 0;
        this.setFieldValidity(this.lastNameInput, isValid, 'Last name is required');
        return isValid;
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
    validateConfirmPassword() {
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        const isValid = password === confirmPassword && password.length > 0;
        this.setFieldValidity(this.confirmPasswordInput, isValid, 'Passwords do not match');
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
        const isFirstNameValid = this.validateFirstName();
        const isLastNameValid = this.validateLastName();
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        const isConfirmPasswordValid = this.validateConfirmPassword();
        if (!isFirstNameValid || !isLastNameValid || !isEmailValid || !isPasswordValid || !isConfirmPasswordValid) {
            UIUtils.showAlert('Please correct the errors in the form', 'error', this.alertContainer);
            return;
        }
        const formData = {
            email: this.emailInput.value.trim(),
            password: this.passwordInput.value,
            first_name: this.firstNameInput.value.trim(),
            last_name: this.lastNameInput.value.trim(),
            role: this.roleSelect.value,
        };
        UIUtils.showLoading(this.submitButton, true);
        try {
            const response = await authManager.register(formData);
            if (response.success) {
                UIUtils.showAlert('Registration successful! Redirecting to login...', 'success', this.alertContainer);
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            }
            else {
                UIUtils.showAlert(response.message || 'Registration failed', 'error', this.alertContainer);
            }
        }
        catch (error) {
            console.error('Registration error:', error);
            UIUtils.showAlert('An error occurred during registration. Please try again.', 'error', this.alertContainer);
        }
        finally {
            UIUtils.showLoading(this.submitButton, false);
        }
    }
    handleLoginLink(event) {
        event.preventDefault();
        window.location.href = '/login';
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new RegisterPage();
});
//# sourceMappingURL=register.js.map