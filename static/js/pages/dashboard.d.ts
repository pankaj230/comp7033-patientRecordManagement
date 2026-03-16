declare class Dashboard {
    private userInfo;
    private alertContainer;
    private medicalRecordsSection;
    private appointmentsSection;
    private prescriptionsSection;
    private patientsSection;
    private logoutButton;
    private bookAppointmentBtn;
    constructor();
    private initializeElements;
    private attachEventListeners;
    private checkAuthentication;
    private loadDashboardData;
    private displayUserInfo;
    private showWelcomeAlert;
    private showAlert;
    private loadMedicalRecords;
    private displayMedicalRecord;
    private loadAppointments;
    private displayAppointments;
    private loadPrescriptions;
    private displayPrescriptions;
    private loadAndShowClinicianPatients;
    private displayClinicianPatientsInModal;
    private handleLogout;
    private handleBookAppointment;
    private closeModal;
    private loadClinicians;
    private handleAppointmentSubmit;
}
export { Dashboard };
//# sourceMappingURL=dashboard.d.ts.map