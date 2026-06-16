from django.urls import path, include

urlpatterns = [
    path("", include("accounts.urls")),
    path("", include("companies.urls")),
    path("", include("bookings.urls")),
    path("", include("trips.urls")),
    path("", include("payments.urls")),
    path("", include("tickets.urls")),
]
