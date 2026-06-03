from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        SUCCESS = "success", "Success"
        PENDING = "pending", "Pending"
        FAILED = "failed", "Failed"

    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    tracking_code = models.CharField(max_length=120, unique=True, blank=True)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def set_tracking_code(cls) -> str:
        previous_codes = cls.objects.values_list("tracking_code", flat=True)
        new_code = get_random_string(120)
        while new_code in previous_codes:
            new_code = get_random_string(120)
        return new_code

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = self.set_tracking_code()
        if not self.amount:
            self.amount = self.booking.total_price
        if self.status == self.PaymentStatus.SUCCESS:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking} / {self.status}"

    class Meta:
        db_table = "payment"
