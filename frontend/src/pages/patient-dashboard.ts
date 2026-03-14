import { authManager } from '../auth/manager.js';
import { apiClient } from '../api/client.js';
import { FormatUtils, DataUtils } from '../utils/index.js';

class PatientDashboard {
  private userInfo!: HTMLElement;
  private medicalRecordsSection!: HTMLElement;
  private appointmentsSection!: HTMLElement;
  private prescriptionsSection!: HTMLElement;
  private logoutButton!: HTMLElement;
  private bookAppointmentBtn!: HTMLElement;

  constructor() {
    this.initializeElements();
    this.attachEventListeners();
    this.checkAuthentication();
    this.loadDashboardData();
  }

  private initializeElements(): void {
    this.userInfo = document.getElementById('userInfo') as HTMLElement;
    this.medicalRecordsSection = document.getElementById('medicalRecordsSection') as HTMLElement;
    this.appointmentsSection = document.getElementById('appointmentsSection') as HTMLElement;
    this.prescriptionsSection = document.getElementById('prescriptionsSection') as HTMLElement;
    this.logoutButton = document.getElementById('logoutButton') as HTMLElement;
    this.bookAppointmentBtn = document.getElementById('bookAppointmentBtn') as HTMLElement;
  }

  private attachEventListeners(): void {
    this.logoutButton.addEventListener('click', this.handleLogout.bind(this));
    this.bookAppointmentBtn.addEventListener('click', this.handleBookAppointment.bind(this));

    const closeBtn = document.querySelector('.close') as HTMLElement;
    if (closeBtn) {
      closeBtn.addEventListener('click', this.closeModal.bind(this));
    }

    const appointmentForm = document.getElementById('appointmentForm') as HTMLFormElement;
    if (appointmentForm) {
      appointmentForm.addEventListener('submit', this.handleAppointmentSubmit.bind(this));
    }
  }

  private checkAuthentication(): void {
    if (!authManager.requirePatient()) {
      return;
    }
  }

