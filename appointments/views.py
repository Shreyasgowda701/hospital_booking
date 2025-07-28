from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from .models import Appointment, PatientHistory
from .forms import DoctorSearchForm, AppointmentBookingForm
from doctors.models import Doctor, Department, Specialization, DoctorAvailability
from users.models import User

def doctor_search(request):
    """Search and filter doctors"""
    form = DoctorSearchForm(request.GET or None)
    doctors = Doctor.objects.filter(is_available=True).select_related('user', 'specialization', 'department')
    
    if form.is_valid():
        department = form.cleaned_data.get('department')
        specialization = form.cleaned_data.get('specialization')
        availability_date = form.cleaned_data.get('availability_date')
        
        if department:
            doctors = doctors.filter(department=department)
        
        if specialization:
            doctors = doctors.filter(specialization=specialization)
        
        if availability_date:
            # Filter doctors who have availability on the selected date
            weekday = availability_date.weekday()
            doctors = doctors.filter(
                availability_slots__day_of_week=weekday,
                availability_slots__is_available=True
            ).distinct()
    
    # Add average rating to each doctor
    for doctor in doctors:
        doctor.avg_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'form': form,
        'doctors': doctors,
        'departments': Department.objects.all(),
        'specializations': Specialization.objects.all(),
    }
    return render(request, 'appointments/doctor_search.html', context)

def doctor_detail(request, doctor_id):
    """Doctor detail page with availability and booking"""
    doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)
    
    # Get doctor's reviews
    reviews = doctor.reviews.select_related('patient').order_by('-created_at')[:5]
    avg_rating = doctor.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get doctor's availability for next 7 days
    availability_slots = []
    for i in range(7):
        date = timezone.now().date() + timedelta(days=i)
        weekday = date.weekday()
        
        slots = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=weekday,
            is_available=True
        )
        
        if slots:
            # Get booked appointments for this date
            booked_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date__date=date,
                status__in=['pending', 'confirmed']
            ).values_list('appointment_date__time', flat=True)
            
            available_times = []
            for slot in slots:
                # Generate 30-minute time slots
                current_time = datetime.combine(date, slot.start_time)
                end_time = datetime.combine(date, slot.end_time)
                
                while current_time < end_time:
                    if current_time.time() not in booked_appointments:
                        available_times.append(current_time.time())
                    current_time += timedelta(minutes=30)
            
            if available_times:
                availability_slots.append({
                    'date': date,
                    'times': available_times
                })
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': doctor.reviews.count(),
        'availability_slots': availability_slots,
    }
    return render(request, 'appointments/doctor_detail.html', context)

@login_required
def book_appointment(request, doctor_id):
    """Book an appointment with a doctor"""
    if request.user.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('appointments:doctor_search')
    
    doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, doctor=doctor)
        
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            
            # Check if the time slot is still available
            appointment_datetime = appointment.appointment_date
            existing_appointment = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_datetime,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_appointment:
                messages.error(request, 'This time slot is no longer available. Please choose another time.')
            else:
                appointment.save()
                messages.success(request, f'Appointment booked successfully with Dr. {doctor.get_full_name()}!')
                return redirect('appointments:patient_appointments')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AppointmentBookingForm(doctor=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def patient_appointments(request):
    """Patient's appointment management page"""
    if request.user.role != 'patient':
        return redirect('access_denied')
    
    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=timezone.now(),
        status__in=['pending', 'confirmed']
    ).select_related('doctor__user', 'doctor__specialization').order_by('appointment_date')
    
    past_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__lt=timezone.now()
    ).select_related('doctor__user', 'doctor__specialization').order_by('-appointment_date')[:10]
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'appointments/patient_appointments.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=request.user,
        status__in=['pending', 'confirmed']
    )
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('patient_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointments/cancel_appointment.html', context)

