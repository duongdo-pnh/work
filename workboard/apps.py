from django.apps import AppConfig


class WorkboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workboard'
    def ready(self):
        import workboard.signals  
