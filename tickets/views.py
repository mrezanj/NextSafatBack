from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated


class TicketViewset(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == user.AccountRole.OWNER and hasattr(user, "company"):
            return Ticket.objects.filter(booking__trip__company=user.company)
        return Ticket.objects.filter(booking__user=user)
