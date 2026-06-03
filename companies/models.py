from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.OneToOneField(
        "accounts.Account", on_delete=models.CASCADE, related_name="company"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.owner and self.owner.role != "owner":
            raise ValidationError({"owner": "account role must be owner"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        db_table = "company"


class Bus(models.Model):

    class BusType(models.TextChoices):
        NORMAL = "normal", "Normal"
        VIP = "vip", "VIP"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="buses")
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10, choices=BusType.choices, default=BusType.NORMAL
    )
    seat_count = models.PositiveSmallIntegerField(
        default=25,
        validators=[
            MinValueValidator(15, message="Your Bus must have At least 15 seats")
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + "-" + self.type

    class Meta:
        verbose_name_plural = "Buses"
        db_table = "bus"


class Seat(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="seats")
    number = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"bus:{self.bus} number:{self.number}"

    class Meta:
        db_table = "seat"


@receiver(signal=post_save, sender=Bus)
def generate_bus_seats(sender, instance, created, **kwargs):
    if created:
        for number in range(1, instance.seat_count + 1):
            Seat.objects.create(bus=instance, number=number)
