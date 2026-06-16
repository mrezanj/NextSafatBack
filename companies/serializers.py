from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Bus


class BusSerializer(ModelSerializer):
    company = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Bus
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)
