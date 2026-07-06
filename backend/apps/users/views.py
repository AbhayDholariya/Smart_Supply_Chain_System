from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    """Public endpoint to create a new user account."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the currently authenticated user's profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user


class UserListView(generics.ListAPIView):
    """Admin-only list of all users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated successfully."})
