from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('actividad_economica/', views.actividad_economica, name='actividad_economica'),
    path('get_municipios/', views.get_municipios, name='get_municipios'),
    path('profile/', views.profile, name='comprador'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_, name='logout'),
    path('signup/', views.signup, name='signup'), 
    path('login/', views.login_, name='login'),
    #path('register/', views.signup, name='register'),
]

