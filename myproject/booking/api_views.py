from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Venue, Court, Booking, Review, Payment, Advertisement, Tournament
from .serializers import VenueSerializer, VenueListSerializer, CourtSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer, AdvertisementSerializer
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


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new payment for booking, advertisement, or sponsorship."""
        import uuid
        from . import utils
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate unique transaction ID
        transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
        
        # Set user and transaction ID
        payment = serializer.save(
            user=request.user,
            transaction_id=transaction_id,
            status='pending'
        )
        
        # Send SMS to admin about new payment request
        utils.notify_admin_payment(payment)
        
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Admin confirms and approves payment."""
        payment = self.get_object()
        
        if not (request.user.is_superuser or request.user.email == 'admin@example.com'):
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.status != 'pending':
            return Response(
                {'error': f'Payment is already {payment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Confirm the related booking/advertisement/tournament
        payment.status = 'completed'
        payment.admin_approved = True
        payment.admin_approved_at = timezone.now()
        payment.admin_approved_by = request.user
        payment.save()
        
        # Update related object status
        if payment.booking:
            payment.booking.status = 'confirmed'
            payment.booking.save()
        elif payment.advertisement:
            payment.advertisement.status = 'active'
            payment.advertisement.save()
        elif payment.tournament:
            payment.tournament.status = 'upcoming'
            payment.tournament.save()
        
        # Send notification to user
        from . import utils
        utils.notify_user_payment_confirmed(payment)
        
        return Response(
            {'status': 'Payment approved and booking confirmed'},
            PaymentSerializer(payment).data
        )

    @action(detail=True, methods=['post'])
    def reject_payment(self, request, pk=None):
        """Admin rejects payment and initiates refund."""
        payment = self.get_object()
        
        if not (request.user.is_superuser or request.user.email == 'admin@example.com'):
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if payment.status != 'pending':
            return Response(
                {'error': f'Payment is already {payment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        admin_notes = request.data.get('admin_notes', '')
        
        # Refund payment
        payment.status = 'refunded'
        payment.admin_notes = admin_notes
        payment.admin_approved_by = request.user
        payment.save()
        
        # Update related object status
        if payment.booking:
            payment.booking.status = 'cancelled'
            payment.booking.save()
        elif payment.advertisement:
            payment.advertisement.status = 'rejected'
            payment.advertisement.save()
        elif payment.tournament:
            payment.tournament.status = 'cancelled'
            payment.tournament.save()
        
        # Send refund notification to user
        from . import utils
        utils.notify_user_payment_rejected(payment, admin_notes)
        
        return Response(
            {'status': 'Payment refunded'},
            PaymentSerializer(payment).data
        )

    @action(detail=False, methods=['get'])
    def pending_payments(self, request):
        """Get all pending payments (admin only)."""
        if not (request.user.is_superuser or request.user.email == 'admin@example.com'):
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending = Payment.objects.filter(status='pending').order_by('-created_at')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


class AdvertisementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AdvertisementSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        # only return advertisements owned by the requesting user
        user = self.request.user
        if user and user.is_authenticated:
            return Advertisement.objects.filter(user=user)
        return Advertisement.objects.none()

    def perform_create(self, serializer):
        # associate advertisement with the user who created it
        serializer.save(user=self.request.user)


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
