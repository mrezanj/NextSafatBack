from django.db import models
from datetime import timedelta
from django.utils import timezone

# from background_task import background  # type: ignore


class Booking(models.Model):

    class BookingStatus(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING_PAYMENT = "pending_payment", "Payment Pending"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="bookings"
    )
    trip = models.ForeignKey(
        "trips.Trip", on_delete=models.CASCADE, related_name="bookings"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_at_booking = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING_PAYMENT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_expired(self):
        if self.status != self.BookingStatus.PENDING_PAYMENT:
            return False
        if not self.expires_at:
            return False
        return self.expires_at <= timezone.now()

    def mark_expired_if_needed(self):
        if self.is_expired and self.status == self.BookingStatus.PENDING_PAYMENT:
            self.status = self.BookingStatus.EXPIRED
            self.save(update_fields=["status"])
            return True
        return False

    def update_total_price(self):
        total_price = self.price_at_booking * self.passengers.count()
        self.total_price = total_price
        self.save(update_fields=["total_price"])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_at_booking = self.trip.price
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
        # if not self.pk:
        #     expire_booking(self.id, schedule=timedelta(minutes=10))

    def __str__(self):
        return f"trip:{self.trip} status: {self.status}"

    class Meta:
        db_table = "booking"


# @background
# def expire_booking(booking_id):
#     try:
#         booking = Booking.objects.get(id=booking_id)
#         if booking.status == Booking.BookingStatus.PENDING_PAYMENT:
#             booking.status = Booking.BookingStatus.EXPIRED
#             booking.save(update_fields=["status"])
#     except Booking.DoesNotExist:
#         pass
