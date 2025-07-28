from django.urls import path
from .views import patient_dashboard, doctor_dashboard, admin_dashboard, CustomLoginView, CustomLogoutView, patient_signup, doctor_signup, admin_signup, home, coming_soon

urlpatterns = [
    path("dashboard/patient/", patient_dashboard, name="patient_dashboard"),
    path("dashboard/doctor/", doctor_dashboard, name="doctor_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("signup/patient/", patient_signup, name="signup_patient"),
    path("signup/doctor/", doctor_signup, name="signup_doctor"),
    path("signup/admin/", admin_signup, name="signup_admin"),
    path("coming-soon/", coming_soon, name="coming_soon"),
    path("", home, name="home"),
]