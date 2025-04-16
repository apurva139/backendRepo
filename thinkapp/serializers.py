# 4th create serializers
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import CustomUser

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    # class Meta:
    #     model = CustomUser
    #     fields = ["id", "username", "email", "password", "role"]

    # def validate_email(self, value):
    #     """Check if email already exists."""
    #     if CustomUser.objects.filter(email=value).exists():
    #         raise serializers.ValidationError("A user with this email already exists.")
    #     return value

    # def create(self, validated_data):
    #     role = validated_data.pop("role", "student")  # Default to 'student' if no role provided

    #     # Create user
    #     user = CustomUser.objects.create_user(**validated_data, role=role)

    #     # Assign user to the correct group
    #     try:
    #         group = Group.objects.get(name=role)
    #         user.groups.add(group)
    #     except Group.DoesNotExist:
    #         raise serializers.ValidationError({"role": "Invalid role. Group does not exist."})

    #     return user
    confirmPassword = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'dob', 'empCode', 'mobile',
            'age', 'email', 'username', 'password', 'confirmPassword',
            'isAdmin', 'isActive', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmPassword')
        user = CustomUser.objects.create_user(**validated_data)
        return user

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)
    
#     def validate(self, data):
#         user = authenticate(username=data["username"], password=data["password"])
#         if user:
#             refresh = RefreshToken.for_user(user)
#             return {
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh),
#                 "role": user.role,
#             }
#         raise serializers.ValidationError("Invalid credentials")

# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         email = data.get("email")
#         password = data.get("password")

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid email or password")

#         user = authenticate(username=user.username, password=password)

#         if not user:
#             raise serializers.ValidationError("Invalid email or password")

#         # You can return JWT token or session here as per your auth method
#         return {
            
#             "message": "Login successful",
#             "user_id": user.id,
#             "email": user.email,
#             "username": user.username,
#             "role": user.role  # if you have roles
#         }

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        # ✅ Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "message": "Login successful",
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "access": str(access),
            "refresh": str(refresh),
        }
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# class UserListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ["id", "username", "email", "role"]  # Exclude password
