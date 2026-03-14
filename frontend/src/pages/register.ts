import { authManager } from '../auth/manager.js';
import { ValidationUtils, UIUtils } from '../utils/index.js';
import { RegisterFormData } from '../types/index.js';

class RegisterPage {
  private form!: HTMLFormElement;
  private firstNameInput!: HTMLInputElement;
  private lastNameInput!: HTMLInputElement;
  private emailInput!: HTMLInputElement;
  private passwordInput!: HTMLInputElement;
  private confirmPasswordInput!: HTMLInputElement;
  private roleSelect!: HTMLSelectElement;
  private submitButton!: HTMLButtonElement;
  private loginLink!: HTMLElement;
  private alertContainer!: HTMLElement;

  constructor() {
    this.initializeElements();
    this.attachEventListeners();
    this.checkAuthentication();
  }

  private initializeElements(): void {
    this.form = document.getElementById('registerForm') as HTMLFormElement;
    this.firstNameInput = document.getElementById('firstName') as HTMLInputElement;
    this.lastNameInput = document.getElementById('lastName') as HTMLInputElement;
    this.emailInput = document.getElementById('email') as HTMLInputElement;
    this.passwordInput = document.getElementById('password') as HTMLInputElement;
    this.confirmPasswordInput = document.getElementById('confirmPassword') as HTMLInputElement;
    this.roleSelect = document.getElementById('role') as HTMLSelectElement;
    this.submitButton = document.getElementById('submitButton') as HTMLButtonElement;
    this.loginLink = document.getElementById('loginLink') as HTMLElement;
    this.alertContainer = document.getElementById('alertContainer') as HTMLElement;
  }

  private attachEventListeners(): void {
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    this.loginLink.addEventListener('click', this.handleLoginLink.bind(this));

    this.firstNameInput.addEventListener('blur', this.validateFirstName.bind(this));
    this.lastNameInput.addEventListener('blur', this.validateLastName.bind(this));
    this.emailInput.addEventListener('blur', this.validateEmail.bind(this));
    this.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
    this.confirmPasswordInput.addEventListener('blur', this.validateConfirmPassword.bind(this));
  }

  private checkAuthentication(): void {
    if (authManager.isAuthenticated()) {
      authManager.redirectToDashboard();
    }
  }

  private validateFirstName(): boolean {
    const firstName = this.firstNameInput.value.trim();
    const isValid = firstName.length > 0;

    this.setFieldValidity(this.firstNameInput, isValid, 'First name is required');
    return isValid;
  }

  private validateLastName(): boolean {
    const lastName = this.lastNameInput.value.trim();
    const isValid = lastName.length > 0;

    this.setFieldValidity(this.lastNameInput, isValid, 'Last name is required');
    return isValid;
  }

  private validateEmail(): boolean {
    const email = this.emailInput.value.trim();
    const isValid = ValidationUtils.isValidEmail(email);

    this.setFieldValidity(this.emailInput, isValid, 'Please enter a valid email address');
    return isValid;
  }

  private validatePassword(): boolean {
    const password = this.passwordInput.value;
    const isValid = ValidationUtils.isValidPassword(password);

    this.setFieldValidity(this.passwordInput, isValid, 'Password must be at least 8 characters long');
    return isValid;
  }

  private validateConfirmPassword(): boolean {
    const password = this.passwordInput.value;
    const confirmPassword = this.confirmPasswordInput.value;
    const isValid = password === confirmPassword && password.length > 0;

    this.setFieldValidity(this.confirmPasswordInput, isValid, 'Passwords do not match');
    return isValid;
  }

  private setFieldValidity(input: HTMLInputElement, isValid: boolean, errorMessage: string): void {
    const formGroup = input.closest('.form-group') as HTMLElement;
    const errorElement = formGroup.querySelector('.error-message') as HTMLElement;

    if (isValid) {
      input.classList.remove('invalid');
      input.classList.add('valid');
      if (errorElement) errorElement.style.display = 'none';
    } else {
      input.classList.remove('valid');
      input.classList.add('invalid');
      if (errorElement) {
        errorElement.textContent = errorMessage;
        errorElement.style.display = 'block';
      }
    }
  }

  private async handleSubmit(event: Event): Promise<void> {
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

    const formData: RegisterFormData = {
      email: this.emailInput.value.trim(),
      password: this.passwordInput.value,
      first_name: this.firstNameInput.value.trim(),
      last_name: this.lastNameInput.value.trim(),
      role: this.roleSelect.value as 'patient' | 'clinician' | 'admin',
    };

    UIUtils.showLoading(this.submitButton, true);

    try {
      const response = await authManager.register(formData);

      if (response.success) {
        UIUtils.showAlert('Registration successful! Redirecting to login...', 'success', this.alertContainer);
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      } else {
        UIUtils.showAlert(response.message || 'Registration failed', 'error', this.alertContainer);
      }
    } catch (error) {
      console.error('Registration error:', error);
      UIUtils.showAlert('An error occurred during registration. Please try again.', 'error', this.alertContainer);
    } finally {
      UIUtils.showLoading(this.submitButton, false);
    }
  }

  private handleLoginLink(event: Event): void {
    event.preventDefault();
    window.location.href = '/login';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new RegisterPage();
});
