from django.urls import path, include
from .views import PaymentViewset
from rest_framework.routers import DefaultRouter

payment_router = DefaultRouter()
payment_router.register("payments/pay", PaymentViewset, basename="payment_api")

urlpatterns = [
    path("", include(payment_router.urls)),
]
