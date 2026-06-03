from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Account(AbstractUser):

    class AccountRole(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"
        OWNER = "owner", "Owner"

    username = models.CharField(blank=True, null=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    phone = models.CharField(
        _("phone number"),
        max_length=11,
        validators=[RegexValidator(r"^09\d{9}$")],
        help_text="format : 09XXXXXXXXX",
        unique=True,
    )
    email = models.EmailField(_("email"), unique=True)
    role = models.CharField(
        _("role"), max_length=10, choices=AccountRole.choices, default=AccountRole.USER
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email", "username"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = Account.AccountRole.ADMIN
        # self.username = f"username_{self.phon}"
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.phone

    class Meta:
        db_table = "account"
