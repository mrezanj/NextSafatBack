from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewset

trip_router = DefaultRouter()
trip_router.register("company/trips", TripViewset, basename="trip_api")

urlpatterns = [
    path("", include(trip_router.urls)),
]
