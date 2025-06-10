# myapp/tasks.py
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings

@shared_task
def my_task(): 
    print('Hello from Celery!')
    return

@shared_task
def send_email_task(subject, from_email, recipient_list, template_name, context):
    # Carga la plantilla HTML
    template = get_template(template_name)
    
    # Renderiza la plantilla con el contexto proporcionado
    content = template.render(context)
    
    # Crea el mensaje de correo electrónico
    message = EmailMultiAlternatives(
        subject,  # Título
        '',  # El cuerpo del mensaje en texto plano (puede estar vacío si solo enviarás HTML)
        from_email,  # Remitente
        recipient_list  # Destinatario(s)
    )
    
    # Adjunta el contenido HTML
    message.attach_alternative(content, 'text/html')
    
    # Envía el correo
    message.send()
