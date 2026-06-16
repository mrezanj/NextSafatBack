from rest_framework.serializers import ModelSerializer
from .models import Booking
from django.db import DatabaseError
from rest_framework import serializers
from trips.models import Trip
from tickets.models import Passenger
from django.db import transaction
from companies.models import Seat


def is_valid_seat(trip_id: int, selected_seat_id: int) -> bool:
    try:
        trip = Trip.objects.get(id=trip_id)
        taken_seat_ids: list = trip.passengers.filter(
            booking__status__in=[
                Booking.BookingStatus.PAID,
                Booking.BookingStatus.PENDING_PAYMENT,
            ]
        ).values_list("seat__id", flat=True)

        return selected_seat_id not in taken_seat_ids

    except Trip.DoesNotExist:
        return False


class BookingSerializer(ModelSerializer):
    seat_ids = serializers.ListField(write_only=True, child=serializers.IntegerField())
    passengers = serializers.ListField(write_only=True)
    trip = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Trip.objects.all()
    )
    trip_details = serializers.SerializerMethodField()
    passenger_count = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "expires_at",
            "total_price",
            "status",
            "seat_ids",  # w.o
            "passengers",  # w.o
            "trip",  # w.o
            "trip_details",
            "passenger_count",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "expires_at": {"read_only": True},
            "total_price": {"read_only": True},
            "status": {"read_only": True},
        }

    def get_passenger_count(self, obj):
        return obj.passengers.count()

    def get_trip_details(self, obj):
        trip = obj.trip

        return {
            "id": trip.id,
            "origin_city": trip.origin_city.name,
            "destination_city": trip.destination_city.name,
            "departure": trip.departure,
            "arrival": trip.arrival,
            "price": trip.price,
        }

    def validate(self, attrs):
        trip = attrs.get("trip")
        seat_ids = attrs.get("seat_ids", [])
        passengers = attrs.get("passengers", [])

        if len(seat_ids) != len(passengers):
            raise serializers.ValidationError(
                "Number of seats must match number of passengers"
            )

        if len(seat_ids) != len(set(seat_ids)):
            raise serializers.ValidationError({"seat_ids": "Duplicate seats selected"})

        for seat_id in seat_ids:
            if not is_valid_seat(trip.id, seat_id):
                raise serializers.ValidationError(
                    {"seat_ids": f"Seat {seat_id} is not available"}
                )
        for idx, passenger in enumerate(passengers):
            required_fields = ["first_name", "last_name", "phone", "national_code"]
            for field in required_fields:
                if field not in passenger:
                    raise serializers.ValidationError(
                        f"Passenger {idx + 1} missing {field}"
                    )

        return attrs

    @transaction.atomic
    def create(self, validated_data) -> Booking:
        user = self.context.get("request").user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"user": "user must be authenticated"})
        if user.role != user.AccountRole.USER:
            raise serializers.ValidationError(
                {"user": "account role must be user to add booking"}
            )

        trip: Trip = validated_data.pop("trip")
        passengers: list = validated_data.pop("passengers")
        seat_ids: list = validated_data.pop("seat_ids")

        try:
            seats = Seat.objects.filter(
                id__in=seat_ids, bus__trip=trip
            ).select_for_update(nowait=True)
        except DatabaseError:
            raise serializers.ValidationError(
                {"seat_ids": "Some seats are currently being booked. Please try again."}
            )

        if seats.count() != len(seat_ids):
            raise serializers.ValidationError(
                {
                    "seat_ids": "Seat-ids must be for this trip. Please refresh and try again."
                }
            )

        for seat_id in seat_ids:
            if not is_valid_seat(trip.id, seat_id):
                raise serializers.ValidationError(
                    {"seat_ids": f"Seat {seat_id} is not available"}
                )

        booking: Booking = Booking.objects.create(user=user, trip=trip)
        for passenger, seat in zip(passengers, seats):
            Passenger.objects.create(
                booking=booking,
                trip=trip,
                seat=seat,
                first_name=passenger.get("first_name"),
                last_name=passenger.get("last_name"),
                national_code=passenger.get("national_code"),
                phone=passenger.get("phone"),
            )

        return booking
