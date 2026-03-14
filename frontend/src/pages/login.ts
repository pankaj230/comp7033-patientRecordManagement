import { authManager } from '../auth/manager.js';
import { ValidationUtils, UIUtils } from '../utils/index.js';
import { LoginFormData } from '../types/index.js';

class LoginPage {
  private form!: HTMLFormElement;
  private emailInput!: HTMLInputElement;
  private passwordInput!: HTMLInputElement;
  private roleSelect!: HTMLSelectElement;
  private submitButton!: HTMLButtonElement;
  private registerLink!: HTMLElement;
  private alertContainer!: HTMLElement;

  constructor() {
    this.initializeElements();
    this.attachEventListeners();
    this.checkAuthentication();
  }

  private initializeElements(): void {
    this.form = document.getElementById('loginForm') as HTMLFormElement;
    this.emailInput = document.getElementById('email') as HTMLInputElement;
    this.passwordInput = document.getElementById('password') as HTMLInputElement;
    this.roleSelect = document.getElementById('role') as HTMLSelectElement;
    this.submitButton = document.getElementById('submitButton') as HTMLButtonElement;
    this.registerLink = document.getElementById('registerLink') as HTMLElement;
    this.alertContainer = document.getElementById('alertContainer') as HTMLElement;
  }

  private attachEventListeners(): void {
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    this.registerLink.addEventListener('click', this.handleRegisterLink.bind(this));

    this.emailInput.addEventListener('blur', this.validateEmail.bind(this));
    this.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
  }

  private checkAuthentication(): void {
    if (authManager.isAuthenticated()) {
      authManager.redirectToDashboard();
    }
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

    const isEmailValid = this.validateEmail();
    const isPasswordValid = this.validatePassword();

    if (!isEmailValid || !isPasswordValid) {
      UIUtils.showAlert('Please correct the errors in the form', 'error', this.alertContainer);
      return;
    }

    const formData: LoginFormData = {
      email: this.emailInput.value.trim(),
      password: this.passwordInput.value,
      role: this.roleSelect.value as 'patient' | 'clinician' | 'admin',
    };

    UIUtils.showLoading(this.submitButton, true);

    try {
      const response = await authManager.login(
        formData.email,
        formData.password,
        formData.role
      );

      if (response.success) {
        UIUtils.showAlert('Login successful! Redirecting...', 'success', this.alertContainer);
        setTimeout(() => {
          authManager.redirectToDashboard();
        }, 1000);
      } else {
        UIUtils.showAlert(response.message || 'Login failed', 'error', this.alertContainer);
      }
    } catch (error) {
      console.error('Login error:', error);
      UIUtils.showAlert('An error occurred during login. Please try again.', 'error', this.alertContainer);
    } finally {
      UIUtils.showLoading(this.submitButton, false);
    }
  }

  private handleRegisterLink(event: Event): void {
    event.preventDefault();
    window.location.href = '/register';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new LoginPage();
});
