from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Bus, Company


class BusSerializer(ModelSerializer):
    company = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Bus
        fields = ["id", "company", "name", "type", "seat_count", "created_at"]
