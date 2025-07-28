from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from doctors.models import Specialization

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