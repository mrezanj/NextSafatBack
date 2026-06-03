from django.urls import path, include
from .views import TicketViewset
from rest_framework.routers import DefaultRouter

ticket_router = DefaultRouter()
ticket_router.register("tickets", TicketViewset, basename="ticket_api")
urlpatterns = [
    path("", include(ticket_router.urls)),
]
