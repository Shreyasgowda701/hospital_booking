from django.contrib import admin
from .models import Department, Specialization, Doctor, DoctorAvailability

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'department', 'experience_years', 'rating', 'is_available']
    list_filter = ['specialization', 'department', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['rating', 'total_reviews']

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_of_week_display', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
