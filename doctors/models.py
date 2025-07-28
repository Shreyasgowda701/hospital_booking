from django.db import models
from users.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='specializations')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True, default="TEMP000")
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=200, default="General Practitioner")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    biography = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization.name}"
    
    def get_full_name(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"

class DoctorAvailability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"