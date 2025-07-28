from django.db import models
from django.utils import timezone
from users.models import User
from doctors.models import Doctor

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rescheduled', 'Rescheduled'),
        ('no_show', 'No Show'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('routine_checkup', 'Routine Checkup'),
    ]
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'}, related_name='patient_appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateTimeField()
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='consultation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    duration = models.IntegerField(default=30, help_text="Duration in minutes")  # Duration in minutes

    reason = models.TextField(default="General consultation", blank=True)  # Main reason field
    reason_for_visit = models.TextField(default="General consultation")  # Keep for compatibility
    notes = models.TextField(blank=True)  # Patient notes
    doctor_notes = models.TextField(blank=True)  # Doctor notes
    prescription = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.patient.username} - Dr. {self.doctor.user.username} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        return self.appointment_date > timezone.now() and self.status in ['pending', 'confirmed']
    
    @property
    def is_today(self):
        return self.appointment_date.date() == timezone.now().date()
    
    @property
    def appointment_time(self):
        """Get just the time portion of appointment_date"""
        return self.appointment_date.time()

class PatientHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'}, related_name='medical_history')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patient_records')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    visit_date = models.DateTimeField(default=timezone.now)
    chief_complaint = models.TextField(default="General complaint")
    diagnosis = models.TextField(default="Pending diagnosis")
    prescription = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    lab_results = models.TextField(blank=True)
    vital_signs = models.JSONField(default=dict, blank=True)  # Store BP, pulse, temp, etc.
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        verbose_name_plural = "Patient Histories"
    
    def __str__(self):
        return f"{self.patient.username} - {self.visit_date.strftime('%Y-%m-%d')} - {self.diagnosis[:50]}"

class Review(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'appointment']
    
    def __str__(self):
        return f"{self.patient.username} - Dr. {self.doctor.user.username} - {self.rating} stars"