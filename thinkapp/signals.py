# 2nd create signals
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from .models import CustomUser  # Import your CustomUser model

@receiver(post_migrate)
def create_user_roles(sender, **kwargs):
    if sender.name != "thinkapp":  # Replace with your app name
        return

    # Get content type for CustomUser model
    user_content_type = ContentType.objects.get_for_model(CustomUser)

    # Define groups and their permissions

    roles_permissions = {
    "admin": ["add_customuser", "change_customuser", "delete_customuser", "view_customuser"],
    "manager": ["add_customuser", "change_customuser", "view_customuser", "delete_customuser"],  # Can delete only self
    "student": ["change_customuser", "delete_customuser", "view_customuser"],  # Can only modify their own account
}

    # Create valid groups and assign permissions
    for role, permissions in roles_permissions.items():
        group, _ = Group.objects.get_or_create(name=role)
        for perm in permissions:
            permission = Permission.objects.get(codename=perm, content_type=user_content_type)
            group.permissions.add(permission)

    print("Roles and permissions successfully created!")
