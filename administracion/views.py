from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from compras.models import solicitud
from proveedores.models import propuestas_sol
from logistica.models import SolicitudIngreso

def dashboard_administracion(request):
    total_compras = solicitud.objects.count()
    total_logistica = SolicitudIngreso.objects.count()
    total_proveedores = propuestas_sol.objects.values('id_homologacion').distinct().count()
    total_usuarios = User.objects.exclude(is_superuser=True).count()

    grafico_data = {
        "compras": total_compras,
        "logistica": total_logistica,
        "proveedores": total_proveedores,
        "usuarios": total_usuarios,
    }

    return render(request, 'administracion/dashboard/index.html', {"grafico_data": grafico_data})

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

@user_passes_test(lambda u: hasattr(u, 'groups') and u.groups.filter(name='Administrador').exists()) # type: ignore
def gestionar_grupos(request):
    grupos = Group.objects.all()
    return render(request, 'administracion/grupos/listar.html', {'grupos': grupos})