from rest_framework import serializers
from companies.models import Company
from accounts.models import Account
from django.db import transaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone", "email", "password"]

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")

        if Account.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                {"phone": "This phone has already registered"}
            )
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "This email has already registered"}
            )

        return attrs

    def create(self, validated_data):
        arrived_phone = validated_data.get("phone")
        user = Account.objects.create_user(
            **validated_data,
            username=f"username{arrived_phone}",
            role=Account.AccountRole.USER,
        )
        return user


class OwnerRegistrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "password",
            "company_name",
        ]

    def validate(self, attrs):
        phone = attrs.get("phone")
        email = attrs.get("email")
        company_name = attrs.get("company_name")
        if Account.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                {"phone": "This phone has already registered"}
            )
        if Account.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "This email has already registered"}
            )

        if Company.objects.filter(name=company_name).exists():
            raise serializers.ValidationError(
                {"company_name": "company name must be unqiue"}
            )

        return attrs

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")
        arrived_phone = validated_data.get("phone")
        owner = None

        with transaction.atomic():
            try:
                owner = Account.objects.create_user(
                    **validated_data,
                    username=f"username{arrived_phone}",
                    role=Account.AccountRole.OWNER,
                )
                Company.objects.create(name=company_name, owner=owner)
            except Exception as e:
                raise serializers.ValidationError(
                    f"Registration failed due to an error: {e}"
                )

        return owner


class AccountLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")
        account = Account.objects.filter(phone=phone).first()
        if not account or not account.is_active or not account.check_password(password):
            raise serializers.ValidationError("Invalid credentials")
        attrs["account"] = account
        return attrs


class AccountProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "role",
            "company_name",
        ]
        read_only_fields = ["id", "first_name", "last_name", "phone", "email", "role"]

    def get_company_name(self, obj):
        if (
            obj.role == Account.AccountRole.OWNER
            and hasattr(obj, "company")
            and obj.company
        ):
            return obj.company.name
        return None
