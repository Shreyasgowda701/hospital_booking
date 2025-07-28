from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Doctor search and booking
    path('doctors/', views.doctor_search, name='doctor_search'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:doctor_id>/book/', views.book_appointment, name='book_appointment'),
    
    # Patient appointment management
    path('my-appointments/', views.patient_appointments, name='patient_appointments'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    
    # Medical history
    path('medical-history/', views.patient_medical_history, name='patient_medical_history'),
    
    # Doctor portal
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/availability/', views.manage_availability, name='manage_availability'),
    path('doctor/patients/', views.patient_records, name='patient_records'),
    path('doctor/patients/<int:patient_id>/', views.patient_record_detail, name='patient_record_detail'),
    path('doctor/appointments/<int:appointment_id>/status/', views.update_appointment_status, name='update_appointment_status'),
    
    # AJAX endpoints
    path('api/doctor/<int:doctor_id>/availability/', views.get_doctor_availability, name='doctor_availability_api'),
]
