from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Trip, City
from django.db.models import Count
from rest_framework import serializers
from companies.models import Company, Bus


class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "slug"]


class TripSerializer(ModelSerializer):
    available_seats = serializers.SerializerMethodField()
    bus_type = serializers.CharField(source="bus.type", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    company = PrimaryKeyRelatedField(read_only=True)
    bus = PrimaryKeyRelatedField(queryset=Bus.objects.all())
    origin_city = PrimaryKeyRelatedField(queryset=City.objects.all())
    destination_city = PrimaryKeyRelatedField(queryset=City.objects.all())
    origin_city_name = serializers.CharField(source="origin_city.name", read_only=True)
    destination_city_name = serializers.CharField(
        source="destination_city.name", read_only=True
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "bus",
            "origin_city",
            "origin_city_name",
            "destination_city",
            "destination_city_name",
            "departure",
            "arrival",
            "price",
            "status",
            "company",
            "company_name",
            "bus_type",
            "available_seats",
        ]

    def get_available_seats(self, obj):
        reserved_seats = (
            obj.bookings.filter(status="paid").aggregate(total=Count("passengers"))[
                "total"
            ]
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
        if bus.seat_count < 10:
            raise serializers.ValidationError(
                f"Bus {bus.id} does not have enough seats , must have 10 seats at least"
            )
        trip = Trip.objects.create(**validated_data)
        return trip
