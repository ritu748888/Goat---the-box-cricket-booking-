from django.urls import path
from .views import signup_view, CustomLoginView, AdminLoginView, logout_view, home_view, profile_view

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]