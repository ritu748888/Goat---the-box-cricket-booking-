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
    """Notify a contact about advertisement activation status.

    This function is kept for backward compatibility with any code that calls it, but
    it does not assume any particular fields are present on the Advertisement model.
    """
    try:
        title = ad.title
    except AttributeError:
        title = 'Advertisement'

    subject = f"Your advertisement '{title}' has been {'activated' if approved else 'deactivated'}"
    message = (
        f"Hello,\n\n"
        f"Your advertisement '{title}' has been {'activated' if approved else 'deactivated'}.\n"
        "If you have any questions, please contact support.\n"
    )

    email = getattr(ad, 'link', None)
    if email and email.startswith('mailto:'):
        recipient = email.replace('mailto:', '')
    else:
        recipient = None

    if recipient:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])


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

def notify_admin_payment(payment):
    """Send SMS and email notification to admin about new payment request."""
    related_obj = payment.get_related_object()
    
    if payment.transaction_type == 'booking':
        subject = f"New Payment Request: Booking by {payment.user.email}"
        message = (
            f"New payment request received!\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"User: {payment.user.email}\n"
            f"Amount: ₹{payment.amount}\n"
            f"Payment Method: {payment.get_payment_method_display()}\n"
            f"Type: Ground Booking\n"
            f"Venue: {related_obj.court.venue.name}\n"
            f"Court: {related_obj.court.name}\n"
            f"Date: {related_obj.date} {related_obj.start_time} - {related_obj.end_time}\n"
            f"\nPlease review and approve/reject this payment in your admin panel."
        )
    elif payment.transaction_type == 'advertisement':
        subject = f"New Payment Request: Advertisement by {payment.user.email}"
        message = (
            f"New payment request received!\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"User: {payment.user.email}\n"
            f"Amount: ₹{payment.amount}\n"
            f"Payment Method: {payment.get_payment_method_display()}\n"
            f"Type: Advertisement\n"
            f"Title: {related_obj.title}\n"
            f"Position: {related_obj.get_position_display()}\n"
            f"Active Window: {related_obj.start_date} - {related_obj.end_date}\n"
            f"\nPlease review and activate/deactivate this advertisement in your admin panel."
        )
    elif payment.transaction_type == 'sponsorship':
        subject = f"New Payment Request: Sponsorship by {payment.user.email}"
        message = (
            f"New payment request received!\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"User: {payment.user.email}\n"
            f"Amount: ₹{payment.amount}\n"
            f"Payment Method: {payment.get_payment_method_display()}\n"
            f"Type: Tournament Sponsorship\n"
            f"Tournament: {related_obj.name}\n"
            f"Date: {related_obj.start_date}\n"
            f"\nPlease review and approve/reject this payment in your admin panel."
        )
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL])
    
    # Send SMS to admin (if configured)
    admin_phone = getattr(settings, 'ADMIN_PHONE', None)
    if admin_phone and getattr(settings, 'TWILIO_ACCOUNT_SID', None):
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sms_body = f"New Payment: {payment.transaction_id} - ₹{payment.amount} ({payment.transaction_type})"
            client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=admin_phone
            )
        except Exception as exc:
            print(f"Failed to send SMS to admin: {exc}")


