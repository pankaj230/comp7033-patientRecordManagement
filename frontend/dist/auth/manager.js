import { apiClient } from '../api/client.js';
export class AuthManager {
    constructor() {
        this.currentUser = null;
        this.loadUserFromStorage();
    }
    static getInstance() {
        if (!AuthManager.instance) {
            AuthManager.instance = new AuthManager();
        }
        return AuthManager.instance;
    }
    loadUserFromStorage() {
        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('current_user');
        if (token && userStr) {
            try {
                this.currentUser = JSON.parse(userStr);
            }
            catch (error) {
                console.error('Error parsing stored user data:', error);
                this.logout();
            }
        }
    }
    saveUserToStorage(user) {
        localStorage.setItem('current_user', JSON.stringify(user));
    }
    clearUserFromStorage() {
        localStorage.removeItem('current_user');
    }
    async login(email, password, role) {
        try {
            const response = await apiClient.login({ email, password, role });
            if (response.success && response.user && response.access_token) {
                this.currentUser = response.user;
                this.saveUserToStorage(response.user);
                apiClient.setToken(response.access_token);
            }
            return response;
        }
        catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    }
    async register(userData) {
        try {
            return await apiClient.register(userData);
        }
        catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    }
    logout() {
        this.currentUser = null;
        this.clearUserFromStorage();
        apiClient.clearToken();
    }
    getCurrentUser() {
        return this.currentUser;
    }
    isAuthenticated() {
        return apiClient.isAuthenticated() && this.currentUser !== null;
    }
    getUserRole() {
        return this.currentUser?.role || null;
    }
    hasRole(role) {
        return this.currentUser?.role === role;
    }
    isAdmin() {
        return this.hasRole('admin');
    }
    isClinician() {
        return this.hasRole('clinician');
    }
    isPatient() {
        return this.hasRole('patient');
    }
    requireAuth() {
        if (!this.isAuthenticated()) {
            this.redirectToLogin();
            return false;
        }
        return true;
    }
    requireRole(role) {
        if (!this.requireAuth())
            return false;
        if (!this.hasRole(role)) {
            this.redirectToDashboard();
            return false;
        }
        return true;
    }
    requireAdmin() {
        return this.requireRole('admin');
    }
    requireClinician() {
        return this.requireRole('clinician');
    }
    requirePatient() {
        return this.requireRole('patient');
    }
    redirectToLogin() {
        window.location.href = '/login';
    }
    redirectToDashboard() {
        const role = this.getUserRole();
        if (role === 'admin') {
            window.location.href = '/admin-dashboard';
        }
        else if (role === 'clinician') {
            window.location.href = '/clinician-dashboard';
        }
        else if (role === 'patient') {
            window.location.href = '/patient-dashboard';
        }
        else {
            window.location.href = '/';
        }
    }
    redirectToHome() {
        window.location.href = '/';
    }
}
export const authManager = AuthManager.getInstance();
export default authManager;
//# sourceMappingURL=manager.js.map