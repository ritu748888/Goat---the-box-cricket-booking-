from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Venue, Court, Booking, Review
from .serializers import VenueSerializer, VenueListSerializer, CourtSerializer, BookingSerializer, ReviewSerializer
from user.models import CustomUser
from user.serializers import UserSerializer


class VenueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'address']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['-rating']

    def get_queryset(self):
        return Venue.objects.all().prefetch_related('courts', 'reviews')

    def get_serializer_class(self):
        if self.action == 'list':
            return VenueListSerializer
        return VenueSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get available time slots for a venue on a given date."""
        venue = self.get_object()
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response({'error': 'date parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format (use YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        courts = venue.courts.filter(is_active=True)
        availability = {}
        
        for court in courts:
            bookings = Booking.objects.filter(court=court, date=date, status='confirmed')
            booked_slots = [(b.start_time, b.end_time) for b in bookings]
            availability[court.id] = {
                'court_name': court.name,
                'booked_slots': [{'start': str(s), 'end': str(e)} for s, e in booked_slots]
            }
        
        return Response(availability)


class CourtViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Court.objects.filter(is_active=True)
    serializer_class = CourtSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'venue__name']
    ordering_fields = ['price_per_hour', 'capacity']


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'start_time']
    ordering = ['-date', 'start_time']

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings for the user."""
        today = timezone.now().date()
        bookings = Booking.objects.filter(user=request.user, date__gte=today, status='confirmed').order_by('date', 'start_time')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past bookings for the user."""
        today = timezone.now().date()
        bookings = Booking.objects.filter(user=request.user, date__lt=today).order_by('-date', '-start_time')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()
        if booking.user != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        if booking.status == 'cancelled':
            return Response({'error': 'Already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'Booking cancelled'})


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        venue_id = self.request.query_params.get('venue_id')
        if venue_id:
            return Review.objects.filter(venue_id=venue_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
