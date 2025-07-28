from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    
    # Doctor Management
    path('doctors/', views.doctor_management, name='doctor_management'),
    path('doctors/add/', views.add_doctor, name='add_doctor'),
    path('doctors/<int:doctor_id>/edit/', views.edit_doctor, name='edit_doctor'),
    path('doctors/<int:doctor_id>/delete/', views.delete_doctor, name='delete_doctor'),
    
    # Hospital Management
    path('hospital/', views.hospital_management, name='hospital_management'),
    
    # Department Management
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:department_id>/delete/', views.delete_department, name='delete_department'),
    
    # Specialization Management
    path('specializations/add/', views.add_specialization, name='add_specialization'),
    path('specializations/<int:specialization_id>/edit/', views.edit_specialization, name='edit_specialization'),
    path('specializations/<int:specialization_id>/delete/', views.delete_specialization, name='delete_specialization'),
    
    # Appointments
    path('appointments/', views.appointment_overview, name='appointment_overview'),
    
    # Reports
    path('reports/', views.system_reports, name='system_reports'),
]
