# 5th create views
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import (
    UserRegisterSerializer, LoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer
)
from .models import CustomUser
from rest_framework import generics
from django.contrib.auth.models import Group
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]  # Allow registration for all

    @swagger_auto_schema(tags=['auth'],
                        #  security=[],
                         request_body=UserRegisterSerializer)
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     @swagger_auto_schema(
#             tags=['auth'], 
#             # security=[],
#             request_body=LoginSerializer
#             )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.validated_data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    @swagger_auto_schema(
        tags=['auth'], 
        request_body=LoginSerializer
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        tags=['auth'],
        # operation_summary="Logout API",
        operation_description="Logs out the user by blacklisting the refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="Refresh token for logout"
                ),
            },
        ),
        responses={
            200: "Successfully logged out",
            400: "Invalid or missing refresh token"
        }
    )
    def post(self, request):
        try:
            # Extract refresh token from the request body
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Decode the refresh token and blacklist it
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags=['auth'],request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not check_password(serializer.validated_data["old_password"], user.password):
                return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            user.password = make_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    @swagger_auto_schema(tags=['auth'],request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, email=serializer.validated_data["email"])
            token = default_token_generator.make_token(user)
            # Normally, you would send an email with a reset link
            return Response({"message": "Password reset link sent", "token": token}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TokenRefreshView(APIView):
#     # @swagger_auto_schema(tags=['refreshToken'])
#     @swagger_auto_schema(
#         tags=['auth'],
#         operation_summary="Refresh Access Token",
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             required=["refresh"],  # This field is required in the request
#             properties={
#                 "refresh": openapi.Schema(
#                     type=openapi.TYPE_STRING,
#                     description="The refresh token obtained during login."
#                 )
#             }
#         ),
#         responses={
#             200: openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     "access": openapi.Schema(
#                         type=openapi.TYPE_STRING,
#                         description="The new access token"
#                     )
#                 }
#             ),
#             400: openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     "error": openapi.Schema(
#                         type=openapi.TYPE_STRING,
#                         description="Invalid token error message"
#                     )
#                 }
#             )
#         }
#     )
    
#     def post(self, request):
#         try:
#             refresh_token = request.data["refresh"]
#             token = RefreshToken(refresh_token)
#             return Response({"access": str(token.access_token)}, status=status.HTTP_200_OK)
#         except Exception:
#             return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class MyPagination(PageNumberPagination):
        page_size_query_param = 'page_size'
        max_page_size = 100  # Optional, limits the maximum page size

class UserListView(generics.ListAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MyPagination


    def get_queryset(self):
        queryset = CustomUser.objects.all()
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        search_query = self.request.query_params.get('search', None)
        search_first_name = self.request.query_params.get("search_first_name", None)

        if search_first_name:
              return  queryset.filter(
                Q(first_name__icontains=search_first_name)
            )
            
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
            )
            
        return queryset
    # def get_paginated_response(self, data):
    #     print(data,"::::::::::::::::::::;")
    #     return super().get_paginated_response(data)
    # def paginate_queryset(self, queryset):
    #     print(":::::::::", queryset)

    #     page = super().paginate_queryset(queryset)
    #     print(page, "::::::::::::::::::")
    #     return page
    # def get(self, request, *args, **kwargs):
    #     print("::::::::::::::::::")
    #     return super().get(request, *args, **kwargs)
    


class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can view details
    lookup_field = "pk"  # Retrieve user by primary key (ID)


class AssignRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # @swagger_auto_schema(tags=[])
    def post(self, request):
        print("Request Data:", request.data)  
        print("Data Type:", type(request.data))
        print("User:", request.user)
        print("User Role:", request.user.role)
        if request.user.role != "admin":
            return Response({"error": "Only Admin can assign roles"}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("id")  # Get user ID from payload
        new_role = request.data.get("role")  # Get role from payload

        if not user_id or not new_role:
            return Response({"error": "User ID and role are required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_role not in ["admin", "manager", "student"]:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
            user.role = new_role
            user.save()

            # # Convert role to match the Group name (Title Case: "Admin", "Manager", "Student")
            # group_name = new_role.capitalize()
            # group = Group.objects.get(name=group_name)

            # user.groups.clear()  # Remove previous group
            # user.groups.add(group)
            
            # Assign the user to the appropriate group
            group = Group.objects.get(name=new_role)
            user.groups.clear()  # Remove previous group
            user.groups.add(group)

            return Response({"message": f"Role updated to {new_role} for user {user.username}"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Role group not found"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id=None):
        user = request.user

        if user.role == "admin":
            # Admin can delete any user by ID (except themselves)
            if not user_id:
                return Response({"error": "User ID required for admin"}, status=status.HTTP_400_BAD_REQUEST)

            if user.id == user_id:
                return Response({"error": "Admin cannot delete their own account"}, status=status.HTTP_403_FORBIDDEN)

            user_to_delete = get_object_or_404(CustomUser, id=user_id)
            user_to_delete.delete()
            return Response({"message": f"User {user_to_delete.username} deleted by Admin"}, status=status.HTTP_200_OK)

        elif user.role in ["manager", "student"]:
            # Managers and Students can only delete their own accounts
            if user_id and user_id != user.id:
                return Response({"error": "You can only delete your own account"}, status=status.HTTP_403_FORBIDDEN)

            username = user.username
            user.delete()
            return Response({"message": f"Account {username} deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Unauthorized action"}, status=status.HTTP_403_FORBIDDEN)

# ------------- Admin view --------------
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin, IsManager, IsStudent

class AdminUserListView(APIView):
    """Admin can view all users."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminUserCreateView(APIView):
    """Admin can add new users."""
    permission_classes = [IsAuthenticated, IsAdmin]

    
    @swagger_auto_schema(
        tags=['admin'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "email", "password", "role"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, example="admincreated2"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, example="newadminuser2@example.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, example="Admin@123"),
                "role": openapi.Schema(type=openapi.TYPE_STRING, example="student")  # or "manager"
            }
        ),
        responses={201: "User Created", 400: "Bad Request", 403: "Forbidden"}
    )

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent non-superusers from creating Admin users
            if request.user.role != "admin" and serializer.validated_data["role"] == "admin":
                return Response({"error": "You cannot create an Admin user."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUserUpdateView(APIView):
    """Admin can update any user."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserRegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent role change to admin by unauthorized users
            if request.user.role != "admin" and serializer.validated_data.get("role") == "admin":
                return Response({"error": "You cannot change a user to Admin."}, status=status.HTTP_403_FORBIDDEN)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUserDeleteView(APIView):
    """Admin can delete any user."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# --------- Manager Views ---------
class ManagerUserListView(APIView):
    """Manager can view all users."""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ManagerUserCreateView(APIView):
    """Manager can add new users (but not Admins)."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Prevent Manager from creating an Admin user
            if serializer.validated_data["role"] == "admin":
                return Response({"error": "Managers cannot create Admin users."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManagerUserUpdateView(APIView):
    """Manager can update any user (but not roles)."""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent role changes
            if "role" in serializer.validated_data:
                return Response({"error": "Managers cannot change user roles."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManagerUserDeleteOwnAccountView(APIView):
    """Manager can delete only their own account."""
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Your account has been deleted"}, status=status.HTTP_204_NO_CONTENT)

# --------- Student Views ---------
class StudentUserListView(APIView):
    """Student can view all users (but cannot edit them)."""
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        users = CustomUser.objects.all()  # Should this be limited?
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentUserUpdateView(APIView):
    """Student can update only their own account (but not role)."""
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request):
        user = request.user  # Only allow updating own account
        serializer = UserRegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Prevent students from updating their role
            if "role" in serializer.validated_data:
                return Response({"error": "Students cannot change their role."}, status=status.HTTP_403_FORBIDDEN)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentUserDeleteView(APIView):
    """Student can delete only their own account."""
    permission_classes = [IsAuthenticated, IsStudent]

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Your account has been deleted"}, status=status.HTTP_204_NO_CONTENT)