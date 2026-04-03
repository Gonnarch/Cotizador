from django import forms

class ListaForm(forms.Form):
    imagen = forms.ImageField()