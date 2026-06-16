from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Trip, City
from django.db.models import Count
from rest_framework import serializers
from companies.models import Company, Bus
from bookings.models import Booking


class TripSerializer(ModelSerializer):
    company = PrimaryKeyRelatedField(read_only=True)
    bus = PrimaryKeyRelatedField(queryset=Bus.objects.all())
    origin_city = PrimaryKeyRelatedField(queryset=City.objects.all())
    destination_city = PrimaryKeyRelatedField(queryset=City.objects.all())
    available_seats = serializers.SerializerMethodField()
    bus_type = serializers.CharField(source="bus.type", read_only=True)
    origin_city_name = serializers.CharField(source="origin_city.name", read_only=True)
    destination_city_name = serializers.CharField(
        source="destination_city.name", read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "company",
            "bus",
            "origin_city",
            "destination_city",
            "departure",
            "arrival",
            "price",
            "status",
            "available_seats",
            "bus_type",
            "origin_city_name",
            "destination_city_name",
        ]

    def get_available_seats(self, obj):
        reserved_seats = (
            obj.bookings.filter(
                status__in=[
                    Booking.BookingStatus.PAID,
                    Booking.BookingStatus.PENDING_PAYMENT,
                ]
            )
            .aggregate(total=Count("passengers"))
            .get("total")
            or 0
        )
        return obj.bus.seat_count - reserved_seats

    def create(self, validated_data):
        if validated_data.get("origin_city") == validated_data.get("destination_city"):
            raise serializers.ValidationError(
                "Origin city and destination city cannot be the same."
            )
        if validated_data.get("departure") >= validated_data.get("arrival"):
            raise serializers.ValidationError(
                "Arrival time must be after departure time."
            )
        if validated_data.get("price") <= 0:
            raise serializers.ValidationError("Price must be positive.")
        bus = validated_data.get("bus")
        if bus.seat_count < 15:
            raise serializers.ValidationError(
                {
                    "bus": f"Bus {bus.id} does not have enough seats , must have 15 seats at least"
                }
            )
        company = validated_data["company"]
        if bus.company != company:
            raise serializers.ValidationError(
                {"bus": f"Bus {bus.id} does not belong to this Company"}
            )
        trip = Trip.objects.create(**validated_data)
        return trip
