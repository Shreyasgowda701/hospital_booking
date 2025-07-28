from django.contrib import admin
from .models import Appointment, PatientHistory, Review

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'appointment_type']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['patient__username', 'doctor__user__username']
    date_hierarchy = 'appointment_date'

@admin.register(PatientHistory)
class PatientHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'visit_date', 'diagnosis']
    list_filter = ['visit_date', 'doctor']
    search_fields = ['patient__username', 'diagnosis']
    date_hierarchy = 'visit_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['patient__username', 'doctor__user__username']
