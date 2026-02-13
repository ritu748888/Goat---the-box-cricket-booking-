from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm, AdvertisementForm
from .models import Booking, Court, Venue, Advertisement, Tournament
from django.contrib import messages
from django.utils import timezone
from datetime import date


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date', 'start_time')
    return render(request, 'booking/booking_list.html', {'bookings': bookings})


@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # simple availability check: same court/date overlapping times
            overlaps = Booking.objects.filter(
                court=booking.court,
                date=booking.date,
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time,
                status='confirmed'
            )
            if overlaps.exists():
                messages.error(request, 'Selected slot is already booked for this court')
            else:
                booking.save()
                messages.success(request, 'Booking confirmed')
                return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'booking/booking_create.html', {'form': form})


@login_required
def booking_detail(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': b})


def venue_list(request):
    venues = Venue.objects.all()
    return render(request, 'booking/venues.html', {'venues': venues})


def venue_detail(request, pk):
    v = get_object_or_404(Venue, pk=pk)
    courts = v.courts.all()
    return render(request, 'booking/venue_detail.html', {'venue': v, 'courts': courts})


def advertise_page(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST)
        if form.is_valid():
            advertisement = form.save()
            messages.success(request, f'Thank you {form.cleaned_data["brand_name"]}! Your advertisement request has been submitted. We will review and contact you shortly.')
            return redirect('advertise_success')
    else:
        form = AdvertisementForm()
    return render(request, 'booking/advertise.html', {'form': form})


def advertise_success(request):
    return render(request, 'booking/advertise_success.html')


def tournament_list(request):
    tournaments = Tournament.objects.filter(start_date__gte=date.today()).order_by('start_date')
    return render(request, 'booking/tournaments.html', {'tournaments': tournaments})


def about_page(request):
    return render(request, 'booking/about.html')
