from django import forms
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking, Court, Advertisement


class BookingForm(forms.ModelForm):
    number_of_players = forms.IntegerField(min_value=1, max_value=12, required=True)
    
    class Meta:
        model = Booking
        fields = ('court', 'date', 'start_time', 'end_time', 'number_of_players')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        court = cleaned.get('court')
        date = cleaned.get('date')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        number_of_players = cleaned.get('number_of_players')
        
        errors = []
        
        # Check if basic times are provided
        if start_time and end_time:
            # Validate end time is after start time
            if start_time >= end_time:
                errors.append('End time must be after start time.')
            
            # Validate booking duration (30 mins to 4 hours)
            duration_hours = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).total_seconds() / 3600
            if duration_hours < 0.5:
                errors.append('Booking duration must be at least 30 minutes.')
            elif duration_hours > 4:
                errors.append('Booking duration cannot exceed 4 hours.')
        
        # Check court capacity
        if court and number_of_players:
            if number_of_players > court.capacity:
                errors.append(f'Court capacity is {court.capacity} players. You cannot book for {number_of_players} players.')
        
        # Check for booking conflicts (overlapping bookings on same court)
        if court and date and start_time and end_time:
            # Find all confirmed bookings on the same court and date
            conflicting_bookings = Booking.objects.filter(
                court=court,
                date=date,
                status='confirmed'
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            # Check if any booking overlaps with the requested time
            conflicts = []
            for booking in conflicting_bookings:
                # Check if there's time overlap
                if not (end_time <= booking.start_time or start_time >= booking.end_time):
                    conflicts.append(f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}")
            
            if conflicts:
                booked_times = ', '.join(conflicts)
                errors.append(f'Court is already booked for this date at: {booked_times}. Please choose a different time slot.')
        
        if errors:
            raise forms.ValidationError(errors)
        
        return cleaned

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ('brand_name', 'contact_person_name', 'email', 'mobile_no', 'promotion_type', 'advertise_duration', 'company_details')
        widgets = {
            'brand_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Brand Name'}),
            'contact_person_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Person Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your.email@example.com'}),
            'mobile_no': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mobile Number (10 digits)'}),
            'promotion_type': forms.Select(attrs={'class': 'form-input'}),
            'advertise_duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 1 month, 3 months, 6 months, 1 year'}),
            'company_details': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Describe your company, products/services, and why you want to sponsor...', 'rows': 5}),
        }
    
    def clean(self):
        cleaned = super().clean()
        mobile_no = cleaned.get('mobile_no')
        
        if mobile_no and not mobile_no.isdigit():
            raise forms.ValidationError('Mobile number should contain only digits.')
        
        if mobile_no and len(mobile_no) != 10:
            raise forms.ValidationError('Mobile number should be 10 digits long.')
        
        return cleaned