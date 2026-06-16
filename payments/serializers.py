from rest_framework.serializers import ModelSerializer
from .models import Payment
from rest_framework import serializers
from bookings.models import Booking
from tickets.models import Ticket
from django.db import transaction


class PaymentSerializer(ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    method = serializers.CharField(write_only=True)

    class Meta:
        model = Payment
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        allowed_methods = ["fake_gateway"]

        booking = validated_data.pop("booking")
        method = validated_data.pop("method")
        if method not in allowed_methods:
            raise serializers.ValidationError("Invalid payment method")
        user = self.context.get("request").user

        payment_already_paid = Payment.objects.filter(
            booking=booking, status=Payment.PaymentStatus.SUCCESS
        ).exists()
        if payment_already_paid:
            raise serializers.ValidationError("Booking already paid")

        if booking.user != user:
            raise serializers.ValidationError("You don't own this booking")
        if booking.status == Booking.BookingStatus.CANCELED:
            raise serializers.ValidationError("Booking status is canceled")
        booking.mark_expired_if_needed()
        if booking.status == Booking.BookingStatus.EXPIRED:
            raise serializers.ValidationError("Booking has expired")
        if booking.status != Booking.BookingStatus.PENDING_PAYMENT:
            raise serializers.ValidationError("Booking status isn't pending")

        passengers = booking.passengers.all()
        if not passengers.exists():
            raise serializers.ValidationError("No passenger found for this booking")
        
        payment = Payment.objects.create(
            booking=booking, status=Payment.PaymentStatus.SUCCESS
        )
        booking.status = Booking.BookingStatus.PAID
        booking.save(update_fields=["status"])

        for passenger in passengers:
            Ticket.objects.create(booking=booking, passenger=passenger)

        return payment