  private async loadDashboardData(): Promise<void> {
    try {
      const user = authManager.getCurrentUser();
      if (!user) return;

      this.displayUserInfo(user);

      await this.loadMedicalRecords(user.id);

      await this.loadAppointments(user.id);

      await this.loadPrescriptions(user.id);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  }

  private displayUserInfo(user: any): void {
    this.userInfo.innerHTML = `
      <div class="user-card">
        <h3>Welcome, ${FormatUtils.formatUserName(user)}</h3>
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>Role:</strong> ${FormatUtils.formatUserRole(user.role)}</p>
        <p><strong>Patient ID:</strong> ${user.id}</p>
      </div>
    `;
  }

  private async loadMedicalRecords(patientId: number): Promise<void> {
    try {
      const response = await apiClient.getPatientRecord(patientId);

      if (response.success && response.record) {
        const record = DataUtils.transformMedicalRecordForDisplay(response.record);
        this.displayMedicalRecord(record);
      } else {
        this.medicalRecordsSection.innerHTML = `
          <div class="no-data">
            <p>No medical records found. Please contact your clinician to create your medical record.</p>
          </div>
        `;
      }
    } catch (error) {
      console.error('Error loading medical records:', error);
      this.medicalRecordsSection.innerHTML = `
        <div class="error">
          <p>Failed to load medical records. Please try again later.</p>
        </div>
      `;
    }
  }

  private displayMedicalRecord(record: any): void {
    this.medicalRecordsSection.innerHTML = `
      <div class="record-card">
        <h4>Medical Record</h4>
        <div class="record-grid">
          <div class="record-item">
            <strong>Age:</strong> ${record.age} years
          </div>
          <div class="record-item">
            <strong>Sex:</strong> ${record.sex}
          </div>
          <div class="record-item">
            <strong>Blood Pressure:</strong> ${record.formatted_blood_pressure}
            <span class="category">(${record.blood_pressure_category})</span>
          </div>
          <div class="record-item">
            <strong>Cholesterol:</strong> ${record.formatted_cholesterol}
            <span class="category">(${record.cholesterol_category})</span>
          </div>
          <div class="record-item">
            <strong>Fasting Blood Sugar >120 mg/dl:</strong> ${FormatUtils.formatBoolean(record.fasting_blood_sugar)}
          </div>
          <div class="record-item">
            <strong>Resting ECG:</strong> ${record.resting_ecg}
          </div>
          <div class="record-item">
            <strong>Exercise Induced Angina:</strong> ${FormatUtils.formatBoolean(record.exercise_induced_angina)}
          </div>
          <div class="record-item full-width">
            <strong>Diagnosis:</strong> ${record.diagnosis || 'Not specified'}
          </div>
          <div class="record-item full-width">
            <strong>Treatment Plan:</strong> ${record.treatment_plan || 'Not specified'}
          </div>
          <div class="record-item full-width">
            <strong>Medical History:</strong> ${record.medical_history || 'Not specified'}
          </div>
          <div class="record-item full-width">
            <strong>Allergies:</strong> ${record.allergies || 'None specified'}
          </div>
          <div class="record-item">
            <strong>Last Updated:</strong> ${record.formatted_updated_at}
          </div>
        </div>
      </div>
    `;
  }

  private async loadAppointments(patientId: number): Promise<void> {
    try {
      const response = await apiClient.getPatientAppointments(patientId);

      if (response.success && response.appointments) {
        const appointments = DataUtils.transformAppointmentsForDisplay(response.appointments);
        this.displayAppointments(appointments);
      } else {
        this.appointmentsSection.innerHTML = `
          <div class="no-data">
            <p>No appointments scheduled.</p>
          </div>
        `;
      }
    } catch (error) {
      console.error('Error loading appointments:', error);
      this.appointmentsSection.innerHTML = `
        <div class="error">
          <p>Failed to load appointments. Please try again later.</p>
        </div>
      `;
    }
  }

  private displayAppointments(appointments: any[]): void {
    if (appointments.length === 0) {
      this.appointmentsSection.innerHTML = `
        <div class="no-data">
          <p>No appointments scheduled.</p>
        </div>
      `;
      return;
    }

    const appointmentsHtml = appointments.map(apt => `
      <div class="appointment-card">
        <div class="appointment-header">
          <span class="status status-${apt.status}">${apt.status_badge}</span>
          <span class="date">${apt.formatted_date}</span>
        </div>
        <div class="appointment-details">
          <p><strong>Reason:</strong> ${apt.reason}</p>
        </div>
      </div>
    `).join('');

    this.appointmentsSection.innerHTML = `
      <div class="appointments-list">
        <h4>Your Appointments</h4>
        ${appointmentsHtml}
      </div>
    `;
  }

  private async loadPrescriptions(patientId: number): Promise<void> {
    try {
      const response = await apiClient.getPatientPrescriptions(patientId);

      if (response.success && response.prescriptions) {
        const prescriptions = DataUtils.transformPrescriptionsForDisplay(response.prescriptions);
        this.displayPrescriptions(prescriptions);
      } else {
        this.prescriptionsSection.innerHTML = `
          <div class="no-data">
            <p>No prescriptions found.</p>
          </div>
        `;
      }
    } catch (error) {
      console.error('Error loading prescriptions:', error);
      this.prescriptionsSection.innerHTML = `
        <div class="error">
          <p>Failed to load prescriptions. Please try again later.</p>
        </div>
      `;
    }
  }

  private displayPrescriptions(prescriptions: any[]): void {
    if (prescriptions.length === 0) {
      this.prescriptionsSection.innerHTML = `
        <div class="no-data">
          <p>No prescriptions found.</p>
        </div>
      `;
      return;
    }

    const prescriptionsHtml = prescriptions.map(pres => `
      <div class="prescription-card">
        <div class="prescription-header">
          <h5>${pres.medication}</h5>
          <span class="date">${pres.formatted_created_at}</span>
        </div>
        <div class="prescription-details">
          <p><strong>Dosage:</strong> ${pres.dosage}</p>
          <p><strong>Duration:</strong> ${pres.duration}</p>
        </div>
      </div>
    `).join('');

    this.prescriptionsSection.innerHTML = `
      <div class="prescriptions-list">
        <h4>Your Prescriptions</h4>
        ${prescriptionsHtml}
      </div>
    `;
  }

  private handleLogout(): void {
    if (confirm('Are you sure you want to logout?')) {
      authManager.logout();
      authManager.redirectToHome();
    }
  }

  private handleBookAppointment(): void {
    this.loadClinicians();
    const modal = document.getElementById('appointmentModal') as HTMLElement;
    if (modal) {
      modal.style.display = 'block';
    }
  }

  private closeModal(): void {
    const modal = document.getElementById('appointmentModal') as HTMLElement;
    if (modal) {
      modal.style.display = 'none';
    }
  }

  private async loadClinicians(): Promise<void> {
    try {
      const response = await apiClient.getClinicians();
      if (response.success && response.clinicians) {
        const clinicians = response.clinicians;
        const select = document.getElementById('clinicianSelect') as HTMLSelectElement;
        if (select) {
          select.innerHTML = '<option value="">Choose a clinician...</option>';
          clinicians.forEach((clinician: { id: number; first_name: string; last_name: string }) => {
            const option = document.createElement('option');
            option.value = clinician.id.toString();
            option.textContent = `Dr. ${clinician.first_name} ${clinician.last_name}`;
            select.appendChild(option);
          });
        }
      }
    } catch (error) {
      console.error('Error loading clinicians:', error);
    }
  }

  private async handleAppointmentSubmit(event: Event): Promise<void> {
    event.preventDefault();

    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    const user = authManager.getCurrentUser();
    if (!user) return;

    const appointmentData = {
      patient_id: user.id,
      clinician_id: parseInt(formData.get('clinician_id') as string),
      appointment_date: formData.get('appointmentDate') as string,
      reason: formData.get('appointmentReason') as string,
    };

    try {
      const response = await apiClient.createAppointment(appointmentData);

      if (response.success) {
        alert('Appointment booked successfully!');
        this.closeModal();
        form.reset();
        this.loadAppointments(user.id);
      } else {
        alert('Failed to book appointment. Please try again.');
      }
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert('Error booking appointment. Please try again later.');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new PatientDashboard();
});
