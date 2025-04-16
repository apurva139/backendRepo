from django.apps import AppConfig

class ThinkappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "thinkapp"

    def ready(self):
        import thinkapp.signals  # Import the signals file
