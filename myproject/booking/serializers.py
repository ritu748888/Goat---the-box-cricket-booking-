from rest_framework import serializers
from .models import Tournament, Team, TournamentRegistration


class TournamentSerializer(serializers.ModelSerializer):
    approved_registrations_count = serializers.IntegerField(source='approved_registrations_count', read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id',
            'name',
            'description',
            'poster',
            'start_date',
            'end_date',
            'start_time',
            'venue',
            'max_teams',
            'entry_fee',
            'status',
            'contact_person',
            'contact_email',
            'contact_phone',
            'rules',
            'prize_pool',
            'approved_registrations_count',
        ]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'captain_name', 'contact_number', 'player_list']


class TournamentRegistrationSerializer(serializers.ModelSerializer):
    team = TeamSerializer()

    class Meta:
        model = TournamentRegistration
        fields = ['id', 'tournament', 'team', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']
