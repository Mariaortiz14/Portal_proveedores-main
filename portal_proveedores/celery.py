# myproject/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración predeterminado de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_proveedores.settings')

app = Celery('portal_proveedores')

# Usar una cadena aquí significa que no tiene que serializar
# la configuración del objeto de configuración en el child process.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir tareas en los módulos de aplicaciones de Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')



