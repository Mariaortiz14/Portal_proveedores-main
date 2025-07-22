from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# Verifica si pertenece al grupo Administrador
def es_administrador(user):
    return user.groups.filter(name='Administrador').exists()

@login_required
@user_passes_test(es_administrador)
def gestionar_usuarios(request):
    usuarios = User.objects.exclude(is_superuser=True)
    return render(request, 'administracion/usuarios/listar.html', {'usuarios': usuarios})

#funcion para mostrar el dashboard de administracion
def dashboard(request):
    return render(request, 'administracion/dashboard/index.html')