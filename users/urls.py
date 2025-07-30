from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('actividad_economica/', views.actividad_economica, name='actividad_economica'),
    path('get_municipios/', views.get_municipios, name='get_municipios'),
    
    path('login/', views.login_, name='login'),
    path('signup/', views.signup, name='signup'),
    path('register/', views.signup, name='register'),
    path('logout/', views.logout_, name='logout'),

    # Recuperación de contraseña
    path('olvide-contrasena/', views.forgot_password, name='forgot_password'),
    path('restablecer-contrasena/<str:username>/', views.reset_password, name='reset_password'),

    # Perfil
    path('profile/', views.profile, name='profile'),
]
