from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

# Get the custom User model
User = get_user_model()

# Create your models here.

class Service(models.Model):
    """Medical services and their pricing"""
    SERVICE_CATEGORIES = [
        ('consultation', 'Consultation'),
        ('diagnostic', 'Diagnostic'),
        ('treatment', 'Treatment'),
        ('surgery', 'Surgery'),
        ('emergency', 'Emergency'),
        ('pharmacy', 'Pharmacy'),
        ('room', 'Room Charges'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES, default='consultation')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class Bill(models.Model):
    """Main billing record for patients"""
    BILL_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Payment'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Bill details
    issue_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=BILL_STATUS, default='draft')
    
    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional info
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        
        # Calculate totals
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.balance_amount = self.total_amount - self.paid_amount
        
        # Update status based on payment
        if self.balance_amount <= 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.due_date and timezone.now() > self.due_date and self.balance_amount > 0:
            self.status = 'overdue'
        elif not self.due_date and self.status == 'draft':
            # Set due date if not provided (30 days from issue date)
            if self.issue_date:
                self.due_date = self.issue_date + timedelta(days=30)
            else:
                self.due_date = timezone.now() + timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def generate_bill_number(self):
        """Generate unique bill number"""
        today = timezone.now().date()
        prefix = f"HMS{today.strftime('%Y%m%d')}"
        
        # Get last bill number for today
        last_bill = Bill.objects.filter(
            bill_number__startswith=prefix
        ).order_by('-bill_number').first()
        
        if last_bill:
            last_number = int(last_bill.bill_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def __str__(self):
        return f"Bill {self.bill_number} - {self.patient.get_full_name()}"


class BillItem(models.Model):
    """Individual items/services in a bill"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    description = models.TextField(blank=True)  # Additional notes for this item
    date_provided = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['date_provided']
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update bill subtotal
        self.bill.subtotal = sum(item.total_price for item in self.bill.items.all())
        self.bill.save()
    
    def __str__(self):
        return f"{self.service.name} x {self.quantity}"


class Payment(models.Model):
    """Payment records for bills"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
        ('other', 'Other'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    payment_id = models.CharField(max_length=50, unique=True, editable=False)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Payment details
    transaction_id = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Processing info
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = self.generate_payment_id()
        
        super().save(*args, **kwargs)
        
        # Update bill paid amount
        if self.status == 'completed':
            self.bill.paid_amount = sum(
                payment.amount for payment in self.bill.payments.filter(status='completed')
            )
            self.bill.save()
    
    def generate_payment_id(self):
        """Generate unique payment ID"""
        return f"PAY{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
    
    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}"


class Insurance(models.Model):
    """Insurance information for patients"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_policies')
    
    provider_name = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    
    # Coverage details
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 0-100%
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Validity
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    # Contact info
    provider_phone = models.CharField(max_length=20, blank=True)
    provider_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def is_valid(self):
        """Check if insurance is currently valid"""
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
    
    def __str__(self):
        return f"{self.provider_name} - {self.policy_number}"


class BillingProfile(models.Model):
    """Billing preferences and information for patients"""
    patient = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_profile')
    
    # Billing address
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_zip = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100, default='United States')
    
    # Preferences
    preferred_payment_method = models.CharField(max_length=20, choices=Payment.PAYMENT_METHODS, default='card')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Emergency contact for billing
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Billing Profile - {self.patient.get_full_name()}"
