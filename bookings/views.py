from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer
from utils.permissions import IsUser
from django.db.models import Count, Q, Sum


class BookingViewset(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.AccountRole.OWNER and hasattr(user, "company"):
            return (
                Booking.objects.filter(trip__company=user.company)
                .select_related("trip", "user")
                .prefetch_related("passengers")
            )
        return (
            Booking.objects.filter(user=user)
            .select_related("trip")
            .prefetch_related("passengers")
        )

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsUser()]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_denied(
                self.request,
                message="Direct updates not allowed. Use /cancel/ endpoints to change status only",
            )

        return super().get_permissions()

    def list(self, request):
        queryset = self.get_queryset().order_by("-created_at")
        status = request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        booking.mark_expired_if_needed()
        if booking.status == Booking.BookingStatus.PAID:
            return Response(
                {"error": "Cannot cancel a paid booking. Please contact support."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.status == Booking.BookingStatus.EXPIRED:
            return Response(
                {"error": "Cannot cancel an expired booking"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.status == Booking.BookingStatus.CANCELED:
            return Response(
                {"error": "Booking is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.BookingStatus.CANCELED
        booking.save(update_fields=["status"])

        return Response(
            {
                "message": "Booking cancelled successfully",
                "booking_id": booking.id,
                "status": booking.status,
                "cancelled_by": (
                    "user"
                    if request.user.role == request.user.AccountRole.USER
                    else "company_owner"
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        bookings = self.get_queryset()
        for booking in bookings:
            booking.mark_expired_if_needed()

        statistics = bookings.aggregate(
            total_bookings=Count("id"),
            paid_bookings=Count("id", filter=Q(status=Booking.BookingStatus.PAID)),
            pending_bookings=Count(
                "id", filter=Q(status=Booking.BookingStatus.PENDING_PAYMENT)
            ),
            cancelled_bookings=Count(
                "id", filter=Q(status=Booking.BookingStatus.CANCELED)
            ),
            expired_bookings=Count(
                "id", filter=Q(status=Booking.BookingStatus.EXPIRED)
            ),
            total_revenue=Sum(
                "total_price", filter=Q(status=Booking.BookingStatus.PAID)
            ),
        )

        return Response(statistics, status=status.HTTP_200_OK)
