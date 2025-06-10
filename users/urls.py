from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('signup/', views.signup, name='signup'), 
    path('login/', views.login_, name='login'),
    path('logout/', views.logout_, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('actividad_economica/', views.actividad_economica, name='actividad_economica'),
    path('get_municipios/', views.get_municipios, name='get_municipios'),
    # Otras rutas relacionadas con los usuarios
]

#path('logout/', views.logout, name='logout')
#path('profile/', views.profile, name='profile'),
