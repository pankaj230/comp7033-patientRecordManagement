import { apiClient } from '../api/client.js';
import { User, AuthResponse } from '../types/index.js';

export class AuthManager {
  private static instance: AuthManager;
  private currentUser: User | null = null;

  private constructor() {
    this.loadUserFromStorage();
  }

  static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  private loadUserFromStorage(): void {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('current_user');

    if (token && userStr) {
      try {
        this.currentUser = JSON.parse(userStr);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        this.logout();
      }
    }
  }

  private saveUserToStorage(user: User): void {
    localStorage.setItem('current_user', JSON.stringify(user));
  }

  private clearUserFromStorage(): void {
    localStorage.removeItem('current_user');
  }

  async login(email: string, password: string, role: string): Promise<AuthResponse> {
    try {
      const response = await apiClient.login({ email, password, role });

      if (response.success && response.user && response.access_token) {
        this.currentUser = response.user;
        this.saveUserToStorage(response.user);
        apiClient.setToken(response.access_token);
      }

      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async register(userData: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role: string;
  }): Promise<AuthResponse> {
    try {
      return await apiClient.register(userData);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  logout(): void {
    this.currentUser = null;
    this.clearUserFromStorage();
    apiClient.clearToken();
  }

  getCurrentUser(): User | null {
    return this.currentUser;
  }

  isAuthenticated(): boolean {
    return apiClient.isAuthenticated() && this.currentUser !== null;
  }

  getUserRole(): string | null {
    return this.currentUser?.role || null;
  }

  hasRole(role: string): boolean {
    return this.currentUser?.role === role;
  }

  isAdmin(): boolean {
    return this.hasRole('admin');
  }

  isClinician(): boolean {
    return this.hasRole('clinician');
  }

  isPatient(): boolean {
    return this.hasRole('patient');
  }


  requireAuth(): boolean {
    if (!this.isAuthenticated()) {
      this.redirectToLogin();
      return false;
    }
    return true;
  }

  requireRole(role: string): boolean {
    if (!this.requireAuth()) return false;

    if (!this.hasRole(role)) {
      this.redirectToDashboard();
      return false;
    }
    return true;
  }

  requireAdmin(): boolean {
    return this.requireRole('admin');
  }

  requireClinician(): boolean {
    return this.requireRole('clinician');
  }

  requirePatient(): boolean {
    return this.requireRole('patient');
  }


  redirectToLogin(): void {
    window.location.href = '/login';
  }

  redirectToDashboard(): void {
    const role = this.getUserRole();
    if (role === 'admin') {
      window.location.href = '/admin-dashboard';
    } else if (role === 'clinician') {
      window.location.href = '/clinician-dashboard';
    } else if (role === 'patient') {
      window.location.href = '/patient-dashboard';
    } else {
      window.location.href = '/';
    }
  }

  redirectToHome(): void {
    window.location.href = '/';
  }
}

export const authManager = AuthManager.getInstance();
export default authManager;
