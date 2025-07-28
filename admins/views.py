from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from users.models import User
from doctors.models import Doctor, Department, Specialization, DoctorAvailability
from appointments.models import Appointment, PatientHistory
from .forms import (
    DoctorCreationForm, DoctorProfileForm, DoctorUpdateForm,
    DepartmentForm, SpecializationForm
)

@login_required
def admin_dashboard(request):
    """Enhanced admin dashboard with statistics"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    # Get statistics for dashboard
    total_users = User.objects.count()
    total_patients = User.objects.filter(role='patient').count()
    total_doctors = User.objects.filter(role='doctor').count()
    total_admins = User.objects.filter(role='admin').count()
    
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    today_appointments = Appointment.objects.filter(
        appointment_date__date=timezone.now().date()
    ).count()
    
    # Recent activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor__user'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_admins': total_admins,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'today_appointments': today_appointments,
        'recent_users': recent_users,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'admins/dashboard.html', context)

@login_required
def user_management(request):
    """Manage all users in the system"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    # Filter users by role if requested
    role_filter = request.GET.get('role', '')
    search_query = request.GET.get('search', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search_query': search_query,
    }
    return render(request, 'admins/user_management.html', context)

@login_required
def doctor_management(request):
    """Manage doctor profiles and information"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    doctors = Doctor.objects.select_related(
        'user', 'specialization', 'department'
    ).order_by('-created_at')
    
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(specialization__name__icontains=search_query) |
            Q(license_number__icontains=search_query)
        )
    
    if department_filter:
        doctors = doctors.filter(department_id=department_filter)
    
    departments = Department.objects.all()
    
    context = {
        'doctors': doctors,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
    }
    return render(request, 'admins/doctor_management.html', context)

@login_required
def hospital_management(request):
    """Manage departments and specializations"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    departments = Department.objects.prefetch_related('specializations').annotate(
        doctor_count=Count('doctor'),
        specialization_count=Count('specializations')
    ).order_by('name')
    
    context = {
        'departments': departments,
    }
    return render(request, 'admins/hospital_management.html', context)

@login_required
def appointment_overview(request):
    """Overview of all appointments in the system"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    doctor_filter = request.GET.get('doctor', '')
    
    appointments = Appointment.objects.select_related(
        'patient', 'doctor__user', 'doctor__specialization'
    ).order_by('-appointment_date')
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointment_date__date=date_filter)
    
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    
    # Statistics
    appointment_stats = {
        'total': appointments.count(),
        'pending': appointments.filter(status='pending').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
    }
    
    doctors = Doctor.objects.select_related('user').order_by('user__first_name')
    
    context = {
        'appointments': appointments[:100],  # Limit to 100 for performance
        'appointment_stats': appointment_stats,
        'doctors': doctors,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'doctor_filter': doctor_filter,
    }
    return render(request, 'admins/appointment_overview.html', context)

@login_required
def system_reports(request):
    """Generate system reports and analytics"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    # Weekly appointment statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    weekly_appointments = Appointment.objects.filter(
        appointment_date__date__gte=week_ago
    ).count()
    
    monthly_appointments = Appointment.objects.filter(
        appointment_date__date__gte=month_ago
    ).count()
    
    # Department wise statistics
    department_stats = Department.objects.annotate(
        doctor_count=Count('doctor'),
        appointment_count=Count('doctor__doctor_appointments')
    ).order_by('-appointment_count')
    
    # Top doctors by appointments
    top_doctors = Doctor.objects.annotate(
        appointment_count=Count('doctor_appointments')
    ).select_related('user', 'specialization').order_by('-appointment_count')[:10]
    
    context = {
        'weekly_appointments': weekly_appointments,
        'monthly_appointments': monthly_appointments,
        'department_stats': department_stats,
        'top_doctors': top_doctors,
    }
    return render(request, 'admins/system_reports.html', context)

@login_required
def user_detail(request, user_id):
    """View detailed information about a specific user"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    user = get_object_or_404(User, id=user_id)
    
    # Get additional information based on user role
    context = {'user': user}
    
    if user.role == 'doctor':
        try:
            doctor = Doctor.objects.select_related(
                'specialization', 'department'
            ).get(user=user)
            appointments = Appointment.objects.filter(doctor=doctor).count()
            context.update({
                'doctor': doctor,
                'appointment_count': appointments,
            })
        except Doctor.DoesNotExist:
            pass
    
    elif user.role == 'patient':
        appointments = Appointment.objects.filter(patient=user).count()
        medical_history = PatientHistory.objects.filter(patient=user).count()
        context.update({
            'appointment_count': appointments,
            'medical_history_count': medical_history,
        })
    
    return render(request, 'admins/user_detail.html', context)

@login_required
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")
    
    return redirect('admins:user_management')

# Doctor CRUD Operations
@login_required
def add_doctor(request):
    """Add a new doctor to the system"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    if request.method == 'POST':
        user_form = DoctorCreationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create user account
                    user = user_form.save()
                    
                    # Create doctor profile
                    doctor = profile_form.save(commit=False)
                    doctor.user = user
                    doctor.save()
                    
                    messages.success(request, f"Doctor {user.get_full_name()} has been added successfully.")
                    return redirect('admins:doctor_management')
            except Exception as e:
                messages.error(request, f"Error creating doctor: {str(e)}")
    else:
        user_form = DoctorCreationForm()
        profile_form = DoctorProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'action': 'Add',
    }
    return render(request, 'admins/doctor_form.html', context)

