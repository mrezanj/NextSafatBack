from rest_framework.permissions import BasePermission
from accounts.models import Account


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        account: Account = request.user
        return (
            hasattr(account, "company")
            and getattr(account.company, "owner_id", None) == account.id
        )


class IsCompanyOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        else:
            return IsCompanyOwner().has_permission(request=request, view=view)


class IsUser(BasePermission):
    def has_permission(self, request, view):
        account: Account = request.user
        return getattr(account, "role", None) == Account.AccountRole.USER
