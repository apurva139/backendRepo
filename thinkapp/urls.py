from django.urls import path,re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    RegisterView, LoginView, LogoutView, ChangePasswordView, ForgotPasswordView,
    AssignRoleView, DeleteAccountView,UserDetailView,UserListView,AdminUserListView, 
    AdminUserCreateView, AdminUserUpdateView, AdminUserDeleteView,
    ManagerUserListView, ManagerUserCreateView, ManagerUserUpdateView, 
    ManagerUserDeleteOwnAccountView,StudentUserListView, StudentUserUpdateView, StudentUserDeleteView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="ThinkProject API",
        default_version="v1",
        description="API documentation for ThinkProject",
        terms_of_service="https://www.yourwebsite.com/terms/",
        contact=openapi.Contact(email="admin@yourwebsite.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # Allow public access to documentation
    permission_classes=(permissions.AllowAny,),  # Allow anyone to view
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("assign-role/", AssignRoleView.as_view(), name="assign_role"), 
    # Delete own account
    path("delete-account/", DeleteAccountView.as_view(), name="delete_own_account"), 
    # For admin deleting others
    path("delete-account/<int:user_id>/", DeleteAccountView.as_view(), name="delete_user"),
    # List all users  
    path("users/", UserListView.as_view(), name="user_list"),  
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),

    # Admin Endpoints
    path("admin/users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("admin/users/create/", AdminUserCreateView.as_view(), name="admin_user_create"),
    path("admin/users/update/<int:pk>/", AdminUserUpdateView.as_view(), name="admin_user_update"),
    path("admin/users/delete/<int:pk>/", AdminUserDeleteView.as_view(), name="admin_user_delete"),

    # Manager Endpoints
    path("manager/users/", ManagerUserListView.as_view(), name="manager_user_list"),
    path("manager/users/create/", ManagerUserCreateView.as_view(), name="manager_user_create"),
    path("manager/users/update/<int:pk>/", ManagerUserUpdateView.as_view(), name="manager_user_update"),
    path("manager/users/delete/", ManagerUserDeleteOwnAccountView.as_view(), name="manager_user_delete"),  # Only delete self

    # Student Endpoints
    path("student/users/", StudentUserListView.as_view(), name="student_user_list"),
    path("student/users/update/", StudentUserUpdateView.as_view(), name="student_user_update"),  # Only update self
    path("student/users/delete/", StudentUserDeleteView.as_view(), name="student_user_delete"),  # Only delete self
    
    # Token Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Swagger Endpoint
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

]
