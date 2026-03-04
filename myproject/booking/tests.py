from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Venue, Court, Booking
from django.core import mail
from django.conf import settings

User = get_user_model()

class BookingWorkflowTests(TestCase):
    def setUp(self):
        # create admin and regular user
        self.admin = User.objects.create_superuser(email=settings.ADMIN_EMAIL, password='adminpass')
        self.user = User.objects.create_user(email='user@example.com', password='userpass')

        self.venue = Venue.objects.create(name='Test Venue')
        self.court = Court.objects.create(venue=self.venue, name='Court1')
        self.client = Client()

    def test_booking_request_creates_pending_and_notifies_admin(self):
        self.client.login(email='user@example.com', password='userpass')
        data = {
            'court': self.court.id,
            'date': '2030-01-01',
            'start_time': '10:00',
            'end_time': '12:00',
            'number_of_players': 6,
        }
        resp = self.client.post(reverse('booking_create'), data)
        self.assertEqual(resp.status_code, 302)
        booking = Booking.objects.get(user=self.user)
        self.assertEqual(booking.status, 'pending')
        # check mail sent to admin
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(settings.ADMIN_EMAIL, mail.outbox[0].to)

    def test_admin_dashboard_requires_admin(self):
        # regular user should be forbidden
        self.client.login(email='user@example.com', password='userpass')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 302)  # redirect to login

        # admin can access directly
        self.client.login(email=settings.ADMIN_EMAIL, password='adminpass')
        resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_login_redirects_to_dashboard(self):
        # use admin-login endpoint and confirm redirect
        resp = self.client.post(reverse('admin_login'), {
            'username': settings.ADMIN_EMAIL,
            'password': 'adminpass'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('admin_dashboard'), resp.url)

