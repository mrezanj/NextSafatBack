from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string


class Passenger(models.Model):
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="passengers"
    )
    trip = models.ForeignKey(
        "trips.Trip", on_delete=models.CASCADE, related_name="passengers"
    )
    seat = models.ForeignKey(
        "companies.Seat", on_delete=models.CASCADE, related_name="passengers"
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^09\d{9}$")],
        help_text="format : 09XXXXXXXXX",
    )
    national_code = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\d{10}$")],
    )

    def clean(self):
        conflicting_passengers = Passenger.objects.filter(
            trip=self.trip, seat=self.seat
        ).exclude(id=self.id)

        if conflicting_passengers.exists():
            raise ValidationError({"seat": "This seat is already taken for this trip"})

        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        db_table = "passenger"
        unique_together = ["trip", "seat"]


@receiver(signal=post_save, sender=Passenger)
def update_total_price(sender: Passenger, instance: Passenger, created, **kwargs):
    if created:
        instance.booking.update_total_price()


class Ticket(models.Model):
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="tickets"
    )
    passenger = models.OneToOneField(
        Passenger, on_delete=models.CASCADE, related_name="ticket"
    )
    ticket_code = models.CharField(max_length=100, unique=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def set_ticket_code(cls) -> str:
        previous_codes = Ticket.objects.values_list("ticket_code", flat=True)
        new_code = get_random_string(100)
        while new_code in previous_codes:
            new_code = get_random_string(100)
        return new_code

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = self.set_ticket_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.passenger} ticket issued at : {self.issued_at}"

    class Meta:
        db_table = "ticket"
