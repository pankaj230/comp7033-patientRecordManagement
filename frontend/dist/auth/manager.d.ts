import { User, AuthResponse } from '../types/index.js';
export declare class AuthManager {
    private static instance;
    private currentUser;
    private constructor();
    static getInstance(): AuthManager;
    private loadUserFromStorage;
    private saveUserToStorage;
    private clearUserFromStorage;
    login(email: string, password: string, role: string): Promise<AuthResponse>;
    register(userData: {
        email: string;
        password: string;
        first_name: string;
        last_name: string;
        role: string;
    }): Promise<AuthResponse>;
    logout(): void;
    getCurrentUser(): User | null;
    isAuthenticated(): boolean;
    getUserRole(): string | null;
    hasRole(role: string): boolean;
    isAdmin(): boolean;
    isClinician(): boolean;
    isPatient(): boolean;
    requireAuth(): boolean;
    requireRole(role: string): boolean;
    requireAdmin(): boolean;
    requireClinician(): boolean;
    requirePatient(): boolean;
    redirectToLogin(): void;
    redirectToDashboard(): void;
    redirectToHome(): void;
}
export declare const authManager: AuthManager;
export default authManager;
//# sourceMappingURL=manager.d.ts.map