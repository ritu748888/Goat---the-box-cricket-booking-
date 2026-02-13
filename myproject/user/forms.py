from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone')
        field_classes = {'email': forms.EmailField}

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
