from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('', views.billing_dashboard, name='dashboard'),
    
    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('bills/create/', views.create_bill, name='create_bill'),
    
    # Payments
    path('bills/<int:bill_id>/payment/', views.record_payment, name='record_payment'),
    path('payments/', views.payment_history, name='payment_history'),
    
    # Services
    path('services/', views.service_list, name='service_list'),
    path('api/service/<int:service_id>/price/', views.get_service_price, name='get_service_price'),
    
    # Insurance
    path('insurance/', views.insurance_list, name='insurance_list'),
]
