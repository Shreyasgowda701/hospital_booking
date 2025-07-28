# 🗄️ Database Schema & Entity Relationship Diagram

## 📊 HMS Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       HOSPITAL MANAGEMENT SYSTEM                           │
│                         DATABASE SCHEMA                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│     auth_user       │         │   users_profile     │
│ (Django Built-in)   │◄────────┤   (Extended User)   │
├─────────────────────┤   1:1   ├─────────────────────┤
│ • id (PK)          │         │ • id (PK)          │
│ • username         │         │ • user_id (FK)     │
│ • first_name       │         │ • role             │
│ • last_name        │         │ • phone            │
│ • email            │         │ • address          │
│ • password         │         │ • date_of_birth    │
│ • is_staff         │         │ • profile_picture  │
│ • is_active        │         │ • created_at       │
│ • is_superuser     │         │ • updated_at       │
│ • date_joined      │         └─────────────────────┘
│ • last_login       │                     │
└─────────────────────┘                     │ 1:1
           │                               │ (role='doctor')
           │ 1:1                          ▼
           │ (role='patient')  ┌─────────────────────┐
           ▼                   │   doctors_doctor    │
┌─────────────────────┐         ├─────────────────────┤
│  patient_profile    │         │ • id (PK)          │
├─────────────────────┤         │ • user_id (FK)     │
│ • id (PK)          │         │ • specialization   │
│ • user_id (FK)     │         │ • department_id    │
│ • emergency_contact│         │ • license_number   │
│ • blood_group      │         │ • experience_years │
│ • medical_history  │         │ • qualification    │
│ • insurance_info   │         │ • bio              │
│ • allergies        │         │ • consultation_fee │
└─────────────────────┘         │ • rating           │
           │                    │ • is_available     │
           │                    │ • created_at       │
           │ 1:M               └─────────────────────┘
           │                              │
           │                              │ M:1
           │                              ▼
           │                    ┌─────────────────────┐
           │                    │ doctors_department  │
           │                    ├─────────────────────┤
           │                    │ • id (PK)          │
           │                    │ • name             │
           │                    │ • description      │
           │                    │ • head_doctor      │
           │                    │ • location         │
           │                    │ • phone            │
           │                    │ • created_at       │
           │                    └─────────────────────┘
           │
           │              ┌─────────────────────┐
           │              │doctors_specialization│
           │              ├─────────────────────┤
           │              │ • id (PK)          │
           │              │ • name             │
           │              │ • description      │
           │              │ • requirements     │
           │              │ • created_at       │
           │              └─────────────────────┘
           │                        ▲
           │                        │ M:M
           │                        │
           ▼                        ▼
┌─────────────────────┐         ┌─────────────────────┐
│appointments_        │         │doctor_specialization│
│    appointment      │         │   (Junction Table)  │
├─────────────────────┤         ├─────────────────────┤
│ • id (PK)          │         │ • id (PK)          │
│ • patient_id (FK)  │◄────────┤ • doctor_id (FK)   │
│ • doctor_id (FK)   │   M:1   │ • specialization_id│
│ • appointment_date │         └─────────────────────┘
│ • appointment_time │
│ • status           │                    │
│ • symptoms         │                    │
│ • notes            │                    │ 1:M
│ • diagnosis        │                    │
│ • prescription     │                    ▼
│ • follow_up_date   │         ┌─────────────────────┐
│ • created_at       │         │appointments_        │
│ • updated_at       │         │  patienthistory     │
└─────────────────────┘         ├─────────────────────┤
           │                    │ • id (PK)          │
           │ 1:M               │ • patient_id (FK)  │
           │                    │ • appointment_id   │
           ▼                    │ • diagnosis        │
