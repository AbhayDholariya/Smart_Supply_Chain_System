from django.urls import path
from .views import RegisterView, UserProfileView, UserListView, ChangePasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("all/", UserListView.as_view(), name="user-list"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
