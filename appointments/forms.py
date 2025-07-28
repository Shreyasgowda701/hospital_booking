from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Appointment
from doctors.models import Doctor, Specialization, Department
from django.utils import timezone
from datetime import datetime, timedelta

class PatientSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    blood_group = forms.CharField(max_length=5, required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    emergency_contact_phone = forms.CharField(max_length=15, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'gender', 'address', 'blood_group',
                 'emergency_contact_name', 'emergency_contact_phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "patient"
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.gender = self.cleaned_data['gender']
        user.address = self.cleaned_data['address']
        user.blood_group = self.cleaned_data['blood_group']
        user.emergency_contact_name = self.cleaned_data['emergency_contact_name']
        user.emergency_contact_phone = self.cleaned_data['emergency_contact_phone']
        if commit:
            user.save()
        return user

class DoctorSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    specialization = forms.ModelChoiceField(queryset=Specialization.objects.all(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "doctor"
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create doctor profile
            from doctors.models import Doctor
            Doctor.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                department=self.cleaned_data['specialization'].department,
                license_number=f"LIC{user.id:06d}",
                qualification="General Practitioner"
            )
        return user

class AdminSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "admin"
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

class DoctorSearchForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments"
    )
    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        required=False,
        empty_label="All Specializations"
    )
    availability_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
        initial=timezone.now().date()
    )

class AppointmentBookingForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()})
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    duration = forms.IntegerField(
        initial=30,
        min_value=15,
        max_value=120,
        widget=forms.NumberInput(attrs={'step': 15})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe your reason for visit...'})
    )
    
    class Meta:
        model = Appointment
        fields = ['appointment_type']
    
    def __init__(self, *args, **kwargs):
        self.doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        appointment = super().save(commit=False)
        # Combine date and time
        appointment_datetime = datetime.combine(
            self.cleaned_data['appointment_date'],
            self.cleaned_data['appointment_time']
        )
        appointment.appointment_date = timezone.make_aware(appointment_datetime)
        appointment.doctor = self.doctor
        appointment.duration = self.cleaned_data.get('duration', 30)
        reason = self.cleaned_data.get('reason', 'General consultation')
        appointment.reason = reason
        appointment.reason_for_visit = reason  # Keep both for compatibility
        if commit:
            appointment.save()
        return appointment
