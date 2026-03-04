from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import BookingForm, AdvertisementForm
from .models import Booking, Court, Venue, Advertisement, Tournament
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.conf import settings
from . import utils


def _is_admin(user):
    # treat superusers and the configured admin email as administrators
    return user.is_authenticated and (user.is_superuser or user.email == getattr(settings, 'ADMIN_EMAIL', ''))


admin_required = user_passes_test(_is_admin)


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
            # simple availability check: same court/date overlapping times, only confirmed slots block
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
                # mark pending until admin approves
                booking.status = 'pending'
                booking.save()
                # notify administrator about new request
                utils.notify_admin_booking_request(booking)
                messages.success(request, 'Booking request submitted. You will receive a confirmation once admin approves it.')
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
    # notify admin that a (logged‑in) user viewed this venue
    if request.user.is_authenticated:
        utils.notify_admin_generic(
            subject=f"Venue viewed: {v.name}",
            message=f"User {request.user.email} opened venue '{v.name}' (id={v.id})."
        )
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


@admin_required
def admin_dashboard(request):
    """Administrator dashboard showing all booking requests and statuses."""
    bookings = Booking.objects.all().order_by('-created_at')
    # pending advertisements
    ads = Advertisement.objects.filter(status='pending').order_by('-created_at')
    # tournaments (show upcoming/ongoing as admin-manageable)
    tournaments = Tournament.objects.filter(status__in=['upcoming', 'ongoing']).order_by('-created_at')
    context = {
        'bookings': bookings,
        'ads': ads,
        'tournaments': tournaments,
    }
    return render(request, 'booking/admin_dashboard.html', context)


@admin_required
def admin_update_booking(request, pk, action):
    """Confirm or cancel a booking from the admin dashboard."""
    booking = get_object_or_404(Booking, pk=pk)
    if action == 'confirm':
        booking.status = 'confirmed'
        booking.save()
        utils.notify_user_booking_status(booking)
        messages.success(request, 'Booking confirmed and user notified.')
    elif action == 'cancel':
        booking.status = 'cancelled'
        booking.save()
        # notify the user that their booking was rejected/cancelled
        utils.notify_user_booking_status(booking)
        messages.info(request, 'Booking cancelled and user notified.')
    else:
        messages.warning(request, 'Unknown action')
    return redirect('admin_dashboard')



@admin_required
def admin_update_advertisement(request, pk, action):
    ad = get_object_or_404(Advertisement, pk=pk)
    if action == 'approve':
        ad.status = 'approved'
        ad.save()
        utils.notify_advertisement_status(ad, approved=True)
        messages.success(request, 'Advertisement approved and applicant notified.')
    elif action == 'reject':
        ad.status = 'rejected'
        ad.save()
        utils.notify_advertisement_status(ad, approved=False)
        messages.info(request, 'Advertisement rejected and applicant notified.')
    else:
        messages.warning(request, 'Unknown action')
    return redirect('admin_dashboard')


@admin_required
def admin_update_tournament(request, pk, action):
    t = get_object_or_404(Tournament, pk=pk)
    if action == 'confirm':
        t.status = 'upcoming'
        t.save()
        utils.notify_tournament_status(t, approved=True)
        messages.success(request, 'Tournament confirmed and contact notified.')
    elif action == 'reject':
        t.status = 'cancelled'
        t.save()
        utils.notify_tournament_status(t, approved=False)
        messages.info(request, 'Tournament rejected and contact notified.')
    else:
        messages.warning(request, 'Unknown action')
    return redirect('admin_dashboard')


def about_page(request):
    return render(request, 'booking/about.html')
