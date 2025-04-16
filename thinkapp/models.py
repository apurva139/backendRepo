# # 1 st create model
# from django.contrib.auth.models import AbstractUser, Group
# from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver

# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ("admin", "Admin"),
#         ("manager", "Manager"),
#         ("student", "Student"),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
#     # username = None  # Remove the username field

#     email = models.EmailField(unique=True)
#     # USERNAME_FIELD = "email"  # Use email for authentication
#     # REQUIRED_FIELDS = []  # Remove username requirement

#     # def __str__(self):
#     #     return self.email 

#     def __str__(self):
#         return self.username # included default username by inherited AbstractUser

# # Automatically assign users to groups based on their role
# @receiver(post_save, sender=CustomUser)
# def assign_group(sender, instance, created, **kwargs):
#     if created:
#         group, _ = Group.objects.get_or_create(name=instance.role)
#         instance.groups.add(group)

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("student", "Student"),
    )

    # Custom fields
    dob = models.DateField(null=True, blank=True)
    empCode = models.CharField(max_length=20, unique=True)
    mobile = models.CharField(max_length=15)
    age = models.PositiveIntegerField(null=True, blank=True)
    isAdmin = models.BooleanField(default=False)
    isActive = models.CharField(max_length=10, choices=[("active", "Active"), ("inactive", "Inactive")], default="active")

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    # Override fields from AbstractUser
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)  # still keeping username
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    REQUIRED_FIELDS = ['email']  # Required when creating superuser
    USERNAME_FIELD = 'username'  # you can change it to 'email' if desired

    def __str__(self):
        return self.username

# Automatically assign users to groups based on their role
@receiver(post_save, sender=CustomUser)
def assign_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name=instance.role)
        instance.groups.add(group)
