from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('admin-panel/', include('admins.urls')),
    path('billing/', include('billing.urls')),
]