@login_required
def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(
        Appointment, 
        id=appointment_id, 
        patient=request.user,
        status__in=['pending', 'confirmed']
    )
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, doctor=appointment.doctor)
        if form.is_valid():
            new_datetime = datetime.combine(
                form.cleaned_data['appointment_date'],
                form.cleaned_data['appointment_time']
            )
            new_datetime = timezone.make_aware(new_datetime)
            
            # Check if the new time slot is available
            existing_appointment = Appointment.objects.filter(
                doctor=appointment.doctor,
                appointment_date=new_datetime,
                status__in=['pending', 'confirmed']
            ).exclude(id=appointment.id).exists()
            
            if existing_appointment:
                messages.error(request, 'This time slot is not available. Please choose another time.')
            else:
                appointment.appointment_date = new_datetime
                appointment.appointment_type = form.cleaned_data['appointment_type']
                appointment.reason_for_visit = form.cleaned_data['reason_for_visit']
                appointment.status = 'rescheduled'
                appointment.save()
                messages.success(request, 'Appointment rescheduled successfully!')
                return redirect('patient_appointments')
    else:
        initial_data = {
            'appointment_date': appointment.appointment_date.date(),
            'appointment_time': appointment.appointment_date.time(),
            'appointment_type': appointment.appointment_type,
            'reason_for_visit': appointment.reason_for_visit,
        }
        form = AppointmentBookingForm(initial=initial_data, doctor=appointment.doctor)
    
    context = {
        'form': form,
        'appointment': appointment,
        'doctor': appointment.doctor,
    }
    return render(request, 'appointments/reschedule_appointment.html', context)

@login_required
def patient_medical_history(request):
    """Patient's medical history page"""
    if request.user.role != 'patient':
        return redirect('access_denied')
    
    medical_history = PatientHistory.objects.filter(
        patient=request.user
    ).select_related('doctor__user', 'appointment').order_by('-visit_date')
    
    context = {'medical_history': medical_history}
    return render(request, 'appointments/patient_medical_history.html', context)

def get_doctor_availability(request, doctor_id):
    """AJAX endpoint to get doctor availability for a specific date"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    weekday = date.weekday()
    
    # Get availability slots for this day
    slots = DoctorAvailability.objects.filter(
        doctor=doctor,
        day_of_week=weekday,
        is_available=True
    )
    
    if not slots:
        return JsonResponse({'available_times': []})
    
    # Get booked appointments
    booked_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_date__time', flat=True)
    
    available_times = []
    for slot in slots:
        current_time = datetime.combine(date, slot.start_time)
        end_time = datetime.combine(date, slot.end_time)
        
        while current_time < end_time:
            if current_time.time() not in booked_appointments:
                available_times.append(current_time.time().strftime('%H:%M'))
            current_time += timedelta(minutes=30)
    
    return JsonResponse({'available_times': available_times})


# ========================
# DOCTOR PORTAL VIEWS
# ========================

@login_required
def doctor_appointments(request):
    """Doctor's appointment management page"""
    if request.user.role != 'doctor':
        return redirect('access_denied')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
    
    # Get today's appointments
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=today
    ).order_by('appointment_date')
    
    # Get upcoming appointments (next 7 days)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date__gt=today,
        appointment_date__date__lte=today + timedelta(days=7),
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')
    
    # Get recent past appointments
    past_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date__lt=today
    ).order_by('-appointment_date')[:10]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'today': today,
    }
    return render(request, 'appointments/doctor_appointments.html', context)

