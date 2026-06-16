from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):

    class AccountRole(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"
        OWNER = "owner", "Owner"

    username = models.CharField(blank=True, null=True, max_length=180)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(
        max_length=11,
        validators=[RegexValidator(r"^09\d{9}$")],
        help_text="format : 09XXXXXXXXX",
        unique=True,
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10, choices=AccountRole.choices, default=AccountRole.USER
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email", "username", "first_name", "last_name"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = Account.AccountRole.ADMIN
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = "account"