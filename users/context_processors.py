from proveedores.models import registro_formulario

def foto_perfil(request):
    if request.user.is_authenticated:
        registro = registro_formulario.objects.filter(usuario=request.user).first()
        return {'foto_perfil': registro.foto.url if registro and registro.foto else None}
    return {'foto_perfil': None}
