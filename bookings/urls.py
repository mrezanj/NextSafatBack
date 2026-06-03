from django.urls import path, include
from .views import BookingViewset
from rest_framework.routers import DefaultRouter

booking_router = DefaultRouter()
booking_router.register("bookings", BookingViewset, basename="booking_api")

urlpatterns = [
    path("", include(booking_router.urls)),
]
