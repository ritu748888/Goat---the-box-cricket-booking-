from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Venue(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    rating = models.FloatField(default=4.5, validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def average_rating(self):
        ratings = self.reviews.all()
        if ratings:
            return sum([r.rating for r in ratings]) / len(ratings)
        return self.rating


class Court(models.Model):
    venue = models.ForeignKey(Venue, related_name='courts', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=8)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.venue.name} - {self.name}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings', on_delete=models.CASCADE)
    court = models.ForeignKey(Court, related_name='bookings', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    number_of_players = models.PositiveIntegerField(default=8)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # new bookings start out pending so that an administrator can review them
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'start_time']
        # allow only one booking with same status at given time; pending and confirmed
        # will no longer conflict with each other
        unique_together = ('court', 'date', 'start_time', 'status')

    def __str__(self):
        return f"{self.user} - {self.court} on {self.date} {self.start_time}-{self.end_time}"

    def calculate_price(self):
        from datetime import datetime
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        hours = (end - start).total_seconds() / 3600
        self.total_price = float(self.court.price_per_hour) * hours
        return self.total_price


class Review(models.Model):
    venue = models.ForeignKey(Venue, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('venue', 'user')

    def __str__(self):
        return f"{self.user} - {self.venue} ({self.rating}/5)"


class Advertisement(models.Model):
    PROMOTION_CHOICES = (
        ('ground', 'Ground Sponsorship'),
        ('tournament', 'Tournament Sponsorship'),
        ('both', 'Both Ground & Tournament'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
    )
    
    brand_name = models.CharField(max_length=100)
    contact_person_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_no = models.CharField(max_length=15)
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_CHOICES)
    company_details = models.TextField()
    advertise_duration = models.CharField(max_length=100, help_text="e.g., 1 month, 3 months, 6 months, 1 year")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.brand_name} - {self.promotion_type} ({self.status})"


class Tournament(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=150)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    venue = models.ForeignKey(Venue, related_name='tournaments', on_delete=models.CASCADE)
    max_teams = models.PositiveIntegerField(default=8)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    contact_person = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    rules = models.TextField(blank=True)
    prize_pool = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.name} - {self.start_date}"
    
    def is_upcoming(self):
        from datetime import date
        return self.start_date >= date.today()


class TournamentSponsor(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
    )
    
    tournament = models.ForeignKey(Tournament, related_name='sponsors', on_delete=models.CASCADE)
    sponsor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    sponsorship_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sponsorship_type = models.CharField(max_length=100, help_text="e.g., Title Sponsor, Gold Partner, Silver Partner")
    company_details = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('tournament', 'sponsor_name')
    
    def __str__(self):
        return f"{self.sponsor_name} - {self.tournament.name} ({self.status})"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('upi', 'UPI'),
        ('paytm', 'PayTM'),
        ('phonepay', 'PhonePay'),
        ('googlepay', 'Google Pay'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('crypto', 'Cryptocurrency'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )
    
    TRANSACTION_TYPE_CHOICES = (
        ('booking', 'Booking'),
        ('advertisement', 'Advertisement'),
        ('sponsorship', 'Sponsorship'),
    )
    
    # Core fields
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='payments', on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Foreign keys (one will be set depending on transaction type)
    booking = models.OneToOneField(Booking, null=True, blank=True, related_name='payment', on_delete=models.CASCADE)
    advertisement = models.OneToOneField(Advertisement, null=True, blank=True, related_name='payment', on_delete=models.CASCADE)
    tournament = models.OneToOneField(Tournament, null=True, blank=True, related_name='payment', on_delete=models.CASCADE)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Admin review
    admin_notes = models.TextField(blank=True)
    admin_approved = models.BooleanField(default=False)
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    admin_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='approved_payments', on_delete=models.SET_NULL)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_type', 'status']),
        ]
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.user.email} ({self.status})"
    
    def get_related_object(self):
        """Get the related object (booking, advertisement, or tournament)"""
        if self.booking:
            return self.booking
        elif self.advertisement:
            return self.advertisement
        elif self.tournament:
            return self.tournament
        return None