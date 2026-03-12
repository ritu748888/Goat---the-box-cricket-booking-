from django import forms
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking, Court, Advertisement, Tournament, Payment


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
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Payment Method',
        required=True
    )
    payment_proof = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input'}),
        label='Payment Proof (optional)'
    )

    class Meta:
        model = Advertisement
        fields = ('title', 'image', 'link', 'position', 'start_date', 'end_date', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Advertisement Title'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://example.com'}),
            'position': forms.Select(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError('End date must be on or after the start date.')

        return cleaned


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ('name', 'description', 'poster', 'venue', 'start_date', 'end_date', 'start_time', 'max_teams', 'entry_fee', 'contact_person', 'contact_email', 'contact_phone', 'rules', 'prize_pool')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tournament Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Tournament Description', 'rows': 4}),
            'poster': forms.FileInput(attrs={'class': 'form-input'}),
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


class TournamentRegistrationForm(forms.Form):
    team_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Team Name'}))
    captain_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Captain Name'}))
    contact_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Number'}))
    player_list = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Add one player per line', 'rows': 5}))
    payment_method = forms.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES, widget=forms.Select(attrs={'class': 'form-input'}))
    payment_proof = forms.FileField(required=True)

    def clean_contact_number(self):
        number = self.cleaned_data.get('contact_number', '')
        if not number.isdigit():
            raise forms.ValidationError('Contact number should contain only digits.')
        if not 10 <= len(number) <= 15:
            raise forms.ValidationError('Contact number should be between 10 and 15 digits.')
        return number