┌─────────────────────┐         │ • treatment        │
│   payment_record    │         │ • prescription     │
├─────────────────────┤         │ • notes            │
│ • id (PK)          │         │ • date_created     │
│ • appointment_id   │         │ • follow_up_date   │
│ • amount           │         │ • doctor_notes     │
│ • payment_method   │         └─────────────────────┘
│ • payment_status   │
│ • transaction_id   │
│ • payment_date     │
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│doctors_availability │         │   system_settings   │
├─────────────────────┤         ├─────────────────────┤
│ • id (PK)          │         │ • id (PK)          │
│ • doctor_id (FK)   │         │ • hospital_name    │
│ • day_of_week      │         │ • address          │
│ • start_time       │         │ • phone            │
│ • end_time         │         │ • email            │
│ • is_active        │         │ • website          │
│ • created_at       │         │ • logo             │
└─────────────────────┘         │ • established_year │
                                │ • license_number   │
                                └─────────────────────┘
```

## 🔗 Relationship Types

### **Primary Relationships**

1. **User ↔ Profile (1:1)**
   ```
   auth_user.id ──── users_profile.user_id
   ```

2. **User ↔ Doctor (1:1)**
   ```
   auth_user.id ──── doctors_doctor.user_id
   WHERE users_profile.role = 'doctor'
   ```

3. **Patient ↔ Appointment (1:M)**
   ```
   auth_user.id ──── appointments_appointment.patient_id
   WHERE users_profile.role = 'patient'
   ```

4. **Doctor ↔ Appointment (1:M)**
   ```
   doctors_doctor.id ──── appointments_appointment.doctor_id
   ```

5. **Department ↔ Doctor (1:M)**
   ```
   doctors_department.id ──── doctors_doctor.department_id
   ```

6. **Appointment ↔ Patient History (1:M)**
   ```
   appointments_appointment.id ──── appointments_patienthistory.appointment_id
   ```

## 📋 Table Descriptions

### **Core User Tables**
- **auth_user**: Django's built-in user authentication table
- **users_profile**: Extended user information with role-based data
- **doctors_doctor**: Doctor-specific profile information

### **Medical Tables**
- **appointments_appointment**: Appointment scheduling and management
- **appointments_patienthistory**: Medical records and treatment history
- **doctors_department**: Hospital departments and specializations
- **doctors_specialization**: Medical specialties and certifications

### **System Tables**
- **doctors_availability**: Doctor working hours and schedule
- **system_settings**: Hospital configuration and settings
- **payment_record**: Payment and billing information

## 🔄 Data Flow Queries

### **Common Query Patterns**

1. **Get Patient Appointments**
   ```sql
   SELECT a.*, d.user_id, u.first_name, u.last_name
   FROM appointments_appointment a
   JOIN doctors_doctor d ON a.doctor_id = d.id
   JOIN auth_user u ON d.user_id = u.id
   WHERE a.patient_id = ?
   ```

2. **Get Doctor's Schedule**
   ```sql
   SELECT a.*, p.first_name, p.last_name
   FROM appointments_appointment a
   JOIN auth_user p ON a.patient_id = p.id
   WHERE a.doctor_id = ? AND DATE(a.appointment_date) = ?
   ```

3. **Get Patient Medical History**
   ```sql
   SELECT ph.*, a.appointment_date, d.user_id, u.first_name
   FROM appointments_patienthistory ph
   JOIN appointments_appointment a ON ph.appointment_id = a.id
   JOIN doctors_doctor d ON a.doctor_id = d.id
   JOIN auth_user u ON d.user_id = u.id
   WHERE ph.patient_id = ?
   ORDER BY a.appointment_date DESC
   ```

## 🔐 Security Considerations

### **Data Protection**
- **Password Hashing**: Django's built-in password hashing
- **Role-based Access**: User roles determine data access
- **Foreign Key Constraints**: Maintain data integrity
- **Audit Trail**: Created/updated timestamps on critical tables

### **Privacy Compliance**
- **Medical Data**: Patient history and appointments are protected
- **User Information**: Personal data access is role-restricted
- **Appointment Privacy**: Only patient, doctor, and admin can view

This database schema ensures data integrity, security, and efficient querying for your Hospital Management System.
