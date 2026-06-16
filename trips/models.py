from django.db import models
from django.db.models import Q, F
from django.utils.text import slugify


class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"
        db_table = "city"


class Trip(models.Model):

    class TripStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="trips",
    )
    bus = models.ForeignKey(
        "companies.Bus", on_delete=models.CASCADE, related_name="trips"
    )
    origin_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="trip_origins"
    )
    destination_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="trip_destinations"
    )
    departure = models.DateTimeField()
    arrival = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=15, choices=TripStatus.choices, default=TripStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin_city.name} → {self.destination_city.name}"

    class Meta:
        db_table = "trip"
        constraints = [
            models.CheckConstraint(
                condition=~Q(origin_city=F("destination_city")),
                name="origin-should-not-be-same-with-destination",
            ),
            models.CheckConstraint(
                condition=Q(arrival__gt=F("departure")),
                name="arrival-must-be-after-departure",
            ),
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="price-must-be-positive",
            ),
        ]
