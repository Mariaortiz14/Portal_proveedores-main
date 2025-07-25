from django import forms
from django.contrib.auth.models import User, Group
from django import forms
from django.contrib.auth.models import User, Group

# Formulario para crear un nuevo usuario
class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': ' '
        })
    )

    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label='Asignar grupo',
        widget=forms.Select(attrs={
            'class': 'input',
            'placeholder': ' '
        })
    )

    username = forms.CharField(
        label="Nombre de acceso",
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': ' '
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input',
            'placeholder': ' '
        }),
        required=False 
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'grupo']