@login_required
def edit_doctor(request, doctor_id):
    """Edit an existing doctor's information"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        user_form = DoctorUpdateForm(request.POST, instance=doctor.user)
        profile_form = DoctorProfileForm(request.POST, instance=doctor)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()
                    
                    messages.success(request, f"Doctor {doctor.user.get_full_name()} has been updated successfully.")
                    return redirect('admins:doctor_management')
            except Exception as e:
                messages.error(request, f"Error updating doctor: {str(e)}")
    else:
        user_form = DoctorUpdateForm(instance=doctor.user)
        profile_form = DoctorProfileForm(instance=doctor)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'doctor': doctor,
        'action': 'Edit',
    }
    return render(request, 'admins/doctor_form.html', context)

@login_required
def delete_doctor(request, doctor_id):
    """Delete a doctor from the system"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        try:
            # Check if doctor has any appointments
            appointment_count = Appointment.objects.filter(doctor=doctor).count()
            
            if appointment_count > 0:
                messages.warning(
                    request, 
                    f"Cannot delete Dr. {doctor.user.get_full_name()} because they have {appointment_count} appointment(s). "
                    "Please reassign or cancel their appointments first."
                )
            else:
                doctor_name = doctor.user.get_full_name()
                doctor.user.delete()  # This will cascade delete the doctor profile
                messages.success(request, f"Dr. {doctor_name} has been deleted successfully.")
                
        except Exception as e:
            messages.error(request, f"Error deleting doctor: {str(e)}")
    
    return redirect('admins:doctor_management')

# Department CRUD Operations
@login_required
def add_department(request):
    """Add a new department"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f"Department '{department.name}' has been added successfully.")
            return redirect('admins:hospital_management')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'action': 'Add',
        'title': 'Add Department',
    }
    return render(request, 'admins/department_form.html', context)

@login_required
def edit_department(request, department_id):
    """Edit an existing department"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{department.name}' has been updated successfully.")
            return redirect('admins:hospital_management')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
        'action': 'Edit',
        'title': 'Edit Department',
    }
    return render(request, 'admins/department_form.html', context)

@login_required
def delete_department(request, department_id):
    """Delete a department"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    department = get_object_or_404(Department, id=department_id)
    
    if request.method == 'POST':
        try:
            # Check if department has doctors or specializations
            doctor_count = Doctor.objects.filter(department=department).count()
            specialization_count = Specialization.objects.filter(department=department).count()
            
            if doctor_count > 0 or specialization_count > 0:
                messages.warning(
                    request,
                    f"Cannot delete department '{department.name}' because it has {doctor_count} doctor(s) "
                    f"and {specialization_count} specialization(s). Please reassign them first."
                )
            else:
                department_name = department.name
                department.delete()
                messages.success(request, f"Department '{department_name}' has been deleted successfully.")
                
        except Exception as e:
            messages.error(request, f"Error deleting department: {str(e)}")
    
    return redirect('admins:hospital_management')

# Specialization CRUD Operations
@login_required
def add_specialization(request):
    """Add a new specialization"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    if request.method == 'POST':
        form = SpecializationForm(request.POST)
        if form.is_valid():
            specialization = form.save()
            messages.success(request, f"Specialization '{specialization.name}' has been added successfully.")
            return redirect('admins:hospital_management')
    else:
        form = SpecializationForm()
    
    context = {
        'form': form,
        'action': 'Add',
        'title': 'Add Specialization',
    }
    return render(request, 'admins/specialization_form.html', context)

@login_required
def edit_specialization(request, specialization_id):
    """Edit an existing specialization"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    specialization = get_object_or_404(Specialization, id=specialization_id)
    
    if request.method == 'POST':
        form = SpecializationForm(request.POST, instance=specialization)
        if form.is_valid():
            form.save()
            messages.success(request, f"Specialization '{specialization.name}' has been updated successfully.")
            return redirect('admins:hospital_management')
    else:
        form = SpecializationForm(instance=specialization)
    
    context = {
        'form': form,
        'specialization': specialization,
        'action': 'Edit',
        'title': 'Edit Specialization',
    }
    return render(request, 'admins/specialization_form.html', context)

@login_required
def delete_specialization(request, specialization_id):
    """Delete a specialization"""
    if request.user.role != 'admin':
        return render(request, 'users/access_denied.html')
    
    specialization = get_object_or_404(Specialization, id=specialization_id)
    
    if request.method == 'POST':
        try:
            # Check if specialization has doctors
            doctor_count = Doctor.objects.filter(specialization=specialization).count()
            
            if doctor_count > 0:
                messages.warning(
                    request,
                    f"Cannot delete specialization '{specialization.name}' because it has {doctor_count} doctor(s). "
                    "Please reassign them first."
                )
            else:
                specialization_name = specialization.name
                specialization.delete()
                messages.success(request, f"Specialization '{specialization_name}' has been deleted successfully.")
                
        except Exception as e:
            messages.error(request, f"Error deleting specialization: {str(e)}")
    
    return redirect('admins:hospital_management')
