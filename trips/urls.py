from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewset, TripViewset

trip_router = DefaultRouter()
trip_router.register("cities", CityViewset, basename="city_api")
trip_router.register("company/trips", TripViewset, basename="trip_api")

urlpatterns = [
    path("", include(trip_router.urls)),
]
