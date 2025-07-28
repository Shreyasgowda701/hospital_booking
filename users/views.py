from django.shortcuts import render, redirect, redirect
from django.contrib.auth import login
from .forms import PatientSignUpForm, DoctorSignUpForm, AdminSignUpForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Custom Login View
class CustomLoginView(LoginView):
    template_name = "users/login.html"
    
    def get_success_url(self):
        """Redirect user to appropriate dashboard based on their role"""
        user = self.request.user
        if user.role == 'patient':
            return reverse('patient_dashboard')
        elif user.role == 'doctor':
            return reverse('doctor_dashboard')
        elif user.role == 'admin':
            return reverse('admin_dashboard')
        else:
            # Fallback to home if role is not recognized
            return reverse('home')

# Custom Logout View for convenience
class CustomLogoutView(LogoutView):
    next_page = 'home'  # Redirect to home after logout
    http_method_names = ['get', 'post']  # Allow both GET and POST for compatibility

def home(request):
    return render(request, "users/home.html")

def coming_soon(request):
    """Generic coming soon page for unimplemented features"""
    feature_name = request.GET.get('feature', 'New Feature')
    description = request.GET.get('description', '')
    progress = request.GET.get('progress', '65')
    eta = request.GET.get('eta', '')
    
    # Default upcoming features based on feature type
    upcoming_features = []
    if 'reschedule' in feature_name.lower():
        upcoming_features = [
            'Reschedule appointments with available time slots',
            'Automatic notifications to doctors and patients',
            'Conflict detection and resolution',
            'Rescheduling history tracking'
        ]
    elif 'cancel' in feature_name.lower():
        upcoming_features = [
            'Cancellation with reason selection',
            'Automatic refund processing',
            'Email notifications to all parties',
            'Cancellation analytics for admins'
        ]
    elif 'review' in feature_name.lower():
        upcoming_features = [
            'Doctor rating and review system',
            'Review moderation tools',
            'Average rating calculations',
            'Review response functionality'
        ]
    elif 'medical' in feature_name.lower() or 'history' in feature_name.lower():
        upcoming_features = [
            'Complete medical history tracking',
            'PDF export functionality',
            'Medical document uploads',
            'Doctor notes and prescriptions'
        ]
    elif 'report' in feature_name.lower():
        upcoming_features = [
            'Advanced analytics dashboard',
            'Custom report generation',
            'Export to PDF/Excel',
            'Automated report scheduling'
        ]
    else:
        upcoming_features = [
            'User-friendly interface design',
            'Real-time data synchronization',
            'Mobile-responsive layout',
            'Advanced filtering and search'
        ]
    
    context = {
        'feature_name': feature_name,
        'description': description,
        'progress': progress,
        'eta': eta,
        'upcoming_features': upcoming_features,
    }
    return render(request, "coming_soon.html", context)
# Patient dashboard
@login_required
def patient_dashboard(request):
    if request.user.role != "patient":
        return render(request, "users/access_denied.html")
    return render(request, "users/patient_dashboard.html")

# Doctor dashboard
@login_required
def doctor_dashboard(request):
    if request.user.role != "doctor":
        return render(request, "users/access_denied.html")
    return render(request, "users/doctor_dashboard.html")

# Admin dashboard
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return render(request, "users/access_denied.html")
    # Redirect to the enhanced admin dashboard
    return redirect('admins:dashboard')

# Patient signup view
def patient_signup(request):
    if request.method == "POST":
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("patient_dashboard")
    else:
        form = PatientSignUpForm()
    return render(request, "users/signup_patient.html", {"form": form})

# Doctor signup view
def doctor_signup(request):
    if request.method == "POST":
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("doctor_dashboard")
    else:
        form = DoctorSignUpForm()
    return render(request, "users/signup_doctor.html", {"form": form})

# Admin signup view
def admin_signup(request):
    if request.method == "POST":
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("admin_dashboard")
    else:
        form = AdminSignUpForm()
    return render(request, "users/signup_admin.html", {"form": form})