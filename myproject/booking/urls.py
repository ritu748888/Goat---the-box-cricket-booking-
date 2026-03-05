from django.urls import path
from .views import (
    booking_list, booking_create, booking_detail,
    booking_payment, booking_payment_success,
    venue_list, venue_detail,
    advertise_page, advertise_success,
    tournament_list, tournament_create, tournament_detail, about_page,
    admin_dashboard, admin_update_booking, admin_update_advertisement, admin_update_tournament, admin_update_tournament_sponsor
)

urlpatterns = [
    path('', booking_list, name='booking_list'),
    path('create/', booking_create, name='booking_create'),
    path('<int:pk>/', booking_detail, name='booking_detail'),
    path('venues/', venue_list, name='venue_list'),
    path('venues/<int:pk>/', venue_detail, name='venue_detail'),
    path('advertise/', advertise_page, name='advertise'),
    path('advertise/success/', advertise_success, name='advertise_success'),
    path('tournaments/', tournament_list, name='tournaments'),
    path('tournaments/create/', tournament_create, name='tournament_create'),
    path('tournaments/<int:pk>/', tournament_detail, name='tournament_detail'),
    path('about/', about_page, name='about'),
    # payment flow for bookings
    path('payment/', booking_payment, name='booking_payment'),
    path('payment/success/<int:pk>/', booking_payment_success, name='booking_payment_success'),
    # custom admin/dashboard for booking requests
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/dashboard/booking/<int:pk>/<str:action>/', admin_update_booking, name='admin_update_booking'),
    path('admin/dashboard/advertisement/<int:pk>/<str:action>/', admin_update_advertisement, name='admin_update_advertisement'),
    path('admin/dashboard/tournament/<int:pk>/<str:action>/', admin_update_tournament, name='admin_update_tournament'),
    path('admin/dashboard/sponsor/<int:pk>/<str:action>/', admin_update_tournament_sponsor, name='admin_update_tournament_sponsor'),
]
