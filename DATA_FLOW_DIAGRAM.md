# 🔄 Hospital Management System - Data Flow Diagram

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HOSPITAL MANAGEMENT SYSTEM (HMS)                        │
│                           Data Flow Diagram                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     PATIENT     │    │     DOCTOR      │    │     ADMIN       │
│                 │    │                 │    │                 │
│ • View Profile  │    │ • Manage        │    │ • User          │
│ • Book Appts    │    │   Patients      │    │   Management    │
│ • Medical Hist  │    │ • View Schedule │    │ • System Config │
│ • Dashboard     │    │ • Update        │    │ • Reports       │
│                 │    │   Records       │    │ • Analytics     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTP Requests        │ HTTP Requests        │ HTTP Requests
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DJANGO FRAMEWORK                                 │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────┐  │
│ │     VIEWS       │ │   TEMPLATES     │ │      URLS       │ │  FORMS   │  │
│ │                 │ │                 │ │                 │ │          │  │
│ │ • Authentication│ │ • Patient       │ │ • Route         │ │ • Login  │  │
│ │ • Dashboard     │ │   Dashboard     │ │   Mapping       │ │ • Signup │  │
│ │ • CRUD Ops      │ │ • Doctor        │ │ • Namespace     │ │ • User   │  │
│ │ • Business      │ │   Dashboard     │ │   Management    │ │   Forms  │  │
│ │   Logic         │ │ • Admin         │ │ • URL Patterns  │ │          │  │
│ │                 │ │   Dashboard     │ │                 │ │          │  │
│ └─────────┬───────┘ └─────────┬───────┘ └─────────┬───────┘ └────┬─────┘  │
│           │                   │                   │              │        │
│           │     ┌─────────────┼───────────────────┼──────────────┘        │
│           │     │             │                   │                       │
│           ▼     ▼             ▼                   ▼                       │
│ ┌─────────────────────────────────────────────────────────────────────┐   │
│ │                         MODELS (ORM)                               │   │
│ │                                                                     │   │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│ │ │    USER     │ │   DOCTOR    │ │ APPOINTMENT │ │   PATIENT   │   │   │
│ │ │             │ │             │ │             │ │   HISTORY   │   │   │
│ │ │ • id        │ │ • user_id   │ │ • patient   │ │             │   │   │
│ │ │ • username  │ │ • specialty │ │ • doctor    │ │ • patient   │   │   │
│ │ │ • email     │ │ • dept      │ │ • date      │ │ • diagnosis │   │   │
│ │ │ • role      │ │ • schedule  │ │ • status    │ │ • treatment │   │   │
│ │ │ • profile   │ │ • rating    │ │ • notes     │ │ • date      │   │   │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
│           │                                                               │
└───────────┼───────────────────────────────────────────────────────────────┘
            │ SQL Queries/ORM Operations
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE LAYER                                    │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────┐   │
│ │                      SQLite Database (db.sqlite3)                  │   │
│ │                                                                     │   │
│ │  Tables:                                                            │   │
│ │  • auth_user           • doctors_doctor                            │   │
│ │  • users_profile       • appointments_appointment                  │   │
│ │  • doctors_department  • appointments_patienthistory               │   │
│ │  • doctors_specialization                                          │   │
│ │  • django_migrations                                               │   │
│ │                                                                     │   │
│ │  Data Storage:                                                      │   │
│ │  • User credentials & profiles                                     │   │
│ │  • Medical records & history                                       │   │
│ │  • Appointment schedules                                           │   │
│ │  • System configuration                                            │   │
│ └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Detailed Data Flow Processes

### 1. **User Authentication Flow**
```
User Input → Login Form → Django Auth → Session Creation → Role-based Redirect
     ↓           ↓            ↓             ↓                    ↓
  Username/   Validation   Database      Session Store      Patient/Doctor/
  Password    & CSRF      User Check     (Memory)          Admin Dashboard
```

### 2. **Patient Appointment Booking Flow**
```
Patient Dashboard → Book Appointment → Doctor Selection → Date/Time → Confirmation
        ↓                ↓                  ↓               ↓           ↓
   View Available     Load Doctor        Check Doctor     Validate    Save to
     Doctors           List from DB      Availability     Time Slot   Database
                                              ↓               ↓
                                        Query Existing   Create New
                                        Appointments     Appointment
```

