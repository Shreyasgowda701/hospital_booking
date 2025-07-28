# 🏗️ System Architecture Diagram

## 📐 HMS System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   PATIENT   │  │   DOCTOR    │  │    ADMIN    │  │   PUBLIC    │       │
│  │  INTERFACE  │  │  INTERFACE  │  │  INTERFACE  │  │  INTERFACE  │       │
│  │             │  │             │  │             │  │             │       │
│  │ • Dashboard │  │ • Dashboard │  │ • Dashboard │  │ • Home Page │       │
│  │ • Booking   │  │ • Patients  │  │ • Users Mgmt│  │ • Login     │       │
│  │ • History   │  │ • Schedule  │  │ • Reports   │  │ • Register  │       │
│  │ • Profile   │  │ • Records   │  │ • Settings  │  │ • Info      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                 │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            WEB LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DJANGO FRAMEWORK                              │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │    URLS     │  │   VIEWS     │  │  TEMPLATES  │  │  STATIC   │ │   │
│  │  │             │  │             │  │             │  │   FILES   │ │   │
│  │  │ • Routing   │  │ • Business  │  │ • HTML      │  │           │ │   │
│  │  │ • Patterns  │  │   Logic     │  │ • CSS       │  │ • CSS     │ │   │
│  │  │ • Namespace │  │ • Auth      │  │ • JavaScript│  │ • JS      │ │   │
│  │  │   Management│  │ • CRUD Ops  │  │ • Jinja2    │  │ • Images  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MIDDLEWARE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ SECURITY    │  │ SESSION     │  │ CSRF        │  │ CORS        │       │
│  │ MIDDLEWARE  │  │ MIDDLEWARE  │  │ MIDDLEWARE  │  │ MIDDLEWARE  │       │
│  │             │  │             │  │             │  │             │       │
│  │ • Auth      │  │ • Session   │  │ • Token     │  │ • Cross     │       │
│  │ • Perms     │  │   Management│  │   Validation│  │   Origin    │       │
│  │ • Headers   │  │ • User Data │  │ • Form      │  │   Requests  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                                                                   │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   USERS     │  │   DOCTORS   │  │   ADMINS    │  │APPOINTMENTS │       │
│  │     APP     │  │     APP     │  │     APP     │  │     APP     │       │
│  │             │  │             │  │             │  │             │       │
│  │ • Models    │  │ • Models    │  │ • Models    │  │ • Models    │       │
│  │ • Views     │  │ • Views     │  │ • Views     │  │ • Views     │       │
│  │ • Forms     │  │ • Forms     │  │ • Forms     │  │ • Forms     │       │
│  │ • URLs      │  │ • URLs      │  │ • URLs      │  │ • URLs      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│         │                                                                   │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MODEL LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      DJANGO ORM                                     │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │    USER     │  │   DOCTOR    │  │ APPOINTMENT │  │  PATIENT  │ │   │
│  │  │   MODEL     │  │   MODEL     │  │    MODEL    │  │  HISTORY  │ │   │
│  │  │             │  │             │  │             │  │   MODEL   │ │   │
│  │  │ • Fields    │  │ • Fields    │  │ • Fields    │  │           │ │   │
│  │  │ • Methods   │  │ • Methods   │  │ • Methods   │  │ • Fields  │ │   │
│  │  │ • Meta      │  │ • Meta      │  │ • Meta      │  │ • Methods │ │   │
│  │  │ • Relations │  │ • Relations │  │ • Relations │  │ • Meta    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SQLite DATABASE                                 │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │ auth_user   │  │doctors_     │  │appointments_│  │  Custom   │ │   │
│  │  │    TABLE    │  │  doctor     │  │ appointment │  │  Tables   │ │   │
│  │  │             │  │   TABLE     │  │    TABLE    │  │           │ │   │
│  │  │ • id        │  │             │  │             │  │ • patient │ │   │
│  │  │ • username  │  │ • user_id   │  │ • patient   │  │   history │ │   │
│  │  │ • email     │  │ • specialty │  │ • doctor    │  │ • depart  │ │   │
│  │  │ • password  │  │ • department│  │ • datetime  │  │   ments   │ │   │
│  │  │ • is_active │  │ • bio       │  │ • status    │  │ • special │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Communication Flow

### **Request Flow (Top-Down)**
```
1. USER REQUEST
   ↓
2. DJANGO URL DISPATCHER
   ↓
3. MIDDLEWARE PROCESSING
   ↓
4. VIEW FUNCTION/CLASS
   ↓
5. MODEL OPERATIONS (ORM)
   ↓
6. DATABASE QUERIES
   ↓
7. RESPONSE GENERATION
   ↓
8. TEMPLATE RENDERING
   ↓
9. HTTP RESPONSE TO USER
```

### **Response Flow (Bottom-Up)**
```
1. DATABASE RESULT SET
   ↓
2. ORM OBJECT CREATION
   ↓
3. BUSINESS LOGIC PROCESSING
   ↓
4. CONTEXT DATA PREPARATION
   ↓
5. TEMPLATE ENGINE PROCESSING
   ↓
6. HTML GENERATION
   ↓
7. MIDDLEWARE POST-PROCESSING
   ↓
8. HTTP RESPONSE DELIVERY
```

## 🛡️ Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYERS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │    INPUT    │  │    AUTH     │  │ PERMISSION  │  │    DATA     │       │
│  │ VALIDATION  │  │ MIDDLEWARE  │  │   CONTROL   │  │ PROTECTION  │       │
│  │             │  │             │  │             │  │             │       │
│  │ • Form      │  │ • Session   │  │ • Role      │  │ • SQL       │       │
│  │   Validation│  │   Management│  │   Based     │  │   Injection │       │
│  │ • CSRF      │  │ • Login     │  │ • Decorator │  │   Prevention│       │
│  │   Protection│  │   Required  │  │   Based     │  │ • XSS       │       │
│  │ • Sanitize  │  │ • Password  │  │ • View      │  │   Protection│       │
│  │   Input     │  │   Hashing   │  │   Level     │  │ • ORM       │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📱 Component Interaction

### **Frontend Components**
```
HTML Templates ◄──► CSS Styling ◄──► JavaScript
      ▲                  ▲                ▲
      │                  │                │
      ▼                  ▼                ▼
Django Template    Font Awesome      Form Validation
    Engine            Icons           & Interactions
```

### **Backend Components**
```
Django Views ◄──► Django Models ◄──► Database
     ▲                 ▲                ▲
     │                 │                │
     ▼                 ▼                ▼
URL Routing      ORM Operations    SQL Queries
```

### **Authentication Flow**
```
Login Form → Django Auth → Session Store → Permission Check → Dashboard Redirect
    ▲             ▲            ▲               ▲                    ▲
    │             │            │               │                    │
User Input    Password     Session Cookie   Role Validation    Role-based
Validation    Verification     Creation      @login_required     Interface
```

This architecture diagram shows the complete structure of your Hospital Management System, from user interfaces down to the database layer, including security measures and data flow patterns.
