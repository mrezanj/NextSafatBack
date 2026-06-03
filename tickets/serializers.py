from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Ticket
from trips.models import Trip


class PassengerNestedSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    national_code = serializers.CharField()


class TripNestedSerializer(serializers.ModelSerializer):
    origin_city = serializers.CharField(source="origin_city.name", read_only=True)
    destination_city = serializers.CharField(
        source="destination_city.name", read_only=True
    )

    class Meta:
        model = Trip
        fields = ["id", "origin_city", "destination_city", "departure", "arrival"]


class TicketSerializer(ModelSerializer):
    booking_id = serializers.IntegerField(source="booking.id", read_only=True)
    passenger = PassengerNestedSerializer(source="passenger", read_only=True)
    trip = TripNestedSerializer(source="booking.trip", read_only=True)
    seat_number = serializers.IntegerField(
        source="passenger.seat.seat_number", read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "booking_id",
            "passenger",
            "trip",
            "seat_number",
            "ticket_code",
            "issued_at",
        ]