### 3. **Doctor Patient Management Flow**
```
Doctor Dashboard → View Patients → Select Patient → Update Records → Save Changes
       ↓               ↓              ↓              ↓             ↓
  Load Doctor's    Query Patient   Load Patient    Update Patient  Database
  Appointments      Records        History         History         Commit
                       ↓               ↓              ↓
                  Join Patient    Display Medical  Validate
                  & Appointment   Records & Notes  Input Data
                  Tables
```

### 4. **Admin System Management Flow**
```
Admin Dashboard → User Management → CRUD Operations → System Updates → Database Changes
       ↓               ↓                 ↓               ↓                ↓
  Load System     Query All Users   Create/Update/    Apply Changes    Commit
  Statistics      & Statistics      Delete Users      to Models        Transaction
       ↓               ↓                 ↓               ↓
  Calculate       Join Multiple     Validate User     Update Related
  Metrics         Tables            Data & Roles      Records
```

## 📋 Data Entity Relationships

### **Core Entities & Relationships**
```
USER (1) ──────────── (0..1) DOCTOR
 │                              │
 │                              │
 │ (1)                         │ (1)
 │                              │
 ▼                              ▼
PATIENT_PROFILE           DOCTOR_PROFILE
 │                              │
 │ (1)                         │ (1)
 │                              │
 ▼                              ▼
APPOINTMENT ◄──────────────────(M:1)
 │
 │ (1:M)
 ▼
PATIENT_HISTORY

DEPARTMENT (1) ──── (M) DOCTOR
SPECIALIZATION (1) ── (M) DOCTOR
```

## 🔄 Data Flow by User Role

### **📱 Patient Data Flow**
1. **Login** → User table validation → Session creation
2. **Dashboard** → Load patient profile + recent appointments
3. **Book Appointment** → Query available doctors → Create appointment record
4. **View History** → Fetch patient history records
5. **Update Profile** → Modify user/patient profile data

### **👨‍⚕️ Doctor Data Flow**
1. **Login** → User + Doctor table validation → Session creation
2. **Dashboard** → Load doctor profile + today's appointments
3. **Patient Management** → Query assigned patients → Load medical history
4. **Update Records** → Create/modify patient history records
5. **Schedule Management** → View/modify appointment status

### **🔧 Admin Data Flow**
1. **Login** → User table validation (admin role) → Session creation
2. **Dashboard** → Aggregate queries (user count, appointment stats)
3. **User Management** → CRUD operations on user table
4. **Doctor Management** → CRUD operations on doctor + department tables
5. **Reports** → Complex queries across multiple tables
6. **System Config** → Modify system settings and configurations

## 📊 Database Schema Flow

### **Write Operations**
```
User Input → Form Validation → Model Validation → Database Write → Response
    ↓             ↓               ↓                 ↓              ↓
  Forms.py    Clean Methods   Model.save()      SQL INSERT/    Success/Error
  Validation   & Validators   Django ORM       UPDATE Query     Message
```

### **Read Operations**
```
Request → View Processing → Model Query → Database Read → Template Rendering
   ↓           ↓              ↓             ↓                ↓
URL Route   Business Logic  Django ORM   SQL SELECT      HTML Response
Matching    & Permissions   QuerySet     Query Execution  with Data
```

## 🔐 Security Data Flow

### **Authentication & Authorization**
```
Request → Session Check → User Permissions → Role Validation → Access Grant/Deny
   ↓           ↓              ↓                ↓                    ↓
Middleware  Session Store  User.role        @login_required      View Execution
Processing  Validation     Check            Decorator            or Access Denied
```

## 📈 Performance & Optimization

### **Query Optimization Flow**
```
View Request → Query Optimization → Database Execution → Response Caching
     ↓              ↓                    ↓                    ↓
  select_related  Minimize DB hits   Efficient SQL        Template Cache
  prefetch_related   Indexing       Query Planning       Static Files Cache
```

---

This data flow diagram shows how information moves through your Hospital Management System, from user interactions to database operations and back to user interfaces. Each role (Patient, Doctor, Admin) has specific data access patterns optimized for their needs.
