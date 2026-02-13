from rest_framework import serializers
from .models import Venue, Court, Booking, Review
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

    class Meta:
        model = Booking
        fields = ('id', 'court', 'court_name', 'venue_name', 'date', 'start_time', 'end_time', 'number_of_players', 'total_price', 'status', 'notes', 'created_at', 'updated_at', 'user_email')
        read_only_fields = ('total_price', 'created_at', 'updated_at', 'user_email')

    def create(self, validated_data):
        booking = Booking(**validated_data)
        booking.calculate_price()
        booking.save()
        return booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'phone')
