from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import propuestas_sol
from django.core.mail import EmailMessage

@receiver(post_save, sender=propuestas_sol)
def notificar_propuesta_creada(sender, instance, created, **kwargs):
    if created:
        print("🔔 Propuesta nueva guardada, enviar notificación...")
        email = EmailMessage(
            subject="Nueva propuesta registrada",
            body=f"Se ha recibido una nueva propuesta para la solicitud {instance.id_solicitud}.",
            to=["comprador@empresa.com"]
        )
        email.send()
