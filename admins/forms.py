from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from doctors.models import Doctor, Department, Specialization

class DoctorCreationForm(UserCreationForm):
    """Form for creating a new doctor user account"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class DoctorProfileForm(forms.ModelForm):
    """Form for managing doctor profile information"""
    
    class Meta:
        model = Doctor
        fields = [
            'specialization', 'department', 'license_number', 
            'experience_years', 'qualification', 'consultation_fee',
            'biography', 'phone_number', 'is_available'
        ]
        widgets = {
            'biography': forms.Textarea(attrs={'rows': 4}),
            'consultation_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'experience_years': forms.NumberInput(attrs={'min': 0}),
        }

class DoctorUpdateForm(forms.ModelForm):
    """Form for updating doctor user information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

class DepartmentForm(forms.ModelForm):
    """Form for managing departments"""
    
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SpecializationForm(forms.ModelForm):
    """Form for managing specializations"""
    
    class Meta:
        model = Specialization
        fields = ['name', 'department', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
