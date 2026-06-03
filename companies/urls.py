from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusViewset

company_router = DefaultRouter()
company_router.register("company/buses", BusViewset, basename="bus_api")
urlpatterns = [
    path("", include(company_router.urls)),
]
