# Hospital Management System (HMS)

A modern, responsive Hospital Management System built with Django 5.2.4, featuring role-based dashboards for Patients, Doctors, and Administrators.

![HMS Preview](https://img.shields.io/badge/Django-5.2.4-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🏥 **Multi-Role Dashboard System**
- **Patient Dashboard**: Green-themed interface with appointment booking and medical records
- **Doctor Dashboard**: Blue-themed interface with patient management and schedules  
- **Admin Dashboard**: Red-themed interface with comprehensive system administration

### 🎨 **Modern UI/UX**
- Responsive design that works on all devices
- Animated backgrounds with floating medical icons
- Glass-morphism effects and smooth transitions
- Professional medical theme with role-based color schemes
- Font Awesome icons and Google Fonts integration

### 🔐 **User Management**
- Role-based authentication (Patient, Doctor, Admin)
- Secure user registration and login
- User profile management
- Access control based on user roles

### 📊 **Dashboard Features**
- Real-time statistics display
- Appointment management
- Patient records
- Doctor profiles and specializations
- System reports and analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### 1. Clone/Download the Project
```bash
# If you received this as a ZIP file, extract it
# If it's a Git repository:
git clone <repository-url>
cd hospital_booking
```

### 2. Set up Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
Open your web browser and go to: `http://127.0.0.1:8000`

## 👥 Default User Accounts

The database comes with pre-configured user accounts for testing:

### Admin Account
- **Username**: `shreyasadmin`
- **Password**: `admin@123`
- **Role**: Administrator
- **Access**: Full system administration

### Doctor Account
- **Username**: `shreyasdoctor`
- **Password**: `admin@123`
- **Role**: Doctor
- **Access**: Patient management, appointments

### Patient Account
- **Username**: `shreyaspatient`
- **Password**: `admin@123`
- **Role**: Patient
- **Access**: Appointment booking, medical records

*Note: Change these passwords in a production environment*

## 📁 Project Structure

```
hospital_booking/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── db.sqlite3               # SQLite database (includes all data)
├── hospital_booking/        # Main Django project
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── users/                   # User management app
│   ├── models.py            # User models
│   ├── views.py             # Authentication views
│   └── urls.py              # User URLs
├── doctors/                 # Doctor management app
├── admins/                  # Admin management app
├── appointments/            # Appointment management app
└── templates/               # HTML templates
    ├── users/               # User templates (login, dashboards)
    └── admins/              # Admin templates
```

## 🎯 How to Use

### For Patients:
1. Register as a new patient or login with existing credentials
2. Access the green-themed patient dashboard
3. Book appointments with available doctors
4. View medical history and records

### For Doctors:
1. Login with doctor credentials
2. Access the blue-themed doctor dashboard
3. View and manage patient appointments
4. Update patient records and medical history

### For Administrators:
1. Login with admin credentials
2. Access the red-themed admin dashboard
3. Manage users (patients, doctors, admins)
4. View system statistics and reports
5. Configure hospital settings

## 🔧 Customization

### Adding New Users
1. Go to the admin dashboard
2. Use the "User Management" feature
3. Or use Django admin panel at `/admin/`

### Modifying Themes
- Patient theme colors: Edit CSS variables in `templates/users/patient_dashboard.html`
- Doctor theme colors: Edit CSS variables in `templates/users/doctor_dashboard.html`  
- Admin theme colors: Edit CSS variables in `templates/admins/dashboard.html`

### Database Management
```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

## 📱 Responsive Design

The application is fully responsive and works seamlessly on:
- 💻 Desktop computers
- 📱 Mobile phones  
- 📟 Tablets
- 🖥️ Large displays

## 🛠️ Technical Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite3 (included)
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Poppins)
- **Styling**: Modern CSS with animations and gradients

## 🔒 Security Features

- CSRF protection enabled
- User authentication and authorization
- Role-based access control
- SQL injection protection via Django ORM
- XSS protection with Django templates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

If you encounter any issues:

1. **Check the console** for error messages when running `python manage.py runserver`
2. **Verify Python version** is 3.8 or higher: `python --version`
3. **Ensure all dependencies are installed**: `pip install -r requirements.txt`
4. **Check database**: The `db.sqlite3` file should be present in the root directory

## 🎉 Features Showcase

### Modern Authentication
- Beautiful login/signup forms with animations
- Role-based redirection after login
- Secure password handling

### Dashboard Analytics
- Real-time user statistics
- Appointment tracking
- System performance metrics

### Professional Medical Theme
- Color-coded interfaces for different roles
- Medical icons and professional typography
- Smooth animations and transitions

---

**Built with ❤️ using Django and modern web technologies**

*Last updated: July 2025*
