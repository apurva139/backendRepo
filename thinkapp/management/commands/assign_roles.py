from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from thinkapp.models import CustomUser

class Command(BaseCommand):
    help = "Create default user groups and assign permissions"

    def handle(self, *args, **kwargs):
        # Create Groups
        admin_group, _ = Group.objects.get_or_create(name="admin")
        manager_group, _ = Group.objects.get_or_create(name="manager")
        student_group, _ = Group.objects.get_or_create(name="student")

        # Get all user permissions
        all_permissions = Permission.objects.filter(content_type__app_label="thinkapp")

        # Assign Permissions
        admin_group.permissions.set(all_permissions)  # Admin has all permissions

        # Manager Permissions (All user permissions except deleting others' accounts)
        manager_permissions = all_permissions.exclude(codename="delete_customuser")
        manager_group.permissions.set(manager_permissions)

        # Student Permissions (Can view all users, but only manage their own account)
        student_permissions = [
            "view_customuser",
            "add_customuser",
            "change_customuser",
            "delete_customuser",
        ]
        student_group.permissions.set(Permission.objects.filter(codename__in=student_permissions))

        self.stdout.write(self.style.SUCCESS("Groups and permissions assigned successfully!"))
