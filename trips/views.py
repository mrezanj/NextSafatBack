from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .serializers import CitySerializer, TripSerializer
from .models import City, Trip
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from utils.permissions import IsCompanyOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination
from bookings.models import Booking


class CustomTripPagination(PageNumberPagination):
    page_size = 10


class CityViewset(ReadOnlyModelViewSet):
    queryset = City.objects.all().order_by("name")
    serializer_class = CitySerializer
    permission_classes = [AllowAny]


class TripViewset(ModelViewSet):
    serializer_class = TripSerializer
    authentication_classes = [JWTAuthentication]
    pagination_class = CustomTripPagination

    def get_queryset(self):
        user = self.request.user
        if (
            user.is_authenticated
            and hasattr(user, "company")
            and getattr(user, "company", None)
        ):
            return Trip.objects.filter(company=user.company)
        return Trip.objects.all()

    def get_permissions(self):
        if self.action in ["list", "retrieve", "search", "seats"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsCompanyOwnerOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)

    @action(detail=False, methods=["get"])
    def search(self, request: Request):
        trips = self.get_queryset()
        origin = request.query_params.get("origin")
        destination = request.query_params.get("destination")
        date = request.query_params.get("date")
        if origin:
            trips = trips.filter(origin_city__name__iexact=origin)
        if destination:
            trips = trips.filter(destination_city__name__iexact=destination)
        if date:
            trips = trips.filter(departure__date=date)
        if trips.exists():
            serializer: TripSerializer = self.get_serializer(instance=trips, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "No Trip Found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["get"])
    def seats(self, request: Request, pk=None):
        trip = self.get_object()
        trip_seats = trip.bus.seats.all()
        seats_data = []
        for seat in trip_seats:
            seats_data.append(
                {"id": seat.id, "number": seat.number, "status": "available"}
            )
        passengers = trip.passengers.select_related("seat", "booking")
        for passenger in passengers:
            booking = passenger.booking
            seat_id = passenger.seat.id
            for seat_data in seats_data:
                if seat_data["id"] == seat_id:
                    if booking.status == Booking.BookingStatus.PENDING_PAYMENT:
                        seat_data["status"] = "reserved"
                    elif booking.status == Booking.BookingStatus.PAID:
                        seat_data["status"] = "unavailable"
                    break

        return Response(seats_data, status=status.HTTP_200_OK)
