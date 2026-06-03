from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView  # type: ignore

from .views import (
    UserRegistrationViewset,
    OwnerRegistrationViewset,
    AccountLoginAPIView,
    AccountProfileAPIView,
)

account_router = DefaultRouter()
account_router.register(
    "user/register",
    UserRegistrationViewset,
    basename="user_registration_api",
)
account_router.register(
    "owner/register",
    OwnerRegistrationViewset,
    basename="owner_registration_api",
)

urlpatterns = [
    path("", include(account_router.urls)),
    path("account/login", AccountLoginAPIView.as_view()),
    path("accounts/me/", AccountProfileAPIView.as_view(), name="account-profile"),
    path("refresh-token/", TokenRefreshView.as_view(), name="refresh-token"),
]
