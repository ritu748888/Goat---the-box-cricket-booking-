from django import forms
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking, Court, Advertisement, Tournament, TournamentSponsor


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


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ('name', 'description', 'venue', 'start_date', 'end_date', 'start_time', 'max_teams', 'entry_fee', 'contact_person', 'contact_email', 'contact_phone', 'rules', 'prize_pool')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tournament Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Tournament Description', 'rows': 4}),
            'venue': forms.Select(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'max_teams': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Maximum Teams'}),
            'entry_fee': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Entry Fee (₹)', 'step': '0.01'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Person Name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contact@example.com'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'rules': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Tournament Rules and Guidelines', 'rows': 4}),
            'prize_pool': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 1st: ₹50,000 | 2nd: ₹30,000 | 3rd: ₹20,000'}),
        }
    
    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')
        start_time = cleaned.get('start_time')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('End date must be after or equal to start date.')
        
        return cleaned


class TournamentSponsorForm(forms.ModelForm):
    class Meta:
        model = TournamentSponsor
        fields = ('sponsor_name', 'contact_person', 'email', 'phone', 'sponsorship_amount', 'sponsorship_type', 'company_details')
        widgets = {
            'sponsor_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company/Brand Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Person Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'sponsorship_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Sponsorship Amount (₹)', 'step': '0.01'}),
            'sponsorship_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Title Sponsor, Gold Partner, Silver Partner'}),
            'company_details': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Tell us about your company and why you want to sponsor this tournament...', 'rows': 5}),
        }
    
    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get('phone')
        sponsorship_amount = cleaned.get('sponsorship_amount')
        
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number should contain only digits.')
        
        if phone and len(phone) < 10:
            raise forms.ValidationError('Phone number should be at least 10 digits.')
        
        if sponsorship_amount and sponsorship_amount <= 0:
            raise forms.ValidationError('Sponsorship amount must be greater than 0.')
        
        return cleaned