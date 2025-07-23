from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from compras.models import solicitud
from proveedores.models import propuestas_sol
from logistica.models import SolicitudIngreso
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CrearUsuarioForm

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

def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # encriptar
            user.save()
            grupo = form.cleaned_data['grupo']
            user.groups.add(grupo)
            return redirect('administracion:gestionar_usuarios')
    else:
        form = CrearUsuarioForm()

    return render(request, 'administracion/usuarios/crear_usuario.html', {'form': form})

def detalle_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        if 'activar' in request.POST:
            usuario.is_active = True
            usuario.save()
        elif 'desactivar' in request.POST:
            usuario.is_active = False
            usuario.save()
        elif 'actualizar' in request.POST:
            nuevo_username = request.POST.get('username')
            nueva_password = request.POST.get('password')
            if nuevo_username:
                usuario.username = nuevo_username
            if nueva_password:
                usuario.set_password(nueva_password)
            usuario.save()
            messages.success(request, "Usuario actualizado con éxito.")
            return redirect('administracion:detalle_usuario', usuario_id=usuario.pk)

    return render(request, 'administracion/usuarios/detalle.html', {'usuario': usuario})