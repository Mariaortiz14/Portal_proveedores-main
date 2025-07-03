from django import template
register = template.Library()

@register.filter
def get_homologacion_id(homologaciones, user):
    for h in homologaciones:
        if h.usuario_hologa == user:
            return h.id_registro.id
    return h.id_registro_id 