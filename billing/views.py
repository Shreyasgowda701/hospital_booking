from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
import json
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Service, Bill, BillItem, Payment, Insurance, BillingProfile
from appointments.models import Appointment
from doctors.models import Doctor

# Get the custom User model
User = get_user_model()


@login_required
def billing_dashboard(request):
    """Billing dashboard for different user roles"""
    user = request.user
    
    if user.role == 'admin':
        # Admin can see all billing data
        recent_bills = Bill.objects.select_related('patient').order_by('-created_at')[:10]
        total_revenue = Bill.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        pending_bills = Bill.objects.filter(status__in=['pending', 'overdue']).count()
        recent_payments = Payment.objects.select_related('bill__patient').order_by('-payment_date')[:10]
        
        context = {
            'recent_bills': recent_bills,
            'total_revenue': total_revenue,
            'pending_bills': pending_bills,
            'recent_payments': recent_payments,
            'user_type': 'admin'
        }
        
    elif user.role == 'doctor':
        # Doctors can see bills for their patients
        try:
            doctor_instance = user.doctor  # Get the Doctor instance associated with this User
            doctor_appointments = Appointment.objects.filter(doctor=doctor_instance)
            patient_ids = doctor_appointments.values_list('patient_id', flat=True).distinct()
            
            recent_bills = Bill.objects.filter(patient_id__in=patient_ids).select_related('patient').order_by('-created_at')[:10]
            total_revenue = Bill.objects.filter(patient_id__in=patient_ids, status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            pending_bills = Bill.objects.filter(patient_id__in=patient_ids, status__in=['pending', 'overdue']).count()
        except AttributeError:
            # Handle case where user doesn't have a doctor profile
            recent_bills = []
            total_revenue = 0
            pending_bills = 0
        
        context = {
            'recent_bills': recent_bills,
            'total_revenue': total_revenue,
            'pending_bills': pending_bills,
            'user_type': 'doctor'
        }
        
    else:  # Patient
        # Patients can only see their own bills
        user_bills = Bill.objects.filter(patient=user).order_by('-created_at')[:10]
        total_owed = Bill.objects.filter(patient=user).aggregate(Sum('balance_amount'))['balance_amount__sum'] or 0
        paid_bills = Bill.objects.filter(patient=user, status='paid').count()
        pending_bills = Bill.objects.filter(patient=user, status__in=['pending', 'overdue']).count()
        
        context = {
            'user_bills': user_bills,
            'total_owed': total_owed,
            'paid_bills': paid_bills,
            'pending_bills': pending_bills,
            'user_type': 'patient'
        }
    
    return render(request, 'billing/dashboard.html', context)


@login_required
def bill_list(request):
    """List all bills based on user role"""
    user = request.user
    
    if user.role == 'admin':
        bills = Bill.objects.select_related('patient').order_by('-created_at')
    elif user.role == 'doctor':
        # Get patients from doctor's appointments
        try:
            doctor_instance = user.doctor
            doctor_appointments = Appointment.objects.filter(doctor=doctor_instance)
            patient_ids = doctor_appointments.values_list('patient_id', flat=True).distinct()
            bills = Bill.objects.filter(patient_id__in=patient_ids).select_related('patient').order_by('-created_at')
        except AttributeError:
            bills = Bill.objects.none()
    else:  # Patient
        bills = Bill.objects.filter(patient=user).order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        bills = bills.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        bills = bills.filter(
            Q(bill_number__icontains=search_query) |
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bills, 20)
    page_number = request.GET.get('page')
    page_bills = paginator.get_page(page_number)
    
    context = {
        'bills': page_bills,
        'status_filter': status_filter,
        'search_query': search_query,
        'user_type': user.role
    }
    
    return render(request, 'billing/bill_list.html', context)


@login_required
def bill_detail(request, bill_id):
    """View detailed bill information"""
    bill = get_object_or_404(Bill, id=bill_id)
    user = request.user
    
    # Check permissions
    if user.role == 'patient' and bill.patient != user:
        messages.error(request, "You don't have permission to view this bill.")
        return redirect('billing:dashboard')
    elif user.role == 'doctor':
        # Check if this patient is under this doctor's care
        try:
            doctor_instance = user.doctor
            doctor_patients = Appointment.objects.filter(doctor=doctor_instance).values_list('patient_id', flat=True).distinct()
            if bill.patient_id not in doctor_patients:
                messages.error(request, "You don't have permission to view this bill.")
                return redirect('billing:dashboard')
        except AttributeError:
            messages.error(request, "You don't have permission to view this bill.")
            return redirect('billing:dashboard')
    
    bill_items = bill.items.select_related('service').all()
    payments = bill.payments.all().order_by('-payment_date')
    
    context = {
        'bill': bill,
        'bill_items': bill_items,
        'payments': payments,
        'user_type': user.role
    }
    
    return render(request, 'billing/bill_detail.html', context)


@login_required
def create_bill(request):
    """Create a new bill (Admin/Doctor only)"""
    if request.user.role not in ['admin', 'doctor']:
        messages.error(request, "You don't have permission to create bills.")
        return redirect('billing:dashboard')
    
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.POST.get('patient_id')
            appointment_id = request.POST.get('appointment_id')
            due_date = request.POST.get('due_date')
            tax_rate = Decimal(request.POST.get('tax_rate', '0'))
            discount_amount = Decimal(request.POST.get('discount_amount', '0'))
            notes = request.POST.get('notes', '')
            
            # Get services data (JSON from form)
            services_data = json.loads(request.POST.get('services_data', '[]'))
            
            if not services_data:
                messages.error(request, "Please add at least one service to the bill.")
                return redirect('billing:create_bill')
            
            # Create bill
            # Parse due date and make it timezone aware
            due_date_obj = datetime.strptime(due_date, '%Y-%m-%d')
            due_date_obj = timezone.make_aware(due_date_obj) if timezone.is_naive(due_date_obj) else due_date_obj
            
            bill = Bill.objects.create(
                patient_id=patient_id,
                appointment_id=appointment_id if appointment_id else None,
                due_date=due_date_obj,
                tax_rate=tax_rate,
                discount_amount=discount_amount,
                notes=notes,
                created_by=request.user,
                status='pending'
            )
            
            # Create bill items
            for service_data in services_data:
                service = Service.objects.get(id=service_data['service_id'])
                BillItem.objects.create(
                    bill=bill,
                    service=service,
                    quantity=int(service_data['quantity']),
                    unit_price=service.price,
                    description=service_data.get('description', '')
                )
            
            messages.success(request, f"Bill {bill.bill_number} created successfully!")
            return redirect('billing:bill_detail', bill_id=bill.id)
            
        except Exception as e:
            messages.error(request, f"Error creating bill: {str(e)}")
            return redirect('billing:create_bill')
    
    # GET request - show form
    services = Service.objects.filter(is_active=True).order_by('category', 'name')
    
    # Get patients based on user role
    if request.user.role == 'admin':
        patients = User.objects.filter(role='patient')
    else:  # Doctor
        # Get patients from doctor's appointments
        try:
            doctor_instance = request.user.doctor
            patient_ids = Appointment.objects.filter(doctor=doctor_instance).values_list('patient_id', flat=True).distinct()
            patients = User.objects.filter(id__in=patient_ids)
        except AttributeError:
            # Handle case where user doesn't have a doctor profile
            patients = User.objects.none()
    
    context = {
        'services': services,
        'patients': patients,
        'default_due_date': (timezone.now() + timedelta(days=30)).date(),
    }
    
    return render(request, 'billing/create_bill.html', context)


@login_required
@require_POST
def record_payment(request, bill_id):
    """Record a payment for a bill"""
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check permissions
    if request.user.role not in ['admin', 'doctor']:
        messages.error(request, "You don't have permission to record payments.")
        return redirect('billing:bill_detail', bill_id=bill_id)
    
    try:
        amount = Decimal(request.POST.get('amount'))
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')
        
        # Validate amount
        if amount <= 0:
            messages.error(request, "Payment amount must be greater than zero.")
            return redirect('billing:bill_detail', bill_id=bill_id)
        
        if amount > bill.balance_amount:
            messages.error(request, "Payment amount cannot exceed the balance amount.")
            return redirect('billing:bill_detail', bill_id=bill_id)
        
        # Create payment record
        payment = Payment.objects.create(
            bill=bill,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            reference_number=reference_number,
            notes=notes,
            status='completed',
            processed_by=request.user
        )
        
        messages.success(request, f"Payment of ${amount} recorded successfully!")
        
    except Exception as e:
        messages.error(request, f"Error recording payment: {str(e)}")
    
    return redirect('billing:bill_detail', bill_id=bill_id)


@login_required
def service_list(request):
    """List all medical services (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to view services.")
        return redirect('billing:dashboard')
    
    services = Service.objects.all().order_by('category', 'name')
    
    # Filter by category if requested
    category_filter = request.GET.get('category')
    if category_filter:
        services = services.filter(category=category_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_services = paginator.get_page(page_number)
    
    context = {
        'services': page_services,
        'category_filter': category_filter,
        'search_query': search_query,
        'service_categories': Service.SERVICE_CATEGORIES
    }
    
    return render(request, 'billing/service_list.html', context)


@login_required
def payment_history(request):
    """View payment history based on user role"""
    user = request.user
    
    if user.role == 'admin':
        payments = Payment.objects.select_related('bill__patient').order_by('-payment_date')
    elif user.role == 'doctor':
        # Get payments for doctor's patients
        try:
            doctor_instance = user.doctor
            doctor_appointments = Appointment.objects.filter(doctor=doctor_instance)
            patient_ids = doctor_appointments.values_list('patient_id', flat=True).distinct()
        except AttributeError:
            patient_ids = []
        payments = Payment.objects.filter(bill__patient_id__in=patient_ids).select_related('bill__patient').order_by('-payment_date')
    else:  # Patient
        payments = Payment.objects.filter(bill__patient=user).order_by('-payment_date')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_payments = paginator.get_page(page_number)
    
    context = {
        'payments': page_payments,
        'status_filter': status_filter,
        'user_type': user.role
    }
    
    return render(request, 'billing/payment_history.html', context)


@login_required
def get_service_price(request, service_id):
    """AJAX endpoint to get service price"""
    try:
        service = Service.objects.get(id=service_id, is_active=True)
        return JsonResponse({
            'success': True,
            'price': float(service.price),
            'name': service.name,
            'description': service.description
        })
    except Service.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Service not found'})


@login_required
def insurance_list(request):
    """List insurance policies based on user role"""
    user = request.user
    
    if user.role == 'patient':
        insurances = Insurance.objects.filter(patient=user).order_by('-created_at')
    elif user.role == 'admin':
        insurances = Insurance.objects.select_related('patient').order_by('-created_at')
    else:  # Doctor
        # Get insurance for doctor's patients
        try:
            doctor_instance = user.doctor
            doctor_appointments = Appointment.objects.filter(doctor=doctor_instance)
            patient_ids = doctor_appointments.values_list('patient_id', flat=True).distinct()
            insurances = Insurance.objects.filter(patient_id__in=patient_ids).select_related('patient').order_by('-created_at')
        except AttributeError:
            insurances = Insurance.objects.none()
    
    # Pagination
    paginator = Paginator(insurances, 20)
    page_number = request.GET.get('page')
    page_insurances = paginator.get_page(page_number)
    
    context = {
        'insurances': page_insurances,
        'user_type': user.role
    }
    
    return render(request, 'billing/insurance_list.html', context)
