from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.email}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        user = self.request.user
        # If user is admin/staff, redirect to admin panel
        if user.is_staff or user.is_superuser:
            return '/admin/'
        # Otherwise redirect to home page
        return '/'


def logout_view(request):
    messages.success(request, 'You have been logged out successfully.')
    logout(request)
    return redirect('login')


@login_required
def home_view(request):
    return render(request, 'home.html')


@login_required
def profile_view(request):
    # Get user's bookings with proper calculations
    bookings = request.user.bookings.all().order_by('-date', '-start_time')
    
    # Calculate total price for each booking if not already set
    for booking in bookings:
        if not booking.total_price or booking.total_price == 0:
            booking.calculate_price()
            booking.save()
    
    context = {
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'confirmed_bookings': bookings.filter(status='confirmed').count(),
    }
    return render(request, 'profile.html', context)
