from rest_framework.viewsets import ModelViewSet
from .serializers import BusSerializer
from .models import Bus
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.permissions import IsCompanyOwner
from rest_framework.pagination import PageNumberPagination


class CustomBusPagination(PageNumberPagination):
    page_size = 20


class BusViewset(ModelViewSet):
    serializer_class = BusSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCompanyOwner]
    pagination_class = CustomBusPagination

    def get_queryset(self):
        return Bus.objects.filter(company=self.request.user.company)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)
