from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.message = "User is not authenticated. Please log in."
            return False
        if request.user.role != 'Admin':
            self.message = "Sorry, you don't have privileges."
            return False
        return True