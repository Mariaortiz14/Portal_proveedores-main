from logging import PlaceHolder
from mimetypes import init
from pydoc import doc
import re
from django import contrib, forms
from django.forms import formset_factory
from datetime import date
from django.contrib.auth.models import User

class form_propuesta(forms.Form):
    descripcion= forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control ', 'rows': 4, 'placeholder': 'Descripción'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control '}))
    valor_t = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control ', 'placeholder': 'Valor Total'}))
    tiempo_entrega_min = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control ', 'placeholder': 'Tiempo Mínimo'}))
    tiempo_entrega_max = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control ', 'placeholder': 'Tiempo Máximo'}), required=False)    
    moneda = forms.ChoiceField(choices=[('USD', 'USD'), ('COP', 'COP')], widget=forms.Select(attrs={'class': 'form-control '}))
    garantia = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Garantía'}))
    t_pago = forms.ChoiceField(choices=[('Anticipado', 'Anticipado'), ('Contra Entrega', 'Contra Entrega' ), ('50% Anticipo + 50% Contra Entrega','50% Anticipo + 50% Contra Entrega' ), ('60% Anticipo + 40% Contra Entrega', '60% Anticipo + 40% Contra Entrega') ], widget=forms.Select(attrs={'class': 'form-control '}))
    validez = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control ', 'placeholder': 'Validez'}), required=False)