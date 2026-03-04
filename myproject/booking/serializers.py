from rest_framework import serializers
from .models import Venue, Court, Booking, Review, Payment, Advertisement, Tournament
from user.models import CustomUser



class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'user_email', 'rating', 'comment', 'created_at')
        read_only_fields = ('created_at',)


class CourtSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)

    class Meta:
        model = Court
        fields = ('id', 'name', 'venue', 'venue_name', 'capacity', 'price_per_hour', 'description', 'is_active', 'created_at')


class VenueSerializer(serializers.ModelSerializer):
    courts = CourtSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ('id', 'name', 'address', 'city', 'phone', 'email', 'description', 'rating', 'average_rating', 'courts', 'reviews', 'created_at')

    def get_average_rating(self, obj):
        return obj.average_rating()


class VenueListSerializer(serializers.ModelSerializer):
    courts_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = ('id', 'name', 'city', 'rating', 'courts_count')

    def get_courts_count(self, obj):
        return obj.courts.count()


class BookingSerializer(serializers.ModelSerializer):
    court_name = serializers.CharField(source='court.name', read_only=True)
    venue_name = serializers.CharField(source='court.venue.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    payment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'court', 'court_name', 'venue_name', 'date', 'start_time', 'end_time', 'number_of_players', 'total_price', 'status', 'notes', 'payment', 'created_at', 'updated_at', 'user_email')
        read_only_fields = ('total_price', 'created_at', 'updated_at', 'user_email', 'payment')

    def get_payment(self, obj):
        try:
            payment = obj.payment
            return {
                'id': payment.id,
                'status': payment.status,
                'amount': str(payment.amount),
                'payment_method': payment.payment_method,
            }
        except:
            return None

    def create(self, validated_data):
        booking = Booking(**validated_data)
        booking.calculate_price()
        booking.save()
        return booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone')

class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    booking_detail = serializers.SerializerMethodField(read_only=True)
    advertisement_detail = serializers.SerializerMethodField(read_only=True)
    tournament_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'transaction_id', 'transaction_type', 'user', 'user_email',
            'booking', 'booking_detail', 'advertisement', 'advertisement_detail',
            'tournament', 'tournament_detail', 'amount', 'payment_method', 'status',
            'admin_approved', 'admin_notes', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'transaction_id', 'user_email', 'admin_approved',
            'admin_notes', 'created_at', 'updated_at'
        )

    def get_booking_detail(self, obj):
        if obj.booking:
            return {
                'id': obj.booking.id,
                'venue_name': obj.booking.court.venue.name,
                'court_name': obj.booking.court.name,
                'date': obj.booking.date,
                'start_time': obj.booking.start_time,
                'end_time': obj.booking.end_time,
            }
        return None

    def get_advertisement_detail(self, obj):
        if obj.advertisement:
            return {
                'id': obj.advertisement.id,
                'brand_name': obj.advertisement.brand_name,
                'promotion_type': obj.advertisement.promotion_type,
                'duration': obj.advertisement.advertise_duration,
            }
        return None

    def get_tournament_detail(self, obj):
        if obj.tournament:
            return {
                'id': obj.tournament.id,
                'name': obj.tournament.name,
                'start_date': obj.tournament.start_date,
                'entry_fee': obj.tournament.entry_fee,
            }
        return None


class AdvertisementSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Advertisement
        fields = (
            'id', 'brand_name', 'contact_person_name', 'email', 'mobile_no',
            'promotion_type', 'company_details', 'advertise_duration',
            'status', 'payment', 'created_at', 'updated_at'
        )
        read_only_fields = ('status', 'created_at', 'updated_at')