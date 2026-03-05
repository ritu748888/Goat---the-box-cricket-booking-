from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import BookingForm, AdvertisementForm, TournamentForm, TournamentSponsorForm
from .models import Booking, Court, Venue, Advertisement, Tournament, TournamentSponsor, Payment
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.conf import settings
import uuid
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
    """Two‑step booking: first collect details, then send user to payment."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # availability check against already confirmed bookings
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
                # save data to session so we can confirm after payment
                request.session['pending_booking'] = {
                    'court': booking.court.id,
                    'date': str(booking.date),
                    'start_time': str(booking.start_time),
                    'end_time': str(booking.end_time),
                    'number_of_players': booking.number_of_players,
                    'notes': booking.notes,
                }
                # calculate price now and keep it for display
                request.session['pending_price'] = booking.calculate_price()
                return redirect('booking_payment')
    else:
        form = BookingForm()
    return render(request, 'booking/booking_create.html', {'form': form})


@login_required
def booking_detail(request, pk):
    b = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': b})


@login_required
def booking_payment(request):
    """Show payment page for pending booking in session and process payment."""
    from datetime import datetime
    data = request.session.get('pending_booking')
    if not data:
        return redirect('booking_create')
    # fetch objects for display
    court = Court.objects.get(id=data['court'])
    venue = court.venue
    price = request.session.get('pending_price', 0)

    if request.method == 'POST':
        method = request.POST.get('method', 'upi')
        # convert date and time strings back to proper types
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        # Handle time parsing with or without microseconds
        try:
            start_time = datetime.strptime(data['start_time'], '%H:%M:%S.%f').time()
        except ValueError:
            start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
        try:
            end_time = datetime.strptime(data['end_time'], '%H:%M:%S.%f').time()
        except ValueError:
            end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
        
        # create booking as 'pending' waiting for admin approval
        booking = Booking(
            user=request.user,
            court=court,
            date=booking_date,
            start_time=start_time,
            end_time=end_time,
            number_of_players=data['number_of_players'],
            notes=data.get('notes', ''),
            status='pending'
        )
        booking.calculate_price()
        booking.save()
        # record a simple Payment object for demonstration
        Payment.objects.create(
            user=request.user,
            transaction_id=str(uuid.uuid4()),
            transaction_type='booking',
            booking=booking,
            amount=booking.total_price,
            payment_method=method,
            status='completed'
        )
        # clear session
        request.session.pop('pending_booking', None)
        request.session.pop('pending_price', None)
        return redirect('booking_payment_success', pk=booking.pk)

    return render(request, 'booking/payment.html', {
        'booking_data': data,
        'price': price,
        'court': court,
        'venue': venue,
    })


@login_required
def booking_payment_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking/payment_success.html', {'booking': booking})


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


@login_required
def tournament_create(request):
    """Create a new tournament."""
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            messages.success(request, f'Tournament "{tournament.name}" has been created successfully!')
            return redirect('tournament_detail', pk=tournament.pk)
    else:
        form = TournamentForm()
    return render(request, 'booking/tournament_create.html', {'form': form})


def tournament_detail(request, pk):
    """Show tournament details and sponsors."""
    tournament = get_object_or_404(Tournament, pk=pk)
    sponsors = tournament.sponsors.filter(status='approved')
    sponsor_form = TournamentSponsorForm() if request.user.is_authenticated else None
    
    if request.method == 'POST' and request.user.is_authenticated:
        sponsor_form = TournamentSponsorForm(request.POST)
        if sponsor_form.is_valid():
            sponsor = sponsor_form.save(commit=False)
            sponsor.tournament = tournament
            # Check if this sponsor already exists
            existing = TournamentSponsor.objects.filter(
                tournament=tournament,
                sponsor_name=sponsor.sponsor_name
            ).first()
            if existing:
                messages.warning(request, f'{sponsor.sponsor_name} is already a sponsor for this tournament.')
            else:
                sponsor.save()
                messages.success(request, 'Thank you for your interest in sponsoring! Your sponsorship request has been submitted. Admin will review and contact you shortly.')
                return redirect('tournament_detail', pk=tournament.pk)
    
    context = {
        'tournament': tournament,
        'sponsors': sponsors,
        'sponsor_form': sponsor_form,
    }
    return render(request, 'booking/tournament_detail.html', context)


@admin_required
def admin_dashboard(request):
    """Administrator dashboard showing all booking requests and statuses."""
    # Pending payment bookings (after user paid, awaiting admin approval)
    pending_payment_bookings = Booking.objects.filter(status='pending').order_by('-created_at')
    # All confirmed bookings
    confirmed_bookings = Booking.objects.filter(status='confirmed').order_by('-created_at')
    # Cancelled bookings
    cancelled_bookings = Booking.objects.filter(status='cancelled').order_by('-created_at')
    # pending advertisements
    ads = Advertisement.objects.filter(status='pending').order_by('-created_at')
    # tournaments (show upcoming/ongoing as admin-manageable)
    tournaments = Tournament.objects.filter(status__in=['upcoming', 'ongoing']).order_by('-created_at')
    context = {
        'pending_payment_bookings': pending_payment_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
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
    elif action == 'cancel' or action == 'reject':
        booking.status = 'cancelled'
        booking.save()
        # notify the user that their booking was rejected/cancelled with refund info
        utils.notify_user_booking_status(booking)
        messages.info(request, 'Booking rejected. User will be notified about refund.')
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


@admin_required
def admin_update_tournament_sponsor(request, pk, action):
    """Approve or reject a tournament sponsorship request."""
    sponsor = get_object_or_404(TournamentSponsor, pk=pk)
    if action == 'approve':
        sponsor.status = 'approved'
        sponsor.save()
        messages.success(request, f'{sponsor.sponsor_name} has been approved as a sponsor for {sponsor.tournament.name}.')
    elif action == 'reject':
        sponsor.status = 'rejected'
        sponsor.save()
        messages.info(request, f'Sponsorship request from {sponsor.sponsor_name} has been rejected.')
    else:
        messages.warning(request, 'Unknown action')
    return redirect('admin_dashboard')


def about_page(request):
    return render(request, 'booking/about.html')
