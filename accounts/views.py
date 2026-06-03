from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from .serializers import (
    UserRegistrationSerializer,
    OwnerRegistrationSerializer,
    AccountLoginSerializer,
    AccountProfileSerializer,
)
from .models import Account
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework.permissions import IsAuthenticated


class UserRegistrationViewset(CreateModelMixin, GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserRegistrationSerializer(instance=user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class OwnerRegistrationViewset(CreateModelMixin, GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = OwnerRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        owner = serializer.save()
        refresh = RefreshToken.for_user(owner)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "owner": OwnerRegistrationSerializer(instance=owner).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AccountLoginAPIView(APIView):
    serializer_class = AccountLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data["account"]
        refresh_token = RefreshToken.for_user(account)
        access_token = refresh_token.access_token
        response_data = {
            "access": str(access_token),
            "refresh": str(refresh_token),
            "account": {
                "id": account.id,
                "first_name": account.first_name,
                "last_name": account.last_name,
                "role": account.role,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)


class AccountProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AccountProfileSerializer

    def get(self, request):
        account = request.user
        serializer = self.serializer_class(instance=account)
        return Response(serializer.data, status=status.HTTP_200_OK)


# from django.core.cache import cache
# import random


# class ForgotPasswordAPIView(APIView):
#     def post(self, request):
#         phone = request.data.get("phone")
#         try:
#             account = Account.objects.get(phone=phone, is_active=True)
#         except Account.DoesNotExist:
#             return Response({"error": "No account found"}, status=404)
#         otp = random.randint(100000, 999999)
#         cache_key = f"reset_pass_{phone}"
#         cache.set(cache_key, otp, timeout=300)
#         return Response({"message": "OTP sent successfully"})


# class VerifyOTPAPIView(APIView):
#     def post(self, request):
#         phone = request.data.get("phone")
#         user_otp = request.data.get("otp")
#         new_password = request.data.get("new_password")
#         cache_key = f"reset_pass_{phone}"
#         saved_otp = cache.get(cache_key)

#         if not saved_otp or str(saved_otp) != str(user_otp):
#             return Response({"error": "Invalid or expired OTP"}, status=400)
#         account = Account.objects.get(phone=phone)
#         account.set_password(new_password)
#         account.save()
#         cache.delete(cache_key)

#         return Response({"message": "Password reset successful"})
