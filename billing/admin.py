from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Service, Bill, BillItem, Payment, Insurance, BillingProfile

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'is_active')
        }),
    )


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 0
    readonly_fields = ['total_price']
    fields = ['service', 'quantity', 'unit_price', 'total_price', 'description', 'date_provided']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_id', 'created_at']
    fields = ['amount', 'payment_method', 'status', 'transaction_id', 'payment_date']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'patient_name', 'status', 'total_amount', 'balance_amount', 'due_date', 'created_at']
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['bill_number', 'patient__first_name', 'patient__last_name', 'patient__email']
    readonly_fields = ['bill_number', 'subtotal', 'tax_amount', 'total_amount', 'balance_amount', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    inlines = [BillItemInline, PaymentInline]
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_number', 'patient', 'appointment', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount', 'balance_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'appointment')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'bill_number', 'patient_name', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['payment_id', 'transaction_id', 'bill__bill_number', 'bill__patient__first_name', 'bill__patient__last_name']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'bill', 'amount', 'payment_method', 'payment_date', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'reference_number', 'notes')
        }),
        ('Processing Information', {
            'fields': ('processed_by', 'created_at', 'updated_at')
        }),
    )
    
    def bill_number(self, obj):
        return obj.bill.bill_number
    bill_number.short_description = 'Bill Number'
    bill_number.admin_order_field = 'bill__bill_number'
    
    def patient_name(self, obj):
        return obj.bill.patient.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'bill__patient__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill__patient', 'processed_by')


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'provider_name', 'policy_number', 'coverage_percentage', 'is_valid_display', 'end_date']
    list_filter = ['is_active', 'provider_name', 'start_date', 'end_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'provider_name', 'policy_number']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Insurance Provider', {
            'fields': ('provider_name', 'policy_number', 'group_number')
        }),
        ('Coverage Details', {
            'fields': ('coverage_percentage', 'deductible_amount', 'annual_limit')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('provider_phone', 'provider_email')
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__first_name'
    
    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'billing_city', 'billing_state', 'preferred_payment_method', 'email_notifications']
    list_filter = ['preferred_payment_method', 'email_notifications', 'sms_notifications', 'billing_state']
    search_fields = ['patient__first_name', 'patient__last_name', 'billing_city', 'billing_state']
    ordering = ['patient__first_name', 'patient__last_name']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state', 'billing_zip', 'billing_country')
        }),
        ('Preferences', {
            'fields': ('preferred_payment_method', 'email_notifications', 'sms_notifications')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name(self, obj):
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient')
