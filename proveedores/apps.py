from django.apps import AppConfig


class ProveedoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proveedores'
    
def ready(self):
    import proveedores.signals
