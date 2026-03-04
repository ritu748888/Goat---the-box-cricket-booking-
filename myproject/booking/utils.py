from django.core.mail import send_mail
from django.conf import settings


def notify_admin_booking_request(booking):
    """Send email notification to admin about a new booking request."""
    subject = f"New booking request from {booking.user.email}"
    message = (
        f"User: {booking.user.get_full_name() or booking.user.email}\n"
        f"Venue: {booking.court.venue.name}\n"
        f"Court: {booking.court.name}\n"
        f"Date: {booking.date} {booking.start_time} - {booking.end_time}\n"
        f"Players: {booking.number_of_players}\n"
        "\nPlease review the request in your admin panel."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])


def notify_admin_generic(subject, message):
    """Send a simple message to the administrator. Useful for tracking views or other events."""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])


def notify_user_booking_status(booking):
    """Inform the user that their booking status has changed via email and SMS (if configured)."""
    # Email notification
    subject = f"Your booking at {booking.court} has been {booking.status}"
    message = (
        f"Hello {booking.user.get_full_name() or booking.user.email},\n\n"
        f"Your booking for {booking.court} on {booking.date} ({booking.start_time} - {booking.end_time}) "
        f"is now '{booking.get_status_display()}'.\n"
        f"Thank you for using our service.\n"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.user.email])

    # SMS notification (optional; requires Twilio credentials)
    phone = getattr(booking.user, 'phone', None)
    if phone and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sms_body = (
                f"Booking {booking.status}: {booking.court} on {booking.date} {booking.start_time}."
            )
            client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as exc:
            # in a real project you should log this
            print(f"failed to send sms: {exc}")


def notify_advertisement_status(ad, approved=True):
    """Notify advertisement applicant about approval/rejection."""
    subject = f"Your advertisement request '{ad.brand_name}' has been {'approved' if approved else 'rejected'}"
    message = (
        f"Hello {ad.contact_person_name},\n\n"
        f"Your advertisement request for '{ad.brand_name}' (type: {ad.promotion_type}) has been {'approved' if approved else 'rejected'}.\n"
        "We will contact you with next steps if approved.\n"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ad.email])
    phone = getattr(ad, 'mobile_no', None)
    if phone and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sms_body = f"Ad { 'Approved' if approved else 'Rejected' }: {ad.brand_name}"
            client.messages.create(body=sms_body, from_=settings.TWILIO_PHONE_NUMBER, to=phone)
        except Exception as exc:
            print(f"failed to send sms: {exc}")


def notify_tournament_status(tournament, approved=True):
    """Notify tournament contact about approval/rejection."""
    subject = f"Tournament '{tournament.name}' has been {'confirmed' if approved else 'rejected'}"
    message = (
        f"Hello {tournament.contact_person},\n\n"
        f"Your tournament '{tournament.name}' at {tournament.venue.name} on {tournament.start_date} has been {'confirmed' if approved else 'rejected'}.\n"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [tournament.contact_email])
    phone = getattr(tournament, 'contact_phone', None)
    if phone and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sms_body = f"Tournament { 'Confirmed' if approved else 'Rejected' }: {tournament.name}"
            client.messages.create(body=sms_body, from_=settings.TWILIO_PHONE_NUMBER, to=phone)
        except Exception as exc:
            print(f"failed to send sms: {exc}")