def notify_user_payment_confirmed(payment):
    """Notify user about payment confirmation and booking."""
    related_obj = payment.get_related_object()
    
    if payment.transaction_type == 'booking':
        subject = f"Payment Confirmed! Your Ground Booking is Confirmed - {related_obj.court.venue.name}"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Congratulations! Your payment has been confirmed.\n\n"
            f"BOOKING DETAILS:\n"
            f"Ground/Venue: {related_obj.court.venue.name}\n"
            f"Court: {related_obj.court.name}\n"
            f"Date: {related_obj.date}\n"
            f"Time: {related_obj.start_time} - {related_obj.end_time}\n"
            f"Total Amount: ₹{payment.amount}\n"
            f"Player ID: {payment.user.id}\n"
            f"Booking ID: {related_obj.id}\n"
            f"Transaction ID: {payment.transaction_id}\n\n"
            f"Thank you for booking with us! Have a great game!\n"
        )
    elif payment.transaction_type == 'advertisement':
        subject = f"Payment Confirmed! Your Advertisement is Active"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Congratulations! Your payment has been confirmed.\n\n"
            f"ADVERTISEMENT DETAILS:\n"
            f"Title: {related_obj.title}\n"
            f"Position: {related_obj.get_position_display()}\n"
            f"Active Window: {related_obj.start_date} - {related_obj.end_date}\n"
            f"Amount: ₹{payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n\n"
            f"Your advertisement is now active!\n"
        )
    elif payment.transaction_type == 'sponsorship':
        subject = f"Payment Confirmed! Your Sponsorship is Active"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Congratulations! Your payment has been confirmed.\n\n"
            f"SPONSORSHIP DETAILS:\n"
            f"Tournament: {related_obj.name}\n"
            f"Date: {related_obj.start_date}\n"
            f"Amount: ₹{payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n\n"
            f"Thank you for your sponsorship!\n"
        )
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payment.user.email])
    
    # Send SMS confirmation
    phone = getattr(payment.user, 'phone', None)
    if phone and getattr(settings, 'TWILIO_ACCOUNT_SID', None):
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            if payment.transaction_type == 'booking':
                sms_body = f"Payment confirmed! Booking at {related_obj.court.venue.name} on {related_obj.date} {related_obj.start_time}. Your Player ID: {payment.user.id}"
            elif payment.transaction_type == 'advertisement':
                sms_body = f"Payment confirmed! Your advertisement for {related_obj.brand_name} is now live."
            else:
                sms_body = f"Payment confirmed! Your sponsorship for {related_obj.name} is active."
            
            client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as exc:
            print(f"Failed to send SMS to user: {exc}")


def notify_user_payment_rejected(payment, admin_notes=''):
    """Notify user about payment rejection and refund."""
    related_obj = payment.get_related_object()
    
    if payment.transaction_type == 'booking':
        subject = f"Payment Refunded - Booking Request Rejected"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Unfortunately, your payment and booking request have been rejected.\n\n"
            f"BOOKING DETAILS:\n"
            f"Ground/Venue: {related_obj.court.venue.name}\n"
            f"Court: {related_obj.court.name}\n"
            f"Date: {related_obj.date}\n"
            f"Time: {related_obj.start_time} - {related_obj.end_time}\n"
            f"Amount Refunded: ₹{payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"\nReason: {admin_notes if admin_notes else 'No specific reason provided'}\n\n"
            f"The refund will be processed within 5-7 business days.\n"
            f"Please contact support if you have any questions.\n"
        )
    elif payment.transaction_type == 'advertisement':
        subject = f"Payment Refunded - Advertisement Request Rejected"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Unfortunately, your advertisement request has been rejected.\n\n"
            f"ADVERTISEMENT DETAILS:\n"
            f"Title: {related_obj.title}\n"
            f"Position: {related_obj.get_position_display()}\n"
            f"Active Window: {related_obj.start_date} - {related_obj.end_date}\n"
            f"Amount Refunded: ₹{payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"\nReason: {admin_notes if admin_notes else 'No specific reason provided'}\n\n"
            f"The refund will be processed within 5-7 business days.\n"
        )
    elif payment.transaction_type == 'sponsorship':
        subject = f"Payment Refunded - Sponsorship Request Rejected"
        message = (
            f"Hello {payment.user.get_full_name() or payment.user.email},\n\n"
            f"Unfortunately, your sponsorship request has been rejected.\n\n"
            f"SPONSORSHIP DETAILS:\n"
            f"Tournament: {related_obj.name}\n"
            f"Date: {related_obj.start_date}\n"
            f"Amount Refunded: ₹{payment.amount}\n"
            f"Transaction ID: {payment.transaction_id}\n"
            f"\nReason: {admin_notes if admin_notes else 'No specific reason provided'}\n\n"
            f"The refund will be processed within 5-7 business days.\n"
        )
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [payment.user.email])
    
    # Send SMS about refund
    phone = getattr(payment.user, 'phone', None)
    if phone and getattr(settings, 'TWILIO_ACCOUNT_SID', None):
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            sms_body = f"Payment rejected and refunded: {payment.transaction_id}. Amount: ₹{payment.amount}. Refund in 5-7 days."
            client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as exc:
            print(f"Failed to send refund SMS to user: {exc}")