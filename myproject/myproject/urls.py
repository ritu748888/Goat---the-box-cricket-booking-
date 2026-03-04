from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from booking.api_views import (
    VenueViewSet,
    CourtViewSet,
    BookingViewSet,
    ReviewViewSet,
    PaymentViewSet,
    AdvertisementViewSet
)

from user.api_views import UserViewSet

router = DefaultRouter()
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'courts', CourtViewSet, basename='court')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'advertisements', AdvertisementViewSet, basename='advertisement')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('user.urls')),
    path('booking/', include('booking.urls')),
]