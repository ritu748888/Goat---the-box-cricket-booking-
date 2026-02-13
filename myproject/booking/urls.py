from django.urls import path
from .views import booking_list, booking_create, booking_detail, venue_list, venue_detail, advertise_page, advertise_success, tournament_list, about_page

urlpatterns = [
    path('', booking_list, name='booking_list'),
    path('create/', booking_create, name='booking_create'),
    path('<int:pk>/', booking_detail, name='booking_detail'),
    path('venues/', venue_list, name='venue_list'),
    path('venues/<int:pk>/', venue_detail, name='venue_detail'),
    path('advertise/', advertise_page, name='advertise'),
    path('advertise/success/', advertise_success, name='advertise_success'),
    path('tournaments/', tournament_list, name='tournaments'),
    path('about/', about_page, name='about'),
]
