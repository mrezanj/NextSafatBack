from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from .serializers import PaymentSerializer
from .models import Payment
from bookings.models import Booking
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class PaymentViewset(CreateModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        booking = payment.booking
        ticket_ids = None
        if booking.status == Booking.BookingStatus.PAID:
            ticket_ids = list(booking.tickets.values_list("id", flat=True))
        data = {
            "payment": self.get_serializer(payment).data,
            "ticket_ids": ticket_ids,
        }
        return Response(
            data=data,
            status=status.HTTP_201_CREATED,
        )