@login_required
def manage_availability(request):
    """Doctor's availability management page"""
    if request.user.role != 'doctor':
        return redirect('access_denied')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
    
    # Get current availability slots
    availability_slots = DoctorAvailability.objects.filter(doctor=doctor).order_by('day_of_week', 'start_time')
    
    if request.method == 'POST':
        # Handle availability update
        action = request.POST.get('action')
        
        if action == 'add_slot':
            day_of_week = request.POST.get('day_of_week')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            
            if day_of_week and start_time and end_time:
                # Check for overlapping slots
                overlapping = DoctorAvailability.objects.filter(
                    doctor=doctor,
                    day_of_week=day_of_week,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                ).exists()
                
                if overlapping:
                    messages.error(request, 'This time slot overlaps with existing availability.')
                else:
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        day_of_week=int(day_of_week),
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    messages.success(request, 'Availability slot added successfully.')
            else:
                messages.error(request, 'Please fill all required fields.')
        
        elif action == 'delete_slot':
            slot_id = request.POST.get('slot_id')
            if slot_id:
                try:
                    slot = DoctorAvailability.objects.get(id=slot_id, doctor=doctor)
                    slot.delete()
                    messages.success(request, 'Availability slot deleted successfully.')
                except DoctorAvailability.DoesNotExist:
                    messages.error(request, 'Availability slot not found.')
        
        elif action == 'toggle_slot':
            slot_id = request.POST.get('slot_id')
            if slot_id:
                try:
                    slot = DoctorAvailability.objects.get(id=slot_id, doctor=doctor)
                    slot.is_available = not slot.is_available
                    slot.save()
                    status = 'enabled' if slot.is_available else 'disabled'
                    messages.success(request, f'Availability slot {status} successfully.')
                except DoctorAvailability.DoesNotExist:
                    messages.error(request, 'Availability slot not found.')
        
        return redirect('appointments:manage_availability')
    
    # Days of week for the form
    days_of_week = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    context = {
        'doctor': doctor,
        'availability_slots': availability_slots,
        'days_of_week': days_of_week,
    }
    return render(request, 'appointments/manage_availability.html', context)

@login_required
def update_appointment_status(request, appointment_id):
    """Update appointment status (doctor only)"""
    if request.user.role != 'doctor':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        
        if request.method == 'POST':
            new_status = request.POST.get('status')
            doctor_notes = request.POST.get('doctor_notes', '')
            
            if new_status in ['confirmed', 'completed', 'cancelled']:
                appointment.status = new_status
                if doctor_notes:
                    appointment.doctor_notes = doctor_notes
                appointment.save()
                
                return JsonResponse({'success': True, 'message': f'Appointment {new_status} successfully.'})
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
        
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor profile not found'}, status=404)
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def patient_records(request):
    """Doctor's patient records page"""
    if request.user.role != 'doctor':
        return redirect('access_denied')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
    
    # Get all patients who have had appointments with this doctor
    patient_ids = Appointment.objects.filter(doctor=doctor).values_list('patient', flat=True).distinct()
    patients = User.objects.filter(id__in=patient_ids, role='patient')
    
    # Get search query
    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Add appointment counts for each patient
    for patient in patients:
        patient.appointment_count = Appointment.objects.filter(doctor=doctor, patient=patient).count()
        patient.last_appointment = Appointment.objects.filter(
            doctor=doctor, 
            patient=patient
        ).order_by('-appointment_date').first()
    
    context = {
        'doctor': doctor,
        'patients': patients,
        'search_query': search_query,
    }
    return render(request, 'appointments/patient_records.html', context)

@login_required
def patient_record_detail(request, patient_id):
    """Detailed view of a patient's medical records (doctor only)"""
    if request.user.role != 'doctor':
        return redirect('access_denied')
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        patient = get_object_or_404(User, id=patient_id, role='patient')
        
        # Verify doctor has treated this patient
        if not Appointment.objects.filter(doctor=doctor, patient=patient).exists():
            messages.error(request, 'You do not have permission to view this patient\'s records.')
            return redirect('patient_records')
        
        # Get all appointments between this doctor and patient
        appointments = Appointment.objects.filter(
            doctor=doctor,
            patient=patient
        ).order_by('-appointment_date')
        
        # Get medical history records
        medical_history = PatientHistory.objects.filter(
            patient=patient,
            doctor=doctor
        ).order_by('-visit_date')
        
        context = {
            'doctor': doctor,
            'patient': patient,
            'appointments': appointments,
            'medical_history': medical_history,
        }
        return render(request, 'appointments/patient_record_detail.html', context)
        
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
